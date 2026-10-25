# Scontorno generico: maschera del modello + chiave sul cielo dove lo sfondo ricostruito è cielo.
import sys, numpy as np, cv2
src, coarse_p, out, x0, x1 = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
I=cv2.imread(src).astype(np.float32)/255.; H,W=I.shape[:2]
coarse=cv2.imread(coarse_p,cv2.IMREAD_UNCHANGED)[...,3].astype(np.float32)/255.
coarse[:,:x0]=0; coarse[:,x1:]=0
fg=(coarse>0.5).astype(np.uint8)
k=max(3,int(W/40))|1; core=cv2.erode(fg,np.ones((k*3,k*3),np.uint8))
band=cv2.dilate((coarse>0.05).astype(np.uint8),np.ones((k,k),np.uint8))
s=4; small=cv2.resize(I,(W//s,H//s)); bm=cv2.resize(band,(W//s,H//s),interpolation=cv2.INTER_NEAREST)
B=cv2.inpaint((small*255).astype(np.uint8),bm*255,15,cv2.INPAINT_TELEA)
B=cv2.resize(cv2.GaussianBlur(B,(0,0),3),(W,H)).astype(np.float32)/255.
sky=((B[...,0]-B[...,2])>0.06)&(B.mean(2)>0.5)            # BGR: blu > rosso e chiaro
dist=np.sqrt(((I-B)**2).sum(2)); a=np.clip((dist-0.12)/0.22,0,1)
L=I.mean(2); Lb=B.mean(2); a_l=np.clip((Lb-0.16-L)/np.maximum(Lb-0.46,0.1),0,1)
warm=(I[...,2]-I[...,0])>0.08
a=np.where(warm,a,np.minimum(a,a_l))
alpha=np.where(core>0,1.0,np.where(band>0,np.where(sky,a,coarse),0.0)).astype(np.float32)
solid=((alpha>0.9)&(band>0)).astype(np.uint8); sm=cv2.resize(solid,(W//s,H//s),interpolation=cv2.INTER_NEAREST)
F=cv2.inpaint((small*255).astype(np.uint8),(1-sm)*255,9,cv2.INPAINT_TELEA)
F=cv2.resize(cv2.GaussianBlur(F,(0,0),1.5),(W,H)).astype(np.float32)/255.
w=np.where(sky,np.clip((alpha-0.6)/0.35,0,1),1.0)[...,None]
C=np.where(core[...,None]>0,I,I*w+F*(1-w))
alpha=cv2.GaussianBlur(alpha,(0,0),0.8)
cv2.imwrite(out,np.dstack([(np.clip(C,0,1)*255).astype(np.uint8),(alpha*255).astype(np.uint8)]))
