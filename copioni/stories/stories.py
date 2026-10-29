# Storie IG 9:16 (1080x1920) dal lungo montato: foto + testo + spazio per quiz/sondaggio/box domande.
#   python3 copioni/stories/stories.py   (dalla radice; lunghi in work/stories/, scaricati da Drive montati/<video>)
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import numpy as np
W,H=1080,1920
TOP,BOT=260,380   # zone coperte dall'interfaccia di IG (barra profilo in alto, risposta in basso)
BEBAS='assets/fonts/BebasNeue-Regular.ttf'  # OFL, da google/fonts
INTER='/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
INTERB='/usr/share/fonts/opentype/inter/Inter-Bold.otf'
LOGO='assets/brand/logo_vocivere_trasparente_chiaro.png'
YEL=(255,214,10); WHITE=(255,255,255); GOLD=(182,138,75)
SRC={'mercato':'work/stories/VociVere_mercato_long_v6_3840x2160.mp4','arthunkal':'work/stories/VociVere_arthunkal_long_4K.mp4',
     'te':'work/te_copy/VociVere_te_long_4K.mp4'}

def frame(video,t):
    out=f'work/stories/f_{video}_{t}.png'
    if not os.path.exists(out):
        subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',SRC[video],'-frames:v','1',out],check=True)
    return out

def crop916(path,cx=.5,zoom=1.0,cy=.5):
    # il lungo ha i sottotitoli impressi in basso: si usa solo l'82% alto del fotogramma
    im=Image.open(path).convert('RGB'); w,h=im.size; uh=int(h*0.82); ch=int(uh/zoom); cw=int(ch*9/16)
    x=int((w-cw)*cx); y=int((uh-ch)*cy); im=im.crop((x,y,x+cw,y+ch)).resize((W,H),Image.LANCZOS)
    im=ImageEnhance.Contrast(im).enhance(1.06); return ImageEnhance.Color(im).enhance(1.1)

def grad(im,spots):
    g=np.zeros((H,W),np.float32); y=np.arange(H)[:,None]/H
    for a,b,op in spots:  # sfuma verso il nero tra a e b (frazioni dell'altezza)
        g=np.maximum(g,np.clip((y-a)/(b-a) if b>a else (a-y)/(a-b),0,1)*op)
    m=Image.fromarray((np.broadcast_to(g,(H,W))*255).astype('uint8'))
    return Image.composite(Image.new('RGB',(W,H),(0,0,0)),im,m)

def wrap(d,text,font,maxw):
    out=[]
    for para in text.split('\n'):
        line=''
        for w in para.split():
            t=(line+' '+w).strip()
            if d.textlength(t,font=font)<=maxw: line=t
            else: out.append(line); line=w
        out.append(line)
    return out

def drop(base,fn,r=8,op=210):
    sh=Image.new('RGBA',base.size,(0,0,0,0)); fn(ImageDraw.Draw(sh),(0,0,0,op),4)
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(r))); fn(ImageDraw.Draw(base),None,0)

