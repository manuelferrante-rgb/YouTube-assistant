# Carosello "I volti" (Manuel, 4/11): il secondo carosello di ogni lungo, solo primi piani delle persone.
# 1 copertina (il volto più forte + "I volti di ...") + 5 volti + chiusura "Segui Voci Vere" con il logo.
# Filtro Voci Vere: opaco (neri sollevati), chiaro, avvolgente (bagliore morbido, tono caldo oro, vignetta leggera).
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

# (file, cx, cy, h): centro del ritaglio e altezza in frazioni del fotogramma.
# Nei fotogrammi dal lungo i sottotitoli impressi stanno all'85-90% dell'altezza: il ritaglio resta sopra.
V = {
 'mercato': dict(kicker='MARARI, KERALA, INDIA', title='I volti del mercato del pesce',
   cover=('m01.jpg', .53, .42, .72, 'Prepara le reti per la prossima uscita'),   # lungo v6, 54 s
   faces=[('mx_90.jpg', .47, .52, .56, 'Pescatore da trent\'anni'),                # lungo, 90 s
          ('m04.jpg', .50, .52, .60, 'Ci ha portati al mercato'),                  # lungo, 234 s
          ('mx_197.jpg', .64, .40, .66, 'All\'asta, sulla sabbia'),                # lungo, 197 s
          ('m09.jpg', .49, .40, .66, 'Il pesce appena arrivato'),                  # girato 0124, 2.5 s
          ('m10.jpg', .60, .50, .62, 'Si sceglie a mano')]),                       # girato 0120, 4 s
 'arthunkal': dict(kicker='ARTHUNKAL, KERALA, INDIA', title='I volti del pellegrinaggio',
   cover=('a10.jpg', .80, .50, .80, 'Elizabeth, 26 anni, la prima volta'),         # girato 0247, 1 s
   faces=[('a02.jpg', .60, .40, .72, 'All\'arrivo, ad Arthunkal'),                 # girato 0301
          ('a05.jpg', .68, .42, .70, 'Sulla spiaggia, all\'alba'),                 # lungo, 120 s
          ('a07.jpg', .52, .48, .70, 'In strada, dopo 13 km'),                     # lungo, 228 s
          ('a09.jpg', .52, .48, .80, 'Verso la basilica'),                         # girato 0293
          ('a11.jpg', .66, .40, .74, 'Camminano insieme')]),                       # lungo, 166 s
 'te': dict(kicker='MUNNAR, KERALA, INDIA', title='I volti del tè',
   cover=('t01.jpg', .60, .40, .72, 'Sadish, di Munnar'),                          # lungo, 66 s
   faces=[('t07.jpg', .76, .44, .80, 'Sadish, tra i filari'),                      # girato 0384
          ('t03.jpg', .45, .42, .78, 'Sul bus verso Munnar'),                      # girato 0348
          ('t04.jpg', .44, .40, .78, 'Lungo la strada per Munnar'),                # girato 0334
          ('t09.jpg', .26, .50, .80, 'Shaharon, al chiosco del chai'),             # lungo, 351 s
          ('t06.jpg', .16, .58, .70, 'Sul bus, tra le curve')]),                   # girato 0342
}

def crop45(path, cx, cy, h):
    im = Image.open(F + path).convert('RGB'); w0, h0 = im.size
    ch = int(h0 * h); cw = int(ch * 4 / 5)
    x = int(min(max(cx * w0 - cw / 2, 0), w0 - cw)); y = int(min(max(cy * h0 - ch / 2, 0), h0 - ch))
    return im.crop((x, y, x + cw, y + ch)).resize((W, H), Image.LANCZOS)

