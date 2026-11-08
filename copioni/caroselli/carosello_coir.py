# Carosello "fatto" del lungo coir (Copy, 8/11): Made in India, chi c'è dietro. 8 slide 4:5, testi in copioni/coir_testi.md.
# Fotogrammi dal girato originale (work/coir/raw, Drive cartella "Coir"). Volto sempre libero dalla scritta (Insights 8/11).
#   python3 copioni/caroselli/carosello_coir.py
import sys; sys.path.insert(0, 'copioni/caroselli')
from carosello_lib import *
os.makedirs(OUT,exist_ok=True)
for f in os.listdir(OUT): os.remove(os.path.join(OUT,f))
T=8; o=lambda n,ext='jpg': f'{OUT}/{n:02d}.{ext}'
def cover_txt(im):
    y=big(im,[("SOPRA C'È SCRITTO",WHITE),("MADE IN INDIA",YEL)],64,H-SAFE-430,128)
    rich(im,'Anathalavattom, **Kerala**. Chi fa i nostri tappeti di cocco.',64,y+16,W-128,42)
    f=ImageFont.truetype(BOLD,34); shadow_text(im,(W-64-ImageDraw.Draw(im).textlength('Scorri  →',font=f),H-SAFE-60),'Scorri  →',f,YEL)
s_video(o(1,'mp4'),('0549',1.0),6.0,0.62,cover_txt,1,T,[(0.45,1.0,0.9)])
s_halfblack(o(2),('0542',5.0),0.47,[("NON C'È SCRITTO",WHITE),("CHI L'HA FATTO",YEL)],'Lei apre gusci di cocco a mano da **quarant\'anni**.',2,T,top_black=True)
s_photo(o(3),('0107',4.0),0.5,'LA LAGUNA','MESI SOTT\'ACQUA','Da **sei mesi a un anno**, finché la fibra non si stacca.',H-SAFE-430,3,T)
s_photo(o(4),('0046',3.0),0.45,'76 ANNI','BARCA DA 50','Ogni giorno scende in acqua e tira su i gusci, **a mano**.',H-SAFE-430,4,T)
s_para(o(5),('0109',2.0),0.5,'**A mano, fino alle due.** Sedute per terra, sotto il sole, aprono i gusci uno a uno e ne tirano fuori la fibra.',H-SAFE-330,5,T)
def kg_txt(im):
    y=big(im,[("280 PEZZI",YEL),("IN 8 ORE",WHITE)],64,H-SAFE-420,140)
    rich(im,'Due fili, intrecciati **camminando all\'indietro**.',64,y+16,W-128,42)
s_video(o(6,'mp4'),('0069',0.0),2.3,0.38,kg_txt,6,T,[(0.45,1.0,0.85)])
im=Image.new('RGBA',(W,H),(0,0,0,255)); logo(im); num(im,7,T)
y=quote(im,90,380,W-180,'Con un salario così basso, **i giovani non vengono**.',58)
rich(im,'Chi lavora qui. Il salario: **400 rupie al giorno**, circa 4 euro.',90,y+80,W-180,40); im.convert('RGB').save(o(7),quality=92)
def end_txt(im): big(im,[("FUORI ORA IL VIDEO",WHITE),("SU YOUTUBE",YEL)],64,SAFE+200,120)
s_video(o(8,'mp4'),('0087',0.0),2.3,0.5,end_txt,8,T,[(0.45,0.0,0.8)])
ims=[]
for n in range(1,T+1):
    p=o(n) if os.path.exists(o(n)) else o(n,'mp4').replace('.mp4','_YT.jpg'); ims.append(Image.open(p).resize((216,270)))
G=Image.new('RGB',(226*T+10,290),(20,20,20))
for i,m in enumerate(ims): G.paste(m,(10+i*226,10))
G.save('copioni/caroselli/coir_anteprima.jpg',quality=85)
print('ok')
