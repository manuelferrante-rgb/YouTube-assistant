# Miniature v3 (Copy, 8/11): stile dei riferimenti di Manuel (Progetto Happiness, Kevin Pianezze ecc.):
# persona del posto grande e frontale, sguardo in camera, colore cinematografico (poco saturo, contrastato, caldo),
# testo ENORME condensato bianco: (1) parola dietro la testa (profondità, scontorno della persona), (2) riga piccola +
# riga enorme in basso a sinistra, (3) citazione con una parola rossa. Ogni miniatura in italiano e in inglese.
#   python3 copioni/miniature_v3/miniature_v3.py   (fotogrammi dal girato originale in work/, modello in work/models)
import os, subprocess, numpy as np, cv2, onnxruntime as ort
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W, H = 1280, 720
ANTON = 'models/Anton-Regular.ttf'; BEB = 'assets/fonts/BebasNeue-Regular.ttf'
RED = (226, 38, 38); WHITE = (255, 255, 255)
SEG = 'work/models/u2net_human_seg.onnx'
OUT = 'copioni/{}_miniature/v3/'

def frame(src, t):
    o = f"work/mini/f_{os.path.basename(src)}_{t}.png"
    if not os.path.exists(o):
        os.makedirs('work/mini', exist_ok=True)
        if src.endswith('.png'): return src
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', str(t), '-i', src, '-frames:v', '1', o], check=True)
    return o

def crop(im, cx, cy, zoom):
    w, h = im.size; ch = h / zoom; cw = ch * 16 / 9
    if cw > w: cw = w; ch = cw * 9 / 16
    x = min(max(cx * w - cw / 2, 0), w - cw); y = min(max(cy * h - ch / 2, 0), h - ch)
    return im.crop((int(x), int(y), int(x + cw), int(y + ch))).resize((W, H), Image.LANCZOS)

def grade(im, night=False, flip=False):
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    a = np.asarray(im)
    if night:
        a = cv2.fastNlMeansDenoisingColored(a[:, :, ::-1].copy(), None, 6, 6, 7, 21)[:, :, ::-1]
        a = (np.power(a / 255., 0.8) * 255).astype(np.uint8)
    a = a.astype(np.float32) / 255
    lum = a @ np.array([.299, .587, .114], np.float32)
    a = lum[..., None] + (a - lum[..., None]) * 0.82                     # meno saturo
    a = np.clip((a - 0.5) * 1.18 + 0.5, 0, 1)                            # contrasto
    a = a * np.array([1.05, 1.0, 0.92]) + (1 - a) * np.array([0, 0.01, 0.03])   # luci calde, ombre fredde
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2)
    a = a * (1 - np.clip(r - 0.55, 0, 1) ** 1.5 * 0.55)[..., None]
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype('uint8'))
    return im.filter(ImageFilter.UnsharpMask(2, 60, 2))

_sess = None
def mask(im):
    global _sess
    _sess = _sess or ort.InferenceSession(SEG, providers=['CPUExecutionProvider'])
    x = np.asarray(im.resize((320, 320), Image.LANCZOS)).astype(np.float32) / 255.
    x = (x / x.max() - np.array([.485, .456, .406])) / np.array([.229, .224, .225])
    m = _sess.run(None, {_sess.get_inputs()[0].name: x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0, 0]
    m = (m - m.min()) / (m.max() - m.min())
    return Image.fromarray((np.clip((m - 0.35) / 0.3, 0, 1) * 255).astype(np.uint8)).resize(im.size, Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))

def fit(txt, font, target_w, max_h=None):
    d = ImageDraw.Draw(Image.new('L', (10, 10)))
    s = 100; f = ImageFont.truetype(font, s); w = d.textbbox((0, 0), txt, font=f)[2]
    s = int(s * target_w / w)
    if max_h:
        while True:
            f = ImageFont.truetype(font, s); bb = d.textbbox((0, 0), txt, font=f)
            if bb[3] - bb[1] <= max_h: break
            s -= 4
    return ImageFont.truetype(font, s)

