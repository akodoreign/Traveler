# usage: apply.py tag "i:c,i:c,..." note   -> npc_picks.json + newkeys<tag>.txt ; skip list for "i:x"
import json,os,sys
os.chdir(r'D:\RokuganTraveler')
S=r'D:\RokuganTraveler\_art\preview\agents\busts\batch'
tag,spec,note=sys.argv[1],sys.argv[2],sys.argv[3]
sel=json.load(open(S+r'\picksel%s.json'%tag))
p='_art/busts/npc_picks.json';d=json.load(open(p,encoding='utf-8'))
sk=set(json.load(open(S+r'\skipped.json'))) if os.path.exists(S+r'\skipped.json') else set()
keys=[]
for it in spec.split(','):
    i,c=it.split(':');sp,k,n,cs,l=sel[int(i)]
    if c=='x': sk.add(sp);continue
    old=d.get(k,{})
    d[k]=dict(names=old.get('names',[sp]),file='review/cand_s%d.png'%cs[int(c)-1],note=note+('; was '+old['file'] if old.get('file') else ''))
    keys.append(k)
json.dump(d,open(p,'w',encoding='utf-8'),indent=1,ensure_ascii=False)
json.dump(sorted(sk),open(S+r'\skipped.json','w'))
open(S+r'\newkeys%s.txt'%tag,'w',newline='\n').write('\n'.join(keys)+'\n');print(len(keys),'picks')
