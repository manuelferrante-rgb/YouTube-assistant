#!/usr/bin/env python3
"""Discesa dallo spazio fino a un punto della Terra (verticale 1080x1920), con immagini satellitari vere.

Immagini (scaricate con --fetch nella cartella --tiles):
  - Terra e zoom intermedi: "Blue Marble" (NASA) dal servizio di mappe EOX, livelli 4, 6, 8.
  - Ultimi livelli: "Sentinel-2 cloudless 2016" di EOX (CC BY 4.0), livelli 10, 12, 14.
    Attribuzione da mettere in descrizione: "Sentinel-2 cloudless 2016 by EOX IT Services GmbH (contains modified
    Copernicus Sentinel data 2016), CC BY 4.0; Blue Marble: NASA".
La camera guarda in basso (nadir) e scende in modo esponenziale; il punto sotto la camera scivola verso il bersaglio
e il quadro ruota un po'. Alla fine le nuvole (procedurali) passano davanti e si va al bianco.
    python3 tools/space_zoom.py out_dir --lat 10.0417 --lon 77.0393 [--fetch] [--dur 3.3]
Scrive out_dir/%04d.png (fotogrammi a 30 fps).
"""
import argparse, math, os, subprocess, concurrent.futures as cf
import numpy as np, cv2

R = 6371.0
W, H, FPS = 1080, 1920, 30
HFOV = math.radians(28.0)
F = (W / 2) / math.tan(HFOV / 2)
LEVELS = [("bluemarble_3857", 6), ("bluemarble_3857", 8), ("s2cloudless_3857", 10), ("s2cloudless_3857", 12),
          ("s2cloudless_3857", 14)]


def tile_xy(lat, lon, z):
    n = 2 ** z
    return (lon + 180) / 360 * n, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n


def fetch(tiles, lat, lon):
    os.makedirs(tiles, exist_ok=True)
    jobs = [("bluemarble_3857", 4, x, y) for x in range(16) for y in range(16)]
    for layer, z in LEVELS:
        cx, cy = tile_xy(lat, lon, z)
        jobs += [(layer, z, x, y) for x in range(int(cx) - 8, int(cx) + 8) for y in range(int(cy) - 8, int(cy) + 8)]

    def get(j):
        layer, z, x, y = j
        p = f"{tiles}/{layer}_{z}_{x}_{y}.img"
        if os.path.exists(p) and os.path.getsize(p):
            return 0
        u = f"https://tiles.maps.eox.at/wmts/1.0.0/{layer}/default/g/{z}/{y}/{x}.jpg"
        return min(subprocess.run(["curl", "-sS", "-f", "--max-time", "40", "-o", p, u]).returncode for _ in range(1))
    with cf.ThreadPoolExecutor(16) as ex:
        bad = sum(1 for r in ex.map(get, jobs) if r)
    if bad:
        raise SystemExit(f"{bad} tile non scaricate")


class Level:
    """Mosaico mercatore (16x16 tile) a livello z, con le sue versioni ridotte (mip)."""
    def __init__(self, tiles, layer, z, lat, lon, glob=False):
        n = 2 ** z
        if glob:
            x0 = y0 = 0
        else:
            cx, cy = tile_xy(lat, lon, z)
            x0, y0 = int(cx) - 8, int(cy) - 8
        M = np.zeros((4096, 4096, 3), np.uint8)
        for i in range(16):
            for j in range(16):
                im = cv2.imread(f"{tiles}/{layer}_{z}_{x0 + i}_{y0 + j}.img")
                if im is not None:
                    M[j * 256:(j + 1) * 256, i * 256:(i + 1) * 256] = cv2.resize(im, (256, 256))
        self.z, self.x0, self.y0, self.glob = z, x0 * 256, y0 * 256, glob
        self.mips = [M.astype(np.float32)]
        for _ in range(4):
            self.mips.append(cv2.resize(self.mips[-1], None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))

    def sample(self, lat, lon, zf):
        """Campiona dove il mosaico copre il punto; zf = livello ideale (texel ~ pixel). -> (rgb, peso)."""
        k = int(np.clip(round(self.z - zf), 0, len(self.mips) - 1))
        M = self.mips[k]
        s = 256 * 2 ** self.z
        X = (lon + 180) / 360 * s - self.x0
        Y = (1 - np.arcsinh(np.tan(np.radians(np.clip(lat, -85, 85)))) / np.pi) / 2 * s - self.y0
        if self.glob:
            X = np.mod(X, 4096)
        X, Y = (X / 2 ** k).astype(np.float32), (Y / 2 ** k).astype(np.float32)
        S = M.shape[0]
        rgb = cv2.remap(M, X, Y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT if self.glob else cv2.BORDER_CONSTANT)
        if self.glob:
            return rgb, np.ones(X.shape, np.float32)
        e = np.minimum(np.minimum(X, S - X), np.minimum(Y, S - Y)) / (S * 0.08)   # bordo sfumato
        return rgb, np.clip(e, 0, 1).astype(np.float32)


