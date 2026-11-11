"""Editable, deterministic HUD reconstruction from the supplied UI-kit reference.

The reference is the style anchor. Geometry, state derivation, text and strips are
authored here at the specification's exact 2x dimensions rather than trusting
generated sheet coordinates. This differs from automatic slicing of AI sheets.
"""
import json,math,re
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
from palette_snap import snap
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'out/run-crowbar-heist-kit/ui'; OUT.mkdir(parents=True,exist_ok=True)
C={'dark':'#1E2226','slate':'#4A5258','steel':'#8C969C','green':'#2F6B3A','gold':'#D9A923','red':'#C8302A','blue':'#2A5DB0','cream':'#E8E2D0'}
def image(w,h): return Image.new('RGBA',(w,h))
def font(size): return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',size)
def panel(w,h,fill='slate',rim='steel',radius=16):
    im=image(w,h); d=ImageDraw.Draw(im)
    d.rounded_rectangle((2,2,w-3,h-3),radius,fill=C[rim],outline=C['dark'],width=4)
    d.rounded_rectangle((10,10,w-11,h-11),max(3,radius-8),fill=C[fill],outline=C['dark'],width=4)
    d.line((16,15,w-17,15),fill=C['cream'],width=3)
    return im
def stripes(im,box,color='gold'):
    w,h=im.size; layer=image(w,h); d=ImageDraw.Draw(layer)
    for x in range(-h,w+h,42): d.polygon([(x,0),(x+20,0),(x+h+20,h),(x+h,h)],fill=C[color])
    mask=Image.new('L',(w,h)); ImageDraw.Draw(mask).rectangle(box,fill=255)
    layer.putalpha(ImageChops.multiply(layer.getchannel('A'),mask)); im.alpha_composite(layer)
def text(im,value,size=30,color='cream'):
    d=ImageDraw.Draw(im); f=font(size); bounds=d.textbbox((0,0),value,font=f)
    d.text(((im.width-(bounds[2]-bounds[0]))/2,(im.height-(bounds[3]-bounds[1]))/2-bounds[1]),value,font=f,fill=C[color])
def star(size,fill):
    im=image(size,size); pts=[]
    for i in range(10):
        a=-math.pi/2+i*math.pi/5; r=size*(.43 if i%2==0 else .20)
        pts.append((size/2+math.cos(a)*r,size/2+math.sin(a)*r))
    d=ImageDraw.Draw(im); d.polygon(pts,fill=C[fill]); d.line(pts+[pts[0]],fill=C['dark'],width=4,joint='curve')
    return im
def eye(state):
    im=image(128,128); d=ImageDraw.Draw(im); color=['steel','gold','red'][state]
    if state==0:
        d.arc((14,30,114,85),0,180,fill=C['dark'],width=10)
        for x in range(30,110,20): d.line((x,72,x-6,84),fill=C['steel'],width=4)
    else:
        d.polygon([(12,64),(35,35 if state==2 else 49),(64,27 if state==2 else 40),(95,39),(116,64),(94,88),(64,99 if state==2 else 85),(35,88)],fill=C[color],outline=C['dark'],width=4)
        d.ellipse((43,43,85,85),fill=C['dark']); d.ellipse((49,47,61,59),fill=C['cream'])
    return im
def ring(size,fill=1,color='gold',width=14):
    im=image(size,size); d=ImageDraw.Draw(im); b=(6,6,size-7,size-7)
    d.ellipse(b,outline=C['dark'],width=width+6); d.ellipse((10,10,size-11,size-11),outline=C['slate'],width=width)
    if fill>0: d.arc((10,10,size-11,size-11),-90,-90+fill*359.9,fill=C[color],width=width)
    return im
def save(name,im): snap(im).save(OUT/f'{name}.png'); return im
def strip(name,frames):
    out=image(frames[0].width*len(frames),frames[0].height)
    for i,f in enumerate(frames): out.alpha_composite(f,(i*f.width,0))
    save(name,out)

save('wanted-meter-bar-frame',panel(560,112,'dark'))
save('wanted-star-empty',star(96,'slate')); save('wanted-star-filled',star(96,'gold'))
strip('wanted-star-flashing_strip8',[star(96,'red' if i in [2,3,4,5] else 'gold') for i in range(8)])
timer=panel(320,128,'dark'); stripes(timer,(16,14,303,26)); save('heist-timer-frame',timer)
digits=image(528,80)
for i,char in enumerate('0123456789:'):
    cell=image(48,80); text(cell,char,64); d=ImageDraw.Draw(cell)
    if char!=':': d.rectangle((22,0,25,79),fill=(0,0,0,0))
    digits.alpha_composite(cell,(i*48,0))
