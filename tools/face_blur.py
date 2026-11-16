#!/usr/bin/env python3
"""Volti dei bambini sfocati (fortkochi, Manuel 16/11: i bambini di Ashwasa si vedono, ma col volto sfocato).

1) Rilevamento e tracce: YuNet (opencv_zoo, `work/models/yunet.onnx`) su ogni fotogramma a 1920x1080; le facce si
   uniscono in tracce per vicinanza tra fotogrammi; per ogni traccia si salva una miniatura per scegliere chi sfocare.
       python3 tools/face_blur.py detect clip.mp4 workdir
   -> workdir/<clip>_tracks.json e workdir/<clip>_track<N>.jpg
2) Sfocatura delle tracce scelte (le altre, gli adulti, restano nitide). Ogni box è allargato, tenuto qualche
   fotogramma prima e dopo (i buchi del rilevatore su profili e teste girate), con bordo sfumato. Uscita 4K
   alla stessa cadenza, x264 crf 12, audio copiato.
       python3 tools/face_blur.py blur clip.mp4 workdir out.mp4 1,3,4 [--all] [--boxes x,y,w,h@t0-t1;...]
   --all sfoca tutte le tracce; --boxes aggiunge zone fisse (coordinate 1920x1080, tempi in secondi) per volti che il
   rilevatore non vede (foto piccole sui muri, bambini lontani).
"""
import json, os, subprocess, sys
import cv2, numpy as np

MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work", "models", "yunet.onnx")
URL = "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
W, H = 1920, 1080


def probe(src):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,r_frame_rate", "-of", "csv=p=0", src], capture_output=True, text=True).stdout
    w, h, r = o.strip().split("\n")[0].split(",")
    a, b = r.split("/")
    return int(w), int(h), float(a) / float(b), r


def frames(src, w, h):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-map", "0:v:0", "-vf", f"scale={w}:{h}",
                          "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE, bufsize=10 ** 8)
    n = w * h * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3)
    p.wait()


def detect(src, wd):
    if not os.path.exists(MODEL):
        os.makedirs(os.path.dirname(MODEL), exist_ok=True)
        subprocess.run(["curl", "-sSfL", "-o", MODEL, URL], check=True)
    os.makedirs(wd, exist_ok=True)
    det = cv2.FaceDetectorYN.create(MODEL, "", (W, H), 0.55)
    name = os.path.splitext(os.path.basename(src))[0]
    tracks, best = [], {}
    for i, im in enumerate(frames(src, W, H)):
        _, F = det.detect(im)
        for x, y, w, h, *_rest, sc in ([] if F is None else F):
            cx, cy = x + w / 2, y + h / 2
            tr = None
            for t in tracks:
                fi, (px, py, pw, ph) = t["f"][-1], t["b"][-1]
                if i - fi <= 24 and abs(px + pw / 2 - cx) < max(pw, w) * 1.2 and abs(py + ph / 2 - cy) < max(ph, h) * 1.2:
                    if fi != i:
                        tr = t; break
            if tr is None:
                tr = {"id": len(tracks), "f": [], "b": []}; tracks.append(tr)
            tr["f"].append(i); tr["b"].append([float(x), float(y), float(w), float(h)])
            if w * h > best.get(tr["id"], (0,))[0]:
                x0, y0 = max(0, int(x - w)), max(0, int(y - h))
                best[tr["id"]] = (w * h, im[y0:int(y + 2 * h), x0:int(x + 2 * w)].copy(), i)
    tracks = [t for t in tracks if len(t["f"]) >= 2]
    for t in tracks:
        a, crop, i = best[t["id"]]
        crop = cv2.resize(crop, (240, int(240 * crop.shape[0] / max(1, crop.shape[1]))))
        cv2.putText(crop, f"{t['id']} f{t['f'][0]}-{t['f'][-1]}", (4, 22), 0, 0.7, (0, 255, 255), 2)
        cv2.imwrite(f"{wd}/{name}_track{t['id']}.jpg", crop)
    json.dump(tracks, open(f"{wd}/{name}_tracks.json", "w"))
    print(name, [(t["id"], t["f"][0], t["f"][-1], len(t["f"])) for t in tracks])


