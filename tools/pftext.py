"""Pocket Fighter WS text model: tokenize / encode."""
import struct
CTRL_PARAMS={'N':0,'P':0,'S':0,'E':0,'L':0,'C':2,'F':1,'T':1,'W':1,'M':1}
STORY_BANK=0x12; STORY_TABLE=0x20; STORY_COUNT=36
def story_ptrs(rom):
    b=STORY_BANK<<16
    return list(struct.unpack('<%dH'%STORY_COUNT, rom[b+STORY_TABLE:b+STORY_TABLE+2*STORY_COUNT]))
def tokenize_story(rom, off):
    """returns list of tokens: ('c',letter,params bytes) or ('t',2-byte code) until E-terminated stream end (next ptr)"""
    b=STORY_BANK<<16; o=b+off; toks=[]
    while True:
        if rom[o]==0x81 and rom[o+1]==0x94:
            L=chr(rom[o+2]); n=CTRL_PARAMS.get(L)
            if n is None: raise ValueError('unknown ctrl %r at %x'%(L,o))
            toks.append(('c',L,bytes(rom[o+3:o+3+n]))); o+=3+n
            if L=='E': 
                # stream continues? stop at E only if next is end of story (caller provides bound)
                pass
        else:
            toks.append(('t',bytes(rom[o:o+2]))); o+=2
        yield_end = o
        if toks[-1][0]=='c' and toks[-1][1]=='E' and getattr(tokenize_story,'stop_at_E',False): break
        if o>=tokenize_story.bound or rom[o:o+2]==b'\xff\xff': break
    return toks, o-b
def enc_tokens(toks):
    out=bytearray()
    for t in toks:
        if t[0]=='c': out+=b'\x81\x94'+t[1].encode()+t[2]
        else: out+=t[1]
    return bytes(out)
def tok_str(toks):
    s=[]
    for t in toks:
        if t[0]=='c': s.append('{%s%s}'%(t[1],(':'+t[2].hex()) if t[2] else ''))
        else: s.append(t[1].decode('shift_jis'))
    return ''.join(s)
