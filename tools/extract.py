"""Extract all JP text units of Pocket Fighter WS into text/master.json"""
import json, struct, sys
sys.path.insert(0,'/home/user/pocketfighter/tools'); import pftext
rom=open('/home/user/pocketfighter/orig/pf.ws','rb').read()
units=[]
# ---- story
ps=pftext.story_ptrs(rom); order=sorted(set(ps)); bounds=order[1:]+[0x3c40]; end_of=dict(zip(order,bounds))
story=[]
for si,p in enumerate(ps):
    pftext.tokenize_story.bound=(0x12<<16)+end_of[p]
    toks,_=pftext.tokenize_story(rom,p)
    pages=[]; pre=[]; lines=['']
    for t in toks:
        if t[0]=='t': lines[-1]+=t[1].decode('shift_jis')
        elif t[1]=='N': lines.append('')
        elif t[1] in 'PE':
            pages.append({'pre':[[x[1],x[2].hex()] for x in pre],'jp':lines,'end':t[1]}); pre=[]; lines=['']
        else: pre.append(t)
    assert lines==[''] and not pre, (si,lines,pre)
    story.append({'id':'S%02d'%si,'ptr':p,'pages':pages})
# ---- fixed records
def ptr_table(bank,off,lo,hi):
    o=(bank<<16)+off; out=[]
    while True:
        v=struct.unpack('<H',rom[o:o+2])[0]
        if not (lo<=v<hi): break
        out.append(v); o+=2
    return out
FIX=[('F1',0x13,0x8298,44,[22,22]),('F2',0x13,0xc6a8,48,[24,24]),('F3',0x13,0xca90,48,[24,24]),
     ('F4',0x13,0xd6c2,16,[16]),('F5',0x13,0xcf34,42,[21,21]),('F6',0x10,0xf470,42,[21,21])]
fixed=[]
for name,bank,toff,L,split in FIX:
    ps=ptr_table(bank,toff,0x8000,0xff00)
    seen={}
    for k,p in enumerate(ps):
        if p in seen: continue
        seen[p]=1
        raw=rom[(bank<<16)+p:(bank<<16)+p+2*L]
        try: s=raw.decode('shift_jis')
        except Exception: s=None
        if s is None or len(s)!=L: 
            fixed.append({'id':'%s_%03d'%(name,k),'bank':bank,'off':p,'cells':L,'bad':raw.hex()}); continue
        ls=[];i=0
        for n in split: ls.append(s[i:i+n]); i+=n
        fixed.append({'id':'%s_%03d'%(name,k),'bank':bank,'off':p,'cells':L,'split':split,'jp':ls})
# ---- wonder gate / misc records (variable, ｅ-terminated, in place)
def sj_ok(c): return (0x81<=c[0]<=0x9f or 0xe0<=c[0]<=0xef) and 0x40<=c[1]<=0xfc and c[1]!=0x7f
def wg_scan():
    import re
    out=[]; i=0; n=len(rom)
    E=b'\x82\x85'
    for m in re.finditer(re.escape(E),rom):
        pass
    return out
wg=[]; done=set(); n=len(rom)
import re
for m in re.finditer(re.escape(b'\x82\x85'),rom):
    e=m.start()
    if e in done or (e>>16) in (0x12,0x13): continue
    # walk back to run start (2-byte aligned with e)
    o=e
    while o-2>=0 and (sj_ok(rom[o-2:o]) ) : o-=2
    # also allow ｆ+param before: skip
    st=o
    # forward tokenize from st to end of run, splitting at ｅ
    o=st; cur=[]; recst=st
    while o<n-1:
        c=rom[o:o+2]
        if c==b'\x82\x86': cur.append('{f:%02x}'%rom[o+2]); o+=3; continue
        if not sj_ok(c): break
        try: cur.append(c.decode('shift_jis'))
        except Exception: cur.append('{x:%s}'%c.hex())
        o+=2
        if c==b'\x82\x85':
            done.add(o-2); wg.append({'id':'W%06x'%recst,'off':recst,'bytes':o-recst,'jp':''.join(cur)}); cur=[]; recst=o
    # trailing non-terminated part ignored
wg=[w for w in wg if any('\u3040'<=ch<='\u30ff' for ch in w['jp'])]
wg.sort(key=lambda w:w['off'])
json.dump({'story':story,'fixed':fixed,'wg':wg},open('/home/user/pocketfighter/text/master.json','w'),ensure_ascii=False,indent=1)
print('story pages',sum(len(s['pages']) for s in story),'fixed',len(fixed),'bad',sum(1 for f in fixed if 'bad' in f),'wg',len(wg))
