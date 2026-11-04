# Carosello "I volti" (Manuel, 4/11): il secondo carosello di ogni lungo, solo primi piani delle persone.
# 1 copertina (il volto più forte + "I volti di ...") + 5 volti + chiusura "Segui Voci Vere" con il logo.
# Filtro Voci Vere: scuro, neri profondi, colore spento, contrasto sul viso, vignetta forte (rifatto il 4/11).
# Volti senza scritte; solo la copertina ha titolo e una riga di contesto.
# 4:5 1080x1350, testo e logo dentro il quadrato centrale 1080x1080 (YouTube ritaglia a quadrato).
#   python3 copioni/caroselli/carosello_volti.py [mercato|arthunkal|te]
# Fotogrammi in work/volti/f/ (estratti dal lungo e dal girato su Drive, elenco in work/volti/f/sources.txt;
# sorgenti scritte qui sotto per poterli rifare).
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1080, 1350
SQ0, SQ1 = 135, 1215          # quadrato centrale visibile anche su YouTube
TIT = 'assets/fonts/VVTitolo-PoppinsExtraBold.ttf'
BODY = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
LOGO = 'assets/brand/logo_vocivere_trasparente_chiaro.png'
GOLD = (182, 138, 75)
F = 'work/volti/f/'

# Volti scelti (Manuel, 4/11: "primo piano vero"): trovati con un rilevatore di volti (YuNet) su tutto il lungo e il
# girato, Manuel escluso con il riconoscimento (SFace). Sorgente, secondo e riquadro del viso in
# copioni/caroselli/volti_scelti.json. Esclusi: la ragazza di Manuel e il chai master del tè (non ha voluto parlare).
import json, subprocess
SEL = json.load(open('copioni/caroselli/volti_scelti.json'))
V = {
 'mercato': dict(kicker='MARARI, KERALA, INDIA', title='I volti del mercato del pesce',
   context='Pescatori e venditori, all\'alba sulla spiaggia'),
 'arthunkal': dict(kicker='ARTHUNKAL, KERALA, INDIA', title='I volti del pellegrinaggio',
   context='13 km a piedi, di notte, fino alla basilica'),
 'te': dict(kicker='MUNNAR, KERALA, INDIA', title='I volti del tè',
   context='Le colline del tè, a oltre 1.500 metri'),
}
ZOOM = 2.5   # altezza del ritaglio = 2.5 volte l'altezza del viso: il viso riempie la foto

def crop45(e):
    os.makedirs(F, exist_ok=True); o = F + os.path.basename(e['p']) + f"_{e['t']}.png"
    if not os.path.exists(o):
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', str(e['t']), '-i', e['p'], '-frames:v', '1', o], check=True)
    im = Image.open(o).convert('RGB'); w0, h0 = im.size
    x, y, fw, fh = e['box']; ch = min(fh * ZOOM, h0); cw = ch * 4 / 5
    cx, cy = x + fw / 2, y + fh / 2
    x0 = min(max(cx - cw / 2, 0), w0 - cw); y0 = min(max(cy - ch * 0.42, 0), h0 - ch)
    return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)

def vv_filter(im):
    # Filtro Voci Vere (Manuel, 4/11, riferimento: ritratto del minatore): scuro, neri profondi, poco colore,
    # contrasto locale sul viso, vignetta forte. Il viso resta leggibile, il resto affonda nel buio.
    im = im.filter(ImageFilter.UnsharpMask(radius=30, percent=35, threshold=3))   # chiarezza: rughe, pelle, occhi
    im = im.filter(ImageFilter.UnsharpMask(radius=1.5, percent=30, threshold=2))
    a = np.asarray(im).astype(np.float32) / 255
    lum = a @ np.array([.299, .587, .114], np.float32)
    a = a * 0.55 + lum[..., None] * 0.45                       # colore spento
    a = a * np.array([1.03, 1.0, 0.95], np.float32)            # appena caldo
    a = np.clip(a, 0, 1) ** 1.35 * 0.95                         # più scuro
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W * 0.55)) ** 2 + ((yy - H * 0.42) / (H * 0.55)) ** 2)
    a = a * (1 - np.clip((r - 0.45) / 0.75, 0, 1) ** 1.3 * 0.85)[..., None]   # vignetta forte
    rng = np.random.default_rng(7); a = a + rng.normal(0, 0.016, (H, W, 1)).astype(np.float32)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype('uint8'))

