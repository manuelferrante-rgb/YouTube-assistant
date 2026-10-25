#!/usr/bin/env python3
"""Mappa "carta nautica" (stile diverso da map_anim.py): globo -> India -> Kerala -> percorso lungo la costa.

Proiezione ortografica unica dallo spazio fino alla costa (zoom continuo, dati Natural Earth reali).
Terra color carta, mare blu petrolio con linee di profondità, percorso oro che si disegna con piccoli puntini
che camminano, contatore dei km. Tempi agganciati al parlato:
    python3 tools/route_map.py out.mp4 --route "Kalavoor|9.55|76.307|santuario di Kreupasanam;Marari|9.62646|76.296;
        Arthunkal|9.6611|76.3008|basilica di Sant'Andrea" --km 13 --t-a 4.1 --t-b 6.0 --dur 8 [--w 3840 --h 2160]
--t-a: compare il punto di partenza (la parola "Kalavoor"); --t-b: si arriva (la parola "Arthunkal");
--t-km: il contachilometri arriva al totale (la parola "tredici"), anche dopo che la linea è arrivata.
"""
import argparse, json, os, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GEO, M = f"{ROOT}/models/geo", f"{ROOT}/models"

BG = np.array([222, 233, 240], np.float32)         # BGR: fondo carta chiara
SEA_NEAR = np.array([222, 208, 168], np.float32)   # bassi fondali: celeste (carta nautica)
SEA_DEEP = np.array([242, 238, 226], np.float32)   # largo: quasi bianco
PAPER = np.array([186, 220, 238], np.float32)      # terra color carta (#EEDCBA)
PAPER_IN = np.array([166, 204, 226], np.float32)   # entroterra un filo più scuro
INK = np.array([38, 46, 58], np.float32)
GOLD = np.array([75, 138, 182], np.float32)        # #B68A4B
GOLD_RGB, INK_RGB, PAPER_RGB = (182, 138, 75), (58, 46, 38), (236, 222, 196)


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t) if t < 1 else 1.0


def ease3(t):
    t = min(max(t, 0.0), 1.0)
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def polys(geom):
    return [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]


def font(name, size, var=None):
    f = ImageFont.truetype(f"{M}/{name}", int(size))
    if var:
        f.set_variation_by_name(var)
    return f


def chaikin(p, it=2):
    """Arrotonda gli spigoli dei poligoni a bassa risoluzione (costa e lago più naturali da vicino)."""
    for _ in range(it):
        q = np.roll(p, -1, 0)
        out = np.empty((len(p) * 2, 2))
        out[0::2], out[1::2] = 0.75 * p + 0.25 * q, 0.25 * p + 0.75 * q
        p = out
    return p


