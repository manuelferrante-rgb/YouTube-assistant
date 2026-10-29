# Carosello del lungo te, v2 (Manuel 29/10, riferimenti latiumani e Progetto Happiness): slide diverse tra loro.
# Foto piena con testo a altezze diverse, mezza slide nera con poche parole grandi, foto che continua da una slide
# all'altra (la seconda metà con la citazione su nero), due inquadrature con sottotitoli, slide video animate.
# 4:5 (1080x1350), testi nel quadrato centrale 1080x1080 (YouTube ritaglia i post). Fotogrammi dal lungo v7.
#   python3 copioni/caroselli/carosello_te.py   (dalla radice; lungo in work/te_copy/)
import os, subprocess, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
W,H=1080,1350; SAFE=135
V='work/te_copy/VociVere_te_long_4K.mp4'; WK='work/te_copy/car2'; OUT='copioni/caroselli/te'
BEB='assets/fonts/BebasNeue-Regular.ttf'; IF='/usr/share/fonts/opentype/inter/'
REG,BOLD,IT,BIT,BLACK=IF+'Inter-Regular.otf',IF+'Inter-Bold.otf',IF+'Inter-Italic.otf',IF+'Inter-BoldItalic.otf',IF+'Inter-Black.otf'
LOGO='assets/brand/logo_vocivere_trasparente_chiaro.png'
YEL=(255,214,10); WHITE=(255,255,255); GOLD=(182,138,75)
UH=0.82   # il lungo ha i sottotitoli impressi in basso: si usa solo l'82% alto del fotogramma

def frame(t):
    p=f'{WK}/f_{t}.png'
    if not os.path.exists(p): subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',V,'-frames:v','1',p],check=True)
    return Image.open(p).convert('RGB')
def grade(im): return ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.08)).enhance(1.12)
def crop(im,w,h,cx=.5,zoom=1.0,cy=0.0):
    uh=int(im.height*UH); ch=int(uh/zoom); cw=int(ch*w/h)
    if cw>im.width: cw=im.width; ch=int(cw*h/w)
    x=int((im.width-cw)*cx); y=int((uh-ch)*cy); return grade(im.crop((x,y,x+cw,y+ch)).resize((w,h),Image.LANCZOS))
def shade(im,spots):
    g=np.zeros((im.height,im.width),np.float32); y=np.arange(im.height)[:,None]/im.height
    for a,b,op in spots: g=np.maximum(g,np.clip((y-a)/(b-a),0,1)*op)
    m=Image.fromarray((np.broadcast_to(g,(im.height,im.width))*255).astype('uint8'))
    return Image.composite(Image.new('RGB',im.size,(0,0,0)),im.convert('RGB'),m)
def logo(im,w=170,x=64,y=SAFE+18):
    l=Image.open(LOGO).convert('RGBA'); l=l.crop(l.getbbox()); l=l.resize((w,int(l.height*w/l.width)),Image.LANCZOS); im.alpha_composite(l,(x,y))
def num(im,n,tot):
    d=ImageDraw.Draw(im); f=ImageFont.truetype(BOLD,28); t=f'{n}/{tot}'; d.text((W-64-d.textlength(t,font=f),SAFE+24),t,font=f,fill=(255,255,255,210))
def shadow_text(im,xy,t,font,fill,r=6,op=200):
    sh=Image.new('RGBA',im.size,(0,0,0,0)); ImageDraw.Draw(sh).text((xy[0]+3,xy[1]+4),t,font=font,fill=(0,0,0,op))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(r))); ImageDraw.Draw(im).text(xy,t,font=font,fill=fill)

def rich(im,text,x,y,maxw,size,italic=False,col=WHITE,lh=1.28,shadow=True):
    """Testo a capo con **parole in grassetto**; ritorna la y finale."""
    fr=ImageFont.truetype(IT if italic else REG,size); fb=ImageFont.truetype(BIT if italic else BOLD,size)
    toks=[]
    for i,part in enumerate(re.split(r'\*\*',text)):
        for w in part.split():
            if toks and re.match(r'^[.,:;!?»”]',w) and not part.startswith(' '): toks[-1]=(toks[-1][0],toks[-1][1],w)  # punteggiatura attaccata
            else: toks.append((w,i%2==1,''))
    d=ImageDraw.Draw(im); lines=[[]]; cur=0; sp=d.textlength(' ',font=fr)
    for w,b,pn in toks:
        wl=d.textlength(w,font=fb if b else fr); pl=d.textlength(pn,font=fr)
        if lines[-1] and cur+sp+wl+pl>maxw: lines.append([]); cur=0
        cur+=(sp if lines[-1] else 0)+wl+pl; lines[-1].append((w,b,wl,pn,pl))
    for ln in lines:
        xx=x
        for w,b,wl,pn,pl in ln:
            for tt,f,ww in ((w,fb if b else fr,wl),(pn,fr,pl)):
                if not tt: continue
                if shadow: shadow_text(im,(xx,y),tt,f,col)
                else: ImageDraw.Draw(im).text((xx,y),tt,font=f,fill=col)
                xx+=ww
            xx+=sp
        y+=int(size*lh)
    return y