def boxes_per_frame(tracks, ids, n, fps, extra, hold=8):
    per = [[] for _ in range(n)]
    for t in tracks:
        if ids != "all" and t["id"] not in ids:
            continue
        f, b = np.array(t["f"]), np.array(t["b"])
        for j in range(max(0, f[0] - hold), min(n, f[-1] + hold + 1)):
            k = np.searchsorted(f, j)
            if k == 0 or k >= len(f):
                bb = b[min(k, len(f) - 1)]
            else:  # interpolazione tra due rilevamenti
                u = (j - f[k - 1]) / max(1, f[k] - f[k - 1])
                bb = b[k - 1] * (1 - u) + b[k] * u
            per[j].append(bb)
    for (x, y, w, h, t0, t1) in extra:
        for j in range(max(0, int(t0 * fps)), min(n, int(t1 * fps) + 1)):
            per[j].append(np.array([x, y, w, h]))
    return per


def blur(src, wd, out, ids, extra):
    w0, h0, fps, rate = probe(src)
    name = os.path.splitext(os.path.basename(src))[0]
    tracks = json.load(open(f"{wd}/{name}_tracks.json"))
    n = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                            "stream=nb_read_packets", "-of", "csv=p=0", src], capture_output=True, text=True).stdout)
    per = boxes_per_frame(tracks, ids, n, fps, extra)
    s = w0 / W
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w0}x{h0}",
                            "-r", rate, "-i", "-", "-i", src, "-map", "0:v", "-map", "1:a:0?", "-c:a", "copy",
                            "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-pix_fmt", "yuv420p", out],
                           stdin=subprocess.PIPE)
    for j, im in enumerate(frames(src, w0, h0)):
        im = im.copy()
        for x, y, w, h in (per[j] if j < n else []):
            cx, cy, r = (x + w / 2) * s, (y + h / 2) * s, max(w, h) * s * 0.95
            x0, y0 = int(max(0, cx - r * 1.3)), int(max(0, cy - r * 1.5))
            x1, y1 = int(min(w0, cx + r * 1.3)), int(min(h0, cy + r * 1.4))
            if x1 - x0 < 4 or y1 - y0 < 4:
                continue
            roi = im[y0:y1, x0:x1]
            small = cv2.resize(roi, (max(1, roi.shape[1] // 24), max(1, roi.shape[0] // 24)), interpolation=cv2.INTER_AREA)
            bl = cv2.GaussianBlur(cv2.resize(small, (roi.shape[1], roi.shape[0]), interpolation=cv2.INTER_LINEAR), (0, 0), r / 6)
            m = np.zeros(roi.shape[:2], np.float32)
            cv2.ellipse(m, (int(cx - x0), int(cy - y0)), (int(r * 1.05), int(r * 1.25)), 0, 0, 360, 1, -1)
            m = cv2.GaussianBlur(m, (0, 0), r / 8)[..., None]
            im[y0:y1, x0:x1] = (bl * m + roi * (1 - m)).astype(np.uint8)
        enc.stdin.write(im.tobytes())
    enc.stdin.close(); enc.wait()
    print("sfocato", out)


if __name__ == "__main__":
    a = sys.argv
    if a[1] == "detect":
        detect(a[2], a[3])
    else:
        ids = "all" if "--all" in a else [int(x) for x in a[5].split(",") if x]
        extra = []
        if "--boxes" in a:
            for part in a[a.index("--boxes") + 1].split(";"):
                b, t = part.split("@")
                t0, t1 = map(float, t.split("-"))
                extra.append((*map(float, b.split(",")), t0, t1))
        blur(a[2], a[3], a[4], ids, extra)
