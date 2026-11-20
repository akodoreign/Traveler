"""Transparent two-mark decal sheets for Traveler's native wearable items."""
import math

LAYOUT = (128, 64)
SIZE = (256, 128)
SCALE = 4


def draw_mark(draw, clan, cx, cy, radius, ink, highlight):
    """Draw a clan emblem or the stitch mark used by unaffiliated wearers."""
    def point(p):
        return (round((cx + p[0] * radius) * SCALE), round((cy + p[1] * radius) * SCALE))

    def line(points, colour=ink, width=.13):
        draw.line([point(p) for p in points], fill=colour,
                  width=max(1, round(width * radius * SCALE)), joint="curve")

    def poly(points, colour=ink):
        draw.polygon([point(p) for p in points], fill=colour)

    def disc(x, y, r, colour=ink):
        draw.ellipse([point((x - r, y - r)), point((x + r, y + r))], fill=colour)

    if clan == "crab":
        poly([(-.43, .05), (-.23, -.23), (.23, -.23), (.43, .05), (.29, .32), (-.29, .32)])
        for s in (-1, 1):
            line([(s*.24, .13), (s*.58, -.12), (s*.66, -.47)], width=.19)
            poly([(s*.53, -.43), (s*.50, -.75), (s*.77, -.91), (s*.89, -.58),
                  (s*.78, -.36), (s*.65, -.55)])
            for y in (.02, .2, .36):
                line([(s*.29, y), (s*.57, y + .05), (s*.67, y + .21)])
        disc(0, -.06, .09, highlight)
    elif clan == "crane":
        poly([(-.14, .30), (-.94, -.57), (-.52, -.43), (-.15, -.16), (0, .07),
              (.25, -.42), (.89, -.64), (.52, -.29), (.21, .28), (.14, .5), (-.15, .55)])
        line([(.07, .31), (.29, .04), (.33, -.36), (.51, -.57), (.67, -.52)], width=.12)
        line([(-.05, .46), (-.34, .72), (-.64, .77)], width=.11)
        disc(.53, -.56, .055, highlight)
    elif clan == "dragon":
        spiral = [(math.cos(a) * r, math.sin(a) * r) for i in range(40)
                  for a, r in [(i * .185 - .7, .79 - .55 * i / 39)]]
        line(spiral, width=.19)
        x, y = spiral[0]
        poly([(x-.13, y+.17), (x-.07, y-.26), (x+.11, y-.40),
              (x+.13, y-.19), (x+.34, y-.13), (x+.37, y+.04), (x+.10, y+.10)])
        disc(x+.14, y-.12, .05, highlight)
        line([(-.56, -.16), (-.83, -.37), (-.89, -.20)], width=.11)
    elif clan == "lion":
        poly([(math.cos(i*math.pi/8)*(.84 if i%2 == 0 else .63),
               math.sin(i*math.pi/8)*(.84 if i%2 == 0 else .63)) for i in range(16)])
        poly([(-.41, -.41), (-.23, -.27), (.24, -.27), (.43, -.42), (.42, .17),
              (.26, .47), (-.26, .47), (-.43, .17)], highlight)
        line([(-.25, .01), (-.12, .01)], width=.10)
        line([(.12, .01), (.25, .01)], width=.10)
        poly([(-.13, .16), (.13, .16), (0, .33)])
    elif clan == "phoenix":
        for s in (-1, 1):
            poly([(0, .34), (s*.44, .21), (s*.83, -.42), (s*.88, -.77), (s*.66, -.37),
                  (s*.29, -.47), (s*.37, -.13), (s*.12, .03)])
        poly([(-.20, .22), (0, -.53), (.20, .22), (0, .88)])
        poly([(-.11, -.38), (.06, -.84), (.26, -.66), (.05, -.61)])
        line([(-.36, .37), (0, .73), (.36, .37)], highlight, .09)
    elif clan == "scorpion":
        line([(0, .34), (-.23, .14), (-.22, -.25), (-.05, -.57), (.31, -.72), (.53, -.57)], width=.17)
        poly([(.48, -.64), (.78, -.44), (.46, -.35)])
        disc(0, .31, .25)
        for s in (-1, 1):
            line([(s*.14, .3), (s*.55, .23), (s*.72, .01)], width=.15)
            poly([(s*.60, .06), (s*.51, -.26), (s*.77, -.10), (s*.87, -.24),
                  (s*.88, .04), (s*.69, .21)])
        line([(-.1,.35),(.15,.35)], highlight, .09)
    elif clan == "unicorn":
        poly([(-.55,.68), (-.32,.09), (-.44,-.51), (-.21,-.43), (.06,-.56),
              (.23,-.72), (.19,-.39), (.71,.0), (.61,.28), (.30,.22), (.1,.10), (.31,.64)])
        poly([(.28,-.46), (.77,-.91), (.51,-.28)])
        disc(.23, -.25, .065, highlight)
        line([(-.2,-.34), (-.12,.01), (-.27,.41)], highlight, .09)
    elif clan == "imperial":
        for i in range(12):
            a = math.tau * i / 12
            line([(.21*math.cos(a),.21*math.sin(a)), (.72*math.cos(a),.72*math.sin(a))], width=.18)
            disc(.69*math.cos(a), .69*math.sin(a), .12)
        disc(0, 0, .20, highlight)
    elif clan == "mantis":
        poly([(0,-.69),(-.19,-.47),(0,-.16),(.19,-.47)])
        poly([(0,-.25),(-.17,.31),(0,.75),(.17,.31)])
        for s in (-1, 1):
            line([(0,.09),(s*.42,-.17),(s*.65,-.70),(s*.89,-.26),(s*.73,.07)], width=.15)
            line([(s*.08,.27),(s*.54,.4),(s*.66,.64)])
        disc(0, -.47, .055, highlight)
    else:
        # The existing game gives independent wearers no clan mon.
        stitches = {
            "ronin": [(-.69,.27),(-.23,-.27),(.22,.23),(.69,-.27)],
            "peasant": [(-.61,-.38),(-.36,.4),(0,-.43),(.36,.4),(.61,-.38)],
            "eta": [(-.61,.34),(-.21,-.34),(.21,.34),(.61,-.34)],
        }
        line(stitches[clan], width=.17)
        for x, y in stitches[clan]:
            disc(x, y, .10, highlight)


