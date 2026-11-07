"""Cold-boot emucap capture and strict pixel comparison (no external emu module)."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import subprocess
import threading
from PIL import Image, ImageChops

SEQ = ([['wait',400],['shot','title'],['start',4,150],['start',4,120],
        ['shot','menus'],['a',3,90],['a',3,120],['a',3,150],['wait',60],
        ['shot','story1'],['a',3,100],['shot','story2'],['a',3,100],
        ['a',3,100],['shot','story3']] + [['a',3,50] for _ in range(30)] + [['shot','fight']])

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

class MCP:
    def __init__(self, binary: Path, work: Path, mednafen: Path):
        self.serial = 0; self.responses = queue.Queue()
        self.log = (work/'mcp-stderr.log').open('w')
        env = dict(os.environ, MEDNAFEN_BIN=str(mednafen.resolve()),
                   EMUCAP_EMU_HOME=str((work/'runtime').resolve()))
        self.process = subprocess.Popen([str(binary.resolve())],cwd=work,env=env,
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.log,text=True,bufsize=1)
        def reader():
            for line in self.process.stdout:
                try: self.responses.put(json.loads(line))
                except json.JSONDecodeError: self.responses.put({'error':line})
            self.responses.put({'error':'MCP EOF'})
        threading.Thread(target=reader,daemon=True).start()
        self.request('initialize',{'protocolVersion':'2024-11-05','capabilities':{},
                                  'clientInfo':{'name':'pf-regress','version':'1'}})
        self.process.stdin.write(json.dumps({'jsonrpc':'2.0','method':'notifications/initialized'})+'\n')
        self.process.stdin.flush()
    def request(self, method: str, params: dict) -> dict:
        self.serial += 1
        self.process.stdin.write(json.dumps({'jsonrpc':'2.0','id':self.serial,'method':method,'params':params})+'\n')
        self.process.stdin.flush()
        while True:
            item = self.responses.get(timeout=60)
            if 'error' in item: raise RuntimeError(item['error'])
            if item.get('id') == self.serial: return item['result']
    def call(self, name: str, args: dict | None = None) -> dict:
        result = self.request('tools/call',{'name':name,'arguments':args or {}})
        if result.get('isError'): raise RuntimeError(f'{name}: {result}')
        value = result.get('structuredContent')
        if value is None:
            for block in result.get('content',[]):
                if block.get('type') == 'text':
                    try: value = json.loads(block['text']); break
                    except json.JSONDecodeError: pass
        if value is None: value = {}
        if value.get('error') or value.get('ok') is False:
            raise RuntimeError(f'{name}: {value}')
        return value
    def close(self) -> None:
        self.process.terminate()
        try: self.process.wait(timeout=5)
        except subprocess.TimeoutExpired: self.process.kill(); self.process.wait()
        self.log.close()

def capture(rom: Path, out: Path, binary: Path, mednafen: Path, sequence: list) -> dict:
    out = out.resolve()
    if out.exists(): raise ValueError('capture output must be new')
    names = [x[1] for x in sequence if x[0]=='shot']
    if not names or len(names)!=len(set(names)) or any(not re.fullmatch(r'[A-Za-z0-9_-]+',n) for n in names):
        raise ValueError('need unique safe screenshot names')
    out.mkdir(parents=True)
    report = {'rom_sha256':digest(rom),'emucap_sha256':digest(binary),'mednafen_sha256':digest(mednafen),
              'start':'cold boot; fresh emucap home; no imported saves or savestates',
              'sequence':sequence,'scene_labels':'provisional until visually reviewed',
              'screens':{},'events':[],'status':'INCOMPLETE'}
    client = None; launch_id = None
    try:
        client = MCP(binary,out,mednafen)
        report['bootstrap'] = client.call('bootstrap')
        report['plan'] = client.call('launch_plan',{'content_path':str(rom.resolve()),'system':'wswan'})
        client.call('status')
        launch = client.call('launch',{'content_path':str(rom.resolve()),'system':'wswan',
                                      'display':False,'sound':False,'start_frozen':True})
        report['launch'] = launch
        launch_id = launch.get('launch_id')
        if not launch.get('launched') or not launch_id: raise RuntimeError('launch did not succeed')
        status = client.call('status'); report['initial_status'] = status
        if status.get('state')!='frozen' or status.get('contracts',{}).get('state')!='validated':
            raise RuntimeError('runtime not frozen/validated')
        report['rom_info'] = client.call('get_rom_info')
        limit = status['contracts']['constraints']['execution.step.max_count']
        for action in sequence:
            if action[0]=='shot':
                name = action[1]; path = out/f'{name}.png'
                receipt = client.call('screenshot',{'save_path':str(path)})
                with Image.open(path) as image:
                    image.load()
                    if image.size != (224,144): raise ValueError(f'unexpected WS screen size: {image.size}')
                report['screens'][name] = {'file':path.name,'sha256':digest(path),'receipt':receipt}
            elif action[0]=='wait':
                left = action[1]
                while left:
                    n=min(left,limit); client.call('step',{'count':n,'unit':'frames'}); left-=n
            else:
                client.call('tap',{'buttons':[action[0]],'press_frames':action[1],'after_frames':action[2]})
            report['events'].append(action)
        report['final_status'] = client.call('status')
        if digest(rom)!=report['rom_sha256']: raise ValueError('ROM changed during capture')
        report['status']='CAPTURED'
        return report
    except Exception as e:
        report['error']=str(e)
        raise
    finally:
        if client:
            try:
                if launch_id:
                    report['stop']=client.call('stop',{'launch_id':launch_id})
                    if not report['stop'].get('stopped'): report['status']='STOP_UNCONFIRMED'
            except Exception as stop_error:
                report['stop_error'] = str(stop_error)
                report['status'] = 'STOP_UNCONFIRMED'
            finally: client.close()
        (out/'capture.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')

def compare(a: Path,b: Path,out: Path) -> dict:
    left=json.loads((a/'capture.json').read_text()); right=json.loads((b/'capture.json').read_text())
    if left['status']!='CAPTURED' or right['status']!='CAPTURED': raise ValueError('incomplete capture')
    for field in ('sequence','emucap_sha256','mednafen_sha256','start'):
        if left[field]!=right[field]: raise ValueError(f'capture conditions differ: {field}')
    names=set(left['screens'])
    if not names or names!=set(right['screens']): raise ValueError('empty/missing screen set')
    if out.exists(): raise ValueError('comparison output must be new')
    out.mkdir(parents=True)
    results=[]
    for name in sorted(names):
        paths=[]
        for directory,record in ((a,left),(b,right)):
            item=record['screens'][name]; path=directory/item['file']
            if digest(path)!=item['sha256']: raise ValueError(f'screenshot changed: {path}')
            paths.append(path)
        with Image.open(paths[0]) as ia, Image.open(paths[1]) as ib:
            x,y=ia.convert('RGB'),ib.convert('RGB')
            if x.size!=y.size: raise ValueError(f'size mismatch: {name}')
            diff=ImageChops.difference(x,y); box=diff.getbbox()
            raw = diff.tobytes()
            count = sum(any(raw[i:i+3]) for i in range(0,len(raw),3))
            if box: diff.save(out/f'{name}-diff.png')
            results.append({'screen':name,'status':'DIFFERENT' if box else 'IDENTICAL',
                            'changed_pixels':count,'bbox':box})
    report={'baseline_rom':left['rom_sha256'],'candidate_rom':right['rom_sha256'],
            'screens':results,'identical':all(x['status']=='IDENTICAL' for x in results),
            'scope':'captured screens only; labels require visual review; not full gameplay QA'}
    (out/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

def main() -> None:
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest='command',required=True)
    cap=sub.add_parser('capture'); cap.add_argument('rom',type=Path); cap.add_argument('out',type=Path)
    cap.add_argument('--emucap-mcp',type=Path,required=True); cap.add_argument('--mednafen',type=Path,required=True)
    cap.add_argument('--sequence',type=Path)
    diff=sub.add_parser('compare'); diff.add_argument('baseline',type=Path);diff.add_argument('candidate',type=Path);diff.add_argument('out',type=Path)
    args=p.parse_args()
    if args.command=='capture':
        sequence=json.loads(args.sequence.read_text()) if args.sequence else SEQ
        result=capture(args.rom,args.out,args.emucap_mcp,args.mednafen,sequence)
        print(json.dumps({'status':result['status'],'screens':list(result['screens'])}))
        if result['status'] != 'CAPTURED': raise SystemExit(1)
    else:
        result=compare(args.baseline,args.candidate,args.out); print(json.dumps(result))
        raise SystemExit(0 if result['identical'] else 1)
if __name__=='__main__':main()