def block(im,y,title,body,kicker,tsize,hl,center=False):
    d=ImageDraw.Draw(im); M=80
    ft=ImageFont.truetype(BEBAS,tsize); fb=ImageFont.truetype(INTER,44); fk=ImageFont.truetype(INTERB,34)
    def X(t,f): return (W-d.textlength(t,font=f))/2 if center else M
    if kicker:
        kw=d.textlength(kicker,font=fk); x=(W-kw-36)/2 if center else M
        d.rounded_rectangle((x,y,x+kw+36,y+52),radius=10,fill=GOLD); d.text((x+18,y+6),kicker,font=fk,fill=WHITE); y+=76
    tl=wrap(d,title,ft,W-2*M)
    for i,t in enumerate(tl):
        col=YEL if (hl and i>=len(tl)-hl) else WHITE; yy=y; xx=X(t,ft)
        drop(im,lambda dd,c,o,t=t,yy=yy,xx=xx,col=col: dd.text((xx+o,yy+o),t,font=ft,fill=c or col)); y+=int(tsize*0.93)
    if body:
        y+=30
        for t in wrap(d,body,fb,W-2*M):
            yy=y; xx=X(t,fb); drop(im,lambda dd,c,o,t=t,yy=yy,xx=xx: dd.text((xx+o//2,yy+o//2),t,font=fb,fill=c or WHITE),6,180); y+=60
    return y

def height(title,body,kicker,tsize):
    d=ImageDraw.Draw(Image.new('RGB',(W,H))); M=80
    n=len(wrap(d,title,ImageFont.truetype(BEBAS,tsize),W-2*M)); b=len(wrap(d,body,ImageFont.truetype(INTER,44),W-2*M)) if body else 0
    return (76 if kicker else 0)+int(n*tsize*0.93)+(30+b*60 if body else 0)

def story(out,video,t,title,body='',kicker=None,kind='fact',crop=(.5,1.0,.5),hl=1,tsize=150):
    """kind: fact = testo in basso; ask = domanda in alto, centro libero per lo sticker (quiz, sondaggio, domande)."""
    im=crop916(frame(video,t),*crop)
    if kind=='ask':
        im=grad(im,[(0.55,0.0,0.92),(0.62,1.0,0.35)]).convert('RGBA'); y=TOP+150
        block(im,y,title,body,kicker,tsize,hl,center=True)
    else:
        im=grad(im,[(0.40,1.0,0.95),(0.22,0.0,0.55)]).convert('RGBA')
        y=H-BOT-40-height(title,body,kicker,tsize); block(im,y,title,body,kicker,tsize,hl)
    l=Image.open(LOGO).convert('RGBA'); l=l.crop(l.getbbox()); lw=200; l=l.resize((lw,int(l.height*lw/l.width)),Image.LANCZOS)
    im.alpha_composite(l,(74,TOP+10))
    im.convert('RGB').save(out,quality=92)

def build(video,name,items):
    d=f'copioni/stories/{video}/{name}'; os.makedirs(d,exist_ok=True)
    for f in os.listdir(d): os.remove(os.path.join(d,f))
    for i,s in enumerate(items,1): story(f'{d}/{i:02d}.jpg',**s)
    n=len(items); ims=[Image.open(f'{d}/{i:02d}.jpg').resize((216,384)) for i in range(1,n+1)]
    G=Image.new('RGB',(226*n+10,404),(20,20,20))
    for i,m in enumerate(ims): G.paste(m,(10+i*226,10))
    G.save(f'copioni/stories/{video}_{name}_anteprima.jpg',quality=85)

M,A,T='mercato','arthunkal','te'
ONLY=sys.argv[1:]  # es. python3 copioni/stories/stories.py te
_build=build
def build(video,*a):
    if not ONLY or video in ONLY: _build(video,*a)
build(M,'set1_mercato',[
 dict(video=M,t=220,kicker='MARARI, KERALA',title='Un mercato del pesce senza tetto',body='Né banchi, né muri. Solo la spiaggia, le barche e chi compra.',crop=(.5,1,.5)),
 dict(video=M,t=73,kind='ask',title='A che ora si sveglia un pescatore qui?',hl=0,crop=(.5,1,.5),tsize=130),
 dict(video=M,t=157,title='Alle 3 di notte',body='Alle 4 è già in mare. Alle 8 il pesce arriva qui, sulla spiaggia.',crop=(.4,1,.5)),
 dict(video=M,t=223,title='L\'asta si fa sulla sabbia',body='Arriva la barca, tutti si avvicinano, e si comincia a trattare.',crop=(.5,1,.5)),
 dict(video=M,t=226,kind='ask',title='Quanto pesava il pesce più grande della mattina?',hl=0,crop=(.5,1,.5),tsize=124),
 dict(video=M,t=280,title='50-55 chili',body='"Veramente come una persona." Ce l\'hanno detto lì, al mercato.',crop=(.55,1,.5)),
 dict(video=M,t=289,title='Tutto va veloce',body='Ghiaccio nei cesti: il pesce deve partire finché è fresco.',crop=(.4,1,.5)),
 dict(video=M,t=334,kind='ask',title='Com\'è il mercato del pesce dove vivi tu?',body='Raccontamelo qui sotto. Tutta la storia nel video sul canale.',hl=0,crop=(.5,1,.5),tsize=130),
])
build(M,'set2_persone',[
 dict(video=M,t=124,kicker='MARARI, KERALA',title='Fa il pescatore da 30 anni',body='Lo incontriamo sulla spiaggia, seduto sulla sua barca.',crop=(.42,1,.5)),
 dict(video=M,t=88,title='Non è il suo unico lavoro',body='Fa anche la guida in kayak, tra i canali dietro la spiaggia. E ci dice che gli piace di più.',crop=(.5,1,.5)),
 dict(video=M,t=136,title='«Un posto in pace»',body='Cristiani, induisti, musulmani: qui vivono insieme, ci racconta.',crop=(.42,1,.5)),
 dict(video=M,t=145,title='Due giorni senza pesca',body='Succede durante la festa, ci racconta. E il cibo è gratis per chiunque arrivi.',crop=(.4,1,.5)),
 dict(video=M,t=307,kind='ask',title='Come si chiama questo pane del Kerala?',hl=0,crop=(.45,1,.5),tsize=130),
 dict(video=M,t=313,title='Porotta',body='Il pane sfogliato del Kerala, fatto al momento: la colazione dopo il mercato.',crop=(.4,1,.5)),
 dict(video=M,t=82,kind='ask',title='Cosa chiederesti a un pescatore di Marari?',body='Scrivilo qui sotto: le domande migliori le porto nei prossimi video.',hl=0,crop=(.45,1,.5),tsize=124),
])
build(A,'set1_cammino',[
 dict(video=A,t=79,kicker='2:30 DI NOTTE',title='Camminano da mezzanotte',body='Costa del Kerala, India. La strada è già piena.',crop=(.4,1,.5)),
 dict(video=A,t=88,kind='ask',title='Quanti km camminano, pregando?',hl=0,crop=(.5,1,.5),tsize=136),
 dict(video=A,t=97,title='13 km',body='Da Kalavoor alla basilica di Arthunkal, lungo la costa. Senza mai smettere di pregare.',crop=(.55,1,.5)),
 dict(video=A,t=140,kicker='AKHANDA JAPAMALA',title='Il rosario ininterrotto',body='Chi guida dice la prima metà della preghiera, gli altri rispondono. Per chilometri.',crop=(.72,1,.5)),
 dict(video=A,t=19,kind='ask',title='Quante persone camminano?',hl=0,crop=(.5,1,.5),tsize=124),
 dict(video=A,t=304,title='Quasi un milione',body='Le stime che ci danno sul posto vanno da 400 mila a un milione. La prima volta, nel 2002, erano poche centinaia.',crop=(.5,1,.5)),
 dict(video=A,t=34,title='Perché sulla spiaggia?',body='Prima si camminava in strada. Con il traffico, si sono spostati sul bagnasciuga.',crop=(.45,1,.5)),
 dict(video=A,t=1,kind='ask',title='Cammineresti 13 km di notte?',body='Tutta la storia nel video sul canale.',hl=0,crop=(.55,1,.5),tsize=136),
])
build(A,'set2_storie',[
 dict(video=A,t=256,kicker='SULLA STRADA',title='C\'è anche chi non cammina',body='Pentoloni e bicchieri d\'acqua: cibo e acqua gratis a chiunque passa.',crop=(.45,1,.5)),
 dict(video=A,t=203.0,title='Elizabeth, 26 anni',body='Per lei è la prima volta. "È un atto di devozione alla Madonna."',crop=(.52,1,.5)),
 dict(video=A,t=169,title='Tutti insieme',body='Cammina chi è cristiano, e anche ragazzi musulmani. Ce lo raccontano loro.',crop=(.5,1,.5)),
 dict(video=A,t=316,kind='ask',title='Da dove arriva la statua di San Sebastiano di Arthunkal?',hl=0,crop=(.5,1,.5),tsize=118),
 dict(video=A,t=331,title='Da Milano, nel 1647',body='Arriva in una chiesa sul mare del Kerala, ricostruita nel 1584 da un gesuita italiano.',crop=(.45,1,.5)),
 dict(video=A,t=346,kind='ask',title='Come chiamano qui quel gesuita italiano?',hl=0,crop=(.5,1,.5),tsize=130),
 dict(video=A,t=349,kicker='VELUTHACHAN',title='Il padre bianco',body='Padre Giacomo Fenicio. Lo chiamano ancora così, più di 400 anni dopo.',crop=(.55,1,.5)),
 dict(video=A,t=289,kind='ask',title='Hai mai fatto un pellegrinaggio a piedi?',body='Raccontamelo qui sotto.',hl=0,crop=(.5,1,.5),tsize=130),
])
build(T,'set1_raccolta',[
 dict(video=T,t=189,kicker='MUNNAR, KERALA',title='Tutto questo è tè',body='Colline fino all\'orizzonte, a oltre 1.500 metri.',crop=(.5,1,.5)),
 dict(video=T,t=101,kind='ask',title='Quante foglie si staccano da ogni rametto?',hl=0,crop=(.45,1,.5),tsize=124),
 dict(video=T,t=105,title='Solo 2-3 foglie',body='Le buone vanno in fabbrica. Le scure non si usano, ci spiega Sadish.',crop=(.35,1,.5)),
 dict(video=T,t=125,kind='ask',title='Ogni quanto si torna sulla stessa pianta?',hl=0,crop=(.5,1,.5),tsize=124),
 dict(video=T,t=121,title='Ogni 10-15 giorni',body='Oggi qui, domani un\'altra collina. Poi si torna: è un giro.',crop=(.5,1,.5)),
 dict(video=T,t=81,kind='ask',title='Quanti anni vive una pianta di tè?',hl=0,crop=(.5,1,.5),tsize=130),
 dict(video=T,t=73,title='Più di cent\'anni',body='"Questa pianta ha più di cent\'anni", ci dice Sadish.',crop=(.6,1,.5)),
 dict(video=T,t=97,kind='ask',title='Quanti chili raccoglie una persona in un giorno?',hl=0,crop=(.8,1,.5),tsize=118),
 dict(video=T,t=161,title='26-29 chili',body='In media, a mano, ci dice Sadish. Dalle 8 alle 5, con la pausa pranzo.',crop=(.75,1,.5)),
 dict(video=T,t=229,kind='ask',title='Che tè bevi tu?',body='Raccontamelo qui sotto. Tutta la storia nel video sul canale.',hl=0,crop=(.5,1,.5),tsize=140),
])
build(T,'set2_storia',[
 dict(video=T,t=24,kind='ask',title='Nel 1877 queste colline vengono affittate. Per quanto?',hl=0,crop=(.62,1,.5),tsize=118),
 dict(video=T,t=213,title='3.000 rupie l\'anno',body='Circa 136 mila acri, da un raja a un britannico, John Daniel Munro.',crop=(.4,1,.5)),
 dict(video=T,t=253,kicker='1880',title='Il primo tè',body='Prima si provano caffè, cardamomo e china. Dal 1901 la foresta viene tagliata su larga scala.',crop=(.5,1,.5)),
 dict(video=T,t=265,kind='ask',title='Di chi è oggi l\'azienda del tè di queste colline?',hl=0,crop=(.6,1,.5),tsize=118),
 dict(video=T,t=273,kicker='DAL 2005',title='Dei dipendenti',body='Per la maggior parte: circa 13 mila persone.',crop=(.5,1,.5)),
 dict(video=T,t=221,kicker='2015',title='Nove giorni di sciopero',body='Migliaia di raccoglitrici bloccano Munnar. Si chiamano Pombilai Orumai: unità delle donne.',crop=(.5,1,.5)),
 dict(video=T,t=317,kind='ask',title='Chi produce più tè al mondo?',hl=0,crop=(.5,1,.5),tsize=130),
 dict(video=T,t=321,title='La Cina, poi l\'India',body='"L\'India è seconda", ci dice Sadish. "Qui è una cultura molto profonda."',crop=(.8,1,.5)),
 dict(video=T,t=349,title='Il chai master',body='Tira il tè da un bicchiere all\'altro. Gli ho chiesto di parlare: si è rifiutato.',crop=(.42,1,.5)),
 dict(video=T,t=361,kind='ask',title='Hai mai assaggiato il chai?',body='Tutta la storia nel video sul canale.',hl=0,crop=(.45,1,.5),tsize=136),
])
