import sys, numpy as np, onnxruntime as ort
from PIL import Image
src, dst, model = sys.argv[1], sys.argv[2], sys.argv[3]
im = Image.open(src).convert("RGB")
if "isnet" in model:
    S, mean, std = 1024, (0.5,0.5,0.5), (1,1,1)
else:
    S, mean, std = 320, (0.485,0.456,0.406), (0.229,0.224,0.225)
x = np.asarray(im.resize((S,S), Image.LANCZOS)).astype(np.float32)/255.
x = x/ x.max()
x = (x-np.array(mean))/np.array(std)
x = x.transpose(2,0,1)[None].astype(np.float32)
s = ort.InferenceSession(model, providers=["CPUExecutionProvider"])
m = s.run(None, {s.get_inputs()[0].name: x})[0][0,0]
m = (m-m.min())/(m.max()-m.min())
mask = Image.fromarray((m*255).astype(np.uint8)).resize(im.size, Image.LANCZOS)
out = im.copy(); out.putalpha(mask); out.save(dst)
