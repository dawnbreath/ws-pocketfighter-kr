"""Pocket Fighter WS Korean+Color build.
usage: python3 build.py OUT.ws [--ko file.json ...]
"""
import sys, os, json, struct, hashlib, argparse
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from paths import ROOT
import asm, krfont, pftext
import numpy as np
ORIG=ROOT+'/orig/pf.ws'
EXP=0x200000                     # original 2MB placed at 4MB+0x200000
KRFONT_IDX=0x00; STORY_IDX=0x0C; COL_IDX=0x0D  # new banks (font uses 0x00..0x0B)
BANKREG=lambda idx: 0xC0|idx
# ------------------------------------------------------------------ ROM
class Rom:
    def __init__(s):
        o=open(ORIG,'rb').read(); assert len(o)==0x200000
        s.orig=o; s.b=bytearray(b'\xff'*EXP)+bytearray(o); s.log=[]
    def o4(s,off): return off+EXP
    def patch(s,off,expect,new,why=''):
        a=s.o4(off); e=bytes.fromhex(expect) if isinstance(expect,str) else expect
        assert s.b[a:a+len(e)]==e, 'patch mismatch @%x %s: %s'%(off,why,s.b[a:a+len(e)].hex())
        s.b[a:a+len(new)]=new; s.log.append((off,len(new),why))
    def put_free(s,off,data,why=''):
        a=s.o4(off); assert all(x==0xff for x in s.b[a:a+len(data)]), 'not free @%x'%off
        s.b[a:a+len(data)]=data; s.log.append((off,len(data),why))
    def newbank(s,idx): return idx<<16
    def finish(s):
        b=s.b
        b[-6]=0x06            # ROM size 32Mbit
        b[-9]=0x01            # color flag
        c=sum(b[:-2])&0xffff; b[-2]=c&0xff; b[-1]=c>>8
        return bytes(b)
def far(seg,off,*,opcode=0x9a): return bytes([opcode,off&0xff,off>>8,seg&0xff,seg>>8])
# ------------------------------------------------------------------ engine hooks
def apply_engine(R):
    code,sym=asm.assemble('kr_stubs',{'KRFONT_BANK':hex(BANKREG(KRFONT_IDX)),'STORY_BANK':hex(BANKREG(STORY_IDX)),'COL_BANK':hex(BANKREG(COL_IDX))}|({'HYBRID':'1'} if os.environ.get('PF_HYBRID')=='1' else {}))
    R.put_free(0x150000+0xFF34,code,'kr stubs')
    S=lambda n: sym[n]
    R.patch(0x15AFBA,'b800c08ed8',far(0x5000,S('krchk')),'afb6 korean code check')
    blk='80fc01740bb800e08ed8bedcbbe90800b800e08ed8be9ccb'
    for off,why in ((0x15AEDF,'aeb4 fontsel'),(0x19AC2A,'abf9 fontsel')):
        R.patch(off,blk,far(0x5000,S('fontsel'))+bytes([0xeb,24-7])+b'\x90'*17,why)
    for off,why in ((0x15AF05,'aeb4 glyphcopy'),(0x19AC4F,'abf9 glyphcopy')):
        R.patch(off,'9a408f0040',far(0x5000,S('glyphcopy')),why)
    R.patch(0x19C80F,'b800209a60970090',far(0x5000,S('storyseg'))+b'\x90'*3,'story bank seg')
    R.patch(0x19CA0A,'b800209a4c970090',far(0x5000,S('storymap'))+b'\x90'*3,'story bank map')
    R.patch(0x1403C4,'b800108ed8',far(0x5000,S('colstub')),'vblank colour hook')
    if os.environ.get('PF_HYBRID')=='1': R.patch(0x1402A4,'ea20010000',far(0x5000,S('cpstub'),opcode=0xEA),'copier tail-jump trampoline')
    R.patch(0x14028D,'8a2e3c108a0e3d10',far(0x5000,S('oamstub'))+b'\x90\x90\x90','OAM builder: character bands')
# ------------------------------------------------------------------ colour
import colorlib
from class_table import validate_table
def apply_color(R,survey=False,spec_path=None):
    code,_=asm.assemble('col',({'SURVEY':'1'} if survey else {}) | ({'BPP4':'1'} if os.environ.get('PF_BPP4')=='1' else {}) | ({'BPP4':'1','HYBRID':'1'} | ({'CTAB':'1'} if os.environ.get('PF_CLASS_TABLE') else {}) if os.environ.get('PF_HYBRID')=='1' else {}))
    slist=0x800 if os.environ.get('PF_HYBRID')=='1' else 0x600
    assert len(code)<slist
    spec=colorlib.load_spec(spec_path or colorlib.SPEC)
    bank,conf,n=colorlib.build_bank(code,spec,slist)
    for c in conf: print('colour conflict',c)
    print('colour scenes',n)
    b=COL_IDX<<16; R.b[b:b+0x10000]=bank
    if os.environ.get('PF_HYBRID')=='1' and os.environ.get('PF_CLASS_TABLE'):
        tb=open(os.environ['PF_CLASS_TABLE'],'rb').read(); validate_table(tb); R.b[b+0x8000:b+0x8000+len(tb)]=tb; print('class table',len(tb),'bytes at bank+0x8000')