def rich_h(text,maxw,size,italic=False,lh=1.28):
    im=Image.new('RGBA',(W,H)); return rich(im,text,0,0,maxw,size,italic,lh=lh,shadow=False)
def big(im,lines,x,y,size,center=False):
    f=ImageFont.truetype(BEB,size); d=ImageDraw.Draw(im)
    for t,col in lines:
        xx=(W-d.textlength(t,font=f))/2 if center else x
        shadow_text(im,(xx,y),t,f,col,8,220); y+=int(size*0.93)
    return y
def quote(im,x,y,maxw,text,size=46):
    f=ImageFont.truetype(BLACK,150); d=ImageDraw.Draw(im)
    d.text((x-6,y-40),'“',font=f,fill=GOLD)
    y2=rich(im,text,x,y+110,maxw,size,italic=True,shadow=False)
    d.text((x+maxw-90,y2-50),'”',font=f,fill=GOLD)
    return y2

# ---------- slide statiche ----------
def s_split(out_a,out_b,t,x0,photo_frac,para,quote_txt,by,n,tot):
    """Una foto che continua su due slide: A piena con il paragrafo, B con il resto della foto a sinistra e nero a destra."""
    im=frame(t); uh=int(im.height*UH); s=H/uh; pw=int(W*photo_frac)
    strip=grade(im.crop((x0,0,x0+int((W+pw)/s),uh)).resize((W+pw,H),Image.LANCZOS))
    a=shade(strip.crop((0,0,W,H)),[(0.45,1.0,0.85)]).convert('RGBA'); logo(a); num(a,n,tot)
    rich(a,para,64,by,W-128,44); a.convert('RGB').save(out_a,quality=92)
    b=Image.new('RGBA',(W,H),(0,0,0,255)); b.paste(strip.crop((W,0,W+pw,H)),(0,0)); logo(b); num(b,n+1,tot)
    quote(b,pw+44,320,W-pw-80,quote_txt,52); b.convert('RGB').save(out_b,quality=92)
def s_halfblack(out,t,cx,words,small,n,tot,top_black=True):
    im=Image.new('RGBA',(W,H),(0,0,0,255)); ph=crop(frame(t),W,H//2,cx); hy=H//2 if top_black else 0
    im.paste(ph,(0,hy)); logo(im); num(im,n,tot)
    f=ImageFont.truetype(BEB,150); y=SAFE+150 if top_black else H//2+90
    y=big(im,words,64,y,150); rich(im,small,64,y+14,W-128,40)
    im.convert('RGB').save(out,quality=92)
def s_stacked(out,items,n,tot):
    im=Image.new('RGBA',(W,H),(0,0,0,255)); h=H//2
    for i,(t,cx,sub) in enumerate(items):
        ph=crop(frame(t),W,h,cx).convert('RGBA'); im.alpha_composite(ph,(0,i*h))
        f=ImageFont.truetype(BOLD,40); d=ImageDraw.Draw(im); tw=d.textlength(sub,font=f)
        shadow_text(im,((W-tw)/2,i*h+h-(150 if i==1 else 110)),sub,f,WHITE,5,230)
    logo(im); num(im,n,tot); im.convert('RGB').save(out,quality=92)
def s_photo(out,t,cx,kicker,title,body,y,n,tot,zoom=1.0):
    im=shade(crop(frame(t),W,H,cx,zoom),[(0.25,0.75,0.75),(0.75,1.0,0.75)]).convert('RGBA'); logo(im); num(im,n,tot)
    d=ImageDraw.Draw(im); fk=ImageFont.truetype(BOLD,30)
    kw=d.textlength(kicker,font=fk); d.rounded_rectangle((64,y,64+kw+32,y+46),radius=8,fill=GOLD); d.text((80,y+6),kicker,font=fk,fill=WHITE)
    y=big(im,[(title,YEL)],64,y+66,118); rich(im,body,64,y+14,W-128,42); im.convert('RGB').save(out,quality=92)
def s_para(out,t,cx,para,y,n,tot):
    im=shade(crop(frame(t),W,H,cx),[(0.35,0.85,0.8)]).convert('RGBA'); logo(im); num(im,n,tot)
    rich(im,para,64,y,W-128,46); im.convert('RGB').save(out,quality=92)

# ---------- slide video (testo che compare) ----------
def s_video(out,t0,dur,cx,draw_text,n,tot,shade_spots):
    """Clip dal lungo, 4:5, senza audio; il testo entra in dissolvenza dopo 0,4 s. Salva anche il jpg (post YouTube)."""
    base=Image.new('RGBA',(W,H),(0,0,0,0)); g=np.zeros((H,W),np.float32); y=np.arange(H)[:,None]/H
    for a,b,op in shade_spots: g=np.maximum(g,np.clip((y-a)/(b-a),0,1)*op)
    base.putalpha(Image.fromarray((np.broadcast_to(g,(H,W))*255).astype('uint8'))); logo(base); num(base,n,tot)
    txt=Image.new('RGBA',(W,H),(0,0,0,0)); draw_text(txt)
    base.save(f'{WK}/ov_base.png'); txt.save(f'{WK}/ov_txt.png')
    uh=int(2160*UH); cw=int(uh*W/H); x=int((3840-cw)*cx)
    fc=(f"[0:v]crop={cw}:{uh}:{x}:0,scale={W}:{H}:flags=lanczos,eq=contrast=1.06:saturation=1.12,setsar=1[v];"
        f"[1:v]format=rgba[b];[2:v]format=rgba,fade=in:st=0.4:d=0.7:alpha=1[t];[v][b]overlay[vb];[vb][t]overlay,format=yuv420p[o]")
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t0),'-t',str(dur),'-i',V,'-loop','1','-t',str(dur),'-i',f'{WK}/ov_base.png',
                    '-loop','1','-t',str(dur),'-i',f'{WK}/ov_txt.png','-filter_complex',fc,'-map','[o]','-an','-r','30',
                    '-c:v','libx264','-crf','18','-preset','slow','-movflags','+faststart',out],check=True)
    subprocess.run(['ffmpeg','-v','error','-y','-sseof','-0.1','-i',out,'-frames:v','1','-q:v','2',out.replace('.mp4','_YT.jpg')],check=True)