def sheet(destination, clan, palette, item, slot, style):
    from PIL import Image, ImageDraw

    image = Image.new("RGBA", tuple(n * SCALE for n in LAYOUT))
    draw = ImageDraw.Draw(image)
    top, _, accent, armor, lace = palette
    bright = sum((armor if slot == "head" or style in ("lamellar", "plate") else top)) / 3 > 145
    ink = (29, 29, 43, 255) if bright else (249, 226, 172, 255)
    contrast = (*accent, 255) if bright else (*lace, 255)
    hard = style in ("lamellar", "plate", "jingasa", "guard", "scout", "kabuto", "legion", "iron", "jade")
    item_number = int(item[1:])
    edge_ink = (95, 69, 54, 255) if bright else (203, 162, 112, 255)
    for tile, radius in ((0, 22), (1, 22)):
        cx, cy = 32 + 64 * tile, 32
        r = 27 if tile == 0 else 22
        box = tuple(round(v * SCALE) for v in (cx-r, cy-r, cx+r, cy+r))
        if hard:
            draw.ellipse(box, outline=ink, width=round((1.8 if tile == 0 else 1.3) * SCALE))
            lip = tuple(round(v * SCALE) for v in (cx-r+2.2, cy-r+2.2, cx+r-2.2, cy+r-2.2))
            draw.arc(lip, 203, 340, fill=contrast, width=round(.75 * SCALE))
            draw.arc(lip, 28, 155, fill=edge_ink, width=round(.7 * SCALE))
        elif clan not in ("eta", "peasant", "ronin") and tile == 0:
            draw.arc(box, 32, 148, fill=ink, width=SCALE)
            draw.arc(box, 212, 328, fill=ink, width=SCALE)
            sewn = tuple(round(v * SCALE) for v in (cx-r+2, cy-r+2, cx+r-2, cy+r-2))
            for angle in range(0, 360, 15):
                draw.arc(sewn, angle, angle + 5, fill=contrast, width=round(.7 * SCALE))
        if tile == 0:
            # The ring of rivets or stitches distinguishes equipment with the same badge.
            for bit in range(8):
                if not (item_number & (1 << bit)):
                    continue
                a = math.tau * bit / 8
                x, y = (cx + 29.25 * math.cos(a)) * SCALE, (cy + 29.25 * math.sin(a)) * SCALE
                dot = 1.2 * SCALE
                draw.ellipse((x-dot, y-dot, x+dot, y+dot), fill=edge_ink)
        draw_mark(draw, clan, cx, cy, radius, ink, contrast)
    image.resize(SIZE, Image.Resampling.LANCZOS).save(destination, optimize=True)