def shadow_text(layer, xy, parts, font, sh=10, alpha=200):
    """parts: [(testo, colore)] scritti in fila."""
    d = ImageDraw.Draw(layer); x, y = xy
    sl = Image.new('RGBA', layer.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sl)
    xx = x
    for t, c in parts:
        sd.text((xx + 4, y + 6), t, font=font, fill=(0, 0, 0, alpha)); xx += d.textlength(t, font=font)
    layer.alpha_composite(sl.filter(ImageFilter.GaussianBlur(sh)))
    d = ImageDraw.Draw(layer); xx = x
    for t, c in parts:
        d.text((xx, y), t, font=font, fill=c); xx += d.textlength(t, font=font)

_det = None
def face_top(im):
    # parte alta del volto più grande (YuNet), in pixel della miniatura; None se nessun volto
    global _det
    a = np.asarray(im.convert('RGB'))[:, :, ::-1].copy()
    _det = _det or cv2.FaceDetectorYN.create('work/volti/model/face_detection_yunet_2023mar.onnx', '', (W, H), 0.6, 0.3, 50)
    _det.setInputSize((W, H)); _, fs = _det.detect(a)
    if fs is None: return None
    f = max(fs, key=lambda f: f[2] * f[3]); return f[1] - f[3] * 0.35   # fronte e capelli compresi

def text_bottom(layout, text, top):
    if layout == 'basso': return None
    f = fit(text, ANTON, W - 70 if layout == 'dietro' else W - 120, max_h=250 if layout == 'dietro' else 150)
    bb = ImageDraw.Draw(Image.new('L', (10, 10))).textbbox((0, 0), text, font=f)
    return top + (bb[3] - bb[1])