save('heist-timer-digits-stencil',digits)
strip('heist-timer-warning_strip8',[panel(320,128,'dark','red' if i%4<2 else 'steel') for i in range(8)])
for i,state in enumerate(['hidden','suspicious','spotted']): save('stealth-eye-'+state,eye(i))
strip('stealth-detection-fill_strip8',[ring(128,i/7,'red' if i>4 else 'gold',10) for i in range(8)])
loot=panel(288,96,'dark'); ImageDraw.Draw(loot).rounded_rectangle((18,22,78,74),6,fill=C['green'],outline=C['dark'],width=4); save('loot-counter-panel',loot)
alarm=panel(720,128,'red','dark',10); stripes(alarm,(12,12,708,115),'dark'); inner=panel(540,104,'red','dark',6); text(inner,'ALARM TRIGGERED',42); alarm.alpha_composite(inner,(90,12)); save('alarm-triggered-banner',alarm)
strip('alarm-banner-flash_strip8',[alarm if i%4<2 else panel(720,128,'dark','red') for i in range(8)])
card=panel(400,320,'cream'); ImageDraw.Draw(card).rounded_rectangle((130,4,270,55),8,fill=C['steel'],outline=C['dark'],width=4); save('objective-checklist-card',card)
for state in ['empty','ticked','failed']:
    im=panel(64,64,'cream','slate',8); d=ImageDraw.Draw(im)
    if state=='ticked': d.line([(16,32),(27,44),(49,19)],fill=C['green'],width=8)
    if state=='failed':
        d.line((18,18,46,46),fill=C['red'],width=8); d.line((46,18,18,46),fill=C['red'],width=8)
    save('objective-checkbox-'+state,im)
dial=image(384,384); d=ImageDraw.Draw(dial); d.ellipse((8,8,375,375),fill=C['slate'],outline=C['dark'],width=4); d.ellipse((66,66,318,318),fill=C['dark'],outline=C['steel'],width=4)
for i in range(40):
    a=i*math.tau/40; r=166; ri=145 if i%5==0 else 155
    d.line((192+math.sin(a)*ri,192-math.cos(a)*ri,192+math.sin(a)*r,192-math.cos(a)*r),fill=C['cream'],width=4)
    if i%5==0:
        value=str(i); x=192+math.sin(a)*124; y=192-math.cos(a)*124
        d.text((x-12,y-12),value,font=font(24),fill=C['cream'])
save('safe-crack-dial-face',dial); save('safe-crack-dial-ring',ring(384,1,'steel',26))
pointer=image(48,64); ImageDraw.Draw(pointer).polygon([(4,4),(44,4),(24,59)],fill=C['gold'],outline=C['dark'],width=4); save('safe-crack-dial-pointer',pointer)
pins=panel(384,192,'dark'); d=ImageDraw.Draw(pins)
for i in range(5):
    x=46+i*69; d.rounded_rectangle((x,30,x+28,162),5,fill=C['steel'],outline=C['dark'],width=4); d.rectangle((x,88,x+28,97),fill=C['gold'])
save('lockpick-tumbler-pins',pins)
strip('interact-hold-ring_strip8',[ring(160,i/7) for i in range(8)])
save('interact-prompt-bubble',panel(192,96,'dark')); save('payout-screen-panel',panel(640,800,'dark','gold',24))
ribbon=panel(640,144,'gold','dark',4); text(ribbon,'HEIST COMPLETE',48,'dark'); save('payout-ribbon-title',ribbon)
for name,value,color in [('payout-heist-complete-stamp','HEIST COMPLETE','green'),('busted-arrest-stamp','BUSTED','red')]:
    im=image(384,192); d=ImageDraw.Draw(im); d.rounded_rectangle((10,35,374,157),8,outline=C[color],width=8); text(im,value,36 if len(value)>8 else 68,color); save(name,im)
