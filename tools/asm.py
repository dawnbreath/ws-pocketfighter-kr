import os
import subprocess, re, os, tempfile
from paths import ROOT, TMP
SRC=ROOT+'/src/'
def assemble(name, defines=None):
    """assemble SRC/name.asm -> (bytes, symbols dict)"""
    out=(os.makedirs(TMP,exist_ok=True), tempfile.mkdtemp(dir=TMP))[1]
    args=['nasm','-f','bin','-o',out+'/o.bin']
    for k,v in (defines or {}).items(): args.append('-D%s=%s'%(k,v))
    args.append(SRC+name+'.asm')
    subprocess.run(args,check=True,cwd=out)
    syms={}
    mp=out+'/'+name+'.map'
    if os.path.exists(mp):
        txt=open(mp).read()
        sec=txt.split('Real')[-1] if 'Real' in txt else txt
        for m in re.finditer(r'^\s*([0-9A-Fa-f]+)\s+([0-9A-Fa-f]+)\s+(\S+)\s*$',sec,re.M):
            syms[m.group(3)]=int(m.group(2),16)
    return open(out+'/o.bin','rb').read(), syms
