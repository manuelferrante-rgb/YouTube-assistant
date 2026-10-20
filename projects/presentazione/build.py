#!/usr/bin/env python3
"""Monta il video di presentazione Voci Vere (16:9).

Taglia silenzi e pause lunghe (VAD sull'audio), alterna inquadratura normale e stretta sui tagli,
corregge leggermente il colore, sottotitoli giallo-oro, musica bassa, finale sfocato con logo.
    python3 projects/presentazione/build.py
"""
import json, os, subprocess, sys
import numpy as np
import cv2

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = f"{ROOT}/work/presentazione"
OUT = f"{ROOT}/work/build_pres"
os.makedirs(OUT, exist_ok=True)

CLIPS = ["01_IMG_8295", "02a_IMG_8298", "02b_IMG_8298", "03a_IMG_8300", "03b_IMG_8300",
         "04a_IMG_8303", "04b_IMG_8303", "05a_IMG_8306", "05b_IMG_8306"]
JSONS = {c: f"{ROOT}/work/out/pres_{c[:2]}.json" for c in CLIPS}

# correzioni token per token (indice parola -> testo), il testo resta allineato ai tempi delle parole
FIX = {
    "02a_IMG_8298": {"lavorato": "laureato", "provato": "ho provato", "Toccando": "toccando"},
    "03b_IMG_8300": {"cioverò": "troverò"},
    "04a_IMG_8303": {"Viaggiano": "Viaggio", "i": "nei", "lontano": "lontani"},
}
# frasi su cui stringere l'inquadratura (prima parola del segmento, maiuscolo)
STRONG = {"MI", "PER", "MA", "SE", "FORSE"}
# pause in più (s) dopo il segmento che finisce con questa parola
EXTRA_PAUSE_AFTER = {"CAPITATA": 0.25}

FPS = 30
W, H = 1920, 1080
GRADE = "colorbalance=rs=-0.07:gs=-0.01:bs=0.06:rm=-0.06:bm=0.05:rh=-0.02:bh=0.02,eq=contrast=1.05:saturation=0.9"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(" ".join(cmd)); print(r.stderr[-3000:]); sys.exit(1)
    return r.stdout


def audio16k(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


def vad(path, span):
    """Regioni di parlato (s) dentro span, con pause brevi unite."""
    x = audio16k(path)
    hop = 160  # 10 ms
    n = len(x) // hop
    e = np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(e)
    db = np.convolve(db, np.ones(5) / 5, mode="same")
    floor = np.percentile(db, 10)
    voiced = db > max(floor + 14, -52)
    regs, start = [], None
    for i, v in enumerate(voiced):
        t = i * 0.01
        if v and start is None:
            start = t
        if not v and start is not None:
            regs.append([start, t]); start = None
    if start is not None:
        regs.append([start, n * 0.01])
    regs = [r for r in regs if r[1] > span[0] - 0.3 and r[0] < span[1] + 0.5]
    merged = []
    for r in regs:
        if merged and r[0] - merged[-1][1] < 0.30:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    return [r for r in merged if r[1] - r[0] > 0.18]


def face_center(path, dur):
    cap = cv2.VideoCapture(path)
    casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    pts = []
    for t in np.linspace(0.5, max(0.6, dur - 0.5), 8):
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, fr = cap.read()
        if not ok:
            continue
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        f = casc.detectMultiScale(g, 1.1, 6, minSize=(120, 120))
        if len(f):
            x, y, w, h = max(f, key=lambda a: a[2] * a[3])
            pts.append((x + w / 2, y + h / 2))
    if not pts:
        return W / 2, H * 0.35
    return float(np.median([p[0] for p in pts])), float(np.median([p[1] for p in pts]))


def crop_filter(zoom, fc):
    if zoom == 1.0:
        return f"scale={W}:{H}"
    cw, ch = int(W / zoom) // 2 * 2, int(H / zoom) // 2 * 2
    cx = min(max(fc[0] - cw / 2, 0), W - cw)
    cy = min(max(fc[1] - ch * 0.38, 0), H - ch)  # volto nel terzo alto
    return f"crop={cw}:{ch}:{int(cx)}:{int(cy)},scale={W}:{H}:flags=lanczos"


# ---------- 1. segmenti ----------
segs = []  # (clip, s0, s1, words[(text,t,UPPER)])
for c in CLIPS:
    path = f"{SRC}/{c}.mov"
    data = {os.path.basename(d["clip"]): d for d in json.load(open(JSONS[c]))}[f"{c}.mov"]
    toks = data["text"].split()
    fix = FIX.get(c, {})
    words = []
    for tok, (up, t) in zip(toks, data["words"]):
        core = tok.strip(".,?!")
        if core in fix:
            tok = tok.replace(core, fix[core])
        words.append((tok, t, up))
    regs = [r for r in vad(path, data["cut"])
            if any(r[0] - 0.6 <= w[1] < r[1] for w in words)]  # scarta rumori senza parole
    # i tempi parola del modello sono in anticipo di ~0.3 s: ogni parola va al segmento la cui finestra
    # [inizio - 0.6, inizio del successivo - 0.6) la contiene
    for k, (s0, s1) in enumerate(regs):
        nxt = regs[k + 1][0] - 0.6 if k + 1 < len(regs) else 1e9
        ws = [(w[0], w[1] + 0.25, w[2]) for w in words if s0 - 0.6 <= w[1] < nxt]
        segs.append([c, max(0, s0 - 0.10), s1 + 0.12, ws])

# pause espressive
for s in segs:
    last = s[3][-1][2].strip(".,?!")
    if last in EXTRA_PAUSE_AFTER:
        s[2] += EXTRA_PAUSE_AFTER[last]

# centro del volto per clip (misurato sui fotogrammi; opencv headless non ha il rilevatore di volti)
FACES = {"01_IMG_8295": (980, 340), "02a_IMG_8298": (960, 340), "02b_IMG_8298": (960, 340),
         "03a_IMG_8300": (980, 360), "03b_IMG_8300": (1020, 340), "04a_IMG_8303": (980, 340),
         "04b_IMG_8303": (980, 340), "05a_IMG_8306": (940, 340), "05b_IMG_8306": (960, 340)}
faces = FACES

# ---------- 2. render dei segmenti ----------
import sherpa_onnx
sys.path.insert(0, f"{ROOT}/tools")
from analyze_clips import words_from_tokens
_M = f"{ROOT}/models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8"
ASR = sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=f"{_M}/encoder.int8.onnx", decoder=f"{_M}/decoder.int8.onnx", joiner=f"{_M}/joiner.int8.onnx",
    tokens=f"{_M}/tokens.txt", model_type="nemo_transducer", num_threads=4)
