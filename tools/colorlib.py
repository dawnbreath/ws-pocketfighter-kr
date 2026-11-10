import json, struct, os, sys
from paths import ROOT
SPEC=ROOT+'/text/color_spec.json'
NOM=[15,13,11,9,7,5,3,0]   # nominal luma per shade (shade0 lightest)
def hexc(h): return tuple(int(c,16) for c in h)
def rgbw(c): r,g,b=c; return (r<<8)|(g<<4)|b
def ramp_color(anchors,s):
    t=(15-NOM[s])/15.0; n=len(anchors)-1; x=t*n; i=min(int(x),n-1); f=x-i
    a,b=anchors[i],anchors[i+1]
    return tuple(max(0,min(15,int(round(a[j]+(b[j]-a[j])*f)))) for j in range(3))
def load_spec(path=SPEC): return json.load(open(path))
def pal_words(h): b=bytes.fromhex(h); return [b[2*i]|b[2*i+1]<<8 for i in range(16)]
def anchors(spec,name): return [hexc(a) for a in spec['ramps'][name]]
def shade_ramp(spec,name,s):
    """explicit colours for some shades (dict shade->hex rgb); others interpolated by shade index"""
    d={int(k):hexc(v) for k,v in spec['shaderamps'][name].items()}
    ks=sorted(d)
    if s in d: return d[s]
    lo=max([k for k in ks if k<s],default=ks[0]); hi=min([k for k in ks if k>s],default=ks[-1])
    if lo==hi: return d[lo]
    f=(s-lo)/(hi-lo); a,b=d[lo],d[hi]
    return tuple(int(round(a[j]+(b[j]-a[j])*f)) for j in range(3))
def ramp_for(spec,name,s):
    if name in spec.get('shaderamps',{}): return shade_ramp(spec,name,s)
    return ramp_color(anchors(spec,name),s)
def scene_table(spec,use):
    """16 x 8 colour table for a scene: use{p:ramp} over the global default ramps"""
    t=[]
    for p in range(16):
        name=use.get(str(p), spec.get('default',{}).get(str(p)))
        if name is None: t.append([(NOM[s],)*3 for s in range(8)])
        else: t.append([ramp_for(spec,name,s) for s in range(8)])
    return t
def parse_key(s): return tuple(int(x,16) for x in s.split(','))
def expand(spec):
    default=scene_table(spec,{})
    scenes=[]; seen={}; conf=[]
    for sc in spec['scenes']:
        t=scene_table(spec,sc.get('use',{}))
        for kk in sc.get('keys',[]):
            k=parse_key(kk)
            if k in seen:
                if seen[k][1]!=t: conf.append((sc['name'],seen[k][0],kk))
                continue
            seen[k]=(sc['name'],t); scenes.append((k,t))
    return default,scenes,conf
def build_bank(code,spec,slist=0x600,fighter_palettes=None):
    default,scenes,conf=expand(spec)
    bank=bytearray(b'\xff'*0x10000); bank[:len(code)]=code
    enc=lambda t: b''.join(struct.pack('<H',rgbw(c)) for p in range(16) for c in t[p])
    bank[0xC00:0xD00]=enc(default)
    bt=[[shade_ramp(spec,spec['band'][str(p)],s) for s in range(8)] for p in range(8,12)]
    # per-character body rows (palette 12/13), keyed by the hash of the HUD name tiles
    chars=spec.get('chars',[]); rows=bytearray(); pl1=bytearray(); pl2=bytearray()
    import hashlib
    base=0x151480; orig=open(ROOT+'/orig/pf.ws','rb').read()
    def hsh(data):
        h=0
        for i in range(0,len(data),2):
            w=data[i]|data[i+1]<<8; h=(((h<<3)|(h>>13))&0xffff)^w
        return h or 1
    for c in chars:
        tiles=[orig[base+k*16:base+k*16+16] for k in range(c['s'],c['e']+1)]
        p1=b''.join(tiles[:4])
        p2=(b'\x00'*16*7+b''.join(tiles))[-16*7:]
        ro=0xE00+len(rows); rows+=b''.join(struct.pack('<H',rgbw(shade_ramp(spec,c['body'],s))) for s in range(8))+bytes([c.get('c1',45),c.get('c2',100),c.get('c3',100),c.get('flags',6),c.get('xr',0),0,0,0])
        pl1+=struct.pack('<HH',hsh(p1),ro); pl2+=struct.pack('<HH',hsh(p2),ro)
    if fighter_palettes is not None:
        for lookup in (pl1,pl2):
            hashes=[h for h,_ in struct.iter_unpack("<HH",lookup)]
            if len(set(hashes)) != len(hashes):
                raise ValueError("ambiguous HUD name hashes in fighter palette catalogue")
    assert len(pl1)<0x40 and len(pl2)<0x80 and len(rows)<=0x200,len(rows)
    bank[0xD40:0xD40+len(pl1)]=pl1; bank[0xD40+len(pl1):0xD40+len(pl1)+2]=b'\x00\x00'
    bank[0xD80:0xD80+len(pl2)]=pl2; bank[0xD80+len(pl2):0xD80+len(pl2)+2]=b'\x00\x00'
    bank[0xE00:0xE00+len(rows)]=rows
    bank[0xD00:0xD40]=b''.join(struct.pack('<H',rgbw(c)) for r in bt for c in r)
    lst=bytearray(); off=0x1000; tabs=bytearray(); cache={}
    for k,t in scenes:
        e=enc(t)
        if e not in cache: cache[e]=off+len(tabs); tabs+=e
        lst+=struct.pack('<2HH',*k,cache[e])
    lst+=struct.pack('<H',0xFFFF)
    assert slist+len(lst)<=0xC00 and 0x1000+len(tabs)<=0x10000
    bank[slist:slist+len(lst)]=lst; bank[0x1000:0x1000+len(tabs)]=tabs
    if fighter_palettes is not None:
        from fighter_palettes import install
        install(bank,chars,fighter_palettes,off+len(tabs))
    return bytes(bank),conf,len(scenes)
