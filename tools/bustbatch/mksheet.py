# usage: mksheet.py N tag  -> next N stand-in speakers (no bust yet) with candidates; sheets pick<tag>_KK.png + picksel<tag>.json
import os,re,json,glob,sys
from PIL import Image, ImageDraw
os.chdir(r'D:\RokuganTraveler')
S=r'D:\RokuganTraveler\_art\preview\agents\busts\batch'
N=int(sys.argv[1]);tag=sys.argv[2];extra=sys.argv[3:]   # extra: explicit keys:names
have=set(os.listdir('_tools/rpgcobo-tool/project/resource/bust'))
skip=set(json.load(open(S+r'\skipped.json'))) if os.path.exists(S+r'\skipped.json') else set()
rows=[l.split('\t') for l in open(S+r'\standins.txt',encoding='utf-8').read().splitlines()]
txt=''.join(open(p,errors='replace').read() for p in glob.glob('_art/preview/bot/story_*/log.txt'))
sel=[]
def add(sp,k,n):
    d=os.path.join('_art','busts',k,'review')
    if not os.path.isdir(d): return
    cs=sorted((os.path.getmtime(os.path.join(d,f)),int(re.match(r'cand_s(\d+)',f).group(1))) for f in os.listdir(d) if re.match(r'cand_s\d+\.png$',f))
    hi=[s for t,s in cs if s>1000] or [s for t,s in cs]
    if not hi: return
    m=re.findall(r'\[RT\] MSG '+re.escape(sp)+r':(.*)',txt)
    sel.append((sp,k,int(n),hi[-3:],(m[0] if m else '')[:90]))
for e in extra:
    k,sp=e.split(':',1);add(sp,k,0)
for n,sp,stand,k,c in rows:
    if len(sel)>=N: break
    if '(' in sp or k in have or sp=='Nashiko' or sp in skip: continue
    add(sp,k,n)
json.dump(sel,open(S+r'\picksel%s.json'%tag,'w'),indent=0)
for i,s in enumerate(sel): print(i,s[0],s[2],'|',s[4])
tw,th=170,245
for p in range(0,len(sel),8):
    ch=sel[p:p+8];sh=Image.new('RGB',(tw*4,th*len(ch)),(40,40,48));dr=ImageDraw.Draw(sh)
    for r,(sp,k,n,cs,l) in enumerate(ch):
        dr.text((4,r*th+10),'%d %s'%(p+r,sp[:20]),fill=(255,255,0))
        for c,s in enumerate(cs):
            im=Image.open(os.path.join('_art','busts',k,'review','cand_s%d.png'%s));im.thumbnail((tw-4,th-18))
            sh.paste(im,((c+1)*tw,r*th));dr.text(((c+1)*tw+3,r*th+th-16),'%d'%(c+1),fill=(255,255,0))
    sh.save(S+r'\pick%s_%02d.png'%(tag,p//8))
