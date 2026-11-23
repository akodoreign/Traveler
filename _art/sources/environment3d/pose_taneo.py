"""Author a seated idle on the live 50-joint humanoid rig."""

import json
from pathlib import Path
import struct
import sys

import numpy as np
from scipy.spatial.transform import Rotation

HERE = Path(__file__).resolve().parent
REPO = Path(sys.argv[1])
sys.path.insert(0,str(REPO/"tools"))
from motfile import load

NATIVE = REPO / "_tools/rpgcobo-tool/project/resource/native_chara"
SCALE = .01125


def normalized(vec):
    return vec / np.linalg.norm(vec)


def solve_elbow(root, end, upper, lower, pole):
    delta = end-root
    distance = np.clip(np.linalg.norm(delta),abs(upper-lower)+.01,upper+lower-.01)
    unit = normalized(delta)
    x = (upper**2+distance**2-lower**2)/(2*distance)
    perpendicular = normalized(pole-unit*(pole@unit))
    return root+unit*x+perpendicular*np.sqrt(upper**2-x*x)


def aim_bone(bone, next_bone, start, end):
    rest = next_bone["bind"][3,:3]-bone["bind"][3,:3]
    target = normalized(end-start)*np.linalg.norm(rest)
    rotation, _ = Rotation.align_vectors([target], [rest])
    matrix = bone["bind"].copy()
    matrix[:3,:3] = matrix[:3,:3] @ rotation.as_matrix().T
    matrix[3,:3] = start
    return matrix


def bone_key(m):
    scale = np.linalg.norm(m[:3,:3],axis=1)
    if np.linalg.det(m[:3,:3]) < 0:
        scale[0] = -scale[0]
    quat = Rotation.from_matrix((m[:3,:3]/scale[:,None]).T).as_quat()[[3,0,1,2]]
    return (*m[3,:3],*scale,*quat)


def seat(parts):
    by_name = {bone["name"]:bone for bone in parts}
    by_id = {bone["id"]:bone for bone in parts}
    desired = {}
    frame = {}
    positions = {}
    for part in parts:
        name=part["name"]
        parent=part["parent"]
        rest=part["bind"]
        local=rest @ np.linalg.inv(by_id[parent]["bind"]) if parent>=0 else rest.copy()
        if name=="pelvis":
            local[3,:3]=[0.,37.,0.]
        if name.startswith("thigh"):
            side=name[-1]
            hip=(local @ frame[parent])[3,:3]
            shin,foot=(by_name[key+side] for key in ("shin","foot"))
            ankle=np.array([26.,6.55,hip[2]*1.34])
            upper=np.linalg.norm(shin["bind"][3,:3]-part["bind"][3,:3])
            lower=np.linalg.norm(foot["bind"][3,:3]-shin["bind"][3,:3])
            knee=solve_elbow(hip,ankle,upper,lower,np.array([1.,.38,0.]))
            desired[name]=aim_bone(part,shin,hip,knee)
            desired["shin"+side]=aim_bone(shin,foot,knee,ankle)
            desired["foot"+side]=foot["bind"].copy()
            desired["foot"+side][3,:3]=ankle
            positions[side]={"hip":hip.tolist(),"knee":knee.tolist(),"ankle":ankle.tolist()}
        if name.startswith("upper"):
            side=name[-1]
            shoulder=(local @ frame[parent])[3,:3]
            fore,hand=(by_name[key+side] for key in ("fore","hand"))
            hand_at=np.array([16.3,44.2,shoulder[2]*.72])
            upper=np.linalg.norm(fore["bind"][3,:3]-part["bind"][3,:3])
            lower=np.linalg.norm(hand["bind"][3,:3]-fore["bind"][3,:3])
            elbow=solve_elbow(shoulder,hand_at,upper,lower,np.array([-.45,-.40,np.sign(shoulder[2])]))
            desired[name]=aim_bone(part,fore,shoulder,elbow)
            desired["fore"+side]=aim_bone(fore,hand,elbow,hand_at)
        world=desired.get(name,local @ frame[parent] if parent>=0 else local)
        if name in desired:
            local=world @ np.linalg.inv(frame[parent]) if parent>=0 else world
        frame[part["id"]]=world
        yield part, bone_key(local), positions


def motion():
    parts=load(NATIVE/"motion_club.mot")["parts"]
    assert len(parts)==50
    out=bytearray(b"SMOT\0"+bytes([len(parts)]))
    for part, key, positions in seat(parts):
        name=part["name"].encode("latin-1")
        out+=struct.pack(">H",len(name))+name+bytes((part["id"],part["parent"]+1))
        pivot=part["pivot"]
        out+=bytes([bool(pivot)])
        if pivot:
            out+=struct.pack(">3f",*pivot)
        out+=struct.pack(">17f",*part["bind"].ravel(),part["length"])
        out+=struct.pack(">HHB10e",0,7,0,*key)+bytes([7])*7+bytes(4)
    out+=bytes(2)
    path=HERE/"native_environment/taneo_chair.mot"
    path.write_bytes(out)
    built=load(path)["parts"]
    assert len(built)==len(parts) and all(np.array_equal(a["bind"],b["bind"]) for a,b in zip(parts,built,strict=True))
    (HERE/"taneo-chair-fit.json").write_text(json.dumps({"joints":50,"setup":"coast stall seat","legs":positions},indent=2),
                                             encoding="utf-8")


if __name__=="__main__":
    motion()
