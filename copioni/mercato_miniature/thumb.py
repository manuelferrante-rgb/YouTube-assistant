import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
W,H=1280,720
F={'anton':'/root/fonts/anton-latin-400-normal.woff','bebas':'/root/fonts/bebas-neue-latin-400-normal.woff',
   'archivo':'/root/fonts/archivo-black-latin-400-normal.woff','oswald':'/root/fonts/oswald-latin-700-normal.woff'}
GOLD=(214,168,96); YEL=(255,214,10)

def cover(im,w,h,cx=0.5,cy=0.5):
    r=max(w/im.width,h/im.height); im=im.resize((int(im.width*r+.5),int(im.height*r+.5)),Image.LANCZOS)
    x=int((im.width-w)*cx); y=int((im.height-h)*cy); return im.crop((x,y,x+w,y+h))

def grade(im,c=1.15,s=1.25,b=0.95):
    im=ImageEnhance.Contrast(im).enhance(c); im=ImageEnhance.Color(im).enhance(s); return ImageEnhance.Brightness(im).enhance(b)

def bg_sea(name):
    im=Image.open(name).convert('RGB'); im=grade(cover(im,W,H,0.35,0.6),1.25,1.35,0.9)
    # scurisco a sinistra e in alto per il testo
    g=Image.linear_gradient('L').rotate(90).resize((W,H))  # chiaro a destra? 
    shade=Image.new('RGB',(W,H),(5,15,30))
    m=ImageOps.invert(Image.linear_gradient('L').rotate(-90,expand=True).resize((W,H)))
    m=m.point(lambda v:int(v*0.75))
    return Image.composite(shade,im,m)

def manuel(scale=1.0):
    a=Image.open('cut_m.png')
    al=a.getchannel('A').point(lambda v:0 if v<60 else min(255,int((v-60)*1.6)))
    import numpy as np
    A=np.asarray(a.convert('RGB')).astype(int); r,g,b=A[...,0],A[...,1],A[...,2]
    sky=(b>r+12)&((r+g+b)/3>120); sky[1340:]=False
    sky=Image.fromarray((sky*255).astype('uint8')).filter(ImageFilter.MaxFilter(3))
    al=Image.composite(Image.new('L',a.size,0),al,sky)
    d=ImageDraw.Draw(al); d.rectangle((0,0,1000,a.height),fill=0); d.rectangle((3000,0,a.width,a.height),fill=0)
    al=al.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.5))
    rgb=grade(a.convert('RGB'),1.1,1.15,1.05)
    # defringe: i bordi semitrasparenti (cielo tra i capelli) presi scuri come i capelli
    dark=ImageEnhance.Brightness(rgb).enhance(0.35)
    edge=al.point(lambda v:255 if v<200 else int((255-v)*255/55))
    rgb=Image.composite(dark,rgb,edge).convert('RGBA'); rgb.putalpha(al)
    rgb=rgb.crop(al.getbbox())
    h=int(H*scale); w=int(rgb.width*h/rgb.height); return rgb.resize((w,h),Image.LANCZOS)

def glow(base,fg,pos,r=18,col=(0,0,0,200)):
    sh=Image.new('RGBA',base.size,(0,0,0,0)); al=Image.new('L',base.size,0); al.paste(fg.getchannel('A'),pos)
    s=Image.new('RGBA',base.size,col); s.putalpha(al.filter(ImageFilter.GaussianBlur(r)).point(lambda v:int(v*col[3]/255)))
    base.alpha_composite(s); base.alpha_composite(fg,pos)

def inset(base,name,box,cx=0.5,cy=0.5,rot=-4,border=10):
    x,y,w,h=box; im=grade(cover(Image.open(name).convert('RGB'),w,h,cx,cy),1.2,1.3,1.0)
    fr=Image.new('RGBA',(w+2*border,h+2*border),(255,255,255,255)); fr.paste(im,(border,border))
    fr=fr.rotate(rot,expand=True,resample=Image.BICUBIC); glow(base,fr,(x,y),14,(0,0,0,170))

