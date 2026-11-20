"""Silhouette drawings for the extended spells.

Each silhouette has the movement language of its spell. Lines are in a 128px
canvas so the same drawing remains identifiable through party-wide effects.
"""
import math

from PIL import Image, ImageDraw


def engraved(shape):
    mask = Image.new("L",(128,128))
    draw = ImageDraw.Draw(mask)
    def line(*points, width=3):
        draw.line(points,fill=255,width=width,joint="curve")
    def halo(x,y,rx,ry,start=0,end=359,width=3):
        draw.arc((x-rx,y-ry,x+rx,y+ry),start,end,fill=255,width=width)
    def poly(*points, width=3):
        line(*points,points[0],width=width)
    def ray(x,y,r,angle):
        a = math.radians(angle)
        dx,dy = r*math.cos(a),r*math.sin(a)
        line((x,y),(x+dx,y+dy),width=2)
    def sparks(x,y,r,count):
        for i in range(count):
            a = i*math.tau/count
            px,py = x+r*math.cos(a),y+r*math.sin(a)
            halo(px,py,2.5,2.5)
    def plume(x,y,s):
        line((x-s,y),(x-s*.7,y-s*.72),(x,y-s*.45),(x+s*.18,y-s*1.7),
             (x+s*.72,y-s*.85),(x+s,y-s*.22),(x+s*.8,y+s*.56),(x,y+s*.71),
             (x-s*.64,y+s*.53),(x-s,y),width=4)
    def blade(x,y,s,invert=False):
        d = -1 if invert else 1
        poly((x,y-s),(x+s*.24*d,y),(x+s*.58*d,y+s*.48),(x-s*.2*d,y+s*.17))
        line((x,y-s),(x+s*.05*d,y+s*.32),width=2)
    def leaf(x,y,s,d=1):
        draw.ellipse((x-s,y-s*.50,x+s,y+s*.53),outline=255,width=3)
        line((x-s*.80*d,y+s*.29),(x+s*.78*d,y-s*.33),width=2)
    def waves(x,y,lift,n):
        for j in range(n):
            pts = [(i,y+j*9+lift*math.sin((i-x)/12+j*.5)) for i in range(max(9,x-42),min(119,x+43))]
            line(*pts)
    def spiral(x,y,turns,d=1):
        line(*[(x+i*.37*math.cos(i*.075*d),y+i*.30*math.sin(i*.075*d))
               for i in range(int(turns*math.tau/.075))],width=4)

    match shape:
        case "well":
            halo(64,82,44,19); halo(64,82,29,11); rays = (15,55,95,135,175)
            for a in rays: ray(64,56,27,a)
        case "spring":
            for x,y,s in [(33,76,15),(64,46,13),(91,74,18)]: leaf(x,y,s)
            line((37,101),(62,75),(86,94))
        case "sunrise":
            halo(64,83,28,28,183,355,4); halo(64,83,45,43,190,349)
            line((16,83),(112,83)); line((28,92),(97,92))
        case "ember":
            plume(70,61,17); ray(53,68,20,154); ray(53,72,24,176)
        case "comet":
            plume(88,57,14)
            line((15,97),(56,70),(86,61),width=6)
            line((24,72),(54,61),(73,53))
        case "icicles":
            for x,y,s in [(34,56,18),(64,65,26),(93,53,20)]: blade(x,y,s,True)
            line((17,39),(106,39))
        case "sunwheel":
            halo(64,64,31,31,width=5); halo(64,64,23,23)
            for i in range(12):
                a=i*30
                ray(64+35*math.cos(math.radians(a)),64+35*math.sin(math.radians(a)),13,a+19)
        case "band":
            halo(64,57,49,16,0,359,4); halo(64,73,45,16,0,359,4)
            line((15,57),(18,73)); line((113,57),(109,75))
        case "shingles":
            for x,y in [(24,70),(47,54),(71,54),(98,70)]:
                poly((x-11,y-13),(x+11,y-13),(x+9,y+9),(x,y+16),(x-8,y+10))
        case "pennant":
            line((41,112),(50,18),width=5); poly((50,25),(86,20),(111,41),(80,52),(45,45))
        case "motes":
            sparks(64,65,37,8); sparks(64,65,20,5); halo(64,65,5,5)
        case "wings":
            for sign in (-1,1):
                for k in range(3):
                    line((64,80),(64+sign*(18+k*6),66-k*6),(64+sign*(37+k*6),43-k*5))
        case "thorn":
            for x,y in [(31,76),(63,62),(96,78)]:
                poly((x-12,y+15),(x,y-23),(x+12,y+14),(x,y+5))
        case "vortex":
            spiral(65,64,1.35); spiral(66,64,1.31,-1)
            halo(65,64,7,7)
        case "twins":
            halo(43,64,24,30,width=5); halo(84,64,24,30,width=5)
            line((41,64),(84,64),width=2)
        case "pulse":
            line((16,67),(37,67),(45,53),(54,84),(65,38),(75,73),(84,61),(111,61),width=6)
            halo(64,64,42,40,217,333,2)
        case "leaf":
            leaf(64,59,31); rays = [32,85,135]
            for a in rays: ray(63,76,28,a)
        case "frost":
            for i in range(6):
                a=60*i
                ray(64,64,37,a)
                b=math.radians(a)
                for j in (-38,38): ray(64+21*math.cos(b),64+21*math.sin(b),13,a+j)
        case "thread":
            line((37,91),(60,77),(76,61),(93,38),width=4)
            halo(31,94,12,10); halo(96,34,12,10)
            halo(64,72,39,22,2,151)
        case "steps":
            for x,y,w in [(29,84,18),(64,66,16),(94,47,13)]:
                poly((x-w,y+4),(x+w,y),(x+w,y+11),(x-w,y+13))
        case "crown":
            halo(64,72,48,24,0,359,4)
            for x,y,s in [(31,59,11),(64,46,14),(97,59,11)]: plume(x,y,s)
        case "sear":
            line((36,29),(56,48),(47,55),(68,66),(60,76),(85,97),width=6)
            halo(60,62,39,33,80,249)
        case "breath":
            for i in range(4):
                line((20,44+i*9),(43,39+i*12),(76,30+i*16),(113,24+i*22),width=7-i)
        case "cinders":
            for x,y,s in [(26,81,5),(47,51,6),(62,75,3),(86,63,5),(102,44,3),(79,96,5)]:
                poly((x-s,y),(x,y-s),(x+s,y),(x,y+s))
        case "coals":
            for x,y in [(31,84),(55,80),(82,78),(101,75)]:
                halo(x,y,12,8)
                halo(x,y-18,8,15,220,335)
        case "pillars":
            for x,y,s in [(32,79,10),(64,64,14),(95,78,10)]:
                plume(x,y,s); line((x,y+7),(x,y+22),width=5)
        case "cloven":
            line((42,27),(50,49),(62,55),(55,65),(82,83),(94,99),width=6)
            line((87,30),(76,50),(67,53)); line((56,67),(45,86),(28,103))
        case "veil":
            for i in range(4):
                line((23+i*12,28),(33+i*13,51),(26+i*14,91))
            halo(64,62,50,38,300,60,2)
        case "fogBank":
            waves(64,46,10,4)
        case "shutter":
            for i in range(6):
                x=23+i*16
                line((x,37),(x-10,67),(x,91),width=5)
            line((16,37),(112,37)); line((16,91),(112,91))
        case "fogCurl":
            spiral(57,60,1.25)
            halo(74,80,44,21,45,152)
        case "iris":
            line((13,65),(44,43),(64,40),(87,45),(115,65),(88,84),(55,88),(13,65),width=4)
            halo(64,64,16,18); halo(64,64,6,8)
        case "rune":
            poly((29,88),(55,23),(99,81))
            line((29,88),(90,63),(42,56),(80,33),(99,81),width=3)
        case "web":
            for i in range(7): ray(64,64,48,i*360/7)
            for r in (14,26,40): halo(64,64,r,r)
        case "knives":
            for x,y,s in [(27,71,15),(64,57,24),(99,82,12)]: blade(x,y,s,x>64)
        case "enclosure":
            for r in (24,34,44): halo(64,64,r,r,24+r,323-r)
            sparks(64,64,44,8)
        case "tiles":
            for i in range(2):
                for j in range(3):
                    x,y=29+33*j+(i*11),53+25*i
                    poly((x-13,y),(x+9,y-9),(x+19,y),(x-3,y+10))
        case "seven":
            sparks(64,64,42,7)
            for i in range(7): ray(64,64,25,i*360/7)
        case "basalt":
            for x,y,s in [(38,83,18),(68,70,25),(93,83,11)]:
                poly((x-s//2,y+12),(x-s,y-7),(x-s//2,y-s),(x+s//2,y-s),(x+s,y+8))
        case "fanLotus":
            for i in range(5):
                a=math.radians(28+i*31)
                x,y=64+40*math.cos(a),84-41*math.sin(a)
                leaf(x,y,9)
                line((64,93),(x,y),width=2)
        case "crest":
            poly((32,29),(96,29),(98,69),(64,105),(30,69),width=5)
            halo(64,62,21,18); halo(64,62,13,10)
        case "rubble":
            for i,(x,y) in enumerate([(31,74),(53,85),(61,51),(78,91),(96,67),(108,85)]):
                poly((x-8,y),(x,y-11+i),(x+9,y+2),(x,y+6))
        case "fault":
            line((16,77),(39,58),(45,68),(63,46),(67,59),(84,46),(110,52),width=5)
            line((45,68),(49,90),(63,99)); line((68,59),(89,84),(109,89))
        case "bars":
            for x in (25,43,64,85,103): line((x,36),(x,93),width=5)
            halo(64,35,47,17); halo(64,94,47,17)
        case "switchback":
            line((18,88),(55,67),(83,69),(62,59),(97,39),(110,40),width=5)
            line((104,56),(112,42),(98,32),width=3)
        case "scales":
            line((64,31),(64,102),(44,102),(84,102),width=4)
            line((24,49),(64,39),(104,49),width=4)
            for x in (24,104): halo(x,64,14,10,2,177)
        case "lotus":
            for i in range(7):
                a=math.radians(22+i*23)
                x,y=64+44*math.cos(a),79-34*math.sin(a)
                leaf(x,y,12)
            halo(64,81,47,17,0,177)
        case "root":
            line((63,37),(63,83),(52,94),(42,109),width=5)
            for d in (-1,1): line((64,53),(64+d*20,70),(64+d*46,91))
        case "hearth":
            plume(65,55,16); poly((30,75),(102,75),(92,95),(41,95))
        case "palm":
            poly((43,85),(35,68),(45,62),(48,38),(53,40),(54,58),(61,30),(68,32),(69,56),
                 (79,37),(86,41),(82,64),(101,59),(104,65),(86,83),(76,99),(53,96))
        case "screen":
            halo(64,66,46,41,213,327,5); halo(64,66,37,33,218,322,5)
            line((18,66),(23,90),(105,90),(110,66),width=3)
        case "spark":
            for i,r in enumerate((34,19,37,15,28,22,32,18)): ray(64,64,r,i*45)
            halo(64,64,6,6)
        case "rekindle":
            halo(64,77,40,14,0,178,4); plume(64,57,13); sparks(64,68,27,5)
        case _:
            raise ValueError(shape)
    return mask