# errori noti della trascrizione automatica -> parole dette davvero (verificate con Manuel)
TEXT_FIX = [("lavorato", "laureato"), ("desiderava", "desideravo"), ("non ci vuoi", "non ci voglio"),
            ("Adesso vuoi", "Adesso voglio"), ("Na chile vive", "Da chi le vive"), ("Viaggiano i", "Viaggio nei"),
            ("posti lontano", "posti lontani"), ("cioverò", "troverò"), ("ti chiedi?", "ti chiedi:"),
            ("capitata.", "capitata?")]


def seg_words(path):
    """Parole del segmento con tempi relativi, corrette con TEXT_FIX a livello di frase."""
    st = ASR.create_stream(); st.accept_waveform(16000, audio16k(path)); ASR.decode_stream(st)
    r = st.result
    ws = words_from_tokens(list(r.tokens), list(r.timestamps))
    text = " ".join(w for w, _ in ws)
    for a, b in TEXT_FIX:
        text = text.replace(a, b)
    toks = text.split()
    if len(toks) != len(ws):  # la correzione ha cambiato il numero di parole: tempi distribuiti
        t0, t1 = ws[0][1], ws[-1][1]
        return [(tk, t0 + (t1 - t0) * k / max(1, len(toks) - 1)) for k, tk in enumerate(toks)]
    return [(tk, t) for tk, (_, t) in zip(toks, ws)]

parts, timeline, t_out, zoom_prev = [], [], 0.0, None
for i, (c, s0, s1, ws) in enumerate(segs):
    first = ws[0][2]
    zoom = 1.18 if first in STRONG else (1.0 if zoom_prev != 1.0 else 1.1)
    if zoom == zoom_prev:
        zoom = 1.0 if zoom != 1.0 else 1.1
    zoom_prev = zoom
    nfr = round((s1 - s0) * FPS)
    d = nfr / FPS  # durata esatta in fotogrammi: audio e video identici, niente deriva sui tagli
    p = f"{OUT}/seg_{i:02d}.mkv"
    vf = f"{crop_filter(zoom, faces[c])},{GRADE},fps={FPS},trim=end_frame={nfr},setpts=PTS-STARTPTS,format=yuv420p"
    af = f"aresample=48000,apad,atrim=end={d:.4f},afade=t=in:d=0.02,afade=t=out:st={d - 0.03:.3f}:d=0.03"
    if not (os.environ.get("REUSE") and os.path.exists(p)):  # REUSE=1 riusa i segmenti già renderizzati
      run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s0:.3f}", "-t", f"{d + 0.5:.3f}", "-i", f"{SRC}/{c}.mov",
         "-map", "0:v:0", "-map", "0:a:0", "-vf", vf, "-af", af, "-t", f"{d:.4f}", "-c:v", "libx264", "-crf", "14", "-preset", "fast",
         "-c:a", "pcm_s16le", p])
    real = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))
    parts.append(p)
    timeline.append((t_out, real, seg_words(p)))
    t_out += real
    print(f"seg {i:02d} {c} {s0:6.2f}-{s1:6.2f} zoom {zoom}  {' '.join(w[0] for w in ws)}")

