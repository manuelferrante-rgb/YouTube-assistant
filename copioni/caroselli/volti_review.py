# Provino dei candidati di volti_scan.py: persone raggruppate per identità (SFace), Manuel escluso, per ognuna i
# 4 momenti migliori (fermo, nitido, viso grande, sguardo in camera). Ritaglio 4:5 come nel carosello.
#   python3 copioni/caroselli/volti_review.py <video>  -> work/volti/review_<video>_NN.jpg (id = persona_fotogramma)
import json, sys, cv2, numpy as np, subprocess, os
v = sys.argv[1]; C = json.load(open(f'work/volti/cand_{v}.json'))
C = [c for c in C if c['man'] < 0.36]                    # niente Manuel
for c in C:
    fr = max(0, 1 - abs(c['yaw']) / 0.5)                  # 1 = in camera
    st = max(0, 1 - c['still'] / 0.15)                    # 1 = fermo
    c['q'] = 1.5 * fr + 1.0 * st + 0.6 * min(c['sharp'] / 150, 1) + 0.6 * min(c['fh'] / 600, 1)
E = np.array([c['emb'] for c in C], np.float32); E /= np.linalg.norm(E, axis=1, keepdims=True) + 1e-6
order = sorted(range(len(C)), key=lambda i: -C[i]['q']); pid = [-1] * len(C); P = []
for i in order:                                           # raggruppa: stessa persona se coseno > 0.42
    for k, rep in enumerate(P):
        if float(E[i] @ E[rep]) > 0.42: pid[i] = k; break
    else: pid[i] = len(P); P.append(i)
tiles = []; os.makedirs('work/volti/tmp', exist_ok=True)
for k in range(len(P)):
    idx = [i for i in order if pid[i] == k]; pick = []
    for i in idx:
        if all(abs(C[i]['t'] - C[j]['t']) > 0.6 or C[i]['p'] != C[j]['p'] for j in pick): pick.append(i)
        if len(pick) == 4: break
    for j, i in enumerate(pick):
        c = C[i]; o = f'work/volti/tmp/{k}_{j}.png'
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', str(c['t']), '-i', c['p'], '-frames:v', '1', o])
        im = cv2.imread(o)
        if im is None: continue
        h0, w0 = im.shape[:2]; x, y, fw, fh = c['box']; ch = min(fh * 3.2, h0); cw = ch * 0.8
        x0 = int(min(max(x + fw / 2 - cw / 2, 0), w0 - cw)); y0 = int(min(max(y + fh / 2 - ch * 0.42, 0), h0 - ch))
        t = cv2.resize(im[y0:y0 + int(ch), x0:x0 + int(cw)], (240, 300))
        cv2.putText(t, f'{k}_{j} q{c["q"]:.1f}', (4, 20), 0, 0.6, (0, 255, 255), 2)
        cv2.putText(t, f'y{c["yaw"]:+.2f} h{c["fh"]}', (4, 292), 0, 0.5, (0, 255, 255), 1)
        tiles.append(t); c['id'] = f'{k}_{j}'
json.dump({c['id']: {kk: c[kk] for kk in ('p', 't', 'box', 'W', 'H')} for c in C if 'id' in c},
          open(f'work/volti/review_{v}.json', 'w'), indent=0)
n = 8
for s in range(0, len(tiles), n * 5):
    T = tiles[s:s + n * 5]
    while len(T) % n: T.append(np.zeros_like(tiles[0]))
    cv2.imwrite(f'work/volti/review_{v}_{s // (n * 5):02d}.jpg', np.vstack([np.hstack(T[r:r + n]) for r in range(0, len(T), n)]))
print(len(P), 'persone,', len(tiles), 'riquadri')
