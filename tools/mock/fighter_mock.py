import os
import json,sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')); sys.argv=['x']
import region_mock as R, numpy as np
from PIL import Image
S=os.environ.get('PF_WORK','work')+'/'
import os
cap=json.load(open(os.environ.get('PF_WORK','work')+'/sprdump.json'))
PAL={
 'skin':[(246,213,164),(230,148,98),(131,49,0)],
 'red':[(246,0,0),(180,0,0),(100,0,0)],
 'pants':[(246,0,0),(180,0,0),(115,0,0)],
 'blue':[(131,213,246),(0,98,246),(0,16,148)],
 'brown':[(180,82,49),(131,49,16),(82,32,0)],
 'tights':[(214,170,130),(160,110,76),(70,36,20)],
 'white':[(246,246,246),(213,213,246),(82,82,197)],
 'hair':[(110,80,70),(60,36,30),(20,8,8)],
 'silver':[(255,255,255),(176,186,200),(70,74,96)],
}
def inr(x,y,r): return r[0]<=x<r[2] and r[1]<=y<r[3]
# comp-id -> class (ids are for this single capture; production derives them from rules, not ids)
CH={'zan':dict(k=9,s=4,comp={14:'red'},
   rects=[('red',(0,40,48,48)),('red',(20,41,36,48)),('pants',(15,29,22,31)),('pants',(15,31,21,36))],
   hair=(14,3,30,9)),
 'chun':dict(k=7,s=4,comp={1:'skin',3:'skin',4:'skin',5:'skin',8:'skin',9:'skin',17:'skin',12:'skin',21:'skin',27:'skin',25:'skin',18:'skin',19:'skin',22:'skin',7:'skin',2:'white',16:'blue',20:'blue',28:'skin',26:'brown',29:'white',37:'white'},
   rects=[('brown',(5,25,10,36)),('skin',(10,21,15,25),16),('blue',(6,17,10,20)),('skin',(3,20,9,25)),('silver',(4,9,10,13)),('white',(0,36,32,40)),('hair',(8,2,24,5))],
   hair=None)}
ims=[]
for name,c in CH.items():
    g=R.frame(cap,c['k'],c['s']); lab,n=R.segment(g); H,W=g.shape
    cls=[[None]*W for _ in range(H)]
    # component classes; unlisted comps -> nearest listed comp
    known=np.zeros((H,W),bool)
    for y in range(H):
        for x in range(W):
            if lab[y,x] and lab[y,x] in c['comp']: cls[y][x]=c['comp'][lab[y,x]]; known[y,x]=True
    for it in c['rects']:
        cl,r=it[0],it[1]; only=it[2] if len(it)>2 else None
        for y in range(H):
            for x in range(W):
                if g[y,x]>0 and inr(x,y,r) and (only is None or lab[y,x]==only) and (g[y,x]==3 or cl in('silver',) or lab[y,x]==0 or True): cls[y][x]=cl; known[y,x]=True
    # fill: all others skin for zan; chun: unlisted -> nearest known
    ys,xs=np.where(known)
    for y in range(H):
        for x in range(W):
            if g[y,x]>0 and cls[y][x] is None:
                if name=='zan': cls[y][x]='skin'
                else:
                    d=(ys-y)**2+(xs-x)**2; j=d.argmin(); cls[y][x]=cls[ys[j]][xs[j]]
    # outline/dark pixels not claimed by rect: follow neighbours (priority non-skin)
    out=[row[:] for row in cls]
    for y in range(H):
        for x in range(W):
            if g[y,x]==3 and not known[y,x]:
                nb=[cls[yy][xx] for yy in range(max(0,y-1),min(H,y+2)) for xx in range(max(0,x-1),min(W,x+2)) if g[yy,xx] in(1,2) and cls[yy][xx]]
                if nb:
                    pri=[q for q in nb if q not in('skin',)]
                    out[y][x]=max(set(pri),key=pri.count) if pri else 'skin'
    cls=out
    a=np.zeros((H,W,3),np.uint8); a[:]=(48,28,96)
    for y in range(H):
        for x in range(W):
            v=int(g[y,x])
            if v<0: continue
            q=cls[y][x] or 'skin'
            if q=='silver' and v==1 and False: pass
            if q=='hair' and v!=3: q='skin'
            a[y,x]=PAL[q][v-1]
    ims.append(Image.fromarray(a).resize((W*8,H*8),Image.NEAREST))
Wt=sum(i.width for i in ims)+30;Ht=max(i.height for i in ims)
o=Image.new('RGB',(Wt,Ht),(30,0,40));x=0
for i in ims:o.paste(i,(x,0));x+=i.width+30
o.save(S+'mock3.png')
