# Miniature v2 dei lunghi (Copy, 4/11): "meno da blogger" (analisi/miniature.md).
# Protagonista una persona del posto nel momento più forte, Manuel assente, testo 2-4 parole (Bebas Neue,
# bianco + giallo come le miniature già usate). 3 versioni per lungo per "Test e confronto" di YouTube Studio.
#   python3 copioni/miniature_v2/miniature_v2.py
# Fotogrammi (girato originale, scelti col più nitido) in work/thumb/pick/:
#   mercato  m_razza    DJI_20261020044058_0118 1.5-2.2 s   (l'uomo che trascina il pesce enorme sulla sabbia)
#            m_signora  DJI_20261020044058_0118 ~23 s       (la signora del mercato che sorride)
#            m_asta     DJI_20261020044226_0120 ~3 s        (l'asta: chi compra chino sulle ceste)
#   arthunkal a_marrone/a_folla  DJI_20261024023818_0237 fotogrammi 31/57 (2:30 di notte)
#   te       t_sadish113/117  DJI_20261026133721_0385 113 s / 117 s (Sadish con le foglie, le colline dietro)
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W, H = 1280, 720
BEB = 'assets/fonts/BebasNeue-Regular.ttf'; YEL = (255, 214, 10); WHITE = (255, 255, 255)
P = 'work/thumb/pick/'

def crop(im, cx, cy, zoom):
    w, h = im.size; ch = h / zoom; cw = ch * 16 / 9
    x = min(max(cx * w - cw / 2, 0), w - cw); y = min(max(cy * h - ch / 2, 0), h - ch)
    return im.crop((int(x), int(y), int(x + cw), int(y + ch))).resize((W, H), Image.LANCZOS)

def grade(im, c=1.1, s=1.15, b=1.0, night=False):
    if night:   # notte: rumore via, ombre su, colore caldo invariato
        a = cv2.fastNlMeansDenoisingColored(np.asarray(im)[:, :, ::-1].copy(), None, 7, 7, 7, 21)
        a = a.astype(np.float32) / 255.; a = np.power(a, 0.78)
        im = Image.fromarray((a[:, :, ::-1] * 255).clip(0, 255).astype('uint8'))
    return ImageEnhance.Brightness(ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(c)).enhance(s)).enhance(b)

def shade(base, side, dark):
    if side in ('left', 'right'):
        xs = np.linspace(1, 0, W) if side == 'left' else np.linspace(0, 1, W)
        g = np.tile(np.clip(xs * 1.6 - 0.45, 0, 1) ** 1.2, (H, 1))
    else:   # 'top'
        g = np.tile(np.clip(np.linspace(1, 0, H) * 1.7 - 0.55, 0, 1)[:, None] ** 1.2, (1, W))
    m = Image.fromarray((g * dark * 255).astype('uint8'))
    return Image.composite(Image.new('RGB', (W, H), (5, 8, 10)), base, m)

def text(base, lines, x, y, target, right=False):
    base = base.convert('RGBA'); d = ImageDraw.Draw(base)
    for t, col, gap in lines:
        f0 = ImageFont.truetype(BEB, 100); w0 = d.textbbox((0, 0), t, font=f0)[2]
        f = ImageFont.truetype(BEB, int(100 * target / w0)); bb = d.textbbox((0, 0), t, font=f)
        xx = x - bb[2] if right else x
        sh = Image.new('RGBA', base.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((xx + 5, y + 7), t, font=f, fill=(0, 0, 0, 235))
        base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8))); ImageDraw.Draw(base).text((xx, y), t, font=f, fill=col)
        d = ImageDraw.Draw(base); y += bb[3] + gap
    return base.convert('RGB')

def make(out, src, cx, cy, zoom, lines, side, x, y, target, dark=0.75, night=False, **g):
    im = grade(crop(Image.open(P + src).convert('RGB'), cx, cy, zoom), night=night, **g)
    im = shade(im, side, dark)
    im = text(im, lines, x, y, target, right=(side == 'right'))
    im.save(out, quality=92)
    return out

ASTA = [("ALL'ASTA", WHITE, 6), ("SULLA SABBIA", YEL, 0)]
NOTTE = [("DA MEZZANOTTE", YEL, 6), ("PREGANDO", WHITE, 0)]
TE = [("E OGGI", WHITE, 8), ("DI CHI SONO?", YEL, 0)]
D = 'copioni/{}_miniature/'
J = [
 make(D.format('mercato') + 'v4_1_pesce_comeunapersona.jpg', 'm_razza.png', 0.66, 0.58, 1.55,
      [("COME UNA", WHITE, 6), ("PERSONA", YEL, 0)], 'left', 44, 60, 470),
 make(D.format('mercato') + 'v4_2_signora_asta.jpg', 'm_signora.png', 0.45, 0.42, 1.7, ASTA, 'right', W - 44, 60, 520),
 make(D.format('mercato') + 'v4_3_asta_sabbia.jpg', 'm_asta.png', 0.33, 0.52, 1.45, ASTA, 'right', W - 44, 60, 560),
 make(D.format('arthunkal') + 'v2_1_pellegrina.jpg', 'a_marrone.png', 0.47, 0.45, 1.45, NOTTE, 'left', 44, 70, 560, night=True, dark=0.6),
 make(D.format('arthunkal') + 'v2_2_folla.jpg', 'a_folla.png', 0.56, 0.6, 1.25, NOTTE, 'top', 44, 40, 600, night=True, dark=0.55),
 make(D.format('arthunkal') + 'v2_3_pellegrina_vicino.jpg', 'a_marrone.png', 0.5, 0.4, 1.7, NOTTE, 'left', 44, 70, 520, night=True, dark=0.6),
 make(D.format('te') + 'v2_1_sadish.jpg', 't_sadish113.png', 0.62, 0.48, 1.2, TE, 'right', W - 44, 60, 600, dark=0.65),
 make(D.format('te') + 'v2_2_sadish_vicino.jpg', 't_sadish113.png', 0.64, 0.36, 1.65, TE, 'right', W - 44, 60, 600, dark=0.65),
 make(D.format('te') + 'v2_3_sadish_mano.jpg', 't_sadish117.png', 0.58, 0.45, 1.25, TE, 'right', W - 44, 60, 600, dark=0.65),
]
for v in ('mercato', 'arthunkal', 'te'):
    fs = [f for f in J if f'/{v}_' in f]
    G = Image.new('RGB', (1300, 10 + 370 * len(fs)), (20, 20, 20))
    for i, f in enumerate(fs): G.paste(Image.open(f).resize((640, 360)), (10, 10 + i * 370))
    for i, f in enumerate(fs):   # anteprima piccola come nel telefono, a destra
        G.paste(Image.open(f).resize((320, 180)), (670, 10 + i * 370))
    G.save(D.format(v) + '00_v_test_confronto.jpg', quality=85)
print('\n'.join(J))
