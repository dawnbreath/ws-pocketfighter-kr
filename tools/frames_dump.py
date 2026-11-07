"""Dump validated command candidates and proposed masks. Never claims fighter coverage."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw
import pieces

BASE_SHA = 'b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e'
LABELS = {'unknown':0,'skin':1,'cloth':2,'boots':3,'hair':4,'outline':5}

def proposal(frame: Image.Image) -> Image.Image:
    # Geometry/shade guesses only. Unknown includes canvas and shade zero: actual
    # sprite transparency depends on the runtime palette, not the 2bpp value alone.
    mask = Image.new('L',frame.size,0)
    w,h = frame.size
    for y in range(h):
        for x in range(w):
            shade = frame.getpixel((x,y))
            if shade in (0,40): continue
            if shade == 255: region = 'outline'
            elif y < h*0.22: region = 'hair'
            elif y < h*0.42 or x < w*0.18 or x > w*0.82: region = 'skin'
            elif y > h*0.82: region = 'boots'
            else: region = 'cloth'
            mask.putpixel((x,y),LABELS[region])
    return mask

def dump(rom_path: Path, out: Path, mapping_path: Path | None = None) -> dict:
    rom = rom_path.read_bytes(); sha = hashlib.sha256(rom).hexdigest()
    if sha != BASE_SHA: raise ValueError('requires the documented original Pocket Fighter ROM')
    mapping = json.loads(mapping_path.read_text()) if mapping_path else {}
    if mapping and mapping.get('rom_sha256') != sha: raise ValueError('mapping ROM hash mismatch')
    mapping = mapping.get('commands',{})
    if out.exists(): raise ValueError('output must be a new directory')
    out.mkdir(parents=True)
    frames = []; rejected = []; sheets = []; sheet = None
    for command,base,bank,ptr in pieces.find_cmds(rom):
        key = f'{command:06x}'
        try:
            pl = pieces.parse(rom,bank,ptr)
            im = pieces.render(rom,bank,base,pl)
        except ValueError as e:
            rejected.append({'command':key,'reason':str(e)}); continue
        proposed = proposal(im)
        stem = f'candidate-{key}'
        im.save(out/f'{stem}.png'); proposed.save(out/f'{stem}.mask.png')
        identity = mapping.get(key,{})
        if identity and not (identity.get('character') and identity.get('evidence')):
            raise ValueError(f'mapping {key} requires character and evidence')
        x0 = min(p[2] for p in pl); y0 = min(p[1] for p in pl)
        tiles = []
        for index,(word,y,x) in enumerate(pl):
            offset = pieces.bankoff(bank)+base+((word&0x1ffe)>>1)*16
            labels = []
            for yy in range(8):
                for xx in range(8):
                    X = 7-xx if word&0x4000 else xx; Y = 7-yy if word&0x8000 else yy
                    labels.append(proposed.getpixel((x-x0+X,y-y0+Y)))
            tiles.append({'rom_offset':offset,'piece':index,'word':word,'x':x,'y':y,
                          'labels_unflipped':labels})
        frames.append({'command':key,'base':base,'bank':bank,'piece_pointer':ptr,
                       'origin':[x0,y0],'size':list(im.size),'character':identity.get('character'),
                       'identity_evidence':identity.get('evidence'),'status':'proposal-needs-review',
                       'image':f'{stem}.png','mask':f'{stem}.mask.png','tiles':tiles})
        n = len(frames)-1
        if n % 64 == 0:
            if sheet: sheet.save(out/sheets[-1])
            sheet = Image.new('RGB',(8*160,8*160),(50,50,50)); sheets.append(f'sheet-{n//64:03d}.png')
        tx,ty = (n%8)*160,(n%64//8)*160
        preview = im.copy(); preview.thumbnail((152,136),Image.Resampling.NEAREST)
        sheet.paste(preview,(tx,ty+20)); ImageDraw.Draw(sheet).text((tx+3,ty+3),key,fill='white')
    if sheet: sheet.save(out/sheets[-1])
    # Same source tile can occur in several poses/characters: preserve proposals,
    # report conflicts rather than silently choosing one for the engine.
    by_tile = {}; conflicts = []
    for f in frames:
        for t in f['tiles']:
            key = (f['character'],t['rom_offset'])
            value = t['labels_unflipped']
            if key in by_tile and by_tile[key] != value:
                conflicts.append({'character':key[0],'rom_offset':key[1],'command':f['command']})
            else: by_tile[key] = value
    report = {'rom_sha256':sha,'scope':'byte-pattern candidates, not exhaustive animation traversal',
              'fighter_coverage':'UNVERIFIED','palette_semantics':'UNVERIFIED',
              'labels':LABELS,'frames':frames,'rejected':rejected,'sheets':sheets,
              'tile_mask_conflicts':conflicts,'engine_ready':False}
    (out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    if not frames: raise ValueError('no valid candidates; not a successful extraction')
    return report

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,default=Path(__file__).resolve().parents[1]/'orig/pf.ws')
    p.add_argument('--out',type=Path,required=True); p.add_argument('--mapping',type=Path)
    a=p.parse_args(); result=dump(a.rom,a.out,a.mapping)
    print(json.dumps({'candidates':len(result['frames']),'rejected':len(result['rejected']),
                      'conflicts':len(result['tile_mask_conflicts']),'fighter_coverage':result['fighter_coverage']}))
if __name__ == '__main__': main()
