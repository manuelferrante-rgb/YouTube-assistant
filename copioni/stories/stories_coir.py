# Storie IG del lungo coir (Copy, 8/11): 3 set da 6 dal girato originale (testi in copioni/coir_testi.md, sezione STORIE).
# Usa le funzioni di stories.py; fotogrammi dalle clip in work/coir/raw (nessun sottotitolo impresso).
#   python3 copioni/stories/stories_coir.py
import sys, glob, os, subprocess
sys.argv = [sys.argv[0], '__nessuno__']          # stories.py non rigenera gli altri video
sys.path.insert(0, 'copioni/stories'); import stories as S
from PIL import Image, ImageEnhance
def frame(video, t):
    n, s = t; out = f'work/coir/car/s_{n}_{s}.png'
    if not os.path.exists(out):
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', str(s), '-i', glob.glob(f'work/coir/raw/*_{n}_D.MP4')[0], '-frames:v', '1', out], check=True)
    return out
def crop916(path, cx=.5, zoom=1.0, cy=.5):
    im = Image.open(path).convert('RGB'); w, h = im.size; ch = int(h / zoom); cw = int(ch * 9 / 16)
    x = int((w - cw) * cx); y = int((h - ch) * cy); im = im.crop((x, y, x + cw, y + ch)).resize((S.W, S.H), Image.LANCZOS)
    return ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.06)).enhance(1.1)
S.frame, S.crop916 = frame, crop916
C = 'coir'; B = S._build
B(C, 'set1_dietro_le_quinte', [
 dict(video=C, t=('0034', 1.0), kind='ask', title='Sai da dove viene lo zerbino di cocco?', hl=0, crop=(.5, 1, .5), tsize=124),
 dict(video=C, t=('0021', 2.0), kicker='LA LAGUNA', title='Restano sott\'acqua fino a un anno', body='I gusci di cocco, finché la fibra non si stacca.', crop=(.5, 1, .5)),
 dict(video=C, t=('0046', 3.0), title='Ha 76 anni', body='Ogni giorno spinge la sua barca e tira su i gusci, a mano.', crop=(.45, 1, .5)),
 dict(video=C, t=('0063', 14.0), title='Qui si aprono i gusci, a mano', body='Sedute per terra, sotto la tettoia, fino alle due.', crop=(.5, 1, .5)),
 dict(video=C, t=('0542', 5.0), kind='ask', title='Cosa chiederesti a queste donne?', body='Scrivilo qui sotto.', hl=0, crop=(.45, 1, .5), tsize=130),
 dict(video=C, t=('0087', 1.0), kind='ask', title='La storia intera, domenica su YouTube', hl=0, crop=(.5, 1, .5), tsize=124),
])
B(C, 'set2_made_in_india', [
 dict(video=C, t=('0087', 1.0), kicker='MADE IN INDIA', title='Sopra c\'è scritto Made in India', body='Ma non c\'è scritto chi l\'ha fatto.', crop=(.5, 1, .5)),
 dict(video=C, t=('0540', 2.0), kind='ask', title='Quanto va a loro per un tappeto?', hl=0, crop=(.4, 1, .5), tsize=124),
 dict(video=C, t=('0109', 2.0), title='80 rupie', body='Circa 80 centesimi per un tappeto. Ce lo dicono loro.', crop=(.5, 1, .5)),
 dict(video=C, t=('0069', 1.0), title='4 euro al giorno', body='Il salario è di 400 rupie al giorno, ci dice chi lavora qui.', crop=(.35, 1, .5)),
 dict(video=C, t=('0549', 8.0), kind='ask', title='Lo sapevi?', hl=0, crop=(.6, 1, .5), tsize=150),
 dict(video=C, t=('0547', 50.0), kind='ask', title='La storia intera è sul canale', body='Il link qui sotto.', hl=0, crop=(.5, 1, .5), tsize=124),
])
B(C, 'set3_dal_guscio_alla_corda', [
 dict(video=C, t=('0107', 4.0), kicker='1', title='Nell\'acqua, fino a un anno', crop=(.5, 1, .5), tsize=140),
 dict(video=C, t=('0544', 2.0), kicker='2', title='Si tirano su a mano', crop=(.45, 1, .5), tsize=140),
 dict(video=C, t=('0540', 2.0), kicker='3', title='Si aprono, uno a uno', crop=(.4, 1, .5), tsize=140),
 dict(video=C, t=('0017', 5.0), kicker='4', title='La fibra passa alle macchine', crop=(.5, 1, .5), tsize=140),
 dict(video=C, t=('0074', 2.0), kind='ask', kicker='5', title='Diventa corda', body='Nel tuo paese c\'è un mestiere che sta sparendo?', hl=0, crop=(.35, 1, .5), tsize=140),
 dict(video=C, t=('0091', 2.0), kind='ask', title='Ascolta altre voci', body='Tutta la storia nel video sul canale.', hl=0, crop=(.6, 1, .5), tsize=140),
])
print('ok')
