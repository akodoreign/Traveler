"""Additional shape drawings for the physical, kata, and social effects."""
import math

from PIL import Image, ImageDraw

from elemental_marks import engraved


def school_mark(shape):
    canvas = Image.new("L",(128,128))
    draw = ImageDraw.Draw(canvas)
    def line(*points,width=4):
        draw.line(points,fill=255,width=width,joint="curve")
    def arc(cx,cy,rx,ry,begin,end,width=4):
        draw.arc((cx-rx,cy-ry,cx+rx,cy+ry),begin,end,fill=255,width=width)
    def oval(cx,cy,rx,ry,width=4):
        arc(cx,cy,rx,ry,0,359,width)
    def poly(*points,width=4):
        line(*points,points[0],width=width)

    match shape:
        case "crescent":
            arc(65,66,51,37,206,25,6); arc(59,58,42,28,212,26,3)
        case "blade":
            line((30,96),(102,29),(80,59),(36,102),width=5)
            line((23,77),(48,102),width=4)
        case "spearline":
            line((16,81),(99,55),width=7)
            poly((70,55),(113,51),(84,76),width=4)
        case "bands":
            arc(65,56,43,16,10,171,5); arc(65,73,39,16,10,172,5); arc(65,89,33,14,10,172,3)
        case "tracks":
            for x,y in [(23,83),(44,72),(68,60),(92,43)]:
                line((x,y-5),(x+11,y-5),(x+9,y+5),width=3)
        case "thorns":
            line((16,85),(42,45),(50,69),(68,22),(78,62),(103,46),(111,76),width=5)
        case "stillpoint":
            oval(64,64,31,31,4); oval(64,64,13,13,2); oval(64,64,5,5,6)
        case "linebreak":
            line((14,87),(48,68),(62,68),width=5)
            line((69,60),(83,59),(113,36),width=5)
            line((52,37),(74,92),width=3)
        case "orbit":
            arc(64,64,49,24,40,315,3); arc(64,64,34,48,20,297,3)
            oval(105,55,6,6,4); oval(45,20,5,5,2)
        case "coins":
            for x,y,r in [(31,82,10),(63,56,14),(95,67,10)]:
                oval(x,y,r,r,4); poly((x-3,y-3),(x+3,y-3),(x+3,y+3),(x-3,y+3),width=2)
        case "grit":
            for x,y,s in [(25,67,4),(39,49,4),(51,79,6),(70,65,4),(82,40,3),(106,66,7),(85,96,6)]:
                poly((x-s,y+3),(x-s//3,y-s),(x+s,y+1))
        case "boulder":
            poly((21,78),(41,43),(69,34),(96,42),(108,76),(80,96),(44,96))
            line((69,34),(66,55),(79,65),(80,96),(60,77),(32,82),width=3)
        case "venom":
            line((20,89),(36,48),(48,37),(61,56),(77,63),(91,48),(109,37),width=5)
            oval(75,79,8,12,3)
        case "dust":
            arc(39,74,23,18,190,347); arc(64,60,28,23,192,350); arc(97,74,18,18,174,347)
            line((18,80),(109,89),width=3)
        case "rings":
            for r in (16,30,45): oval(64,64,r,r//2,width=4)
        case "wall":
            line((17,38),(30,38),(30,54),(53,54),(53,38),(76,38),(76,54),(97,54),(97,38),(110,38),(110,91),(17,91),(17,38))
            line((17,74),(110,74)); line((42,54),(42,91)); line((84,54),(84,91))
        case "crossing":
            line((17,91),(109,36),width=6); line((33,31),(91,102),width=4)
        case "links":
            for j in range(4):
                x,y=(28+j*23,82-j*12)
                oval(x,y,13,8,4)
        case "needle":
            line((25,91),(107,35),width=4)
            line((79,48),(109,34),(89,57),width=3)
        case "reflection":
            poly((28,44),(98,35),(96,78),(30,87))
            line((31,52),(91,66)); line((46,44),(94,54),width=2)
            line((25,96),(103,88))
        case "burst":
            for i in range(8):
                a=math.pi*i/4
                x,y=math.cos(a),math.sin(a)
                line((64+17*x,64+17*y),(64+48*x,64+48*y),width=4)
            oval(64,64,9,9,4)
        case "doubleCut":
            line((27,96),(94,26),width=6); line((51,103),(110,45),width=4)
        case "shield":
            poly((64,21),(94,37),(93,76),(64,104),(34,76),(34,37),width=6)
            line((64,40),(64,82)); line((47,60),(82,60))
        case "clouds":
            for x,y,s in [(31,69,15),(57,59,20),(79,62,18),(100,70,14)]:
                arc(x,y,s,s,178,350,4)
            line((11,78),(116,78)); line((22,89),(97,89),width=3)
        case "dove":
            line((19,67),(43,70),(62,43),(77,36),(74,51),(96,60),(111,53),(97,76),(79,78),(59,92),(41,78),(19,67))
        case "supplies":
            poly((23,52),(64,36),(104,50),(105,87),(64,102),(23,85),width=4)
            line((23,52),(64,66),(104,50)); line((64,67),(64,102))
            line((44,43),(85,57),(85,95),width=3)
        case "telescope":
            poly((26,78),(89,44),(103,64),(39,96),width=4)
            oval(91,53,11,17,6); oval(91,53,5,10,2)
        case "vow":
            line((39,27),(39,83),(63,101),(89,83),(89,27),width=6)
            poly((53,59),(65,42),(76,60),(65,74))
        case "hook":
            line((36,22),(36,67),(51,91),(81,93),(96,78),(98,53),(83,60),width=5)
        case "blossom":
            for x,y in [(64,38),(86,54),(78,80),(50,80),(42,54)]:
                oval(x,y,12,11,3)
            oval(64,62,7,7,3)
        case "clawmarks":
            for x,y in [(24,93),(48,94),(72,83)]:
                line((x,y),(x+22,y-34),(x+46,y-66),width=5)
        case "lion":
            poly((29,64),(24,41),(43,41),(64,26),(85,41),(103,41),(99,65),(95,81),(76,101),(55,102),(34,83))
            line((41,56),(57,64),(63,77),(69,76),(74,63),(88,56),width=4)
        case "windcut":
            arc(61,63,50,31,201,30,6); arc(70,70,49,21,220,12,3)
        case "scree":
            for x,y,r in [(31,91,12),(52,78,13),(60,52,18),(83,82,11),(101,91,9)]:
                poly((x-r,y),(x,y-r),(x+r,y))
        case "firstLine":
            line((14,79),(103,51),width=5); line((43,86),(116,60),width=2)
            line((91,43),(99,63),width=3)
        case "perch":
            line((27,98),(100,98)); line((40,96),(76,74),(64,57),(80,33),(101,44),width=5)
        case "sky":
            arc(64,77,49,36,182,354,5); arc(64,77,34,24,184,355,3)
            line((64,21),(64,33)); line((17,61),(31,63)); line((99,63),(112,61))
        case "ripple" | "waves":
            for i in range(3):
                r=44-i*10
                arc(64,77-i*8,r,16+i*4,185,357,4)
            line((17,78),(112,78),width=2)
        case "plume" | "steam":
            for j in range(3):
                pts = [(39+j*24+9*math.sin((97-i)/11+j),i) for i in range(27,100)]
                line(*pts,width=3+j)
        case _:
            return engraved(shape)
    return canvas