for kind in ['hazard-stripe','dark-steel','round-action']:
    normal=panel(384,128,'slate','steel') if kind!='round-action' else image(160,160)
    if kind=='hazard-stripe': stripes(normal,(14,14,369,113))
    if kind=='round-action':
        d=ImageDraw.Draw(normal); d.ellipse((4,4,155,155),fill=C['gold'],outline=C['dark'],width=4); d.ellipse((16,16,143,143),fill=C['slate'],outline=C['dark'],width=4)
    for state in ['normal','hover','pressed','disabled']:
        im=normal.copy()
        if state=='hover': ImageDraw.Draw(im).line((26,20,im.width-27,20),fill=C['cream'],width=4)
        if state=='pressed':
            import numpy as np
            a=np.asarray(im).copy();mask=(a[:,:,3]>0)&(a[:,:,:3].max(axis=2)>40)
            a[mask,:3]=(a[mask,:3]*.75).astype('uint8');im=Image.fromarray(a)
            shifted=image(*im.size);shifted.alpha_composite(im.resize((im.width,im.height-6),Image.Resampling.NEAREST),(0,6));im=shifted
        if state=='disabled':
            import numpy as np
            a=np.asarray(im).copy(); mask=(a[:,:,3]>0)&(a[:,:,:3].max(axis=2)>40); a[mask,:3]=[74,82,88]; im=Image.fromarray(a)
        save(f'button-{kind}-{state}',im)
save('panel-dark-charcoal',panel(192,192,'dark'))
hazard=panel(192,192,'dark'); stripes(hazard,(12,12,179,36)); stripes(hazard,(12,155,179,179)); save('panel-hazard-border',hazard)
save('progress-bar-frame',panel(320,48,'dark','steel',12))
for color in ['gold','red']: save('progress-bar-fill-'+color,panel(320,48,color,'dark',10))
save('minimap-frame-radar-round',ring(288,1,'steel',18)); save('joystick-base-ring',ring(256,1,'steel',20))
knob=image(112,112); ImageDraw.Draw(knob).ellipse((4,4,107,107),fill=C['slate'],outline=C['dark'],width=4); save('joystick-knob-thumb',knob)
margins={'wanted-meter-bar-frame':[40]*4,'heist-timer-frame':[48,40,48,40],'loot-counter-panel':[96,32,32,32],'alarm-triggered-banner':[64,0,64,0],'objective-checklist-card':[40,72,40,40],'interact-prompt-bubble':[32]*4,'payout-screen-panel':[64,96,64,64],'panel-dark-charcoal':[48]*4,'panel-hazard-border':[48]*4,'progress-bar-frame':[24,0,24,0],'progress-bar-fill-gold':[24,0,24,0],'progress-bar-fill-red':[24,0,24,0]}
for kind in ['hazard-stripe','dark-steel']:
    for state in ['normal','hover','pressed','disabled']: margins[f'button-{kind}-{state}']=[48,40,48,48]
(OUT/'heist-ui-nineslice.json').write_text(json.dumps({k+'.png':dict(zip('ltrb',v)) for k,v in margins.items()},indent=2))
files=list(OUT.glob('*.png')); print('UI files:',len(files))
# A functional composition uses the exported components without adding labels to them.
hud=Image.new('RGBA',(1080,1920),C['dark']); hud.alpha_composite(Image.open(OUT/'wanted-meter-bar-frame.png'),(260,60))
for i in range(5): hud.alpha_composite(Image.open(OUT/('wanted-star-filled.png' if i<3 else 'wanted-star-empty.png')),(280+i*100,68))
hud.alpha_composite(timer,(380,190)); hud.alpha_composite(eye(1),(850,80)); hud.alpha_composite(card,(50,360)); hud.alpha_composite(alarm,(180,800)); hud.alpha_composite(dial,(348,1080)); hud.alpha_composite(Image.open(OUT/'joystick-base-ring.png'),(70,1590)); hud.alpha_composite(Image.open(OUT/'button-round-action-normal.png'),(830,1630))
value=image(280,90);text(value,'02:48',64);hud.alpha_composite(value,(400,212))
draw=ImageDraw.Draw(hud);draw.text((85,425),'THE NIGHT SHIFT',font=font(28),fill=C['dark'])
for i,(label,done) in enumerate([('Disable cameras',True),('Open the vault',False),('Reach the van',False)]):
    hud.alpha_composite(Image.open(OUT/f'objective-checkbox-{"ticked" if done else "empty"}.png').resize((40,40)),(85,485+i*58))
    draw.text((140,490+i*58),label,font=font(24),fill=C['dark'])
draw.text((370,1020),'CRACK THE SAFE',font=font(32),fill=C['cream'])
draw.text((855,1690),'USE',font=font(28),fill=C['cream'])
(ROOT/'out/qa').mkdir(exist_ok=True); hud.convert('RGB').save(ROOT/'out/qa/hud-mock.png')
