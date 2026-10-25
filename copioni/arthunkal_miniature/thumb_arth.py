import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W,H=1280,720
BEB='/root/fonts/bebas-neue-latin-400-normal.woff'; YEL=(255,214,10); WHITE=(255,255,255)
A='/home/user/YouTube-assistant/work/car/a/'
def cover(im,w,h,cx=.5,cy=.5):
    r=max(w/im.width,h/im.height); im=im.resize((int(im.width*r+.5),int(im.height*r+.5)),Image.LANCZOS)
    x=int((im.width-w)*cx); y=int((im.height-h)*cy); return im.crop((x,y,x+w,y+h))
def grade(im,c,s,b): return ImageEnhance.Brightness(ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(c)).enhance(s)).enhance(b)
def manuel(h):
    a=Image.open('manuel.png').convert('RGBA'); a=a.crop(a.getchannel('A').point(lambda v:255 if v>20 else 0).getbbox())
    rgb=grade(a.convert('RGB'),1.08,1.1,1.05).convert('RGBA'); rgb.putalpha(a.getchannel('A'))
    return rgb.resize((int(a.width*h/a.height),h),Image.LANCZOS)
def text(base,lines,x,y,target):
    for t,col,gap in lines:
        f0=ImageFont.truetype(BEB,100); w0=ImageDraw.Draw(base).textbbox((0,0),t,font=f0)[2]
        sz=int(100*target/w0); f=ImageFont.truetype(BEB,sz); bb=ImageDraw.Draw(base).textbbox((0,0),t,font=f)
        sh=Image.new('RGBA',base.size,(0,0,0,0)); ImageDraw.Draw(sh).text((x+5,y+7),t,font=f,fill=(0,0,0,235))
        base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7))); ImageDraw.Draw(base).text((x,y),t,font=f,fill=col)
        y+=bb[3]+gap
def make(out,bgname,cx,lines,dark=0.75,b=0.95):
    bg=grade(cover(Image.open(A+bgname).convert('RGB'),W,H,cx,0.5),1.2,1.25,b)
    g=np.zeros((H,W),np.float32); xs=np.linspace(1,0,W); g[:]=np.clip(xs*1.15,0,1)**1.4*dark
    g+=np.clip((np.arange(H)[:,None]/H-0.6)/0.4,0,1)*0.35
    sh=Image.fromarray((np.clip(g,0,1)*255).astype('uint8'))
    base=Image.composite(Image.new('RGB',(W,H),(4,10,22)),bg,sh).convert('RGBA')
    m=manuel(int(H*0.86)); pos=(W-m.width+10,H-m.height)
    al=Image.new('L',base.size,0); al.paste(m.getchannel('A'),pos); s=Image.new('RGBA',base.size,(0,0,0,0))
    s.putalpha(al.filter(ImageFilter.GaussianBlur(30)).point(lambda v:int(v*0.55))); base.alpha_composite(s); base.alpha_composite(m,pos)
    text(base,lines,40,40,640)
    base.convert('RGB').save(out,quality=92)
make('A_2e30.jpg','a_023510_0233.jpg',0.3,[("2:30 DI NOTTE",WHITE,10),("13 KM PREGANDO",YEL,0)],0.6,1.15)
make('B_milano.jpg','a_090733_0296.jpg',0.85,[("UNA STATUA",WHITE,6),("DI MILANO",YEL,10),("SULLA COSTA DELL'INDIA",WHITE,0)])
make('C_senzafermarsi.jpg','a_090903_0299.jpg',0.4,[("13 KM",YEL,6),("SENZA MAI FERMARSI",WHITE,0)])