# ------------------------------------------------------------------ font / encoding
# Korean text is pre-rendered per line (proportional, Galmuri11 12px) and sliced into 8x16 cells.
# Each unique cell bitmap gets a 2-byte code: lead 0xA0..0xFE (page), trail 1..254 (index).
FONT=('Galmuri11.ttf',12); DY=2
LEADS=list(range(0xA0,0xFF))
class KR:
    def __init__(s,R):
        s.R=R; s.cellmap={}; s.n=0
    def _alloc(s,cell):
        key=cell.tobytes()
        if key in s.cellmap: return s.cellmap[key]
        h=s.n; s.n+=1; s.cellmap[key]=h
        k,i=divmod(h,254); i+=1
        assert k<len(LEADS), 'Korean glyph pages overflow'
        bank=KRFONT_IDX+(k>>3); base=(bank<<16)+(k&7)*0x2000+(i//16)*0x200+(i%16)*16
        for half,off in ((cell[:8],0),(cell[8:],0x100)):
            t=bytearray()
            for row in half:
                v=0
                for x in range(8): v|=(1 if row[x] else 0)<<(7-x)
                t+=bytes([v,v])
            s.R.b[base+off:base+off+16]=t
        return h
    @staticmethod
    def code(h): k,i=divmod(h,254); return bytes([LEADS[k],i+1])
    def px(s,text):
        s.check(text); return int(round(krfont.font(*FONT).getlength(text)))
    _cmap=None
    def check(s,text):
        if KR._cmap is None:
            from fontTools.ttLib import TTFont
            KR._cmap=set(TTFont(krfont.FD+FONT[0]).getBestCmap().keys())
        bad=[c for c in text if c not in '\n\u3000' and ord(c) not in KR._cmap]
        assert not bad, 'glyph missing in font: %r in %r'%(bad,text)
    def bitmap(s,text,width_px=None):
        w=width_px if width_px is not None else s.px(text)
        w=max(8,(w+7)//8*8)
        return krfont.render(text,w,16,FONT[0],FONT[1],0,DY) if text else np.zeros((16,w),bool)
    def codes_from_bitmap(s,bm):
        out=[]
        for c in range(bm.shape[1]//8):
            cell=bm[:,c*8:c*8+8]
            out.append(b'\x81\x40' if not cell.any() else s.code(s._alloc(cell)))
        return out
    HARD='ＰＫＳＣ←→↑ＬＶ２３年月日\u3000'
    def _tokens(s,text):
        """-> list of ('k',str) korean run | ('h',char) hard SJIS cell | ('c',n) column marker"""
        import re
        out=[]
        for m in re.finditer(r'\{col:(\d+)\}|([ＰＫＳＣ←→↑ＬＶ２３年月日\u3000])|([^{ＰＫＳＣ←→↑ＬＶ２３年月日\u3000]+)',text):
            if m.group(1): out.append(('c',int(m.group(1))))
            elif m.group(2): out.append(('h',m.group(2)))
            else: out.append(('k',m.group(3)))
        return out
    def enc_line(s,text,cells=None,align='left'):
        """text -> list of 2-byte cell codes. Korean runs are proportional (start on a cell boundary);
        hard chars use the game's own SJIS glyphs; {col:N} pads to cell N. cells: total width to pad to."""
        out=[]
        for kind,v in s._tokens(text):
            if kind=='h': out.append(v.encode('shift_jis'))
            elif kind=='c':
                assert v>=len(out),'col %d < %d in %r'%(v,len(out),text); out+=[b'\x81\x40']*(v-len(out))
            else: out+=s.codes_from_bitmap(s.bitmap(v))
        if cells is None: return out
        assert len(out)<=cells,'line too wide %r (%d>%d cells)'%(text,len(out),cells)
        pad=cells-len(out); l=pad//2 if (align=='center' and '{col' not in text) else 0
        return [b'\x81\x40']*l+out+[b'\x81\x40']*(pad-l)
    def cells(s,text):
        n=0
        for kind,v in s._tokens(text):
            if kind=='h': n+=1
            elif kind=='c': n=max(n,v)
            else: n+=(s.px(v)+7)//8
        return n
# ------------------------------------------------------------------ text insertion
def wrap(kr,text,width,indent_cont=False):
    """greedy word wrap into lines of <=width cells (manual \n respected)"""
    lines=[]
    for para in text.split('\n'):
        words=para.split(' '); cur=''
        for w in words:
            cand=(cur+' '+w) if cur else w
            if kr.cells(cand)<=width or not cur: cur=cand
            else:
                lines.append(cur); cur=(' ' if indent_cont else '')+w
        lines.append(cur)
    for l in lines: assert kr.cells(l)<=width, 'line too long: %r'%l
    return lines
def build_story(R,kr,master,ko):
    STB=STORY_IDX<<16
    R.b[STB:STB+0x10000]=R.orig[0x120000:0x130000]
    ps=pftext.story_ptrs(R.orig)
    newptr={}; o=0x68; stories=master['story']
    for si,st in enumerate(stories):
        p=st['ptr']
        if p in newptr: continue
        newptr[p]=o; buf=bytearray()
        for pi,pg in enumerate(st['pages']):
            pre=b''.join(b'\x81\x94'+c.encode()+bytes.fromhex(prm) for c,prm in pg['pre'])
            key='%s#%d'%(st['id'],pi)
            if key in ko:
                t=ko[key]
                if '」\n「' not in t: t=t.replace('\n',' ')
                quote=t.startswith('「')
                lines=wrap(kr,t,23,indent_cont=quote)
                groups=[lines[i:i+2] for i in range(0,len(lines),2)]
            else:
                groups=[pg['jp']]
            for gi,g in enumerate(groups):
                if gi==0: buf+=pre
                for li,l in enumerate(g):
                    if li: buf+=b'\x81\x94N'
                    if key in ko: buf+=b''.join(kr.enc_line(l))
                    else: buf+=l.encode('shift_jis')
                buf+=b'\x81\x94'+(pg['end'] if gi==len(groups)-1 else 'P').encode()
        R.b[STB+o:STB+o+len(buf)]=buf; o+=len(buf)
        assert o<0xFF00,'story bank overflow'
    for k,p in enumerate(ps): struct.pack_into('<H',R.b,STB+0x20+2*k,newptr[p])
    return o
def fit_line(kr,text,width,center):
    return kr.enc_line(text,width,'center' if center else 'left')
def build_fixed(R,kr,master,ko):
    for f in master['fixed']:
        if f['id'] not in ko: continue
        v=ko[f['id']]; lines=v if isinstance(v,list) else v.split('\n')
        assert len(lines)<=len(f['split']),f['id']
        lines+=['']*(len(f['split'])-len(lines))
        out=[]
        for t,w,jl in zip(lines,f['split'],f['jp']):
            center=jl.startswith('　')
            out+=fit_line(kr,t,w,center)
        data=b''.join(out); assert len(data)==2*f['cells']
        a=R.o4((f['bank']<<16)+f['off']); R.b[a:a+len(data)]=data
def build_wg(R,kr,master,ko):
    import re
    for w in master['wg']:
        if w['id'] not in ko: continue
        t=ko[w['id']]; out=bytearray()
        col=0
        for m in re.finditer(r'\{f:([0-9a-f]{2})\}|\{x:([0-9a-f]{4})\}|([ｒｅｌ])|\{col:(\d+)\}|([^ｒｅｌ{]+)',t,re.S):
            if m.group(4):
                n=int(m.group(4)); assert n>=col,(w['id'],'col',n,col)
                out+=b'\x81\x40'*(n-col); col=n; continue
            if m.group(3)=='ｒ': col=0
            if m.group(5): col+=kr.cells(m.group(5))
            if m.group(1): out+=b'\x82\x86'+bytes([int(m.group(1),16)])
            elif m.group(2): out+=bytes.fromhex(m.group(2))
            elif m.group(3): out+=m.group(3).encode('shift_jis')
            else: out+=b''.join(kr.enc_line(m.group(5)))
        assert out.endswith(b'\x82\x85'), w['id']
        assert len(out)<=w['bytes'], '%s too long %d>%d'%(w['id'],len(out),w['bytes'])
        while len(out)+2<=w['bytes']: out+=b'\x81\x40'
        if len(out)<w['bytes']: out+=b'\x40'
        a=R.o4(w['off']); R.b[a:a+len(out)]=out
# ------------------------------------------------------------------ main
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('--ko',nargs='*',default=[]); ap.add_argument('--survey',action='store_true'); ap.add_argument('--spec',default=None); ap.add_argument('--img',action='store_true')
    a=ap.parse_args()
    master=json.load(open(ROOT+'/text/master.json'))
    ko={}
    for f in a.ko: ko.update(json.load(open(f)))
    R=Rom(); apply_engine(R); apply_color(R,a.survey,a.spec); kr=KR(R)
    import imgtext; sys.path.insert(0,ROOT+'/text/ko'); import imgspec
    if a.img: print('image tiles',imgtext.apply(R,imgspec.SPEC)); imgtext.apply_title(R); imgtext.apply_pause(R)
    end=build_story(R,kr,master,ko); build_fixed(R,kr,master,ko); build_wg(R,kr,master,ko)
    data=R.finish(); open(a.out,'wb').write(data)
    print('built',a.out,'halves',kr.n,'story_end',hex(end),'md5',hashlib.md5(data).hexdigest())
if __name__=='__main__': main()
