# Cerca nel girato i momenti "da foto" per il carosello dei volti (Manuel, 5/11): persona ferma, viso grande e
# nitido, che guarda in camera (o di tre quarti), Manuel escluso. Rilevatore YuNet + riconoscimento SFace
# (modelli in work/volti/model, da media.githubusercontent.com/media/opencv/opencv_zoo/...).
#   python3 copioni/caroselli/volti_scan.py <video>      -> work/volti/cand_<video>.json + provino
# Legge le clip in work/volti/raw_<video>/ (girato scaricato da Drive).
import cv2, numpy as np, subprocess, json, sys, glob, os
v = sys.argv[1]; RAW = f'work/volti/raw_{v}/'; M = 'work/volti/model/'
FPS = 3; SW = 1280                       # analisi a 3 fotogrammi al secondo, larghezza 1280
det = cv2.FaceDetectorYN.create(M + 'face_detection_yunet_2023mar.onnx', '', (SW, 720), 0.8, 0.3, 5000)
rec = cv2.FaceRecognizerSF.create(M + 'face_recognition_sface_2021dec.onnx', '')

def emb(img, f):
    return rec.feature(rec.alignCrop(img, f)).flatten()

# riferimenti di Manuel (selfie dai lunghi)
REF = []
for r in glob.glob('work/volti/ref/*.jpg'):
    im = cv2.imread(r); h, w = im.shape[:2]; s = SW / w; im = cv2.resize(im, (SW, int(h * s)))
    det.setInputSize((im.shape[1], im.shape[0])); _, fs = det.detect(im)
    if fs is not None:
        f = max(fs, key=lambda f: f[2] * f[3]); REF.append(emb(im, f))
print('riferimenti Manuel', len(REF))

def probe(p):
    o = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                        'stream=width,height:stream_side_data=rotation:format=duration', '-of', 'json', p],
                       capture_output=True, text=True).stdout
    j = json.loads(o); st = j['streams'][0]; w, h = st['width'], st['height']
    rot = 0
    for sd in st.get('side_data_list', []) or []: rot = int(sd.get('rotation', 0))
    if abs(rot) == 90: w, h = h, w
    return w, h, float(j['format']['duration'])

out = []
clips = sorted(glob.glob(RAW + '*.MP4') + glob.glob(RAW + '*.mp4') + glob.glob(RAW + '*.MOV') + glob.glob(RAW + '*.mov'))
for p in clips:
    try: w, h, dur = probe(p)
    except Exception as e: print('salto', p, e); continue
    sh = int(round(h * SW / w / 2) * 2); scale = w / SW
    cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-i', p, '-vf', f'fps={FPS},scale={SW}:{sh}', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-']
    pr = subprocess.Popen(cmd, stdout=subprocess.PIPE); det.setInputSize((SW, sh))
    prev = []; i = 0; n = 0
    while True:
        b = pr.stdout.read(SW * sh * 3)
        if len(b) < SW * sh * 3: break
        im = np.frombuffer(b, np.uint8).reshape(sh, SW, 3); t = i / FPS; i += 1
        _, fs = det.detect(im); cur = []
        if fs is not None:
            for f in fs:
                x, y, fw, fh = f[:4]; sc = f[-1]
                if fh * scale < 220 or sc < 0.85: continue       # viso troppo piccolo per una foto
                le, re_, no = f[4:6], f[6:8], f[8:10]; ml, mr = f[10:12], f[12:14]
                ed = np.linalg.norm(re_ - le) + 1e-3
                yaw = float((no[0] - (le[0] + re_[0]) / 2) / ed)   # 0 = guarda in camera
                g = cv2.cvtColor(im[max(int(y), 0):int(y + fh), max(int(x), 0):int(x + fw)], cv2.COLOR_BGR2GRAY)
                if g.size == 0: continue
                sharp = float(cv2.Laplacian(g, cv2.CV_64F).var())
                e = emb(im, f)
                man = max([float(rec.match(e, r, cv2.FaceRecognizerSF_FR_COSINE)) for r in REF] or [0])
                # fermo: stesso viso nel fotogramma prima, quasi nello stesso punto
                still = min([np.hypot(x - px, y - py) / fh for px, py, pfh in prev] or [9])
                cur.append((x, y, fh))
                out.append(dict(p=p, t=round(t, 2), box=[int(x * scale), int(y * scale), int(fw * scale), int(fh * scale)],
                                fh=int(fh * scale), yaw=round(yaw, 3), sharp=round(sharp, 1), man=round(man, 3),
                                still=round(float(still), 3), score=round(float(sc), 3), W=w, H=h,
                                emb=[round(float(z), 4) for z in e]))
                n += 1
        prev = cur
    pr.wait(); print(os.path.basename(p), round(dur, 1), 's, volti', n, flush=True)
json.dump(out, open(f'work/volti/cand_{v}.json', 'w'))
print('totale', len(out))
