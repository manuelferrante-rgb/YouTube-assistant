# Miniature del lungo te (Manuel scontornato con copioni/mercato_miniature/cutout.py + u2net_human_seg)
# (1280x720): fotogramma del lungo v7, scritta Bebas Neue, "E OGGI / DI CHI SONO?" (scelta A, 28/10)
#   python3 copioni/te_miniature/thumb_te.py   (fotogrammi in work/te_copy/thumb/)
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W,H=1280,720
BEB='assets/fonts/BebasNeue-Regular.ttf'; YEL=(255,214,10); WHITE=(255,255,255)
F='work/te_copy/thumb/'
def grade(im,c,s,b): return ImageEnhance.Brightness(ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(c)).enhance(s)).enhance(b)
def crop(im,cx,cy,zoom):
    w,h=im.size; ch=int(h/zoom); cw=int(ch*16/9); x=int((w-cw)*cx); y=int((h-ch)*cy)
    return im.crop((x,y,x+cw,y+ch)).resize((W,H),Image.LANCZOS)
def text(base,lines,x,y,target,right=False):
    d=ImageDraw.Draw(base)
    for t,col,gap in lines:
        f0=ImageFont.truetype(BEB,100); w0=d.textbbox((0,0),t,font=f0)[2]
        f=ImageFont.truetype(BEB,int(100*target/w0)); bb=d.textbbox((0,0),t,font=f)
        xx=x-bb[2] if right else x
        sh=Image.new('RGBA',base.size,(0,0,0,0)); ImageDraw.Draw(sh).text((xx+5,y+7),t,font=f,fill=(0,0,0,235))
        base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8))); ImageDraw.Draw(base).text((xx,y),t,font=f,fill=col)
        y+=bb[3]+gap
def make(out,frame,cx,cy,zoom,side,dark=0.7,b=1.0,target=560):
    bg=grade(crop(Image.open(F+frame).convert('RGB'),cx,cy,zoom),1.15,1.25,b)
    xs=np.linspace(1,0,W) if side=='left' else np.linspace(0,1,W)
    g=np.zeros((H,W),np.float32); g[:]=np.clip(xs*1.2-0.15,0,1)**1.3*dark
    sh=Image.fromarray((np.clip(g,0,1)*255).astype('uint8'))
    base=Image.composite(Image.new('RGB',(W,H),(6,14,10)),bg,sh).convert('RGBA')
    L=[("E OGGI",WHITE,8),("DI CHI SONO?",YEL,0)]
    if side=='left': text(base,L,48,70,target)
    else: text(base,L,W-48,70,target,right=True)
    base.convert('RGB').save(out,quality=92)
def cut(name,h,mirror=False):
    a=Image.open(F+name).convert('RGBA'); a=a.crop(a.getchannel('A').point(lambda v:255 if v>40 else 0).getbbox())
    if mirror: a=a.transpose(Image.FLIP_LEFT_RIGHT)
    rgb=grade(a.convert('RGB'),1.1,1.12,1.06).convert('RGBA'); rgb.putalpha(a.getchannel('A').filter(ImageFilter.GaussianBlur(1)))
    return rgb.resize((int(a.width*h/a.height),h),Image.LANCZOS)
def comp(out,bgframe,cx,person,h,px,dark=0.75,mirror=False,target=600,sadish=None):
    bg=grade(crop(Image.open(F+bgframe).convert('RGB'),cx,0.5,1.0),1.15,1.25,1.0)
    g=np.zeros((H,W),np.float32); g[:]=np.clip(np.linspace(1,0,W)*1.25-0.1,0,1)**1.4*dark
    sh=Image.fromarray((np.clip(g,0,1)*255).astype('uint8'))
    base=Image.composite(Image.new('RGB',(W,H),(6,14,10)),bg,sh).convert('RGBA')
    m=cut(person,h,mirror); pos=(px,H-m.height)
    al=Image.new('L',base.size,0); al.paste(m.getchannel('A'),pos); s_=Image.new('RGBA',base.size,(0,0,0,0))
    s_.putalpha(al.filter(ImageFilter.GaussianBlur(30)).point(lambda v:int(v*0.5))); base.alpha_composite(s_); base.alpha_composite(m,pos)
    if sadish:   # Sadish mentre raccoglie (fotogramma 119.2 del lungo), in basso a sinistra, bordi sfumati, niente cornice
        w_,box,sx=sadish; ph=grade(Image.open(F+'q_119.2.png').convert('RGB').crop(box),1.1,1.15,1.05)
        ph=ph.resize((w_,int(ph.height*w_/ph.width)),Image.LANCZOS)
        yy,xx=np.mgrid[0:ph.height,0:ph.width].astype(np.float32); f=40.0
        m=np.minimum.reduce([xx/f,(ph.width-1-xx)/f,yy/f,np.full_like(xx,9)]).clip(0,1)   # in basso esce dal bordo
        ph=ph.convert('RGBA'); ph.putalpha(Image.fromarray((m**1.3*255).astype('uint8')))
        base.alpha_composite(ph,(sx,H-ph.height))
    text(base,[("E OGGI",WHITE,8),("DI CHI SONO?",YEL,0)],44,40 if sadish else 50,target)
    base.convert('RGB').save(out,quality=92)
comp('copioni/te_miniature/A1_indica.jpg','f_27.png',0.5,'clean_1.5.png',640,560,mirror=True)
comp('copioni/te_miniature/A1_sadish.jpg','f_27.png',0.5,'clean_1.5.png',640,560,mirror=True,target=470,sadish=(310,(1600,120,2800,1450),30))
comp('copioni/te_miniature/A2_braccia.jpg','f_27.png',0.5,'clean_25.png',660,590,target=520)
ims=[Image.open(f'copioni/te_miniature/{n}.jpg').resize((640,360)) for n in ('A1_indica','A1_sadish')]
G=Image.new('RGB',(1300,380),(20,20,20))
for i,m in enumerate(ims): G.paste(m,(10+(i%2)*650,10+(i//2)*370))
G.save('copioni/te_miniature/00_tutte.jpg',quality=85)
