# Scontorno fine dei ricci: luma/colour key sul cielo, con il cielo ricostruito per inpainting
import numpy as np, cv2
I=cv2.imread('m_3m47.5.jpg').astype(np.float32)/255.
H,W=I.shape[:2]
coarse=cv2.imread('cut_m.png',cv2.IMREAD_UNCHANGED)[...,3].astype(np.float32)/255.
coarse[:, :1000]=0; coarse[:, 2850:]=0
fg=(coarse>0.5).astype(np.uint8)
core=cv2.erode(fg,np.ones((31,31),np.uint8))
band=cv2.dilate((coarse>0.05).astype(np.uint8),np.ones((61,61),np.uint8))
# cielo dietro la testa: inpainting a 1/4 di risoluzione dalle zone sicuramente di sfondo
s=4; small=cv2.resize(I,(W//s,H//s)); bm=cv2.resize(band,(W//s,H//s),interpolation=cv2.INTER_NEAREST)
B=cv2.inpaint((small*255).astype(np.uint8),bm*255,15,cv2.INPAINT_TELEA)
B=cv2.GaussianBlur(B,(0,0),3); B=cv2.resize(B,(W,H)).astype(np.float32)/255.
# alpha = distanza dal cielo ricostruito (capelli scuri e pelle calda lontani dal cielo, aloni chiari vicini)
dist=np.sqrt(((I-B)**2).sum(2))
a=np.clip((dist-0.07)/0.22,0,1)
# il cielo che finisce più chiaro del previsto (aloni di nitidezza) non conta
lighter=(I.mean(2)>B.mean(2)+0.02)&((I[...,2]-I[...,0])>0.05)
a[lighter]=0
# capelli: chiave di luminanza (ricci scuri sul cielo chiaro); pelle calda: chiave di distanza
L=I.mean(2); Lb=B.mean(2)
a_l=np.clip((Lb-0.08-L)/np.maximum(Lb-0.08-0.30,0.1),0,1)
warm=(I[...,2]-I[...,0])>0.08   # BGR: rosso - blu
a=np.where(warm,a,np.minimum(a,a_l))
core=cv2.erode(fg,np.ones((201,201),np.uint8))
alpha=np.where(core>0,1.0,np.where(band>0,a,0.0)).astype(np.float32)
yh=1340; alpha[yh:]=np.where(core[yh:]>0,1.0,coarse[yh:]*(band[yh:]>0))
# colore: dove il pixel è misto prendo il colore dei capelli vicini (niente cielo nei ricci)
solid=((alpha>0.9)&(band>0)).astype(np.uint8)
sm=cv2.resize(solid,(W//s,H//s),interpolation=cv2.INTER_NEAREST)
F=cv2.inpaint((small*255).astype(np.uint8),(1-sm)*255,9,cv2.INPAINT_TELEA)
F=cv2.resize(cv2.GaussianBlur(F,(0,0),1.5),(W,H)).astype(np.float32)/255.
w=np.clip((alpha-0.6)/0.35,0,1)[...,None]
C=I*w+F*(1-w)
C=np.where(core[...,None]>0,I,C)
alpha=cv2.GaussianBlur(alpha,(0,0),0.8)
out=np.dstack([(np.clip(C,0,1)*255).astype(np.uint8),(alpha*255).astype(np.uint8)])
cv2.imwrite('cut_m2.png',out)
