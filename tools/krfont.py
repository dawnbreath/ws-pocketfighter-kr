from PIL import Image, ImageDraw, ImageFont
import numpy as np
FD='/home/user/pocketfighter/fonts/'
_cache={}
def font(name='neodgm.ttf',size=16):
    k=(name,size)
    if k not in _cache: _cache[k]=ImageFont.truetype(FD+name,size)
    return _cache[k]
def render(ch,w=16,h=16,name='neodgm.ttf',size=16,dx=0,dy=0):
    """returns numpy bool array h x w"""
    f=font(name,size); im=Image.new('1',(w,h),0); d=ImageDraw.Draw(im)
    d.fontmode='1'
    d.text((dx,dy),ch,font=f,fill=1)
    return np.array(im,dtype=bool)
def bbox(ch,name='neodgm.ttf',size=16):
    f=font(name,size); return f.getbbox(ch)
def neo(ch,w=16,h=16,dx=0,dy=0):
    """exact Neo DunGGeunMo 16px bitmap (rendered at 32 and subsampled)"""
    a=render(ch,w*2,h*2,'neodgm.ttf',32,dx*2,dy*2)
    return a[::2,::2]|a[1::2,1::2]
