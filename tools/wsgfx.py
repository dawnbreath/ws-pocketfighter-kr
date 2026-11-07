from PIL import Image
def tile2(b,off):
    px=[]
    for y in range(8):
        lo,hi=b[off+2*y],b[off+2*y+1]
        px.append([((lo>>(7-x))&1)|(((hi>>(7-x))&1)<<1) for x in range(8)])
    return px
def sheet(b,base,n,cols=32,scale=2,shade=(255,170,85,0)):
    rows=(n+cols-1)//cols; im=Image.new('L',(cols*9,rows*9),128)
    for t in range(n):
        p=tile2(b,base+t*16)
        for y in range(8):
            for x in range(8): im.putpixel((t%cols*9+x,t//cols*9+y),shade[p[y][x]])
    return im.resize((im.width*scale,im.height*scale),0)
def glyph816(b,base,i):
    o=base+(i//16)*0x200+(i%16)*16
    return tile2(b,o)+tile2(b,o+0x100)
def gsheet(b,base,n,scale=3,shade=(255,170,85,0),label=True):
    from PIL import ImageDraw
    cols=16; rows=(n+15)//16; im=Image.new('L',(cols*10+30,rows*18),200); d=ImageDraw.Draw(im)
    for i in range(n):
        p=glyph816(b,base,i); x0=30+(i%16)*10; y0=(i//16)*18
        for y in range(16):
            for x in range(8): im.putpixel((x0+x,y0+y),shade[p[y][x]])
    if label:
        for r in range(rows): d.text((0,r*18+3),'%03x'%(r*16),fill=0)
    return im.resize((im.width*scale,im.height*scale),0)
