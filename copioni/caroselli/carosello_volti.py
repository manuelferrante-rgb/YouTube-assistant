# Carosello "I volti" (Manuel, 4/11, rifatto il 5/11): il secondo carosello di ogni lungo, solo ritratti delle persone.
# 1 copertina (il volto più forte + "I volti di ...") + i volti + chiusura "Segui Voci Vere" con il logo.
# 5/11 (Manuel): solo momenti che sembrano foto in posa (persona ferma che guarda in camera, o di tre quarti), mai
# fotogrammi presi a metà di un movimento; qualità più alta possibile; filtro leggero, caldo e naturale.
# Candidati trovati con copioni/caroselli/volti_scan.py + volti_review.py sul girato originale (work/volti/raw_<video>).
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
SEL_FILE = 'copioni/caroselli/volti_scelti.json'

# Volti scelti (Manuel, 4/11: "primo piano vero"): trovati con un rilevatore di volti (YuNet) su tutto il lungo e il
# girato, Manuel escluso con il riconoscimento (SFace). Sorgente, secondo e riquadro del viso in
# copioni/caroselli/volti_scelti.json. Esclusi: la ragazza di Manuel e il chai master del tè (non ha voluto parlare).
import json, subprocess
SEL = json.load(open(SEL_FILE))
V = {
 'mercato': dict(kicker='MARARI, KERALA, INDIA', title='I volti del mercato del pesce',
   context='Pescatori e venditori, all\'alba sulla spiaggia'),
 'arthunkal': dict(kicker='ARTHUNKAL, KERALA, INDIA', title='I volti del pellegrinaggio',
   context='13 km a piedi, di notte, fino alla basilica'),
 'te': dict(kicker='MUNNAR, KERALA, INDIA', title='I volti del tè',
   context='Le colline del tè, a oltre 1.500 metri'),
 'coir': dict(kicker='ANATHALAVATTOM, KERALA, INDIA', title='I volti del coir',
   context='Le donne e l\'uomo che fanno i nostri tappeti'),
 'meenakshi': dict(kicker='MADURAI, TAMIL NADU, INDIA', title='I volti del tempio di Meenakshi',
   context='Chi viene al tempio, la sera'),
}
ZOOM = 2.8   # altezza del ritaglio = 2.8 volte il viso: ritratto (viso e spalle), come una foto

def sharpest(e):
    # tra i fotogrammi a +-0.25 s dal momento scelto prende quello col viso più nitido (niente mosso)
    os.makedirs(F, exist_ok=True); o = F + os.path.basename(e['p']) + f"_{e['t']}.png"
    if os.path.exists(o): return o
    d = F + 'tmp/'; os.makedirs(d, exist_ok=True)
    for f in os.listdir(d): os.remove(d + f)
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-ss', str(max(0, e['t'] - 0.25)), '-i', e['p'], '-t', '0.5',
                    '-vsync', '0', d + '%03d.png'], check=True)
    x, y, fw, fh = e['box']; best = None
    for f in sorted(os.listdir(d)):
        g = np.asarray(Image.open(d + f).convert('L'), np.float32)[max(y, 0):y + fh, max(x, 0):x + fw]
        lap = (g[1:-1, 1:-1] * 4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]).var()
        if best is None or lap > best[0]: best = (lap, f)
    os.replace(d + best[1], o); return o

def crop45(e):
    im = Image.open(sharpest(e)).convert('RGB'); w0, h0 = im.size
    x, y, fw, fh = e['box']; ch = min(max(fh * e.get("zoom", ZOOM), 950), h0); cw = ch * 4 / 5
    if cw > w0: cw = w0; ch = cw * 5 / 4
    cx, cy = x + fw / 2 + e.get('dx', 0) * fw, y + fh / 2
    x0 = min(max(cx - cw / 2, 0), w0 - cw); y0 = min(max(cy - ch * 0.38, 0), h0 - ch)
    return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)