os.makedirs(OUT,exist_ok=True)
for f in os.listdir(OUT): os.remove(os.path.join(OUT,f))
T=9; o=lambda n,ext='jpg': f'{OUT}/{n:02d}.{ext}'
def cover_txt(im):
    y=big(im,[("AFFITTATE PER",WHITE),("3.000 RUPIE L'ANNO",YEL)],64,560,128)
    rich(im,'Le colline del tè di **Munnar**, nel 1877. Kerala, India.',64,y+16,W-128,42)
    f=ImageFont.truetype(BOLD,34); shadow_text(im,(W-64-ImageDraw.Draw(im).textlength('Scorri  →',font=f),H-SAFE-60),'Scorri  →',f,YEL)
s_video(o(1,'mp4'),120.0,7.0,0.5,cover_txt,1,T,[(0.0,0.25,0.0),(0.35,0.9,0.85)])
s_halfblack(o(2),189,0.45,[("TUTTO QUESTO",WHITE),("È TÈ",YEL)],'Munnar, Kerala, a oltre **1.500 metri**.',2,T)
s_split(o(3),o(4),262.5,733,0.55,
        'Sadish è di qui. Ci porta **tra i filari** dove la gente del posto **raccoglie il tè**: non il panorama, il lavoro.',
        'A Munnar **quasi tutti lavorano nel tè**. Già prima che nascessi io, **mio padre e mia madre**.',710,3,T)
s_stacked(o(5),[(97.5,0.7,'«Due, tre foglie: quelle buone»'),(119.2,0.55,'«Le scure non si usano»')],5,T)
def kg_txt(im):
    y=big(im,[("26-29 CHILI",YEL),("AL GIORNO",WHITE)],64,SAFE+170,140)
    rich(im,'Quanto raccoglie **in media una persona**, a mano, ci dice Sadish.',64,y+16,W-128,42)
s_video(o(6,'mp4'),97.0,6.0,0.75,kg_txt,6,T,[(0.45,0.0,0.75)])
s_photo(o(7),265,0.6,'DAL 2005',"L'AZIENDA È DEI DIPENDENTI",'Per la maggior parte: **circa 13 mila persone**.',SAFE+330,7,T)
s_para(o(8),221,0.5,'Nel **2015** migliaia di **raccoglitrici** bloccano Munnar per **nove giorni**, senza sindacati né partiti. '
       'Si chiamano **Pombilai Orumai**: unità delle donne. E ottengono il **bonus al 20%**.',640,8,T)
def end_txt(im): big(im,[("FUORI ORA IL VIDEO",WHITE),("SU YOUTUBE",YEL)],64,SAFE+200,120)
s_video(o(9,'mp4'),347.8,2.7,0.3,end_txt,9,T,[(0.45,0.0,0.8)])

# anteprima: per i video, il fotogramma finale
ims=[]
for n in range(1,T+1):
    p=o(n) if os.path.exists(o(n)) else o(n,'mp4').replace('.mp4','_YT.jpg'); ims.append(Image.open(p).resize((216,270)))
G=Image.new('RGB',(226*T+10,290),(20,20,20))
for i,m in enumerate(ims): G.paste(m,(10+i*226,10))
G.save('copioni/caroselli/te_anteprima.jpg',quality=85)
print('ok')