def ease(u):
    return u * u * (3 - 2 * u)


def fbm(h, w, seed, octaves=6):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        s = 2 ** (o + 2)
        n = rng.random((s, int(s * w / h) + 1)).astype(np.float32)
        out += amp * cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC)
        tot += amp
        amp *= 0.55
    return out / tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--tiles", default=None)
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--dur", type=float, default=3.3)
    ap.add_argument("--h0", type=float, default=26000.0)     # km
    ap.add_argument("--h1", type=float, default=9.0)
    ap.add_argument("--start", default="22,62")              # punto sotto la camera all'inizio (lat,lon)
    ap.add_argument("--roll", type=float, default=-35.0)     # gradi di rotazione in tutta la discesa
    ap.add_argument("--clouds", type=float, default=0.75)    # secondi finali con le nuvole
    ap.add_argument("--size", default="1080x1920")           # 3840x2160 per il lungo 16:9 (te v10)
    ap.add_argument("--fov", type=float, default=28.0)       # gradi in orizzontale (16:9: ~48, stessa copertura del verticale)
    a = ap.parse_args()
    global W, H, F
    W, H = map(int, a.size.split("x"))
    F = (W / 2) / math.tan(math.radians(a.fov) / 2)
    tiles = a.tiles or os.path.join(a.out, "..", "tiles")
    if a.fetch:
        fetch(tiles, a.lat, a.lon)
    os.makedirs(a.out, exist_ok=True)
    levels = [Level(tiles, "bluemarble_3857", 4, a.lat, a.lon, glob=True)] + \
             [Level(tiles, l, z, a.lat, a.lon) for l, z in LEVELS]
    lat0, lon0 = map(float, a.start.split(","))
    N = int(round(a.dur * FPS))
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    px, py = xs - W / 2 + 0.5, ys - H / 2 + 0.5
    rng = np.random.default_rng(7)
    stars = np.zeros((H, W), np.float32)
    ns = int(900 * W * H / (1080 * 1920))
    idx = rng.integers(0, H * W, ns)
    stars.flat[idx] = rng.random(ns) ** 3 * 0.9
    stars = cv2.GaussianBlur(stars, (3, 3), 0.6)
    cl = [fbm(H, W, s) for s in (1, 2, 3)]
    for i in range(N):
        u = i / max(1, N - 1)
        # discesa: lenta all'inizio, veloce a metà, un filo più lenta prima delle nuvole
        s = ease(min(1.0, u * 1.03))
        h = math.exp(math.log(a.h0) + (math.log(a.h1) - math.log(a.h0)) * s)
        m = ease(min(1.0, u / 0.7))
        clat = lat0 + (a.lat - lat0) * m
        clon = lon0 + (a.lon - lon0) * m
        roll = math.radians(a.roll * s)
        # base locale al punto sotto la camera
        la, lo = math.radians(clat), math.radians(clon)
        n = np.array([math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la)])
        e = np.array([-math.sin(lo), math.cos(lo), 0.0])
        nn = np.cross(n, e)
        cr, sr = math.cos(roll), math.sin(roll)
        qx, qy = px * cr - py * sr, px * sr + py * cr
        d = (-n[:, None, None] * F + e[:, None, None] * qx + nn[:, None, None] * (-qy))
        d /= np.linalg.norm(d, axis=0, keepdims=True)
        P = n * (R + h)
        b = np.tensordot(P, d, axes=(0, 0))
        c = P @ P - R * R
        disc = b * b - c
        hit = disc > 0
        t = np.where(hit, -b - np.sqrt(np.maximum(disc, 0)), 0)
        X = P[:, None, None] + d * t
        lat = np.degrees(np.arcsin(np.clip(X[2] / R, -1, 1)))
        lon = np.degrees(np.arctan2(X[1], X[0]))
        # livello ideale: texel (m) ~ impronta del pixel (m), che cresce verso il bordo del disco
        cosi = np.clip(-(np.sum(d * X, axis=0) / R), 0.05, 1)
        foot = t * 1000 / F / cosi
        zf = np.log2(156543.0 * np.cos(np.radians(lat)) / np.maximum(foot, 0.1))
        z_n = float(np.median(zf[hit])) if hit.any() else 0
        img = np.zeros((H, W, 3), np.float32)
        acc = np.zeros((H, W), np.float32)
        for L in levels:                       # dal più grossolano al più fine: il fine copre dove c'è
            if not L.glob and (L.z > z_n + 2.5 or L.z < z_n - 3):
                continue
            rgb, wgt = L.sample(lat, lon, z_n)
            # transizione morbida tra livelli: il livello fine entra quando serve
            wgt = wgt * np.clip((zf - (L.z - 2.2)) / 1.2, 0, 1) if not L.glob else wgt
            img = img * (1 - wgt[..., None]) + rgb * wgt[..., None]
            acc = np.maximum(acc, wgt)
        img[~hit] = 0
        # atmosfera: alone blu sul bordo del disco e foschia leggera vicino al bordo
        dist = np.sqrt(np.maximum(P @ P - b * b, 0))
        glow = np.exp(-np.maximum(dist - R, 0) / (R * 0.012)) * (~hit)
        limb = np.clip((1 - cosi) ** 3, 0, 1) * hit
        atm = np.array([255, 190, 120], np.float32)       # BGR: azzurro
        img = img * (1 - 0.25 * limb[..., None]) + atm * (0.25 * limb[..., None])
        img += atm * (glow[..., None] * 0.7)
        sp = (~hit).astype(np.float32) * stars * 255
        img += sp[..., None]
        # vignettatura leggera
        v = 1 - 0.28 * ((px / (W / 2)) ** 2 + (py / (H / 2)) ** 2) / 2
        img *= v[..., None]
        # nuvole che passano davanti, dall'interno verso fuori, poi bianco
        tc = (u * a.dur - (a.dur - a.clouds)) / a.clouds
        if tc > 0:
            out = img
            for j, C in enumerate(cl):
                sc = 0.6 + 3.2 * (tc + j * 0.18) ** 1.6
                M = cv2.getRotationMatrix2D((W / 2, H / 2), math.degrees(roll) * 0.2 + j * 40, sc)
                cw = cv2.warpAffine(C, M, (W, H), borderMode=cv2.BORDER_REFLECT)
                al = np.clip((cw - 0.42) * 3.2, 0, 1) * np.clip(tc * 2.2 - j * 0.25, 0, 1)
                col = 238 + 17 * cw
                out = out * (1 - al[..., None]) + col[..., None] * al[..., None]
            white = np.clip((tc - 0.55) / 0.45, 0, 1) ** 1.5
            img = out * (1 - white) + 250 * white
        # mosso radiale nella parte più veloce
        speed = abs(math.log(a.h1 / a.h0)) * (ease(min(1, (u + 0.01) * 1.03)) - s) / 0.01
        if speed > 0.15:
            k = 1 + min(0.06, speed * 0.01)
            Mz = cv2.getRotationMatrix2D((W / 2, H / 2), 0, k)
            img = 0.6 * img + 0.4 * cv2.warpAffine(img, Mz, (W, H), borderMode=cv2.BORDER_REFLECT)
        cv2.imwrite(f"{a.out}/{i:04d}.png", np.clip(img, 0, 255).astype(np.uint8))
        if i % 10 == 0:
            print(f"{i}/{N} h={h:.0f} km z={z_n:.1f}", flush=True)


if __name__ == "__main__":
    main()
