# Caroselli IG/YT 4:5 (1080x1350): foto a tutto schermo, titolo Bebas Neue, testo Inter, logo Voci Vere.
#   python3 copioni/caroselli/carosello.py   (dalla radice del repo; foto in work/car/)
import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import numpy as np
W,H=1080,1350
SAFE=135  # YouTube ritaglia i post a quadrato: testo e logo dentro il quadrato centrale 1080x1080
BEBAS='/root/fonts/bebas-neue-latin-400-normal.woff'
INTER='/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
INTERB='/usr/share/fonts/opentype/inter/Inter-Bold.otf'
LOGO='assets/brand/logo_vocivere_trasparente_chiaro.png'
YEL=(255,214,10); WHITE=(255,255,255); GOLD=(182,138,75)

def crop45(path,cx=.5,cy=.5,zoom=1.0,maxh=1.0):
    im=Image.open(path).convert('RGB'); w,h=im.size; ch=int(h*maxh/zoom); cw=int(ch*4/5)
    x=int((w-cw)*cx); y=int((h-ch)*cy); im=im.crop((x,y,x+cw,y+ch)).resize((W,H),Image.LANCZOS)
    im=ImageEnhance.Contrast(im).enhance(1.08); return ImageEnhance.Color(im).enhance(1.12)

def shade(im,top=0.35,bottom=0.85):
    g=np.zeros((H,W),np.float32); y=np.arange(H)[:,None]/H
    g+=np.clip((0.30-y)/0.30,0,1)*top            # in alto per il logo
    g+=np.clip((y-0.42)/0.58,0,1)**1.2*bottom    # in basso per il testo
    m=Image.fromarray((np.clip(g,0,1)*255).astype('uint8'))
    return Image.composite(Image.new('RGB',(W,H),(0,0,0)),im,m)

def shade_top(im):
    g=np.zeros((H,W),np.float32); y=np.arange(H)[:,None]/H
    g+=np.clip((0.62-y)/0.62,0,1)**1.1*0.85
    m=Image.fromarray((np.clip(g,0,1)*255).astype('uint8'))
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

def drop(base,draw_fn,r=8,op=200):
    sh=Image.new('RGBA',base.size,(0,0,0,0)); draw_fn(ImageDraw.Draw(sh),(0,0,0,op),4)
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(r)))
    draw_fn(ImageDraw.Draw(base),None,0)

