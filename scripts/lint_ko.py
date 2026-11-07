"""Lint build-authoritative JSON and report draft drift; never execute text/*.py."""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build
import krfont

BUDGETS = {'F1': (22,22), 'F2': (24,24), 'F3': (24,24),
           'F4': (16,), 'F5': (21,21), 'F6': (21,21)}
ALIASES = {'자기에프':'장기에프', '모리간':'모리건', '펠리시 아':'펠리시아'}
WG = re.compile(r'\{f:([0-9a-f]{2})\}|\{x:([0-9a-f]{4})\}|([ｒｅｌ])|\{col:(\d+)\}|([^ｒｅｌ{}]+)')

def load_json(path: Path) -> dict:
    def unique(pairs):
        out = {}
        for k,v in pairs:
            if k in out: raise ValueError(f'{path}: duplicate key {k}')
            out[k] = v
        return out
    return json.loads(path.read_text(), object_pairs_hook=unique)

def wg_size(kr: build.KR, value: str) -> int:
    pos = total = col = 0
    ended = False
    for m in WG.finditer(value):
        if m.start() != pos or ended: raise ValueError('invalid WG token or text after end')
        pos = m.end()
        if m[1]: total += 3
        elif m[2]: total += 2
        elif m[3]:
            total += 2
            if m[3] == 'ｒ': col = 0
            if m[3] == 'ｅ': ended = True
        elif m[4]:
            n = int(m[4])
            if n < col: raise ValueError(f'backward column {n} < {col}')
            total += 2*(n-col); col = n
        else:
            n = len(kr.enc_line(m[5])); total += 2*n; col += n
    if pos != len(value) or not ended: raise ValueError('WG terminator/token missing')
    return total

class Scratch:
    # Allocation mirrors the existing renderer but is never saved or used as a ROM.
    def __init__(self): self.b = bytearray(0xC0000)

def lint(root: Path, master_path: Path | None = None) -> dict:
    findings = []
    def flag(level, file, key, message):
        findings.append(dict(level=level, file=file, key=key, message=message))
    kr = build.KR(Scratch())
    master = load_json(master_path) if master_path else None
    wgmeta = {x['id']: x for x in master['wg']} if master else {}
    data = {}
    files = {}
    for name in ('story','fixed','wg'):
        path = root/'text'/'ko'/f'{name}.json'
        records = load_json(path); files[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
        if not records: raise ValueError(f'empty corpus: {path}')
        data.update(records)
        for key,value in records.items():
            lines = value if isinstance(value,list) else [value]
            for line in lines:
                for bad,good in ALIASES.items():
                    if bad in line: flag('error',path.name,key,f'{bad} → {good}')
                for pattern,label in [(r' {2,}','repeated ASCII spaces'), (r'…[가-힣]','ellipsis spacing review'),
                                      (r'[가-힣][,.][가-힣]','punctuation spacing review')]:
                    if re.search(pattern,line): flag('review',path.name,key,label)
            try:
                if name == 'story':
                    text = value if '」\n「' in value else value.replace('\n',' ')
                    for line in build.wrap(kr,text,23,indent_cont=text.startswith('「')):
                        kr.enc_line(line,23)
                elif name == 'fixed':
                    limits = BUDGETS[key.split('_')[0]]
                    lines = value if isinstance(value,list) else value.split('\n')
                    if len(lines) > len(limits): raise ValueError('too many fixed lines')
                    for line,width in zip(lines,limits): kr.enc_line(line,width)
                else:
                    used = wg_size(kr,value)
                    if master:
                        if key not in wgmeta: raise ValueError('unknown WG key')
                        if used > wgmeta[key]['bytes']: raise ValueError(f'WG bytes {used} > {wgmeta[key]["bytes"]}')
            except (AssertionError,ValueError,KeyError) as e:
                flag('error',path.name,key,str(e))
    # Drafts are not build inputs. Their differences are visible, not blindly applied.
    drafts = 0
    for path in sorted((root/'text'/'ko').glob('*.py')):
        tree = ast.parse(path.read_text())
        for node in tree.body:
            if not isinstance(node,ast.Assign) or not any(isinstance(t,ast.Name) and t.id in ('KO','FIX') for t in node.targets): continue
            if not isinstance(node.value, ast.Dict): raise ValueError(f'nonliteral draft: {path}')
            keys = [ast.literal_eval(k) for k in node.value.keys]
            if len(keys) != len(set(keys)): flag('error',path.name,'*','duplicate draft keys')
            for key,value in ast.literal_eval(node.value).items():
                drafts += 1
                if key not in data: flag('review',path.name,key,'draft key absent from canonical JSON')
                elif value != data[key]: flag('draft-drift',path.name,key,'draft differs from build JSON; not applied')
    fontpath = Path(krfont.FD)/build.FONT[0]
    return {'scope':'canonical story/fixed/WG JSON; Python drafts compared, image labels excluded',
            'records':len(data),'draft_records':drafts,'inputs':files,
            'font':{'file':fontpath.name,'sha256':hashlib.sha256(fontpath.read_bytes()).hexdigest(),'size':build.FONT[1]},
            'wg_byte_budget':'CHECKED' if master else 'NOT CHECKED: pass --master (local game data)',
            'runtime_smoke':'NOT RUN','findings':findings,
            'errors':sum(x['level']=='error' for x in findings)}

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--master',type=Path)
    parser.add_argument('--report',type=Path)
    args = parser.parse_args()
    result = lint(args.root,args.master)
    output = json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True); args.report.write_text(output)
    print(json.dumps({k:v for k,v in result.items() if k not in ('findings','inputs')},ensure_ascii=False))
    for item in result['findings']:
        if item['level']=='error': print(json.dumps(item,ensure_ascii=False))
    raise SystemExit(1 if result['errors'] else 0)

if __name__ == '__main__': main()