def vv_filter(im):
    a = np.asarray(im).astype(np.float32) / 255
    lum = a @ np.array([.299, .587, .114], np.float32)
    a = a * 0.80 + lum[..., None] * 0.20                       # un po' meno saturo
    a = 0.11 + 0.84 * a                                        # neri sollevati: opaco
    g = np.array(GOLD, np.float32) / 255
    a = a * (1 - 0.14) + (a * g * 1.6) * 0.14                  # velo caldo oro
    blur = np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(28))).astype(np.float32) / 255
    a = 1 - (1 - a) * (1 - blur * 0.28)                        # bagliore morbido (screen): avvolgente
    a = a * 1.03 + 0.02                                        # più chiaro
    yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    a = a * (1 - np.clip(r - 0.75, 0, 1)[..., None] * 0.30)    # vignetta leggera
    rng = np.random.default_rng(7); a = a + rng.normal(0, 0.012, (H, W, 1)).astype(np.float32)
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
    c = V[v]; f, cx, cy, h, cap = c['cover']
    im = shade(vv_filter(crop45(f, cx, cy, h)), SQ1 - 470, SQ1 + 40, 0.82).convert('RGBA')
    d = ImageDraw.Draw(im); ft = ImageFont.truetype(TIT, 92); fk = ImageFont.truetype(BODY, 30); fc = ImageFont.truetype(BODY, 34)
    lines = wrap(d, c['title'].upper(), ft, W - 120); y = SQ1 - 70 - len(lines) * 98 - 56
    kw = d.textlength(c['kicker'], font=fk); d.rounded_rectangle((60, y - 62, 60 + kw + 32, y - 12), radius=8, fill=GOLD)
    d.text((76, y - 37), c['kicker'], font=fk, fill=(255, 255, 255), anchor='lm')
    for i, t in enumerate(lines): text_sh(im, (60, y + i * 98), t, ft, (255, 255, 255) if i < len(lines) - 1 else (235, 196, 128), r=8)
    y += len(lines) * 98 + 14
    text_sh(im, (60, y), cap, fc, (240, 236, 228)); text_sh(im, (W - 60, y), 'Scorri →', fc, (240, 236, 228), anchor='ra')
    logo(im); return im

def face(f, cx, cy, h, cap):
    im = shade(vv_filter(crop45(f, cx, cy, h)), SQ1 - 260, SQ1 + 20, 0.55).convert('RGBA')
    caption(im, cap); logo(im, 130); return im

def closing(v):
    f, cx, cy, h, _ = V[v]['cover']
    im = vv_filter(crop45(f, cx, cy, h)).filter(ImageFilter.GaussianBlur(14))
    im = Image.blend(im, Image.new('RGB', (W, H), (14, 11, 8)), 0.55).convert('RGBA')
    l = Image.open(LOGO).convert('RGBA'); l = l.crop(l.getbbox()); lw = 640; l = l.resize((lw, int(l.height * lw / l.width)), Image.LANCZOS)
    y = 470; im.alpha_composite(l, ((W - lw) // 2, y))
    d = ImageDraw.Draw(im); ft = ImageFont.truetype(TIT, 60); y += l.height + 70
    for t in ['SEGUI VOCI VERE', 'PER SCOPRIRE', 'LE PROSSIME STORIE']:
        text_sh(im, (W // 2, y), t, ft, (255, 255, 255) if t != 'SEGUI VOCI VERE' else (235, 196, 128), anchor='ma'); y += 74
    return im

def build(v):
    out = f'copioni/caroselli/{v}_volti'; os.makedirs(out, exist_ok=True)
    for x in os.listdir(out): os.remove(os.path.join(out, x))
    sl = [cover(v)] + [face(*x) for x in V[v]['faces']] + [closing(v)]
    for i, im in enumerate(sl, 1): im.convert('RGB').save(f'{out}/{i:02d}.jpg', quality=93)
    th = [im.convert('RGB').resize((216, 270)) for im in sl]; G = Image.new('RGB', (226 * len(th) + 10, 290), (20, 20, 20))
    for i, t in enumerate(th): G.paste(t, (10 + i * 226, 10))
    G.save(f'copioni/caroselli/{v}_volti_anteprima.jpg', quality=85)

for v in (sys.argv[1:] or V): build(v)
