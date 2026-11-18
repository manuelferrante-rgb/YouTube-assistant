# Miniature arthunkal v4 (Copy, 17/11, rifacimento): Manuel dentro la scena con il posto enorme (stile "MUMBAI" di
# Progetto Happiness), la folla di notte, la basilica ricostruita da un gesuita italiano. Usa make() di miniature_v3.py.
#   python3 copioni/arthunkal_miniature/v4.py   (girato in work/arth/raw)
import sys; sys.path.insert(0, 'copioni/miniature_v3')
import miniature_v3 as M
M.OUT = 'copioni/{}_miniature/v4/'
R = 'work/arth/raw/'
def c(n): return R + next(f for f in __import__('os').listdir(R) if f'_{n}_' in f)
J = [
 ('M1_manuel_kerala', c('0309'), 0.4, .33, .45, 1.1, 'dietro', {'it': 'KERALA', 'en': 'KERALA'}, False),
 ('M2_notte',        c('0237'), 1.2, .45, .5, 1.1, 'riga', {'it': 'DA MEZZANOTTE ALL\'ALBA', 'en': 'FROM MIDNIGHT TO DAWN'}, True),
 ('M3_basilica',       c('0302'), 1.0, .5, .42, 1.0, 'riga', {'it': 'RICOSTRUITA DA UN ITALIANO', 'en': 'REBUILT BY AN ITALIAN'}, False),
]
for name, src, t, cx, cy, z, lay, txt, night in J:
    for lang in ('it', 'en'):
        print(M.make(name, 'arthunkal', lang, src, t, cx, cy, z, lay, txt[lang], night=night))
