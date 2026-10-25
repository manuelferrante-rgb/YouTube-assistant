import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W,H=1280,720
F={'anton':'/root/fonts/anton-latin-400-normal.woff','bebas':'/root/fonts/bebas-neue-latin-400-normal.woff',
   'archivo':'/root/fonts/archivo-black-latin-400-normal.woff','oswald':'/root/fonts/oswald-latin-700-normal.woff'}
YEL=(255,214,10); WHITE=(255,255,255); GOLD=(214,168,96)
def cover(im,w,h,cx=.5,cy=.5):
    r=max(w/im.width,h/im.height); im=im.resize((int(im.width*r+.5),int(im.height*r+.5)),Image.LANCZOS)
    x=int((im.width-w)*cx); y=int((im.height-h)*cy); return im.crop((x,y,x+w,y+h))
def grade(im,c,s,b): return ImageEnhance.Brightness(ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(c)).enhance(s)).enhance(b)
def soft_mask(w,h,feather):
    # rettangolo con bordi molto sfumati (dissolvenza come lo scontorno)
    m=Image.new('L',(w,h),0); ImageDraw.Draw(m).rounded_rectangle((feather,feather,w-feather,h-feather),radius=feather,fill=255)
    return m.filter(ImageFilter.GaussianBlur(feather*0.6))
def blend(base,name,box,cx=.5,cy=.5,feather=40,op=1.0):
    x,y,w,h=box; im=grade(cover(Image.open(name).convert('RGB'),w,h,cx,cy),1.15,1.25,1.0).convert('RGBA')
    m=soft_mask(w,h,feather).point(lambda v:int(v*op)); im.putalpha(m); base.alpha_composite(im,(x,y))
def manuel(h):
    a=Image.open('cut_m2.png').convert('RGBA'); a=a.crop(a.getchannel('A').point(lambda v:255 if v>20 else 0).getbbox())
    rgb=grade(a.convert('RGB'),1.08,1.1,1.05).convert('RGBA'); rgb.putalpha(a.getchannel('A'))
    return rgb.resize((int(a.width*h/a.height),h),Image.LANCZOS)
def shadow(base,fg,pos,r,op):
    al=Image.new('L',base.size,0); al.paste(fg.getchannel('A'),pos); s=Image.new('RGBA',base.size,(0,0,0,0))
    s.putalpha(al.filter(ImageFilter.GaussianBlur(r)).point(lambda v:int(v*op))); base.alpha_composite(s)
def text(base,lines,font,x,y):
    d=ImageDraw.Draw(base)
    for t,sz,col in lines:
        f=ImageFont.truetype(F[font],sz)
        sh=Image.new('RGBA',base.size,(0,0,0,0)); ImageDraw.Draw(sh).text((x+5,y+7),t,font=f,fill=(0,0,0,235))
        base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)))
        if isinstance(col,tuple) and isinstance(col[0],tuple):
            bb=d.textbbox((x,y),t,font=f); d.rectangle((bb[0]-14,bb[1]-12,bb[2]+14,bb[3]+12),fill=col[1]); d.text((x,y),t,font=f,fill=col[0])
        else: d.text((x,y),t,font=f,fill=col)
        y=d.textbbox((x,y),t,font=f)[3]+int(sz*0.16)
def make(out,font,lines,bgname='f_4m22.jpg',imgs=('crowd','fish')):
    bg=grade(cover(Image.open(bgname).convert('RGB'),W,H,0.35,0.6),1.25,1.35,0.92)
    # scurisco la metà sinistra (testo) e il basso
    g=np.zeros((H,W),np.float32); xs=np.linspace(1,0,W); g[:]=np.clip(xs*1.1,0,1)**1.3*0.7
    g+=np.clip((np.arange(H)[:,None]/H-0.55)/0.45,0,1)*0.45
    shade=Image.fromarray((np.clip(g,0,1)*255).astype('uint8'))
    base=Image.composite(Image.new('RGB',(W,H),(4,12,26)),bg,shade).convert('RGBA')
    if 'crowd' in imgs: blend(base,'f_3m40.jpg',(-20,400,470,340),0.5,0.6,55,0.95)
    if 'fish' in imgs: blend(base,'f_4.5.jpg',(330,430,420,300),0.55,0.65,55,0.95)
    m=manuel(int(H*0.97)); pos=(W-m.width+60,H-m.height)
    shadow(base,m,pos,30,0.55); base.alpha_composite(m,pos)
    text(base,lines,font,40,30)
    base.convert('RGB').save(out,quality=92)
V={
 '1_anton_50chili':('anton',[("50 CHILI",190,YEL),("ALL'ASTA IN SPIAGGIA",70,WHITE)]),
 '2_archivo_comeunapersona':('archivo',[("PESAVA",92,WHITE),("COME UNA",92,WHITE),("PERSONA",112,YEL)]),
 '3_anton_sveglia3':('anton',[("SVEGLIA",110,WHITE),("ALLE 3",170,((0,0,0),YEL)),("MERCATO ALLE 8",64,WHITE)]),
 '4_bebas_senzatetto':('bebas',[("SENZA TETTO",130,WHITE),("NÉ BANCHI",130,YEL),("E UN PESCE DA 50 KG",62,WHITE)]),
}
for k,(f,l) in V.items(): make(f'v2_{k}.jpg',f,l)
