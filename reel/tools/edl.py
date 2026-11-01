U='/root/.claude/uploads/7512deaa-f08b-56d2-bde1-6d165e8dd8a3/'
PH={'P1':U+'800a2547-image.jpg','P2':U+'e82db1d8-image.jpg','P4':U+'688b1bb2-image.jpg','P5':U+'64167bee-image.jpg','P6':U+'0a7759c3-image.jpg','P8':U+'c386cf61-image.jpg'}
# (src, in, dur, mask_track or None, note, opts)
SHOTS=[
 ('v21',76.0,2.5,None,'HOOK lit tree',{'zoom':(1.00,1.05)}),
 ('P2',0,2.5,'P2','toddler waving (photo)',{'cx':400,'zoom':(1.0,1.06)}),
 ('P6',0,2.5,'P6','dad & son set up the room (photo)',{'cx':469,'zoom':(1.0,1.05)}),
 ('P4',0,2.5,'P4','teamwork at the TV (photo)',{'cx':381,'zoom':(1.06,1.0)}),
 ('P5',0,2.5,None,'tree in the box (photo)',{'cx':375,'zoom':(1.0,1.07)}),
 ('v20',1.9,3.0,'v20a','opening the box',{}),
 ('v20',13.0,2.5,'v20b','lifting the first section',{}),
 ('v20',21.0,2.5,None,'fitting the stand',{}),
 ('v20',25.3,2.5,None,'tree standing',{}),
 ('v17',1.0,2.5,None,'spreading lower branches',{}),
 ('v17',6.0,2.5,None,'spreading branches 2',{}),
 ('v19',0.0,2.0,None,'fluffing middle',{}),
 ('v19',15.5,2.5,None,'fluffing close',{}),
 ('v19',19.0,2.5,None,'hands in branches',{}),
 ('v21',13.8,2.5,None,'shaping the top',{}),
 ('v21',5.8,3.4,'dance','toddler dance',{'nat':2.0}),
 ('v21',16.5,2.35,None,'top branches',{}),
 ('v21',21.5,3.5,'baby1','mum + baby join',{}),
 ('v21',27.5,2.25,'baby2','mum laughs to camera',{'nat':1.6}),
 ('v21',40.25,2.5,'baby3','mum reaches the top',{'nat':1.4}),
 ('v19',22.5,2.5,None,'dad final fluff, glance',{}),
 ('v21',1.0,2.5,None,'dad tweaks the top',{}),
 ('v21',48.8,4.0,'plug','toddler heads to the tree',{'zoom':(1.0,1.04)}),
 ('v21',45.8,1.5,None,'tree fully shaped, unlit (cutaway)',{'zoom':(1.12,1.15)}),
 ('v21',52.3,10.5,'plug','toddler plugs in -> LIGHTS ON @70.0',{'zoom':(1.0,1.08),'nat':1.6}),
 ('v21',64.95,2.5,'run','toddler runs to camera',{'nat':1.8}),
 ('v21',71.6,2.75,'dark','room lights off, silhouette',{'nat':1.4}),
 ('P8',0,2.5,'P8','touching the lights (photo)',{'cx':421,'zoom':(1.0,1.06)}),
 ('P1',0,2.5,'P1','toddler by the lit tree (photo)',{'cx':401,'zoom':(1.06,1.0)}),
 ('v21',78.25,7.25,None,'CLOSING glow',{'zoom':(1.0,1.07),'nat':1.4}),
]
DISSOLVE={5.0:0.5, 77.75:0.5, 80.25:0.5, 82.75:0.6}  # boundary time -> length
TEXTS=[("Making Christmas memories",0.35,4.6,'open'),("Our tree.\nOur little traditions.",84.6,89.2,'close')]
def timeline():
    t=0; out=[]
    for s in SHOTS: out.append((t,)+s); t+=s[2]
    return out,t
