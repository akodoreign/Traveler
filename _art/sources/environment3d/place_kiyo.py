"""Move Kiyo's existing talk event behind the counter without changing its pages."""

import json
from pathlib import Path
import re
import sys

HERE=Path(__file__).resolve().parent
repo=Path(sys.argv[1])
code=repo/"tools/gen_maps.py"
data=repo/"_tools/rpgcobo-tool/project/data/map.json"
old_code=code.read_bytes()
old_data=data.read_bytes()
old_term=b'ev.talk(89, 30, EP["kiyo"],'
new_term=b'ev.talk(90, 33, EP["kiyo"],'
assert old_code.count(old_term)==1
updated_code=old_code.replace(old_term,new_term,1)
compile(updated_code,str(code),"exec")

start=re.search(rb'(?m)^\t"M103"\s*:\s*\{',old_data)[0]
offset=old_data.index(start)
next_map=re.search(rb'(?m)^\t"M\d+"\s*:\s*\{',old_data[offset+len(start):])
limit=offset+len(start)+next_map.start()
chunk=old_data[offset:limit]
event=re.search(rb'(?sm)^\t\t\t"#4#"\s*:\s*\{.*?^\t\t\t\}',chunk)[0]
pos=re.search(rb'"pos"\s*:\s*(\[\s*115,\s*4,\s*34,\s*2\s*\])',event)[1]
after_pos=pos.replace(b"115",b"116").replace(b"34",b"37")
updated_event=event.replace(pos,after_pos,1)
updated_data=old_data[:offset]+chunk.replace(event,updated_event,1)+old_data[limit:]
expected=json.loads(old_data)
expected["M103"]["event"]["#4#"]["pos"]=[116,4,37,2]
assert json.loads(updated_data)==expected
assert json.loads(updated_data)["M103"]["event"]["#4#"]["mdlid"]=="EP328"
assert data.read_bytes()==old_data and code.read_bytes()==old_code
try:
    code.write_bytes(updated_code)
    data.write_bytes(updated_data)
except BaseException:
    if code.read_bytes()!=old_code:
        code.write_bytes(old_code)
    if data.read_bytes()!=old_data:
        data.write_bytes(old_data)
    raise
print("Kiyo is behind the soup counter. The only event change is position [116, 4, 37, 2].")
