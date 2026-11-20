"""Draw the small visual vocabulary used by the ninety selectable Support calls."""
import math

from PIL import Image, ImageDraw

from school_marks import school_mark

# The arrow and spear cues encode the shape of each actual volley rather than
# relying on a color swap. Angles are around the center of the projected mark.
PROJECTILES = {
    "arrowRain":("arrow", (-30,0,30), .45, 19),
    "jadeArrows":("jade", (-12,12), .56, 24),
    "boardingPike":("hook", (-18,), .90, 0),
    "daikyu":("arrow", (-34,), 1.0, 0),
    "spearLine":("spear", (-14,), .76, 0),
    "hunterArrow":("arrow", (-13,), .72, 0),
    "crookedSpear":("hook", (20,), .76, 0),
    "matsuSpur":("spear", (-7,20), .54, 17),
    "harpoon":("hook", (12,), .86, 0),
    "cranePike":("spear", (-39,), .84, 0),
    "centipedeVolley":("arrow", (-26,-8,10,28), .42, 15),
    "horseBow":("arrow", (-8,14), .66, 20),
    "picket":("spear", (2,), .86, 0),
    "saddleVolley":("arrow", (25,-24,2), .48, 17),
    "sergeantThrust":("spear", (-6,-15), .76, 12),
    "ferryShot":("arrow", (16,), .78, 0),
    "bearArrow":("arrow", (-43,), .88, 0),
    "craterArrow":("arrow", (-57,-35), .52, 16),
    "hidaJade":("jade", (-32,), .96, 0),
}
WAVES = {
    "stormGust": (3,14,1.1,0), "tideBlessing": (4,8,.62,.4),
    "riverPrayer": (2,9,1.8,.1), "coolingRain": (5,8,2.6,.25),
    "rollingRiver": (4,12,1.7,.42), "iuchiTide": (4,15,1.2,1.0),
    "rememberedWind": (2,14,.92,.85), "craterWind": (3,19,1.45,1.15),
}
CUTS = {
    "lastCut": (1,-.48,.79), "wardCut": (2,.44,.74),
    "staffSweep": (2,-.26,.91), "porterSweep": (3,.34,.74),
    "templeStaff": (1,1.4,.81), "gatePost": (2,.82,.78),
    "noviceStaff": (1,.71,.59), "sweptClean": (3,.2,.78),
    "shadowCut": (2,-.72,.71), "twoSwords": (2,1.57,.88),
    "wakeStaff": (2,1.3,.64), "wideSweep": (3,-.69,.91),
    "laces": (1,.36,.87), "endlessStrike": (4,-.38,.71),
    "fathersTanto": (1,.69,.66),
}
FLOWERS = {
    "ginseng": (3,27,.55), "greenRibbon": (4,22,.9), "cleanse": (5,32,.26),
    "jadePrayer": (6,31,.1), "smallBlessing": (3,24,.31), "foxHerbs": (3,29,.8),
    "saltPoultice": (4,24,.68), "medicWrap": (4,27,.27), "midwifeRoot": (5,29,.35),
}
HALOS = {
    "lanternHalo": (3,41,.16), "ancestorHalo": (3,36,.45), "stormHalo": (2,43,.75),
    "memorial": (3,34,.9), "prayerBead": (1,34,0), "recall": (4,40,1.0),
    "warSong": (3,32,.72), "chorus": (3,39,.12), "lifeblood": (2,35,.71),
}
BURSTS = {
    "impact": (8,17,41,.18), "trollStone": (7,13,49,.46),
    "lampOil": (6,22,45,.83), "acolyteSpark": (5,15,38,.0),
    "jadeStrike": (6,12,49,.36), "agashaFlame": (5,16,48,.59),
    "powder": (9,19,49,.20), "hanabi": (12,21,43,.42),
    "jadeDust": (8,9,36,.73), "thunderclap": (6,4,49,.79),
}


