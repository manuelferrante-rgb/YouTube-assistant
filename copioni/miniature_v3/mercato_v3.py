# Miniature v3 del mercato (Copy, 9/11): stesso stile di miniature_v3.py, rifatte dopo l'analisi di Insights a 7 giorni
# (il cuore del video è l'asta sulla sabbia; titolo = fatto concreto). Girato in work/mercato/raw (Drive, cartella mercato).
#   python3 copioni/miniature_v3/mercato_v3.py
import sys; sys.path.insert(0, 'copioni/miniature_v3')
from miniature_v3 import make
R = 'work/mercato/raw/'
J = {
 'M1_signora': dict(src=R + 'DJI_0118.MP4', t=20.0, cx=.72, cy=.4, zoom=1.7, layout='basso',
     it=("ALL'ASTA", 'SULLA SABBIA'), en=('AUCTIONED', 'ON THE SAND')),
 'M2_mattina': dict(src=R + 'DJI_0120.MP4', t=3.0, cx=.8, cy=.42, zoom=1.6, layout='basso', red=True,
     it=('OGNI MATTINA', 'ALLE 8'), en=('EVERY MORNING', 'AT 8 A.M.')),
 'M3_asta': dict(src=R + 'DJI_0120.MP4', t=4.5, cx=.45, cy=.6, zoom=1.35, layout='basso',
     it=('NIENTE TETTO,', 'NIENTE BANCHI'), en=('NO ROOF,', 'NO STALLS')),
}
for i, (n, p) in enumerate(J.items(), 1):
    p = dict(p); it, en = p.pop('it'), p.pop('en')
    for lang, txt in (('it', it), ('en', en)):
        print(make(f'{i}_{n}', 'mercato', lang, text=txt, **p))