def make(name, video, lang, src, t, cx, cy, zoom, layout, text, night=False, flip=False, red=None, top=24, small_size=46, blur=None):
    # Regola (Insights, 8/11, dati del reel B): il volto è sempre libero, la scritta mai sopra il viso.
    # Se il volto tocca la fascia del testo, il ritaglio si alza finché il volto è sotto la scritta.
    src_im = Image.open(frame(src, t)).convert('RGB')
    base = grade(crop(src_im, cx, cy, zoom), night, flip).convert('RGBA')
    if blur:                     # blur=(x0, y0, x1, y1) in pixel della miniatura: zona sfocata con bordo morbido
        m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).rectangle(blur, fill=255)
        base = Image.composite(base.filter(ImageFilter.GaussianBlur(14)), base, m.filter(ImageFilter.GaussianBlur(18)))
    # spazio sopra il volto: la scritta sta tutta lì; se non basta (<90 px) si passa allo schema in basso
    ft = face_top(base) if layout in ('dietro', 'citazione') else None
    room = None if ft is None else int(ft) - top - 8
    if room is not None and room < 90:
        layout = 'basso'
        if isinstance(text, str): text = ('', text.strip('“”'))
    if layout == 'dietro':       # parola enorme in alto, la persona davanti al testo
        f = fit(text, ANTON, W - 70, max_h=min(250, room) if room else 250); d = ImageDraw.Draw(base)
        bb = d.textbbox((0, 0), text, font=f); x = (W - (bb[2] - bb[0])) // 2 - bb[0]
        txt = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        parts = [(w + ' ', RED if (red and w in red) else WHITE) for w in text.split(' ')]
        parts[-1] = (parts[-1][0].strip(), parts[-1][1])
        shadow_text(txt, (x, top - bb[1]), parts, f)
        out = Image.alpha_composite(base, txt)
        # la persona copre solo la parte bassa delle lettere: la parola resta leggibile
        th = bb[3] - bb[1]; ycut = int(top + th + 4)
        ramp = np.clip((np.arange(H) - ycut) / 25.0, 0, 1)[:, None] * np.ones((1, W))
        m = np.asarray(mask(base.convert('RGB')), np.float32) * ramp
        person = base.copy(); person.putalpha(Image.fromarray(m.astype('uint8')))
        out = Image.alpha_composite(out, person)
    elif layout == 'basso':      # riga piccola + riga enorme in basso a sinistra (stile Progetto Happiness)
        small, big = text
        g = np.zeros((H, W), np.float32); g[:] = np.clip((np.arange(H)[:, None] - H * 0.45) / (H * 0.55), 0, 1) ** 1.3 * 0.75
        out = Image.composite(Image.new('RGBA', (W, H), (0, 0, 0, 255)), base, Image.fromarray((g * 255).astype('uint8')))
        fb = fit(big, ANTON, 640, max_h=190); fs = ImageFont.truetype(ANTON, small_size)
        d = ImageDraw.Draw(out); bb = d.textbbox((0, 0), big, font=fb)
        y_big = H - 40 - bb[3]
        if small:
            sb = d.textbbox((0, 0), small, font=fs)
            shadow_text(out, (48, y_big + bb[1] - 12 - sb[3]), [(small, WHITE)], fs, 6 if small_size < 80 else 10)
        shadow_text(out, (44, y_big), [(big, RED if red is True else WHITE)], fb)
    elif layout == 'riga':       # una sola riga grande, centrata, un po' sopra il fondo (Manuel 11/11, coir)
        g = np.zeros((H, W), np.float32); g[:] = np.clip((np.arange(H)[:, None] - H * 0.45) / (H * 0.55), 0, 1) ** 1.3 * 0.7
        out = Image.composite(Image.new('RGBA', (W, H), (0, 0, 0, 255)), base, Image.fromarray((g * 255).astype('uint8')))
        f = fit(text, ANTON, W - 140, max_h=150); d = ImageDraw.Draw(out)
        bb = d.textbbox((0, 0), text, font=f); x = (W - (bb[2] - bb[0])) // 2 - bb[0]
        parts = [(w + ' ', RED if (red and w in red) else WHITE) for w in text.split(' ')]
        parts[-1] = (parts[-1][0].strip(), parts[-1][1])
        shadow_text(out, (x, H - 120 - bb[3]), parts, f)
    else:                        # 'citazione': frase tra virgolette in alto, una parola rossa
        f = fit(text, ANTON, W - 120, max_h=min(150, room) if room else 150); d = ImageDraw.Draw(base)
        bb = d.textbbox((0, 0), text, font=f); x = (W - (bb[2] - bb[0])) // 2 - bb[0]
        parts = [(w + ' ', RED if (red and w.strip('“”"') in red) else WHITE) for w in text.split(' ')]
        parts[-1] = (parts[-1][0].strip(), parts[-1][1])
        out = base; shadow_text(out, (x, top - bb[1]), parts, f)
    o = OUT.format(video) + f'{name}_{lang}.jpg'; os.makedirs(os.path.dirname(o), exist_ok=True)
    out.convert('RGB').save(o, quality=93); return o