def shade(im, y0, y1, op):  # sfuma verso il nero dal basso del quadrato
    g = np.zeros((H, W), np.float32); y = np.arange(H)[:, None]
    g = np.clip((y - y0) / (y1 - y0), 0, 1) * op
    m = Image.fromarray((np.broadcast_to(g, (H, W)) * 255).astype('uint8'))
    return Image.composite(Image.new('RGB', (W, H), (12, 10, 8)), im, m)

def text_sh(im, xy, t, font, fill, anchor='la', r=6):
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((xy[0] + 2, xy[1] + 3), t, font=font, fill=(0, 0, 0, 170), anchor=anchor)
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(r))); ImageDraw.Draw(im).text(xy, t, font=font, fill=fill, anchor=anchor)

def wrap(d, t, f, mw):
    out, line = [], ''
    for w in t.split():
        s = (line + ' ' + w).strip()
        if d.textlength(s, font=f) <= mw: line = s
        else: out.append(line); line = w
    return out + [line]

def logo(im, w=170, y=SQ0 + 34, x=60):
    l = Image.open(LOGO).convert('RGBA'); l = l.crop(l.getbbox()); l = l.resize((w, int(l.height * w / l.width)), Image.LANCZOS)
    im.alpha_composite(l, (x, y))

def caption(im, t):
    d = ImageDraw.Draw(im); f = ImageFont.truetype(BODY, 36); y = SQ1 - 70
    tw = d.textlength(t, font=f); d.rectangle((60, y + 8, 66, y + 44), fill=GOLD)
    text_sh(im, (84, y + 26), t, f, (255, 255, 255), anchor='lm')

def cover(v):
    c = V[v]; cap = c['context']
    im = shade(vv_filter(crop45(SEL[v]['cover'])), SQ1 - 420, SQ1 + 40, 0.75).convert('RGBA')
    d = ImageDraw.Draw(im); ft = ImageFont.truetype(TIT, 92); fk = ImageFont.truetype(BODY, 30); fc = ImageFont.truetype(BODY, 34)
    lines = wrap(d, c['title'].upper(), ft, W - 120); y = SQ1 - 70 - len(lines) * 98 - 56
    kw = d.textlength(c['kicker'], font=fk); d.rounded_rectangle((60, y - 62, 60 + kw + 32, y - 12), radius=8, fill=GOLD)
    d.text((76, y - 37), c['kicker'], font=fk, fill=(255, 255, 255), anchor='lm')
    for i, t in enumerate(lines): text_sh(im, (60, y + i * 98), t, ft, (255, 255, 255) if i < len(lines) - 1 else (235, 196, 128), r=8)
    y += len(lines) * 98 + 14
    text_sh(im, (60, y), cap, fc, (240, 236, 228)); text_sh(im, (W - 60, y), 'Scorri →', fc, (240, 236, 228), anchor='ra')
    logo(im); return im

def face(e):  # solo il volto: niente scritte (Manuel, 4/11)
    return vv_filter(crop45(e))

def closing(v):
    im = vv_filter(crop45(SEL[v]['cover'])).filter(ImageFilter.GaussianBlur(14))
    im = Image.blend(im, Image.new('RGB', (W, H), (8, 7, 6)), 0.45).convert('RGBA')
    l = Image.open(LOGO).convert('RGBA'); l = l.crop(l.getbbox()); lw = 640; l = l.resize((lw, int(l.height * lw / l.width)), Image.LANCZOS)
    y = 470; im.alpha_composite(l, ((W - lw) // 2, y))
    d = ImageDraw.Draw(im); ft = ImageFont.truetype(TIT, 60); y += l.height + 70
    for t in ['SEGUI VOCI VERE', 'PER SCOPRIRE', 'LE PROSSIME STORIE']:
        text_sh(im, (W // 2, y), t, ft, (255, 255, 255) if t != 'SEGUI VOCI VERE' else (235, 196, 128), anchor='ma'); y += 74
    return im

def build(v):
    out = f'copioni/caroselli/{v}_volti'; os.makedirs(out, exist_ok=True)
    for x in os.listdir(out): os.remove(os.path.join(out, x))
    sl = [cover(v)] + [face(x) for x in SEL[v]['faces']] + [closing(v)]
    for i, im in enumerate(sl, 1): im.convert('RGB').save(f'{out}/{i:02d}.jpg', quality=93)
    th = [im.convert('RGB').resize((216, 270)) for im in sl]; G = Image.new('RGB', (226 * len(th) + 10, 290), (20, 20, 20))
    for i, t in enumerate(th): G.paste(t, (10 + i * 226, 10))
    G.save(f'copioni/caroselli/{v}_volti_anteprima.jpg', quality=85)

for v in (sys.argv[1:] or V): build(v)