# ---------- 3. coda: sfocatura + logo ----------
last_c, last_s0, last_s1 = segs[-1][0], segs[-1][1], segs[-1][2]
TAIL = 3.8
tail = f"{OUT}/tail.mkv"
logo = f"{ROOT}/assets/brand/logo_vocivere_trasparente_chiaro.png"
fc = faces[last_c]
run(["ffmpeg", "-v", "error", "-y", "-ss", f"{last_s1:.3f}", "-i", f"{SRC}/{last_c}.mov", "-loop", "1", "-t", f"{TAIL}", "-i", logo,
     "-filter_complex",
     f"[0:v]{crop_filter(1.0, fc)},{GRADE},fps={FPS},tpad=stop_mode=clone:stop_duration={TAIL},trim=duration={TAIL},"
     f"setpts=PTS-STARTPTS,split[a][b];"
     f"[b]gblur=sigma=28,eq=brightness=-0.24:saturation=0.65[bl];"
     f"[a][bl]xfade=transition=fade:duration=1.0:offset=0.2[v];"
     f"[1:v]scale=980:-1,format=rgba,fade=t=in:st=0.7:d=0.8:alpha=1[lg];"
     f"[v][lg]overlay=(W-w)/2:(H-h)/2:shortest=1,format=yuv420p[out]",
     "-map", "[out]", "-an", "-t", f"{TAIL}", "-c:v", "libx264", "-crf", "14", "-preset", "fast", f"{OUT}/tail_v.mkv"])
run(["ffmpeg", "-v", "error", "-y", "-i", f"{OUT}/tail_v.mkv", "-f", "lavfi", "-t", f"{TAIL}",
     "-i", "anullsrc=r=48000:cl=stereo", "-c:v", "copy", "-c:a", "pcm_s16le", "-shortest", tail])
parts.append(tail)
total = t_out + TAIL

with open(f"{OUT}/list.txt", "w") as f:
    for p in parts:
        f.write(f"file '{p}'\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{OUT}/list.txt", "-c", "copy",
     f"{OUT}/cut.mkv"])

# ---------- 4. sottotitoli ----------
def ts(t):
    h, r = divmod(max(t, 0), 3600); m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"

events = []
for o, dur, ws in timeline:
    chunks, cur = [], []
    for w in ws:
        cur.append(w)
        txt = " ".join(x[0] for x in cur)
        if (w[0][-1] in ".?!,:" and len(cur) >= 2) or len(txt) > 36:
            chunks.append(cur); cur = []
    if cur:
        if chunks and len(" ".join(x[0] for x in chunks[-1] + cur)) <= 42:
            chunks[-1] += cur
        else:
            chunks.append(cur)
    for j, ch in enumerate(chunks):
        a = o if j == 0 else o + max(0.0, ch[0][1] - 0.05)
        b = o + dur if j + 1 == len(chunks) else o + max(0.0, chunks[j + 1][0][1] - 0.05)
        events.append((a, b - 0.02, " ".join(x[0] for x in ch).rstrip(",")))
for a, b, t in events:
    print(f"  sub {a:6.2f}-{b:6.2f}  {t}")

PALE_GOLD = "&H0098D8F2"  # #F2D898 in BGR
ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Poppins Medium,56,{PALE_GOLD},{PALE_GOLD},&H00000000,&H90000000,0,0,0,0,100,100,0.5,0,1,1.6,1.4,2,160,160,70,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
for a, b, t in events:
    ass += f"Dialogue: 0,{ts(a)},{ts(b)},Sub,,0,0,0,,{t}\n"
open(f"{OUT}/subs.ass", "w").write(ass)

# ---------- 5. audio: voce + musica ----------
music = f"{ROOT}/work/musica/yoga_style_chris_haugen.mp3"
end_t = t_out  # inizio coda
run(["ffmpeg", "-v", "error", "-y", "-i", f"{OUT}/cut.mkv", "-i", music, "-filter_complex",
     f"[0:a]highpass=f=80,afftdn=nf=-30,acompressor=threshold=-22dB:ratio=3:attack=10:release=150,"
     f"loudnorm=I=-15:TP=-2:LRA=7,aresample=48000[voc];"
     f"[1:a]atrim=0:{total + 0.5:.2f},asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-2,aresample=48000,"
     f"volume='if(lt(t,{end_t:.2f}),0.075,0.075+min(1,(t-{end_t:.2f})/1.2)*0.20)':eval=frame,"
     f"afade=t=in:d=1.5,afade=t=out:st={total - 1.6:.2f}:d=1.6[mus];"
     f"[voc][mus]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1:LRA=9,aresample=48000[a]",
     "-map", "[a]", "-c:a", "pcm_s16le", "-ar", "48000", f"{OUT}/mix.wav"])

# ---------- 6. finale ----------
final = f"{ROOT}/work/VociVere_presentazione_16x9.mp4"
run(["ffmpeg", "-v", "error", "-y", "-i", f"{OUT}/cut.mkv", "-i", f"{OUT}/mix.wav",
     "-vf", f"ass={OUT}/subs.ass:fontsdir={ROOT}/models", "-map", "0:v", "-map", "1:a",
     "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-profile:v", "high", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", final])
print("durata", round(total, 2), "->", final)
