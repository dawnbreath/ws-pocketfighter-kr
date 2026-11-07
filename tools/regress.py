import emu, sys, hashlib
from PIL import Image, ImageChops
W='/home/user/pocketfighter/work/'
SEQ=[['wait',400],['start',4,150],['start',4,120],['shot','t'],['a',3,90],['a',3,120],['a',3,150],['wait',60],['shot','st1'],['a',3,100],['shot','st2'],['a',3,100],['a',3,100],['shot','st3']]
for i in range(30): SEQ.append(['a',3,50])
SEQ.append(['shot','fight'])
def run(rom,tag):
    emu.relaunch(rom); out=[]
    for it in SEQ:
        if it[0]=='shot': p=W+'rg_%s_%s.png'%(tag,it[1]); emu.shot(p); out.append(p)
        elif it[0]=='wait': emu.step(it[1])
        else: emu.tap(it[0],it[1],it[2])
    return out
if __name__=='__main__':
    a=run(sys.argv[1],'A'); b=run(sys.argv[2],'B')
    for x,y in zip(a,b):
        d=ImageChops.difference(Image.open(x).convert('RGB'),Image.open(y).convert('RGB')).getbbox()
        print(x.split('_')[-1], 'IDENTICAL' if d is None else 'DIFF %s'%(d,))
