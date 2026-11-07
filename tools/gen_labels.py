"""Regenerate text/labels_all.json and text/labels_raw.json (git-ignored) from the user's original ROM.
labels_all = every 04/05 sprite-script label found by pieces.find_cmds (in discovery order, index = idx);
labels_raw = the Japanese image labels that imgtext.py replaces (idx set below, chosen by inspecting the contact sheets)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import ROOT
import pieces
JP_IDX = list(range(15, 21)) + [59, 60, 62, 68, 70] + [127] + list(range(129, 221))
rom = open(ROOT + '/orig/pf.ws', 'rb').read()
seen, allp = set(), []
for at, base, bank, ptr in pieces.find_cmds(rom):
    key = (base, bank, at >> 16, ptr)
    if key in seen: continue
    seen.add(key)
    pl = pieces.parse(rom, at >> 16, ptr)
    if pieces.render(rom, bank, base, pl) is None: continue
    allp.append({'idx': len(allp), 'cmd': at, 'base': base, 'bank': bank, 'plbank': at >> 16, 'ptr': ptr, 'pieces': pl})
raw = [x for x in allp if x['idx'] in JP_IDX]
json.dump(allp, open(ROOT + '/text/labels_all.json', 'w'))
json.dump(raw, open(ROOT + '/text/labels_raw.json', 'w'))
print(len(allp), 'labels,', len(raw), 'Japanese image labels')
