"""Author one cross-channel glacial river strip with a 64-phase gentle flow."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


WIDTH, HEIGHT, PHASES = 1024, 256, 64
TAU = np.float32(2.0 * np.pi)
Y, X = np.meshgrid(
    np.linspace(0., 1., HEIGHT, dtype=np.float32),
    np.arange(WIDTH, dtype=np.float32)/WIDTH,
    indexing="ij",
)


def smooth(start, stop, value):
    t = np.clip((value-start)/(stop-start), 0., 1.)
    return t*t*(3.-2.*t)


def ease(low, high, weight):
    return low + (high-low)*weight


def rgb(color):
    return np.array(color, dtype=np.float32)


def wave(phase):
    return np.sin(TAU*phase)


def periodic_noise(cols, rows, seed):
    """Smooth value noise that wraps only along the river's length."""
    rng = np.random.default_rng(seed)
    field = rng.uniform(0.,1.,(rows+1,cols)).astype(np.float32)
    u = X*cols
    v = Y*rows
    ix, iy = np.floor(u).astype(int), np.floor(v).astype(int)
    tx, ty = u-ix, v-iy
    tx, ty = tx*tx*(3-2*tx), ty*ty*(3-2*ty)
    right, below = (ix+1)%cols, np.minimum(iy+1,rows)
    top = ease(field[iy,ix],field[iy,right],tx)
    bottom = ease(field[below,ix],field[below,right],tx)
    return ease(top,bottom,ty).astype(np.float32)


def bank_stones(shelf, detail):
    """Build individually graded rounded stones in the shallows."""
    rng = np.random.default_rng(680219)
    colors = ((110,91,58),(142,115,76),(104,95,70),(72,92,61),
              (128,108,81),(67,80,54),(144,123,91),(86,103,76))
    ground = np.zeros((HEIGHT,WIDTH,3),dtype=np.float32)
    visible = np.zeros((HEIGHT,WIDTH),dtype=np.float32)
    for i in range(178):
        x = rng.uniform(0.,1.)
        y = .64+.38*rng.beta(2.0,1.18)
        width = rng.uniform(.0035,.0185)
        height = width*rng.uniform(1.2,2.1)
        rotation = rng.uniform(-.75,.75)
        reach = 1.67
        first_x = int(np.floor((x-reach*width)*WIDTH))
        last_x = int(np.ceil((x+reach*width)*WIDTH))+1
        first_y = int(np.clip(np.floor((y-reach*height)*(HEIGHT-1)),0,HEIGHT-1))
        last_y = int(np.clip(np.ceil((y+reach*height)*(HEIGHT-1))+1,1,HEIGHT))
        xgrid = np.arange(first_x,last_x)
        ygrid = np.arange(first_y,last_y)
        col = xgrid%WIDTH
        shape = np.ix_(ygrid,col)
        dx = (xgrid[None,:]/WIDTH-x)/width
        dy = (ygrid[:,None]/(HEIGHT-1)-y)/height
        a,b = np.cos(rotation)*dx-np.sin(rotation)*dy, np.sin(rotation)*dx+np.cos(rotation)*dy
        bump = .095*np.cos(2.6*a+2.3*b+i)
        radius = np.sqrt(a*a+b*b)+bump
        mask = (1.-smooth(.78,1.12,radius)) * smooth(.43,.91,shelf[shape]) * rng.uniform(.47,.94)
        crown = np.clip(1.-radius,0.,1.)
        face_light = 1.+.38*crown-.20*smooth(.05,1.1,a+.61*b)
        color = rgb(colors[i%len(colors)])[None,None,:]*face_light[:,:,None]
        color += ((detail[shape]-.5)*14.)[:,:,None]
        former = visible[shape]
        union = former+(1.-former)*mask
        numerator = ground[shape]*former[:,:,None]*(1.-mask[:,:,None])+color*mask[:,:,None]
        ground[shape] = numerator/np.maximum(union[:,:,None],.0001)
        visible[shape] = union
    return ground,visible


BROAD = periodic_noise(4,4,3391)
MID = periodic_noise(11,12,2027)
FINE = periodic_noise(65,42,9906)
LACE = periodic_noise(34,26,2018)
WARP = periodic_noise(10,9,6378)

