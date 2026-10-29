# Toglie l'alone chiaro (cielo) dal bordo dello scontorno, soprattutto tra i ricci.
#   python3 dehalo.py frame.png cut.png out.png
import sys, numpy as np, cv2
src,cut,out=sys.argv[1:4]
I=cv2.imread(src).astype(np.float32)/255.
a=cv2.imread(cut,cv2.IMREAD_UNCHANGED)[...,3].astype(np.float32)/255.
fg=(a>0.5).astype(np.uint8)
core=cv2.erode(fg,np.ones((61,61),np.uint8))                     # dentro: viso e maglia, intoccabili
band=(cv2.dilate((a>0.02).astype(np.uint8),np.ones((9,9),np.uint8))>0)&(core==0)
B,G,R=I[...,0],I[...,1],I[...,2]; L=I.mean(2); sat=I.max(2)-I.min(2)
warm=(R-B)>0.07                                                   # pelle e capelli caldi
sky=np.clip((L-0.50)/0.18,0,1)*np.clip((0.16-sat)/0.10+((B-R)>0)*1.0,0,1)
sky=np.where(warm,0,sky)
a2=np.where(band,a*(1-sky),a)
a2=np.where(band,np.minimum(a2,cv2.erode(a2,np.ones((3,3),np.uint8))*1.0+0.0),a2)  # assottiglia di 1 px
a2=cv2.GaussianBlur(a2,(0,0),0.7)
# colore: sui bordi semitrasparenti si toglie il cielo rimasto scurendo verso i capelli vicini
hair=cv2.GaussianBlur(I*(a2[...,None]>0.9),(0,0),6)/np.maximum(cv2.GaussianBlur((a2>0.9).astype(np.float32),(0,0),6)[...,None],1e-3)
edge=(band&(a2<0.95))[...,None]
C=np.where(edge,np.minimum(I,hair+0.05),I)
cv2.imwrite(out,np.dstack([(np.clip(C,0,1)*255).astype(np.uint8),(np.clip(a2,0,1)*255).astype(np.uint8)]))
