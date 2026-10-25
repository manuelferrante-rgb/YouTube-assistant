import sys; sys.argv=['x']
exec(open('/tmp/claude-0/-home-user-YouTube-assistant/82f5c6f1-3938-5249-b690-20d5c53cf2e1/scratchpad/thumb2.py').read().split('V={')[0])
def wide_text(base,lines,font,x,y,target,stretch):
    # ogni riga portata alla stessa larghezza (target), con allargamento orizzontale opzionale
    for t,col,gap in lines:
        f0=ImageFont.truetype(F[font],100); w0=ImageDraw.Draw(base).textbbox((0,0),t,font=f0)[2]
        sz=int(100*target/(w0*stretch)); f=ImageFont.truetype(F[font],sz)
        bb=ImageDraw.Draw(base).textbbox((0,0),t,font=f); lw,lh=bb[2]+20,bb[3]+20
        lay=Image.new('RGBA',(lw,lh),(0,0,0,0)); ImageDraw.Draw(lay).text((0,0),t,font=f,fill=col)
        lay=lay.resize((int(lw*stretch),lh),Image.LANCZOS)
        sh=Image.new('RGBA',base.size,(0,0,0,0)); a=lay.getchannel('A')
        blk=Image.new('RGBA',lay.size,(0,0,0,235)); blk.putalpha(a.point(lambda v:int(v*.92)))
        sh.alpha_composite(blk,(x+5,y+7)); base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)))
        base.alpha_composite(lay,(x,y)); y+=bb[3]+gap
def make4(out,target,stretch):
    bg=grade(cover(Image.open('f_4m22.jpg').convert('RGB'),W,H,0.35,0.6),1.25,1.35,0.92)
    g=np.zeros((H,W),np.float32); xs=np.linspace(1,0,W); g[:]=np.clip(xs*1.1,0,1)**1.3*0.7
    g+=np.clip((np.arange(H)[:,None]/H-0.55)/0.45,0,1)*0.45
    shade=Image.fromarray((np.clip(g,0,1)*255).astype('uint8'))
    base=Image.composite(Image.new('RGB',(W,H),(4,12,26)),bg,shade).convert('RGBA')
    blend(base,'f_3m40.jpg',(-20,400,470,340),0.5,0.6,55,0.95)
    blend(base,'f_4.5.jpg',(330,430,420,300),0.55,0.65,55,0.95)
    m=manuel(int(H*0.97)); pos=(W-m.width+60,H-m.height)
    shadow(base,m,pos,30,0.55); base.alpha_composite(m,pos)
    wide_text(base,[("SENZA TETTO",WHITE,6),("NÉ BANCHI",YEL,14),("E UN PESCE DA 50 KG",WHITE,0)],'bebas',36,24,target,stretch)
    base.convert('RGB').save(out,quality=92)
make4('v3_4a_bebas_grande.jpg',640,1.0)
make4('v3_4b_bebas_larga.jpg',660,1.18)
