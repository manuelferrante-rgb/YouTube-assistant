#!/usr/bin/env python3
"""Mappa animata: India -> Kerala -> costa -> segnaposto sulla località (dati Natural Earth reali).

    python3 tools/map_anim.py out.mp4 --lat 9.62646 --lon 76.29600 --name "Marari" --region Kerala [--w 3840 --h 2160]
Stile Voci Vere: mare scuro, terra neutra, regione in oro tenue, segnaposto oro.
"""
import argparse, json, os, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GEO = f"{ROOT}/models/geo"
FONT = f"{ROOT}/models/Poppins-Medium.ttf"

SEA = (24, 20, 16)        # BGR scuro
LAND = (46, 52, 56)
LAND_IN = (72, 82, 90)    # India più chiara dei paesi vicini
EDGE = (110, 118, 124)
GOLD = (75, 138, 182)     # #B68A4B in BGR
TEXT = (235, 235, 235)


def polys(geom):
    if geom["type"] == "Polygon":
        return [geom["coordinates"]]
    return geom["coordinates"]


def ease(t):
    t = min(max(t, 0), 1)
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True); ap.add_argument("--name", required=True)
    ap.add_argument("--region", default="Kerala"); ap.add_argument("--country", default="India")
    ap.add_argument("--w", type=int, default=3840); ap.add_argument("--h", type=int, default=2160)
    ap.add_argument("--dur", type=float, default=4.5); ap.add_argument("--zoomscale", type=float, default=1.0); ap.add_argument("--fps", type=int, default=30)
    a = ap.parse_args()
    W, H = a.w, a.h
    s = W / 3840

    c0 = json.load(open(f"{GEO}/admin0_50m.geojson"))["features"]
    st = json.load(open(f"{GEO}/admin1_10m.geojson"))["features"]
    world = [p for f in c0 if f["properties"]["ADMIN"] != a.country for p in polys(f["geometry"])]
    states = [f for f in st if f["properties"].get("admin") == a.country]
    india = [p for f in states for p in polys(f["geometry"])]
    region = [p for f in states if f["properties"].get("name") == a.region for p in polys(f["geometry"])]
    rlon = np.concatenate([np.array(p[0])[:, 0] for p in region]); rlat = np.concatenate([np.array(p[0])[:, 1] for p in region])

    # inquadrature (centro lon, lat, ampiezza in gradi di longitudine)
    views = [(80.0, 20.5, 50.0),                                             # India intera
             ((rlon.min() + rlon.max()) / 2, (rlat.min() + rlat.max()) / 2, 7.5),  # Kerala
             (a.lon + 0.15, a.lat, 1.6)]                                      # costa, località
    views = [(v[0], v[1], v[2] * a.zoomscale) for v in views]  # verticale: inquadrature più strette
    keys = [0.0, 0.7, 2.4, 3.4]  # tempi: fermo India, zoom Kerala, zoom costa

    def view_at(t):
        if t <= keys[1]:
            return views[0]
        if t <= keys[2]:
            u = ease((t - keys[1]) / (keys[2] - keys[1])); A, B = views[0], views[1]
        else:
            u = ease((t - keys[2]) / (keys[3] - keys[2])); A, B = views[1], views[2]
        # zoom in scala logaritmica: movimento percepito uniforme
        lw = np.exp(np.log(A[2]) + (np.log(B[2]) - np.log(A[2])) * u)
        return (A[0] + (B[0] - A[0]) * u, A[1] + (B[1] - A[1]) * u, lw)

    font_big = ImageFont.truetype(FONT, int(96 * s)); font_mid = ImageFont.truetype(FONT, int(70 * s))
    font_pin = ImageFont.truetype(FONT, int(84 * s))
    n = int(a.dur * a.fps)
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                             "-r", str(a.fps), "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "medium",
                             "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
    for i in range(n):
        t = i / a.fps
        lon0, lat0, lw = view_at(t)
        k = np.cos(np.radians(lat0))
        ppd = W / lw  # pixel per grado di longitudine

        def proj(ring):
            r = np.array(ring)
            x = (r[:, 0] - lon0) * ppd * 1.0 + W / 2
            y = -(r[:, 1] - lat0) * ppd / k + H / 2
            return np.round(np.stack([x, y], 1) * 4).astype(np.int32)  # sub-pixel (shift=2)

        img = np.zeros((H, W, 3), np.uint8); img[:] = SEA
        lt = max(1, int(2 * s))
        for p in world:
            cv2.fillPoly(img, [proj(p[0])], LAND, cv2.LINE_AA, shift=2)
        for p in india:
            cv2.fillPoly(img, [proj(p[0])], LAND_IN, cv2.LINE_AA, shift=2)
        # regione in oro, che si accende durante il primo zoom
        ra = ease((t - 0.5) / 1.2)
        if ra > 0:
            ov = img.copy()
            for p in region:
                cv2.fillPoly(ov, [proj(p[0])], GOLD, cv2.LINE_AA, shift=2)
            img = cv2.addWeighted(ov, 0.55 * ra, img, 1 - 0.55 * ra, 0)
        for p in india:
            cv2.polylines(img, [proj(p[0])], True, EDGE, lt, cv2.LINE_AA, shift=2)

        pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)); d = ImageDraw.Draw(pil)

        def label(txt, lon, lat, font, alpha, dy=0):
            if alpha <= 0:
                return
            x = (lon - lon0) * ppd + W / 2; y = -(lat - lat0) * ppd / k + H / 2 + dy
            col = tuple(int(c * alpha) for c in TEXT[::-1])
            d.text((x, y), txt, font=font, fill=col, anchor="mm")

        label(a.country.upper(), 79.5, 23.0, font_big, 1 - ease((t - 0.6) / 0.6))
        label(a.region.upper(), (rlon.min() + rlon.max()) / 2 + 1.2, (rlat.min() + rlat.max()) / 2,
              font_mid, ease((t - 1.6) / 0.5) * (1 - ease((t - 2.5) / 0.4)))
        img = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

        # segnaposto
        pa = ease((t - 3.2) / 0.4)
        if pa > 0:
            x = int((a.lon - lon0) * ppd + W / 2); y = int(-(a.lat - lat0) * ppd / k + H / 2)
            r = int(22 * s * (0.6 + 0.4 * pa))
            ring = int(r + 26 * s * ease((t - 3.3) / 0.8))
            ov = img.copy(); cv2.circle(ov, (x, y), ring, GOLD, max(1, int(4 * s)), cv2.LINE_AA)
            img = cv2.addWeighted(ov, 0.6 * pa * (1 - ease((t - 3.6) / 0.9)), img, 1 - 0.6 * pa * (1 - ease((t - 3.6) / 0.9)), 0)
            cv2.circle(img, (x, y), r + int(6 * s), (255, 255, 255), -1, cv2.LINE_AA)
            cv2.circle(img, (x, y), r, GOLD, -1, cv2.LINE_AA)
            la = ease((t - 3.5) / 0.4)
            if la > 0:
                pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)); d = ImageDraw.Draw(pil)
                txt = f"{a.name}, {a.region}"
                col = tuple(int(c * la) for c in TEXT[::-1])
                d.text((x + int(60 * s), y), txt, font=font_pin, fill=col, anchor="lm",
                       stroke_width=int(3 * s), stroke_fill=(0, 0, 0))
                img = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
        # dissolvenza in entrata/uscita
        f = min(1, t / 0.25, (a.dur - t) / 0.25)
        proc.stdin.write((img * max(f, 0)).astype(np.uint8).tobytes())
    proc.stdin.close(); proc.wait()


if __name__ == "__main__":
    main()
