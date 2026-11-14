# export.sh tag : gen_busts npc each key; flag colour-key fallbacks; then magenta sheet with chin lines
S="D:/RokuganTraveler/_art/preview/agents/busts/batch"
cd /d/RokuganTraveler
for k in $(cat $S/newkeys$1.txt); do .venv/Scripts/python.exe -E tools/gen_busts.py npc $k > $S/exp_$k.log 2>&1; grep -q "unavailable\|Traceback" $S/exp_$k.log && echo "FAIL $k" || echo "ok $k"; done
.venv/Scripts/python.exe -E - $1 <<'PY'
import sys,json
from PIL import Image, ImageDraw
S=r'D:\RokuganTraveler\_art\preview\agents\busts\batch'
ks=[k.strip() for k in open(S+r'\newkeys%s.txt'%sys.argv[1]) if k.strip()]
cols=8;sh=Image.new('RGB',(160*cols,240*((len(ks)+cols-1)//cols)),(30,30,36));d=ImageDraw.Draw(sh)
for j,k in enumerate(ks):
    try: im=Image.open('_tools/rpgcobo-tool/project/resource/bust/%s/neutral.png'%k).convert('RGBA')
    except Exception: continue
    bg=Image.new('RGBA',im.size,(255,0,255,255));bg.alpha_composite(im)
    fc=json.load(open('_tools/rpgcobo-tool/project/resource/bust/%s/faces.json'%k)).get('base')
    if fc: ImageDraw.Draw(bg).line([(0,fc[2]*im.height),(im.width,fc[2]*im.height)],fill=(0,255,0,255),width=3)
    else: ImageDraw.Draw(bg).rectangle([0,0,40,40],fill=(255,255,0,255))
    bg=bg.resize((int(220*im.width/im.height),220));x,y=(j%cols)*160,(j//cols)*240;sh.paste(bg,(x,y));d.text((x+2,y+224),'%d %s'%(j,k[4:21]),fill=(255,255,0))
sh.save(S+r'\done%s.png'%sys.argv[1])
PY
echo SHEET