def draw_support_mark(shape):
    mask = Image.new("L",(128,128))
    pen = ImageDraw.Draw(mask)
    def line(*v,width=4):
        pen.line(v,fill=255,width=width,joint="curve")
    def oval(x,y,rx,ry,width=3):
        pen.ellipse((x-rx,y-ry,x+rx,y+ry),outline=255,width=width)
    def around(x,y,a,r):
        return x+r*math.cos(a),y+r*math.sin(a)
    def poly(*pts,width=4):
        line(*pts,pts[0],width=width)
    def projectile(kind,x,y,theta,scale):
        angle = math.radians(theta)
        ux,uy = math.cos(angle)*scale,math.sin(angle)*scale
        def p(a,b):
            return x+a*ux-b*uy,y+a*uy+b*ux
        line(p(-44,0),p(35,0),width=4 if kind=="arrow" else 6)
        poly(p(22,-9),p(46,0),p(22,9),width=3)
        if kind=="arrow":
            line(p(-45,-8),p(-30,0),p(-45,8),width=3)
        elif kind=="jade":
            poly(p(30,-14),p(46,0),p(26,13),p(17,0),width=3)
        elif kind=="hook":
            line(p(28,-12),p(19,-8),p(24,-4),width=4)

    if shape in PROJECTILES:
        kind,angles,scale,spacing = PROJECTILES[shape]
        for i,a in enumerate(angles):
            offset = i-(len(angles)-1)/2
            projectile(kind,64+offset*spacing*.4,64+offset*spacing,a,scale)
    elif shape in WAVES:
        rows,height,cycles,phase = WAVES[shape]
        for row in range(rows):
            line(*[(x,50+row*11+height*math.sin((x-24)*cycles/25+phase+row*.7))
                   for x in range(19,110)],width=5-row%3)
    elif shape in CUTS:
        count,tilt,reach = CUTS[shape]
        for i in range(count):
            a=tilt+i*.37
            tip=around(65,65,a,47*reach)
            tail=around(65,65,a+math.pi,45*reach)
            bend=around(65,65,a+math.pi/2,6+i*8)
            line(tail,bend,tip,width=6-i%3)
    elif shape in FLOWERS:
        count,r,seed = FLOWERS[shape]
        for i in range(count):
            x,y=around(64,62,(i/count+seed)*math.tau,r)
            oval(x,y,10+i%3,7+i%4,3)
            line((64,94),(64,68),(x,y),width=2)
    elif shape in HALOS:
        count,r,phase=HALOS[shape]
        for i in range(count):
            oval(64,61+i*4,r-i*9,r-8-i*7,4)
        for i in range(count+3):
            x,y=around(64,63,(i/(count+3)+phase)*math.tau,r+7)
            oval(x,y,3,3)
    elif shape in BURSTS:
        count,core,r,phase = BURSTS[shape]
        for i in range(count):
            a=(i/count+phase)*math.tau
            p=around(64,64,a,core)
            q=around(64,64,a+(i%2-.5)*.17,r-i%3*3)
            line(p,q,width=5-i%3)
        oval(64,64,max(4,core*.45),max(4,core*.36),3)
    else:
        match shape:
            case "letter" | "blankScroll":
                poly((27,39),(100,39),(100,89),(27,89),width=5)
                if shape=="letter":
                    line((28,40),(64,69),(99,40),width=4)
                    line((28,88),(55,63)); line((100,88),(76,63))
                else:
                    oval(27,64,9,28,4); oval(102,64,8,28,4)
            case "barricade":
                for x in (24,43,62,81,100): line((x,88),(x,37-(x%12)),width=5)
                line((20,54),(108,80)); line((20,79),(108,54))
            case "net":
                poly((22,31),(105,40),(97,94),(39,103),width=4)
                for i in range(4):
                    line((28+i*17,35),(44+i*16,99),width=3)
                    line((29+i*2,47+i*13),(102-i*2,48+i*13),width=3)
            case "roller":
                oval(44,64,22,25,5); oval(79,61,24,29,5)
                for i in range(4): line((43,41+i*15),(79,34+i*17),width=4)
            case "lanterns":
                for x,y in [(43,56),(86,72)]:
                    oval(x,y,15,21,5); line((x-9,y-19),(x+9,y-19)); line((x,y+21),(x,y+30))
            case "evidence":
                oval(57,57,28,28,5)
                line((73,78),(96,104),width=7); line((43,55),(51,66),(69,50),width=4)
            case "battleJoy":
                poly((24,79),(44,42),(63,56),(83,31),(105,72),(93,94),(44,98),width=5)
                line((42,80),(61,88),(86,78),width=3)
            case "paperFan":
                pen.arc((18,28,109,110),194,343,fill=255,width=5)
                for x in (21,39,58,77,106): line((x,44+abs(61-x)*.23),(62,100),width=3)
            case "deathMask":
                poly((33,35),(48,26),(83,28),(98,41),(93,83),(64,103),(38,84),width=5)
                line((45,53),(57,57)); line((72,57),(86,51)); line((49,78),(79,76),width=3)
            case "shrineTea":
                oval(63,69,32,10,4); line((31,68),(39,94),(87,94),(95,69),width=4)
                for x in (42,62,82): line((x,56),(x+4,40),(x-1,28),width=3)
            case "mirrors":
                poly((22,46),(47,25),(67,56),(42,86))
                poly((67,65),(89,39),(111,82),(84,98))
                line((39,51),(55,62),width=3); line((83,61),(99,75),width=3)
            case "shuriken":
                poly((65,21),(77,50),(111,56),(81,73),(77,107),(55,84),(20,91),(39,63),(27,31),(56,43),width=4)
                oval(63,64,9,9,3)
            case _:
                return school_mark(shape)
    return mask

