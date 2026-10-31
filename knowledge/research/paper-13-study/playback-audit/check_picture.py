"""Detect the reported white video picture in a real browser screenshot."""
from PIL import Image
import numpy as np,json,sys
p=Image.open(sys.argv[1]).convert('RGB');x,y,w,h=map(float,sys.argv[2:6]);a=np.asarray(p.crop((round(x+12),round(y+12),round(x+w-12),round(y+h-110))))
white=np.mean(np.min(a,axis=2)>245);print(json.dumps({'white_picture_fraction':float(white),'visible_picture':bool(white<.95)}));sys.exit(1 if white>=.95 else 0)
