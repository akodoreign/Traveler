"""Install the optional position animation for fish on the garden pond."""

from pathlib import Path
import sys

from shadowlands_march_worlds import overwrite


def install(profile):
    path=profile/"project/plugin/rokugan/RokuganEnvironmentKit.sk"
    original=path.read_bytes()
    if b"pondFish = null;" in original:
        return
    eol=b"\r\n" if b"\r\n" in original else b"\n"
    code=original.replace(b"\r\n",b"\n")
    insertions=(
        (b"    vegetation = null;\n",b"    pondFish = null;\n"),
        (b"        vegetation = [];\n",b"""        pondFish = [];
        foreach(row in def["pondFish"] || []){
            local fish=add(row[0],row[1],row[2],row[3],row[4],row[8]);
            pondFish.append([fish,row]);
        }
"""),
        (b"        seconds += dt * .001;\n",b"""        foreach(pair in pondFish){
            local fish=pair[0], row=pair[1];
            local a=seconds*row[7]+row[8], sway=Math.sin(a*8.0);
            fish.pos(row[1]+Math.cos(a)*row[5],row[2]+.012*sway,row[3]+Math.sin(a)*row[6]);
            fish.rot.setHPB(a+.09*sway,0.,.025*sway);
            fish.matdirty=true;
        }
"""),
    )
    for mark, addition in insertions:
        if code.count(mark)!=1:
            raise RuntimeError(f"Cannot locate the pond hook in {path}")
        code=code.replace(mark,mark+addition)
    if path.read_bytes()!=original:
        raise RuntimeError(f"The environment runtime changed during install in {profile}")
    overwrite(path,code.replace(b"\n",eol))


if __name__=="__main__":
    install(Path(sys.argv[1]).resolve())