def text(base,lines,font,x,y,size,cols,stroke=0,lh=0.95,shadow=True):
    d=ImageDraw.Draw(base)
    for ln,c in zip(lines,cols):
        sz=size if not isinstance(ln,tuple) else ln[1]; t=ln if not isinstance(ln,tuple) else ln[0]
        f=ImageFont.truetype(F[font],sz)
        if shadow:
            sh=Image.new('RGBA',base.size,(0,0,0,0)); ImageDraw.Draw(sh).text((x+6,y+8),t,font=f,fill=(0,0,0,230),stroke_width=stroke,stroke_fill=(0,0,0,230))
            base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
        if isinstance(c,tuple) and len(c)==2 and isinstance(c[0],tuple):  # testo nero su fascia
            fg,bgc=c; bb=d.textbbox((x,y),t,font=f); d.rectangle((bb[0]-14,bb[1]-10,bb[2]+14,bb[3]+12),fill=bgc); d.text((x,y),t,font=f,fill=fg)
        else:
            d.text((x,y),t,font=f,fill=c,stroke_width=stroke,stroke_fill=(0,0,0))
        bb=d.textbbox((x,y),t,font=f); y=bb[3]+int(sz*(lh-0.8))

def logo(base):
    l=Image.open('/home/user/YouTube-assistant/assets/brand/logo_vocivere_trasparente_chiaro.png').convert('RGBA')
    l=l.resize((150,int(l.height*150/l.width)),Image.LANCZOS); base.alpha_composite(l,(W-l.width-20,H-l.height-16))

def make(out,variant):
    font,lines,cols,size,bgname,ins=variant
    base=bg_sea(bgname).convert('RGBA')
    m=manuel(0.92); mx=W-m.width+40
    if ins=='crowd': inset(base,'f_3m40.jpg',(40,470,330,190),0.5,0.55,-4)
    if ins=='fish': inset(base,'f_4.5.jpg',(40,470,330,190),0.55,0.6,-4)
    if ins=='both':
        inset(base,'f_3m40.jpg',(30,450,300,185),0.5,0.55,-5); inset(base,'f_4.5.jpg',(330,470,260,160),0.55,0.6,4)
    glow(base,m,(mx,H-m.height),25,(0,0,0,190))
    text(base,lines,font,42,34,size,cols)
    base.convert('RGB').save(out,quality=92)

V={
 'A_anton_3dinotte':('anton',[('SVEGLIA',105),('ALLE 3',150),('DI NOTTE',90)],[(255,255,255),YEL,(255,255,255)],0,'f_4m22.jpg','crowd'),
 'B_bebas_50chili':('bebas',[('PESCE DA',120),('50 CHILI',200),('ALL\'ALBA',110)],[(255,255,255),YEL,(255,255,255)],0,'f_4m22.jpg','fish'),
 'C_archivo_comeunapersona':('archivo',[('PESAVA',100),('COME UNA',100),('PERSONA',120)],[(255,255,255),(255,255,255),YEL],0,'f_4m30.jpg','fish'),
 'D_oswald_mercatospiaggia':('oswald',[('IL MERCATO',110),('SENZA TETTO',110),('NÉ BANCHI',90)],[(255,255,255),YEL,(255,255,255)],0,'f_4m22.jpg','both'),
 'E_anton_alle3inmare':('anton',[('ALLE 3',200),('IN MARE',130)],[((0,0,0),YEL),(255,255,255)],0,'f_0m36.jpg','crowd'),
 'F_bebas_postoinpace':('bebas',[('"UN POSTO',130),('IN PACE"',170)],[(255,255,255),GOLD],0,'f_4m22.jpg','both'),
}
for k,v in V.items(): make(f'thumb_{k}.jpg',v)