# Cross-channel shading follows the depth from navy center to turquoise bank.
# Alongshore variation breaks the contours into long patches.
BANK = np.clip(Y + (.13*(BROAD-.5)+.065*(MID-.5))*smooth(.34,.84,Y),0.,1.)
LIGHT = smooth(.10,.85,BANK)
SHOAL = smooth(.59,.99,BANK)
PALE = smooth(.78,1.,BANK)
BED = rgb((4,14,60)) + LIGHT[...,None]*rgb((10,69,77))
BED += SHOAL[...,None]*rgb((22,31,1))
BED += PALE[...,None]*rgb((21,10,-20))
BED += (.58*(BROAD-.5)+.28*(MID-.5)+.14*(FINE-.5))[...,None]*rgb((21,25,23))
ROCK,MASK = bank_stones(BANK,FINE)
FILTERED_ROCK = ROCK*.62 + rgb((15,109,126))*.38
BED += (MASK*(.25+.68*SHOAL))[...,None]*(FILTERED_ROCK-BED)
BED = BED.astype(np.float32)


def frame(phase: int) -> np.ndarray:
    """Return a looping uint8 RGB frame, deep edge first and shore edge last."""
    t = np.float32((phase % PHASES)/PHASES)
    # Multiple wavelengths drift gently downstream over one 17.8-second cycle.
    # Sampling fixed submerged shapes with the small ripple offsets gives them
    # the look of depth while their world positions stay registered.
    warp = .8*(WARP-.5)+.27*(MID-.5)
    roll = .54*wave(15*X+7*Y+warp-t)
    roll += .27*wave(23*X-13*Y-.36*warp-t)
    roll += .19*wave(31*X+18*Y+.59*warp-2*t)
    y_ref = np.clip(Y + .0042*roll*LIGHT,0.,1.)*(HEIGHT-1)
    lo = np.floor(y_ref).astype(int)
    hi = np.minimum(lo+1, HEIGHT-1)
    xcol = np.broadcast_to(np.arange(WIDTH), Y.shape)
    water = ease(BED[lo,xcol],BED[hi,xcol],(y_ref-lo)[...,None])
    water += (roll*(.23+.77*LIGHT))[...,None]*rgb((3.2,5.1,7.5))

    # The broad glacial wash stays transparent-looking over the visible stones.
    haze = LIGHT*.12 + SHOAL*.06 + .021*wave(7*X-3*Y+.28*warp-t)
    cap = rgb((10,72,128))+SHOAL[...,None]*rgb((37,76,38))
    water += haze[...,None]*(cap-water)

    # Irregular low-coverage surface fragments catch a pale edge. The noise
    # weakens the crests in patches instead of stamping shape silhouettes.
    detail = .49*wave(32*X+23*Y+1.2*warp-t)
    detail += .31*wave(27*X-16*Y+.86*(MID-.5)-t)
    detail += .20*wave(52*X+28*Y+.69*(LACE-.5)-2*t)
    breaks = .62*LACE+.24*MID+.14*FINE
    foam = smooth(.44,.95,detail)*smooth(.52,.78,breaks)
    foam *= .27+.73*smooth(.33,.93,BANK)
    wash = smooth(.32,.78,detail)*smooth(.43,.75,breaks)*(.27+.73*LIGHT)
    water += wash[...,None]*rgb((7,12,13))
    water += foam[...,None]*rgb((57,73,66))
    return np.rint(np.clip(water,0,255)).astype(np.uint8)


def preview(path: Path):
    canvas=Image.new("RGB",(950,445),"#16222b")
    draw=ImageDraw.Draw(canvas)
    draw.text((11,9),"Winter river material   |   Deep navy at top. Shallow glacial blue and tawny stones below.",fill="white")
    for row, phase in enumerate((0,21,42)):
        image=Image.fromarray(frame(phase)).resize((900,112),Image.Resampling.LANCZOS)
        canvas.paste(image,(12,39+row*128))
        draw.text((919,47+row*128),f"{phase:02d}",fill="white")
    canvas.save(path,quality=95)


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("preview",type=Path)
    args=p.parse_args()
    preview(args.preview)