def slide(out,photo,title,body='',n=None,tot=None,cover=False,crop=(.5,.5,1.0,1.0),title_col=WHITE,hl=None,kicker=None,top=False):
    im=crop45(photo,*crop)
    im=(shade_top(im) if top else shade(im,0.45,0.9 if body or cover else 0.75)).convert('RGBA')
    d=ImageDraw.Draw(im); M=70
    l=Image.open(LOGO).convert('RGBA'); l=l.crop(l.getbbox()); lw=230 if cover else 170
    l=l.resize((lw,int(l.height*lw/l.width)),Image.LANCZOS); im.alpha_composite(l,(M-6,SAFE+20))
    if n and not cover:
        f=ImageFont.truetype(INTER,30); t=f'{n}/{tot}'; d.text((W-M-d.textlength(t,font=f),SAFE+30),t,font=f,fill=(255,255,255,210))
    tsize=150 if cover else 112
    ft=ImageFont.truetype(BEBAS,tsize); fb=ImageFont.truetype(INTER,40 if not cover else 42); fk=ImageFont.truetype(INTERB,32)
    tl=wrap(d,title,ft,W-2*M); bl=wrap(d,body,fb,W-2*M) if body else []
    th=len(tl)*int(tsize*0.92); bh=len(bl)*54
    y=H-SAFE-40-(70 if cover else 0)-bh-(28 if bl else 0)-th-(56 if kicker else 0)
    if top: y=SAFE+20+int(lw*l.height/l.width)+50
    if kicker:
        kw=d.textlength(kicker,font=fk); d.rounded_rectangle((M,y,M+kw+32,y+46),radius=8,fill=GOLD); d.text((M+16,y+5),kicker,font=fk,fill=WHITE); y+=62
    for i,t in enumerate(tl):
        col=hl if (hl and i==len(tl)-1) else title_col
        yy=y
        drop(im,lambda dd,c,o,t=t,yy=yy,col=col: dd.text((M+o,yy+o),t,font=ft,fill=c or col))
        y+=int(tsize*0.92)
    y+=28
    for t in bl:
        yy=y; drop(im,lambda dd,c,o,t=t,yy=yy: dd.text((M+o//2,yy+o//2),t,font=fb,fill=c or WHITE),6,170); y+=54
    if cover:
        f=ImageFont.truetype(INTERB,34); t='Scorri  →'; d.text((W-M-d.textlength(t,font=f),H-SAFE-60),t,font=f,fill=YEL)
    im.convert('RGB').save(out,quality=92)

def build(name,slides):
    os.makedirs(f'copioni/caroselli/{name}',exist_ok=True); tot=len(slides)
    for i,s in enumerate(slides,1):
        slide(f'copioni/caroselli/{name}/{i:02d}.jpg',n=i,tot=tot,**s)
    ims=[Image.open(f'copioni/caroselli/{name}/{i:02d}.jpg').resize((270,338)) for i in range(1,tot+1)]
    G=Image.new('RGB',(270*4+50,338*2+30),(20,20,20))
    for i,m in enumerate(ims): G.paste(m,(10+(i%4)*(270+10),10+(i//4)*(338+10)))
    G.save(f'copioni/caroselli/{name}_anteprima.jpg',quality=85)

C='work/car/'
build('mercato',[
 dict(photo=C+'m/m_4.5.jpg',cover=True,top=True,crop=(.6,.5,1.0,1.0),title='Pesava come una persona',hl=YEL,
      body='Il mercato del pesce senza tetto né banchi. Kerala, India.'),
 dict(photo=C+'m/m_192.jpg',crop=(.35,.5,1.0,1.0),kicker='MARARI, KERALA',title='Sveglia alle 3',hl=YEL,
      body='In mare alle 4, al mercato alle 8. Ogni giorno.'),
 dict(photo=C+'m/m_172.jpg',crop=(.45,.5,1.0,1.0),title='Alle 8 si torna a riva',
      body='Le barche piccole escono e rientrano ogni giorno.'),
 dict(photo=C+'m/m_220.jpg',crop=(.5,.5,1.0,1.0),title='Niente tetto. Niente banchi.',hl=YEL,
      body='Il mercato è la spiaggia: il pesce si vende all\'asta sulla sabbia.'),
 dict(photo=C+'m/m_4.jpg',crop=(.8,.5,1.0,1.0),title='Nelle ceste, sulle teste',
      body='Poi sulle bilance, dove partono le trattative.'),
 dict(photo=C+'m/m_288.jpg',crop=(.4,.5,1.0,1.0),title='Tutto va veloce',
      body='Ghiaccio nei cesti: il pesce deve partire finché è fresco.'),
 dict(photo=C+'m/m_136.jpg',crop=(.43,0,1.0,0.86),title='«Un posto in pace»',hl=YEL,
      body='Cristiani, induisti, musulmani: qui vivono insieme, ci racconta.'),
 dict(photo='work/thumb/m_3m47.5.jpg',crop=(.5,.5,1.0,1.0),title='Tu ti alzeresti alle 3?',hl=YEL,
      body='Scrivilo nei commenti.\nIl video completo è uscito sul canale.'),
])
build('arthunkal',[
 dict(photo=C+'a/a_090733_0296.jpg',cover=True,crop=(.75,.5,1.0,1.0),title='13 km pregando, senza mai fermarsi',hl=YEL,
      body='Un rosario che dura tutta la notte. Kerala, India.'),
 dict(photo=C+'a/a_023510_0233.jpg',crop=(.45,.5,1.0,1.0),kicker='2:30 DI NOTTE',title='Il tè è già pronto',hl=YEL,
      body='Bancarelle di tè e acqua al buio, per chi cammina.'),
 dict(photo=C+'a/a_023818_0237.jpg',crop=(.5,.5,1.0,1.0),title='Si parte a mezzanotte',
      body='Dal santuario di Kreupasanam, a Kalavoor, sulla costa.'),
 dict(photo=C+'a/a_072504_0246.jpg',crop=(.55,.5,1.0,1.0),kicker='ALL\'ALBA',title='Sulla spiaggia',hl=YEL,
      body='Prima si camminava in strada. Con il traffico, si sono spostati sul bagnasciuga.'),
 dict(photo=C+'a/a_075747_0267.jpg',crop=(.62,.5,1.0,1.0),title='Il rosario non si interrompe',hl=YEL,
      body='Akhanda Japamala, il rosario ininterrotto: 13 km di preghiera.'),
 dict(photo=C+'a/a_091255_0302.jpg',crop=(.5,.3,1.0,1.0),kicker='ARTHUNKAL',title='Mani alzate verso la basilica',
      body='L\'arrivo, la mattina, davanti alla basilica di Sant\'Andrea.'),
 dict(photo=C+'a/a_090825_0298.jpg',crop=(.47,.5,1.0,1.0),title='Un pezzo d\'Italia',hl=YEL,
      body='La chiesa la ricostruisce nel 1584 un gesuita italiano, il «padre bianco». La statua di San Sebastiano arriva da Milano nel 1647.'),
 dict(photo=C+'a/a_093557_0316.jpg',crop=(.45,.5,1.0,1.0),title='Cammineresti 13 km di notte pregando?',hl=YEL,
      body='Scrivi SÌ o NO nei commenti.\nIl video completo è uscito sul canale.'),
])
