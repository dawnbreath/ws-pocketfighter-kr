"""Colour design for Pocket Fighter WS. Regenerates text/color_spec.json.
Scenes are registered with the live palette image of a savestate (via emulator) so (palette, word) keys are exact."""
import json, sys
sys.path.insert(0,'/home/user/tools/py'); sys.path.insert(0,'/home/user/pocketfighter/tools')
RAMPS={
 'gray':['FFF','000'],
 'white_text':['FFF','DDD','888','000'],
 'sky':['FFF','8CE','36B','013'],
 'navy':['CDF','68C','247','012'],
 'grass':['EFA','6C4','271','031'],
 'sunset':['FFD','FB6','D52','402'],
 'sun':['FFF','FE8','F90','A30'],
 'stage':['FFF','DDE','98C','236'],
 'ember':['FDA','F90','A30','310'],
 'brick':['FEC','D96','853','210'],
 'stone':['EEF','A9B','656','213'],
 'skin':['FFF','FDB','D85','521'],
 'gi':['FFF','CDF','78B','124'],
 'card':['FFF','9DF','36A','012'],
 'capcom':['FFF','FCC','D22','400'],
 'ui_blue':['FFF','8CF','24C','003'],
 'ui_yellow':['FFC','FE4','E80','410'],
 'ui_red':['FEE','F88','C22','300'],
 'ui_green':['EFE','8E8','2A3','040'],
 'ui_purple':['FEF','C8F','74C','204'],
 'ui_cyan':['EFF','6EE','29B','024'],
 'p1_red':['FFF','FA8','C22','200'],
 'p2_blue':['FFF','9CF','36C','013'],
 'hud':['FFF','FE6','E60','200'],
 'hudbar':['EFE','6E6','1A2','031'],
}
SHADERAMPS={
 # explicit colours for mono shade 0 (white), 4 (mid grey), 7 (black) of the character palettes
 'p1_head':{0:'FDB',4:'C74',7:'321'}, 'p1_body':{0:'FFF',4:'E33',7:'201'}, 'p1_legs':{0:'FFE',4:'59D',7:'013'},
 'p2_head':{0:'FDB',4:'C74',7:'321'}, 'p2_body':{0:'FFF',4:'3AF',7:'014'}, 'p2_legs':{0:'FFD',4:'F93',7:'410'},
}
# name, name tiles (first,last), cloth ramp, cuts c1,c2,c3 (% of sprite height), flags bits0..3 = band0..3 is cloth (else skin), xr = cloth only within +-xr px of the sprite centre (0 = no limit)
def ch(n,s,e,r,c1=45,c2=100,c3=100,f=0b0110,xr=0): return dict(name=n,s=s,e=e,body=r,c1=c1,c2=c2,c3=c3,flags=f,xr=xr)
CHARS=[
 ch('RYU',2,5,'c_ryu'), ch('KEN',6,9,'c_ken'),
 ch('CHUN-LI',10,16,'c_chun',c1=36,c2=80,c3=100,f=0b0010,xr=13),   # blue dress only; head/arms/legs skin
 ch('SAKURA',17,23,'c_sakura',c1=45,c2=78,c3=100,f=0b0010,xr=14),
 ch('MORRIGAN',24,31,'c_morr'), ch('LEI-LEI',32,38,'c_lei'), ch('FELICIA',39,45,'c_feli'),
 ch('TABASA',46,51,'c_taba'), ch('IBUKI',52,56,'c_ibuki'),
 ch('ZANGIEF',57,63,'c_zang',c1=52,c2=76,c3=86,f=0b1010,xr=12),         # red trunks + red boots, rest bare skin
 ch('DAN',64,67,'c_dan'), ch('GOUKI',68,75,'c_gouki')]
SHADERAMPS.update({
 'c_ryu':{0:'FFF',4:'CCD',7:'224'}, 'c_ken':{0:'F99',4:'D22',7:'300'}, 'c_chun':{0:'DEF',4:'36E',7:'013'},
 'c_sakura':{0:'FFF',4:'E58',7:'301'}, 'c_morr':{0:'FDF',4:'84C',7:'204'}, 'c_lei':{0:'DFF',4:'2A8',7:'031'},
 'c_feli':{0:'FFC',4:'FB2',7:'420'}, 'c_taba':{0:'FEF',4:'95D',7:'214'}, 'c_ibuki':{0:'EDF',4:'648',7:'103'},
 'c_zang':{0:'E66',4:'B11',7:'300'}, 'c_dan':{0:'FEF',4:'F6B',7:'402'}, 'c_gouki':{0:'EDD',4:'765',7:'110'}})
BAND={8:'p1_head',9:'p1_head',10:'p1_head',11:'p1_head'}
DEFAULT={0:'stage',1:'stage',2:'stage',3:'stage',4:'ui_cyan',5:'ui_yellow',6:'ui_red',7:'ui_purple',
         8:'ui_blue',9:'ui_yellow',10:'ui_green',11:'ui_red',12:'p1_body',13:'p2_body',14:'white_text',15:'white_text'}
# scene -> (keys "p0,p1" of the mono palette words, {palette: ramp})
SCENES={
 'capcom':(['0246,7675','5730,7675'],{0:'capcom'}),
 'title':(['3210,4321'],{0:'sky',1:'grass',4:'ui_red',5:'ui_blue',6:'ui_yellow',12:'ui_blue',13:'ui_blue',14:'ui_blue',15:'white_text'}),
 'bselect':(['3456,3210'],{0:'navy',1:'ui_yellow',4:'ui_cyan',5:'ui_yellow',6:'ui_red',12:'ui_blue',13:'ui_blue',14:'ui_blue',15:'white_text'}),
 'link':(['7454,3210'],{0:'ember',4:'ui_yellow',5:'ui_yellow',6:'ui_yellow'}),
 'pselect':(['3210,5321','3210,5432'],{0:'sun',1:'ui_red',2:'gi',3:'card',4:'skin',5:'ui_red',6:'ui_red',12:'p1_red',14:'ui_yellow'}),
 'story':(['3456,1345','3456,2345','4556,2455','5566,3556','5667,4566','6667,5666','6777,6677','7777,7777'],{0:'brick',1:'brick',4:'stone',6:'gray',15:'white_text'}),
}
def build():
    spec={'ramps':RAMPS,'shaderamps':SHADERAMPS,'band':{str(k):v for k,v in BAND.items()},'chars':CHARS,'default':{str(p):n for p,n in DEFAULT.items()},'scenes':[]}
    for name,(keys,use) in SCENES.items():
        spec['scenes'].append({'name':name,'keys':keys,'use':{str(k):v for k,v in use.items()}})
    json.dump(spec,open('/home/user/pocketfighter/text/color_spec.json','w'),indent=1)
    return spec
if __name__=='__main__': build()