A, T, C = 'work/mini/raw_arth/', 'work/mini/raw_te/', 'work/coir/raw/'
def g(d, n): return next((d + f for f in (os.listdir(d) if os.path.isdir(d) else []) if f'_{n}_' in f), d + n)
F = 'work/volti/f/'
J = {
 # ARTHUNKAL
 ('arthunkal', 'A1_notte'): dict(src=g(A, '0237'), t=1.0, cx=.47, cy=.5, zoom=1.35, layout='dietro', night=True,
     it='PREGHIERA INFINITA', en='ENDLESS PRAYER'),
 ('arthunkal', 'A2_anziano'): dict(src=F + 'DJI_20261024090951_0301_D.MP4_0.33.png', t=0, cx=.62, cy=.42, zoom=1.5, layout='basso',
     it=('A PIEDI, DI NOTTE', '13 KM PREGANDO'), en=('ON FOOT, AT NIGHT', '13 KM OF PRAYER')),
 ('arthunkal', 'A3_ragazza'): dict(src=F + 'DJI_20261024072623_0247_D.MP4_3.67.png', t=0, cx=.42, cy=.42, zoom=1.6, layout='dietro',
     it='TUTTA LA NOTTE', en='ALL NIGHT LONG'),
 ('arthunkal', 'A4_basilica'): dict(src=F + 'DJI_20261024091255_0302_D.MP4_1.6_luogo.png', t=0, cx=.5, cy=.45, zoom=1.0, layout='basso', red=True,
     it=('LA STATUA ARRIVA', 'DA MILANO, 1647'), en=('THE STATUE CAME', 'FROM MILAN, 1647')),
 ('arthunkal', 'A5_folla'): dict(src=g(A, '0236'), t=0.2, cx=.5, cy=.5, zoom=1.15, layout='citazione', night=True, red=['MEZZANOTTE', 'MIDNIGHT'], top=30,
     it='“IN CAMMINO DA MEZZANOTTE”', en='“WALKING SINCE MIDNIGHT”'),
 # TE
 ('te', 'T1_sadish'): dict(src=g(T, '0388'), t=10.0, cx=.6, cy=.45, zoom=1.5, layout='dietro', red=['CHI', 'WHO'],
     it='DI CHI SONO?', en='WHO OWNS THEM?'),
 ('te', 'T2_sorriso'): dict(src=g(T, '0386'), t=14.1, cx=.74, cy=.42, zoom=1.55, layout='basso',
     it=('AFFITTATE PER', '3.000 RUPIE'), en=('LEASED FOR', '3,000 RUPEES')),
 ('te', 'T3_profilo'): dict(src=F + 'DJI_20261026133625_0383_D.MP4_4.67.png', t=0, cx=.62, cy=.45, zoom=1.25, layout='dietro',
     it='1877', en='1877'),
 ('te', 'T4_colline'): dict(src=g(T, '0392'), t=60.1, cx=.55, cy=.5, zoom=1.0, layout='basso',
     it=('IL TÈ CHE BEVIAMO', 'CHI LO RACCOGLIE'), en=('THE TEA WE DRINK', 'WHO PICKS IT')),
 ('te', 'T5_filari'): dict(src=g(T, '0386'), t=58.0, cx=.45, cy=.42, zoom=1.35, layout='citazione', red=['MANO', 'HAND'], top=24,
     it='“TUTTO RACCOLTO A MANO”', en='“ALL PICKED BY HAND”'),
 # COIR
 ('coir', 'C1_premilla'): dict(src=g(C, '0549'), t=8.0, cx=.6, cy=.45, zoom=1.55, layout='dietro',
     it='40 ANNI A MANO', en='40 YEARS BY HAND'),
 ('coir', 'C2_sorriso'): dict(src=g(C, '0542'), t=6.0, cx=.48, cy=.5, zoom=1.5, layout='basso', red=True,
     it=('PER UN TAPPETO', '80 CENTESIMI'), en=('FOR ONE RUG', '80 CENTS')),
 ('coir', 'C3_corda'): dict(src=g(C, '0069'), t=1.5, cx=.42, cy=.45, zoom=1.4, layout='basso', red=True,
     it=('PER UNA GIORNATA', '4€ AL GIORNO'), en=('FOR A FULL DAY', '€4 A DAY')),
 ('coir', 'C4_laguna'): dict(src=g(C, '0052'), t=3.0, cx=.5, cy=.55, zoom=1.35, layout='dietro',
     it='MADE IN INDIA', en='MADE IN INDIA'),
 ('coir', 'C5_manuel'): dict(src=g(C, '0050'), t=1.0, cx=.5, cy=.45, zoom=1.2, layout='basso',
     it=('CHI FA', 'I NOSTRI TAPPETI'), en=('WHO MAKES', 'OUR DOORMATS')),
 # COIR v4 (Manuel 11/11): espressioni serie, testo coerente con i primi secondi del lungo
 # (0:00 l'uomo nella laguna "Così viene raccolta la materia prima..."; VO0 "...non c'è scritto chi li ha fatti, né quanto le hanno pagate")
 ('coir', 'C6_laguna'): dict(src=g(C, '0052'), t=3.45, cx=.50, cy=.63, zoom=1.35, layout='riga',
     it='I NOSTRI TAPPETI NASCONO QUI', en='OUR DOORMATS START HERE'),
 ('coir', 'C7_donne'): dict(src=g(C, '0540'), t=13.5, cx=.5, cy=.5, zoom=1.0, layout='basso', red=True, flip=True,
     it=('A MANO, SEDUTE A TERRA', 'QUANTO LE PAGANO?'), en=('BY HAND, ON THE GROUND', 'HOW MUCH ARE THEY PAID?')),
 ('coir', 'C8_anziana'): dict(src=g(C, '0063'), t=15.5, cx=.5, cy=.5, zoom=1.35, layout='dietro', red=['CHI', 'WHO'],
     it='CHI LI HA FATTI?', en='WHO MADE THEM?'),
 # alternative per la seconda (Manuel 11/11): le donne sedute davanti alla saracinesca, 0:20-0:30 del lungo
 ('coir', 'C7b_rosa'): dict(src=g(C, '0525'), t=10.0, cx=.42, cy=.42, zoom=1.25, layout='basso', red=True,
     it=('A MANO, PER GENERAZIONI', 'ORA NON LO FANNO PIÙ'), en=('BY HAND, FOR GENERATIONS', 'NOW NOBODY DOES IT')),
 ('coir', 'C7c_fila'): dict(src=g(C, '0529'), t=2.0, cx=.5, cy=.42, zoom=1.0, layout='basso', red=True,
     it=('LO FACEVANO A MANO', 'DAL 1975'), en=('THEY DID IT BY HAND', 'SINCE 1975')),
 # seconda, donne che lavorano il cocco sedute in fila e guardano in camera (Manuel 11/11)
 ('coir', 'C7d_fila'): dict(src=g(C, '0063'), t=2.8, cx=.52, cy=.5, zoom=1.15, layout='basso', red=True,
     it=('A MANO, SEDUTE A TERRA', 'QUANTO LE PAGANO?'), en=('BY HAND, ON THE GROUND', 'HOW MUCH ARE THEY PAID?')),
 ('coir', 'C7e_occhiali'): dict(src=g(C, '0542'), t=21.0, cx=.5, cy=.45, zoom=1.2, layout='basso', red=True, flip=True,
     it=('A MANO, SEDUTE A TERRA', 'QUANTO LE PAGANO?'), en=('BY HAND, ON THE GROUND', 'HOW MUCH ARE THEY PAID?')),
 ('coir', 'C7f_lavoro'): dict(src=g(C, '0540'), t=20.0, cx=.5, cy=.5, zoom=1.0, layout='basso', red=True, flip=True,
     it=('A MANO, SEDUTE A TERRA', 'QUANTO LE PAGANO?'), en=('BY HAND, ON THE GROUND', 'HOW MUCH ARE THEY PAID?')),
 # scelta di Manuel 11/11: le due inquadrature della signora piccolina che guarda in camera, una riga sola
 ('coir', 'C9_madeinindia'): dict(src=g(C, '0063'), t=9.2, cx=.535, cy=.52, zoom=1.45, layout='riga',
     it='MADE IN INDIA', en='MADE IN INDIA'),
 ('coir', 'C10_80centesimi'): dict(src=g(C, '0063'), t=15.5, cx=.52, cy=.45, zoom=1.35, layout='riga',
     it='80 CENTESIMI A TAPPETO', en='80 CENTS PER RUG'),
}
if __name__ == '__main__':
    import sys
    only = sys.argv[1:]
    for (v, n), p in J.items():
        if only and v not in only and n not in only: continue
        p = dict(p); it, en = p.pop('it'), p.pop('en')
        for lang, txt in (('it', it), ('en', en)):
            print(make(n, v, lang, text=txt, **p))
