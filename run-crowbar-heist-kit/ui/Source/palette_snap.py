"""Palette map per pixel, retaining alpha. Hue gates protect gold and cream ramps."""
import numpy as np
from PIL import Image
HEX=['1E2226','4A5258','8C969C','2F6B3A','D9A923','C8302A','2A5DB0','E8E2D0']
BASE=np.array([[int(h[i:i+2],16) for i in (0,2,4)] for h in HEX],dtype=float)
PALETTE=np.clip(np.array([BASE*s for s in [.55,.75,1,1.12]]).reshape(-1,3),0,255).round().astype('uint8')
def snap(image):
    a=np.asarray(image.convert('RGBA')).copy(); rgb=a[:,:,:3].astype(float)
    # Hue from Pillow is on a 0..255 circle; classify each pixel independently.
    hsv=np.asarray(image.convert('RGB').convert('HSV')); hue=hsv[:,:,0]/255
    flat=rgb.reshape(-1,3); result=np.empty_like(flat,dtype='uint8')
    for start in range(0,len(flat),32000):
        block=flat[start:start+32000]
        dist=((block[:,None,:]-PALETTE[None,:,:].astype(float))**2).sum(2)
        result[start:start+len(block)]=PALETTE[dist.argmin(1)]
    result=result.reshape(rgb.shape)
    for index,mask in [(4,(hue>.075)&(hue<.18)&(hsv[:,:,1]>70)),(7,(hue>.08)&(hue<.2)&(hsv[:,:,1]<70)&(hsv[:,:,2]>110))]:
        ramps=PALETTE[np.array([0,8,16,24])+index].astype(float)
        pixels=rgb[mask]
        if len(pixels): result[mask]=ramps[((pixels[:,None,:]-ramps[None,:,:])**2).sum(2).argmin(1)]
    a[:,:,:3]=result; return Image.fromarray(a)

if __name__=='__main__':
    import sys
    snap(Image.open(sys.argv[1])).save(sys.argv[2])
