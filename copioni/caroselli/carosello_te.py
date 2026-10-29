# Carosello del lungo te (8 immagini 4:5): stesse funzioni di carosello.py, fotogrammi del lungo v7 in work/te_copy/car/
#   python3 copioni/caroselli/carosello_te.py   (dalla radice del repo)
src=open('copioni/caroselli/carosello.py').read()
exec(src[:src.index("C='work/car/'")])
BEBAS='assets/fonts/BebasNeue-Regular.ttf'
C='work/te_copy/car/t_'
M=0.82  # solo la parte alta del fotogramma: in basso ci sono i sottotitoli impressi
build('te',[
 dict(photo=C+'125.jpg',cover=True,crop=(.5,0,1.0,M),title='Affittate per 3.000 rupie l\'anno',hl=YEL,
      body='Le colline del tè di Munnar, nel 1877. Kerala, India.'),
 dict(photo=C+'189.jpg',crop=(.45,0,1.0,M),kicker='MUNNAR, KERALA',title='Oltre 1.500 metri',hl=YEL,
      body='Tutto quello che vedi, fino all\'orizzonte, è tè.'),
 dict(photo=C+'105.jpg',crop=(.35,0,1.0,M),title='Solo 2-3 foglie',hl=YEL,
      body='Le buone si staccano a mano. Le scure non si usano, ci spiega Sadish.'),
 dict(photo=C+'97.jpg',crop=(.85,0,1.0,M),title='26-29 chili al giorno',
      body='Quanto raccoglie in media una persona, a mano, ci racconta Sadish.'),
 dict(photo=C+'213.jpg',crop=(.4,0,1.0,M),kicker='1880',title='Il primo tè',hl=YEL,
      body='Prima c\'era la foresta. Dal 1901 viene tagliata su larga scala.'),
 dict(photo=C+'265.jpg',crop=(.6,0,1.0,M),kicker='DAL 2005',title='L\'azienda è dei dipendenti',hl=YEL,
      body='La maggior parte, circa 13 mila persone.'),
 dict(photo=C+'221.jpg',crop=(.5,0,1.0,M),kicker='2015',title='Nove giorni di sciopero',hl=YEL,
      body='Migliaia di raccoglitrici bloccano Munnar, senza sindacati né partiti. Ottengono il bonus al 20%.'),
 dict(photo=C+'349.jpg',crop=(.4,0,1.0,M),title='Fuori ora il video su YouTube',hl=YEL),
])
