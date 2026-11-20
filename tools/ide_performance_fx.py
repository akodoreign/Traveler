"""Draw the original heart and musical linework used by Ide's native performances."""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw


SIZE = 96
AA = 4
FRAME_COUNT = 8
PLUM = (77, 24, 64, 255)
ROSE = (249, 94, 140, 255)
CREAM = (255, 232, 207, 255)
GOLD = (255, 214, 130, 255)
PURPLE = (77, 45, 102, 255)


def cubic(start, control_a, control_b, end, count=32):
    points = []
    for i in range(count + 1):
        t = i / count
        u = 1.0 - t
        points.append(tuple(u**3 * a + 3 * u*u*t * b + 3*u*t*t*c + t**3 * d
                            for a, b, c, d in zip(start, control_a, control_b, end)))
    return points


def stroke(draw, points, color, width):
    if len(points) < 2:
        return
    scaled = [(round(x * AA), round(y * AA)) for x, y in points]
    draw.line(scaled, fill=color, width=round(width * AA), joint="curve")
    r = width * AA * .5
    for x, y in (scaled[0], scaled[-1]):
        draw.ellipse((x-r, y-r, x+r, y+r), fill=color)


def heart(index):
    image = Image.new("RGBA", (SIZE * AA, SIZE * AA))
    pencil = ImageDraw.Draw(image)
    line = (
        cubic((46, 28), (41, 13), (23, 11), (15, 25))
        + cubic((15, 25), (2, 45), (27, 62), (46, 82))
        + cubic((46, 82), (67, 67), (94, 48), (82, 26))
        + cubic((82, 26), (74, 10), (55, 15), (46, 28))
    )
    fraction = (.34, .69, .88, 1., 1., 1., 1., 1.)[index]
    trace = line[: max(2, int(len(line) * fraction))]
    stroke(pencil, trace, PLUM, 8.0)
    stroke(pencil, trace, ROSE, 5.2)
    stroke(pencil, trace, CREAM, 2.0)
    if 3 <= index < 7:
        stroke(pencil, [(12, 16), (8, 11)], ROSE, 2.4)
        stroke(pencil, [(82, 12), (86, 7)], ROSE, 2.4)
    return image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def song(index):
    image = Image.new("RGBA", (SIZE * AA, SIZE * AA))
    pencil = ImageDraw.Draw(image)
    lead = cubic((15, 70), (24, 72), (51, 47), (74, 51))
    tail = cubic((18, 76), (32, 72), (63, 56), (86, 58))
    fraction = (.34, .65, .86, 1., 1., 1., 1., 1.)[index]
    for line, offset in ((lead, 0), (tail, 3)):
        trace = line[: max(2, int(len(line) * fraction) - offset)]
        stroke(pencil, trace, PURPLE, 5.0)
        stroke(pencil, trace, GOLD, 2.2)
    for x, y, show in ((31, 58, 1), (53, 44, 2), (73, 35, 3)):
        if index < show:
            continue
        box = ((x-5)*AA, (y-3)*AA, (x+5)*AA, (y+4)*AA)
        pencil.ellipse(box, fill=PURPLE)
        pencil.ellipse(((x-3)*AA, (y-1)*AA, (x+3)*AA, (y+2)*AA), fill=GOLD)
        stroke(pencil, [(x+4, y), (x+4, y-17), (x+11, y-14)], PURPLE, 4.4)
        stroke(pencil, [(x+4, y), (x+4, y-17), (x+11, y-14)], GOLD, 2.2)
    return image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def strip(output, name, draw):
    sheet = Image.new("RGBA", (SIZE * FRAME_COUNT, SIZE))
    for index in range(FRAME_COUNT):
        sheet.paste(draw(index), (index * SIZE, 0))
    sheet.save(output / f"{name}.png")


def particle(output, name, life, width):
    shape = f'{{"axis":0,"r":0.0,"w":{width:.2f},"h":{width:.2f}}}'
    text = f'''// Ide's original hand-drawn billboard. The scene controller floats this group.
parentcoord <- false
currentgroup <- 0
prof <- {{"showbnd":[0,0,0,1,1,1],"maxbnd":[0,0,0,1,1,1],"showtime":{life},"wholebnd":[0,0,0,1,1,1]}}
groups <- [
    with ParticleGroupData(){{
        name = "{name}"
        enabled = true
        aimtype = 1
        localcoord = true
        emitter = with ParticleEmitter(){{
            num = 1
            start = 0, start_spr = 0
            life = {life}, life_spr = 0
            posx = 0.0, posy = 0.0, posz = 0.0
            dirx = 0.0, diry = 0.0, dirz = 0.0
            linearbits = 0
        }},
        shapetype = 0
        shapedata = {shape}
        texture = "/resource/efx/rt/{name}.png"
        color = 0xffffffff
        blendmode = 5
        blend = 1
        Ka = 0xffffffff
        Ks = 0
        mod = [
            {{"classid":"ptcmod_texanime","frame":[0,{FRAME_COUNT}]}},
            {{"color":[-1,-1,-1,-256],"classid":"ptcmod_color"}},
        ]
    }},
]
'''
    (output / f"{name}.ptd").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--song", action="store_true")
    args = parser.parse_args()
    args.directory.mkdir(parents=True, exist_ok=True)
    strip(args.directory, "ide_heart_listens", heart)
    particle(args.directory, "ide_heart_listens", 1050, 0.86)
    if args.song:
        strip(args.directory, "ide_song_kirin", song)
        particle(args.directory, "ide_song_kirin", 1100, 1.05)