def coast_path(kerala, lat_a, lat_b, inland=0.0025, n=240):
    """Linea lungo la spiaggia: longitudine della costa (dati reali) a ogni latitudine, poco verso terra."""
    lats = np.linspace(lat_a, lat_b, n)
    lons = []
    for lat in lats:
        xs = []
        for p in kerala:
            r = np.array(p[0])
            y1, y2 = r[:-1, 1], r[1:, 1]
            m = ((y1 - lat) * (y2 - lat) <= 0) & (y1 != y2)
            xs += list(r[:-1, 0][m] + (r[1:, 0][m] - r[:-1, 0][m]) * (lat - y1[m]) / (y2[m] - y1[m]))
        lons.append(min(xs) + inland)
    lons = np.convolve(np.pad(lons, 12, mode="edge"), np.ones(25) / 25, "valid")
    return np.stack([lons, lats], 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--route", required=True); ap.add_argument("--km", default="13")
    ap.add_argument("--t-a", type=float, default=4.1); ap.add_argument("--t-b", type=float, default=6.0)
    ap.add_argument("--t-km", type=float, default=None)   # il contatore arriva al totale qui (la parola "tredici")
    ap.add_argument("--dur", type=float, default=8.0); ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--w", type=int, default=3840); ap.add_argument("--h", type=int, default=2160)
    a = ap.parse_args()
    W, H, fps = a.w, a.h, a.fps
    s = W / 3840
    stops = []
    for x in a.route.split(";"):
        f = x.strip().split("|")
        stops.append((f[0], float(f[1]), float(f[2]), f[3] if len(f) > 3 else ""))

    c0 = json.load(open(f"{GEO}/admin0_50m.geojson"))["features"]
    st = json.load(open(f"{GEO}/admin1_10m.geojson"))["features"]
    world = [np.array(p[0], np.float64) for f in c0 if f["properties"]["ADMIN"] != "India" for p in polys(f["geometry"])]
    world = [p for p in world if np.ptp(p[:, 0]) + np.ptp(p[:, 1]) > 0.6]     # niente isolotti (anelli nel mare)
    states = [f for f in st if f["properties"].get("admin") == "India"]
    india = [np.array(p[0], np.float64) for f in states for p in polys(f["geometry"])]
    kerala_raw = [p for f in states if f["properties"]["name"] == "Kerala" for p in polys(f["geometry"])]
    kerala = [np.array(p[0], np.float64) for p in kerala_raw]
    india, kerala = [chaikin(p) for p in india], [chaikin(p) for p in kerala]
    allpolys = [(p, 0) for p in world] + [(p, 1) for p in india]
    bbox = [(p[:, 0].min(), p[:, 0].max(), p[:, 1].min(), p[:, 1].max()) for p, _ in allpolys]

    path = coast_path([[p] for p in kerala], stops[0][1], stops[-1][1])
    seg = np.r_[0, np.cumsum(np.hypot(np.diff(path[:, 0]) * np.cos(np.radians(9.6)), np.diff(path[:, 1])))]
    stop_frac = [np.interp(la, path[:, 1], seg) / seg[-1] for _, la, _, _ in stops]
    rmid = ((path[:, 0].min() + path[:, 0].max()) / 2, (path[:, 1].min() + path[:, 1].max()) / 2)

    # ---- camera: (t, lon0, lat0, larghezza vista in gradi) ----
    tA, tB, D = a.t_a, a.t_b, a.dur
    k_globe, k_india, k_ker, k_route = 1.1, 2.0, 2.9, tA - 0.25
    G = 2 * np.degrees(np.arcsin(1.0)) * (W / (0.84 * H)) / 2   # globo intero alto 84% dello schermo
    # un solo avvicinamento all'India, poi uno zoom unico e fluido fino alla costa (niente soste sul Kerala)
    cams = [(0.0, 52.0, 8.0, G * 0.97), (k_globe, 76.5, 14.0, G),
            (k_india, 79.0, 20.0, 40.0), (k_route, rmid[0] + 0.05, rmid[1], 0.40),
            (D, rmid[0] + 0.048, rmid[1] + 0.003, 0.385)]

    def cam(t):
        for (t1, *A), (t2, *B) in zip(cams, cams[1:]):
            if t <= t2:
                u = ease((t - t1) / (t2 - t1)) if t1 == k_india or t2 - t1 >= 2.5 else ease3((t - t1) / (t2 - t1))
                lw = np.exp(np.log(A[2]) + (np.log(B[2]) - np.log(A[2])) * u)
                # il centro segue lo zoom in scala log: niente scivolate laterali a zoom stretto
                # (lo scarto dal punto d'arrivo si riduce con la larghezza: la meta resta sempre in campo)
                v = (A[2] - lw) / (A[2] - B[2]) if abs(A[2] - B[2]) > 1e-9 else u
                return A[0] + (B[0] - A[0]) * v, A[1] + (B[1] - A[1]) * v, lw
        return cams[-1][1:]

    F = dict(place=font("PlayfairDisplay.ttf", 92 * s, "Bold"), sub=font("PlayfairDisplay-Italic.ttf", 58 * s, "Italic"),
             small=font("PlayfairDisplay.ttf", 60 * s, "SemiBold"), caps=font("Poppins-Medium.ttf", 64 * s),
             capsS=font("Poppins-Medium.ttf", 40 * s), km=font("PlayfairDisplay-Italic.ttf", 120 * s, "SemiBold Italic"))

    rng = np.random.default_rng(7)
    grain_tex = cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), 0.8 * s + 0.3)
    paper_tex = cv2.GaussianBlur(rng.standard_normal((H // 8, W // 8)).astype(np.float32), (0, 0), 6)
    paper_tex = cv2.resize(paper_tex / (paper_tex.std() + 1e-6), (W, H))[..., None]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vign = (1 - 0.16 * np.clip(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.70)) ** 2, 0, 1) ** 1.3)[..., None]
    walkers = rng.random(60)

    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                             "-r", str(fps), "-i", "-", "-c:v", "libx264", "-crf", "12", "-preset", "slow",
                             "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
    n = int(round(D * fps))
    for i in range(n):
        t = i / fps
        lon0, lat0, lw = cam(t)
        R = W / np.radians(lw)                                  # raggio della Terra in pixel
        L0, P0 = np.radians(lon0), np.radians(lat0)

        def proj(lonlat, clamp=True):
            lo, la = np.radians(lonlat[:, 0]) - L0, np.radians(lonlat[:, 1])
            x = R * np.cos(la) * np.sin(lo)
            y = R * (np.cos(P0) * np.sin(la) - np.sin(P0) * np.cos(la) * np.cos(lo))
            if clamp:
                back = np.sin(P0) * np.sin(la) + np.cos(P0) * np.cos(la) * np.cos(lo) < 0
                if back.any():
                    r = np.hypot(x[back], y[back]) + 1e-9
                    x[back] *= R / r; y[back] *= R / r
            return np.stack([W / 2 + x, H / 2 - y], 1)

        def P1(lon, lat):
            return proj(np.array([[lon, lat]], np.float64))[0]

        # vista in gradi per scartare i poligoni fuori campo
        half = lw * 0.75 + 1.0
        vis = lambda b: not (b[1] < lon0 - half * 1.3 or b[0] > lon0 + half * 1.3 or b[3] < lat0 - half or b[2] > lat0 + half) \
            if lw < 60 else True
        land = np.zeros((H, W), np.uint8); ind = np.zeros((H, W), np.uint8); ker = np.zeros((H, W), np.uint8)
        borders = []
        for (p, isind), b in zip(allpolys, bbox):
            if not vis(b):
                continue
            q = np.clip(np.round(proj(p) * 4), -2 ** 29, 2 ** 29).astype(np.int32)
            cv2.fillPoly(land, [q], 255, cv2.LINE_AA, shift=2)
            if isind:
                cv2.fillPoly(ind, [q], 255, cv2.LINE_AA, shift=2); borders.append(q)
        for p in kerala:
            q = np.clip(np.round(proj(p) * 4), -2 ** 29, 2 ** 29).astype(np.int32)
            cv2.fillPoly(ker, [q], 255, cv2.LINE_AA, shift=2)

        disc = np.zeros((H, W), np.uint8)
        if R < 4 * W:
            cv2.circle(disc, (int(W * 2), int(H * 2)), int(R * 4), 255, -1, cv2.LINE_AA, shift=2)
        else:
            disc[:] = 255
        discf = disc.astype(np.float32)[..., None] / 255
        landf = (land.astype(np.float32) / 255)[..., None] * discf

        # mare: più chiaro vicino alla costa, linee di profondità (distanza dalla terra, mezza risoluzione)
        hs = 2
        sm = cv2.resize(255 - land, (W // hs, H // hs), interpolation=cv2.INTER_AREA)
        dsea = cv2.resize(cv2.distanceTransform((sm > 127).astype(np.uint8), cv2.DIST_L2, 5), (W, H)) * hs
        sea_g = np.exp(-dsea / (260 * s))[..., None]
        sea = SEA_DEEP + (SEA_NEAR - SEA_DEEP) * sea_g
        cont = np.zeros((H, W), np.float32)
        for dd, al in ((16, .55), (42, .38), (80, .28), (135, .2), (210, .14)):
            cont = np.maximum(cont, al * np.clip(1 - np.abs(dsea - dd * s) / (1.4 * s + .6), 0, 1))
        sea = sea + (np.array([165, 135, 90], np.float32) - sea) * cont[..., None] * 0.6
        # entroterra appena più scuro, grana della carta
        sl = cv2.resize(land, (W // hs, H // hs), interpolation=cv2.INTER_AREA)
        dland = np.minimum(cv2.resize(cv2.distanceTransform((sl > 127).astype(np.uint8), cv2.DIST_L2, 5), (W, H)), 1e6) * hs
        inl = np.clip(dland / (500 * s), 0, 1)[..., None]
        paper = PAPER + (PAPER_IN - PAPER) * inl + paper_tex * 3.5
        # India un filo più luminosa dei paesi vicini quando si vede il subcontinente
        ia = ease((t - 0.6) / 0.8) * (1 - ease((t - k_ker) / 0.8))
        other = (1 - ind.astype(np.float32)[..., None] / 255) * ia
        paper = paper * (1 - 0.10 * other)
        # Kerala in oro durante l'arrivo sullo Stato, poi torna carta
        ka = ease((t - (k_india - 0.1)) / 0.6) * (1 - ease((t - (k_ker + 0.25)) / 0.7))
        kf = ker.astype(np.float32)[..., None] / 255 * ka
        paper = paper + (GOLD - paper) * kf * 0.62

        img = BG * (1 - discf) + sea * discf
        img = img * (1 - landf) + paper * landf
        # globo: ombra sul bordo (sfera) e alone d'atmosfera
        if R < 4 * W:
            rr = np.hypot(xx - W / 2, yy - H / 2) / R
            limb = np.clip(rr, 0, 1) ** 4
            img = img * (1 - 0.22 * limb[..., None] * discf)
            shadow = np.exp(-np.clip(rr - 1, 0, None) * 14)[..., None] * (1 - discf)
            img = img + (np.array([150, 160, 170], np.float32) - img) * shadow * 0.45
        # confini degli Stati indiani (zoom India/Kerala) e linea di costa
        ov = img.copy()
        ba = ease((t - 1.3) / 0.6) * (1 - ease((t - k_route + 0.5) / 0.5))
        if ba > 0:
            bl = np.zeros((H, W), np.uint8)
            for q in borders:
                cv2.polylines(bl, [q], True, 255, max(1, int(2 * s)), cv2.LINE_AA, shift=2)
            img = img + (INK - img) * (bl.astype(np.float32)[..., None] / 255) * 0.35 * ba * landf
        edge = cv2.morphologyEx(land, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)).astype(np.float32)
        img = img + (INK - img) * (edge[..., None] / 255) * 0.55 * discf
        # reticolo (meridiani e paralleli) a passo che segue lo zoom
        step = 15 if lw > 30 else (2 if lw > 6 else (0.5 if lw > 1.2 else 0.1))
        gl = np.zeros((H, W), np.uint8)
        for v in np.arange(-180, 180, step):
            if abs(v - lon0) > lw * 1.5 + 30 and lw < 60:
                continue
            ln = np.stack([np.full(400, v), np.linspace(-80, 80, 400) if lw > 3 else np.linspace(lat0 - lw, lat0 + lw, 400)], 1)
            pts = proj(ln, clamp=False)
            front = np.sin(P0) * np.sin(np.radians(ln[:, 1])) + np.cos(P0) * np.cos(np.radians(ln[:, 1])) * np.cos(np.radians(ln[:, 0]) - L0) > 0
            if front.sum() > 1:
                cv2.polylines(gl, [np.round(pts[front] * 4).astype(np.int32)], False, 255, max(1, int(1.5 * s)), cv2.LINE_AA, shift=2)
        for v in np.arange(-75, 80, step):
            if abs(v - lat0) > lw + 20 and lw < 60:
                continue
            lons = np.linspace(-180, 180, 900) if lw > 3 else np.linspace(lon0 - 2 * lw, lon0 + 2 * lw, 400)
            ln = np.stack([lons, np.full(len(lons), v)], 1)
            pts = proj(ln, clamp=False)
            front = np.sin(P0) * np.sin(np.radians(v)) + np.cos(P0) * np.cos(np.radians(v)) * np.cos(np.radians(lons) - L0) > 0
            if front.sum() > 1:
                cv2.polylines(gl, [np.round(pts[front] * 4).astype(np.int32)], False, 255, max(1, int(1.5 * s)), cv2.LINE_AA, shift=2)
        img = img + (np.array([150, 120, 80], np.float32) - img) * (gl.astype(np.float32)[..., None] / 255) * 0.16 * discf

        # ---------- percorso, tappe, testi ----------
        pil = Image.fromarray(cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB))
        d = ImageDraw.Draw(pil, "RGBA")

        def text(xy, txt, f, fill, anchor="lm", stroke=None, sw=3, alpha=1.0, spacing=0):
            if alpha <= 0.01:
                return
            col = fill + (int(255 * alpha),)
            if spacing:
                tot = sum(f.getlength(c) for c in txt) + spacing * (len(txt) - 1)
                x = xy[0] - tot / 2 if anchor[0] == "m" else xy[0]
                for c in txt:
                    d.text((x, xy[1]), c, font=f, fill=col, anchor="l" + anchor[1],
                           stroke_width=int(sw * s) if stroke else 0, stroke_fill=(stroke + (int(255 * alpha),)) if stroke else None)
                    x += f.getlength(c) + spacing
                return
            d.text(xy, txt, font=f, fill=col, anchor=anchor, stroke_width=int(sw * s) if stroke else 0,
                   stroke_fill=(stroke + (int(255 * alpha),)) if stroke else None)

        al = ease((t - 0.7) / 0.5) * (1 - ease((t - 2.1) / 0.4))
        text(tuple(P1(78.5, 22.5)), "INDIA", F["caps"], (30, 26, 22), "mm", alpha=al, spacing=int(18 * s))
        al = ease((t - 2.3) / 0.4) * (1 - ease((t - k_route + 0.35) / 0.35))
        x, y = P1(76.9, 10.2)
        text((x + 60 * s, y), "KERALA", F["caps"], (30, 26, 22), "lm", alpha=al, spacing=int(16 * s))
        al = ease((t - 2.5) / 0.5) * (1 - ease((t - k_route + 0.35) / 0.35))
        x, y = P1(74.6, 10.4)
        text((x, y), "MAR ARABICO", F["capsS"], (70, 110, 135), "mm", alpha=al * 0.9, spacing=int(12 * s))
        sa = ease((t - k_route + 0.1) / 0.6)
        x, y = P1(76.21, 9.6)
        text((x, y), "MAR ARABICO", F["capsS"], (70, 110, 135), "mm", alpha=sa * 0.85, spacing=int(12 * s))
        x, y = P1(76.40, 9.64)
        text((x, y), "lago Vembanad", F["sub"], (70, 110, 135), "mm", alpha=sa * 0.85)

        pts = proj(path)
        u = ease3((t - tA) / (tB - tA))                  # frazione del percorso disegnata
        if u > 0:
            k = max(2, int(np.searchsorted(seg / seg[-1], u)))
            line = [tuple(p) for p in pts[:k]]
            j = min(k, len(pts) - 1)
            f0, f1 = seg[k - 1] / seg[-1], seg[j] / seg[-1]
            head = pts[k - 1] + (pts[j] - pts[k - 1]) * ((u - f0) / max(f1 - f0, 1e-9))
            line.append(tuple(head))
            d.line(line, fill=(40, 30, 18, 200), width=int(22 * s), joint="curve")
            d.line(line, fill=GOLD_RGB + (255,), width=int(13 * s), joint="curve")
            # puntini che camminano lungo il tratto già disegnato (i pellegrini)
            for w0 in walkers:
                fw = (w0 + t * 0.09) % 1.0 * u
                q = np.array([np.interp(fw * seg[-1], seg, pts[:, 0]), np.interp(fw * seg[-1], seg, pts[:, 1])])
                r = 3.2 * s
                d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=(255, 246, 225, 230))
            if u < 1:
                for rg, aa in ((46, 40), (30, 80), (18, 255)):
                    r = rg * s
                    d.ellipse([head[0] - r, head[1] - r, head[0] + r, head[1] + r], fill=GOLD_RGB + (aa,))
            # contatore km accanto alla testa, poi fisso a metà percorso
            tkm = a.t_km or tB
            km = float(a.km) * ease3((t - tA) / (tkm - tA))
            ca = ease((t - tA - 0.15) / 0.3)
            if u < 1:
                text((head[0] - 70 * s, head[1]), f"{km:.0f} km", F["km"], INK_RGB, "rm", stroke=(236, 242, 244), sw=5, alpha=ca)
            else:
                mid = pts[len(pts) // 2]
                text((pts[:, 0].min() - 80 * s, mid[1]), f"{km:.0f} km", F["km"], INK_RGB, "rm", stroke=(236, 242, 244), sw=5)
        for si, (name, la, lo, sub) in enumerate(stops):
            first, last = si == 0, si == len(stops) - 1
            t_in = tA - 0.15 if first else (tB if last else tA + (tB - tA) * stop_frac[si])
            pa = ease((t - t_in) / 0.3)
            if pa <= 0:
                continue
            fq = np.interp(stop_frac[si] * seg[-1], seg, np.arange(len(pts)))
            x, y = (np.interp(fq, np.arange(len(pts)), pts[:, 0]), np.interp(fq, np.arange(len(pts)), pts[:, 1]))
            if first or last:
                pop = 1 + 0.35 * np.sin(np.pi * min(1, (t - t_in) / 0.35)) * (1 - min(1, (t - t_in) / 0.35))
                r = 22 * s * pa * pop
                d.ellipse([x - r - 9 * s, y - r - 9 * s, x + r + 9 * s, y + r + 9 * s], fill=PAPER_RGB + (int(255 * pa),),
                          outline=(40, 30, 18, int(255 * pa)), width=max(1, int(3 * s)))
                d.ellipse([x - r, y - r, x + r, y + r], fill=GOLD_RGB + (int(255 * pa),))
                # anello che si allarga una volta
                rr = (22 + 70 * ease((t - t_in) / 0.9)) * s
                ra = 0.7 * (1 - ease((t - t_in) / 0.9))
                if ra > 0.01:
                    d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=GOLD_RGB + (int(255 * ra),), width=max(1, int(5 * s)))
                text((x + 70 * s, y - (22 * s if sub else 0)), name, F["place"], INK_RGB, "lm",
                     stroke=PAPER_RGB, sw=5, alpha=pa)
                if sub:
                    text((x + 72 * s, y + 62 * s), sub, F["sub"], (120, 86, 40), "lm", stroke=PAPER_RGB, sw=4,
                         alpha=ease((t - t_in - 0.15) / 0.35))
            else:
                r = 11 * s * pa
                d.ellipse([x - r - 5 * s, y - r - 5 * s, x + r + 5 * s, y + r + 5 * s], fill=(40, 30, 18, int(230 * pa)))
                d.ellipse([x - r, y - r, x + r, y + r], fill=PAPER_RGB + (int(255 * pa),))
                text((x + 50 * s, y), name, F["small"], INK_RGB, "lm", stroke=PAPER_RGB, sw=4, alpha=pa)
        # rosa dei venti essenziale (nord), in basso a destra, quando siamo sulla costa
        na = ease((t - k_route + 0.2) / 0.5)
        if na > 0:
            cx, cy, r = W - 170 * s, H - 200 * s, 52 * s
            d.polygon([(cx, cy - r), (cx + r * 0.32, cy + r * 0.35), (cx, cy + r * 0.12), (cx - r * 0.32, cy + r * 0.35)],
                      fill=GOLD_RGB + (int(230 * na),))
            text((cx, cy - r - 34 * s), "N", F["capsS"], INK_RGB, "mm", alpha=na)

        img = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR).astype(np.float32)
        img = img * vign + grain_tex[..., None] * 3.0
        proc.stdin.write(np.clip(img, 0, 255).astype(np.uint8).tobytes())   # transizioni nel montaggio
    proc.stdin.close(); proc.wait()


if __name__ == "__main__":
    main()
