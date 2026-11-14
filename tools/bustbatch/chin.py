import re,sys,os
os.chdir(r'D:\RokuganTraveler')
C={a.split('=')[0]:float(a.split('=')[1]) for a in sys.argv[1:]}
p='tools/gen_busts.py';s=open(p,encoding='utf-8').read()
for k in C: s=re.sub(r'"%s": [0-9.]+, '%k,'',s); s=re.sub(r', "%s": [0-9.]+'%k,'',s)
s=s.replace('CHIN_FIX = {','CHIN_FIX = {'+''.join('"%s": %s, '%(k,v) for k,v in C.items()),1)
open(p,'w',encoding='utf-8').write(s)