def vv_filter(im):
    # Filtro Voci Vere v2 (Manuel, 5/11): naturale e un po' caldo. Contrasto morbido, colore vero appena più
    # caldo, vignetta leggera, nitidezza fine. Niente neri schiacciati, niente grana.
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=40, threshold=2))
    a = np.asarray(im).astype(np.float32) / 255
    a = a * np.array([1.045, 1.01, 0.94], np.float32) + np.array([0.008, 0.004, 0], np.float32)   # caldo
    lum = a @ np.array([.299, .587, .114], np.float32)
    a = lum[..., None] + (a - lum[..., None]) * 1.04                                              # colore naturale
    a = np.clip(a, 0, 1); a = a + 0.10 * (a - a * a) * (a - 0.5) * 4 * 0.5 + 0.06 * np.sin((a - 0.5) * np.pi) * 0.5   # S morbida
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W * 0.6)) ** 2 + ((yy - H * 0.42) / (H * 0.6)) ** 2)
    a = a * (1 - np.clip((r - 0.6) / 0.8, 0, 1) ** 1.6 * 0.28)[..., None]                      # vignetta leggera
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

def place(e):   # foto del luogo senza persone, ritaglio 4:5 al centro (o in cx)
    o = F + os.path.basename(e['p']) + f"_{e['t']}_luogo.png"
    if not os.path.exists(o):
        os.makedirs(F, exist_ok=True)
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', str(e['t']), '-i', e['p'], '-frames:v', '1', o], check=True)
    im = Image.open(o).convert('RGB'); w0, h0 = im.size; ch = h0; cw = ch * 4 / 5
    if cw > w0: cw = w0; ch = cw * 5 / 4
    x0 = min(max(e.get('cx', 0.5) * w0 - cw / 2, 0), w0 - cw); y0 = (h0 - ch) * e.get('cy', 0.5)
    return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)

def closing(v):
    # ultima slide (Manuel, 5/11): niente volti, una foto significativa del luogo, sfocata, sotto il logo
    im = vv_filter(place(SEL[v]['closing'])).filter(ImageFilter.GaussianBlur(14))
    im = Image.blend(im, Image.new('RGB', (W, H), (8, 7, 6)), 0.45).convert('RGBA')
    l = Image.open(LOGO).convert('RGBA'); l = l.crop(l.getbbox()); lw = 640; l = l.resize((lw, int(l.height * lw / l.width)), Image.LANCZOS)
    y = 470; im.alpha_composite(l, ((W - lw) // 2, y))
    d = ImageDraw.Draw(im); ft = ImageFont.truetype(TIT, 40); y += l.height + 60  # scritta più piccola (Manuel 10/11, prima 60)
    for t in ['SEGUI VOCI VERE', 'PER SCOPRIRE', 'LE PROSSIME STORIE']:
        text_sh(im, (W // 2, y), t, ft, (255, 255, 255) if t != 'SEGUI VOCI VERE' else (235, 196, 128), anchor='ma'); y += 50
    return im

def build(v):
    out = f'copioni/caroselli/{v}_volti'; os.makedirs(out, exist_ok=True)
    for x in os.listdir(out): os.remove(os.path.join(out, x))
    sl = [cover(v)] + [face(x) for x in SEL[v]['faces']] + [closing(v)]
    # ordine (Manuel, 5/11): 01 copertina con un volto forte ma non il più forte, 02 il volto più forte, ogni persona
    # una volta sola; l'ordine è quello di volti_scelti.json (faces[0] = il più forte)
    for i, im in enumerate(sl, 1): im.convert('RGB').save(f'{out}/{i:02d}.jpg', quality=96, subsampling=0)
    th = [im.convert('RGB').resize((216, 270)) for im in sl]; G = Image.new('RGB', (226 * len(th) + 10, 290), (20, 20, 20))
    for i, t in enumerate(th): G.paste(t, (10 + i * 226, 10))
    G.save(f'copioni/caroselli/{v}_volti_anteprima.jpg', quality=85)

for v in (sys.argv[1:] or V): build(v)
