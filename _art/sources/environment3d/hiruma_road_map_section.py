"""Physical uphill trail and brush reveal for the postgame Hiruma road."""

HIRUMA_TRAIL = ((0,16,3),(11,16,3),(21,9,3),(34,10,3),(42,31,4),
                (57,44,4),(68,33,5),(76,15,5),(88,15,6),(95,28,7),
                (99,38,8),(112,43,9))
HIRUMA_SPURS = (((25,10,3),(26,6,3)),((71,26,5),(70,24,5)),
                ((98,35,8),(94,34,8)))


def hiruma_road_terrain(m):
    z,x = np.indices((m.d,m.w))
    ridge = 3 + (x>=84) + (x>=96) + (z>=43)
    ridge = ridge.astype(np.int32)
    rough = np.sin(x*.18 + z*.27)+.61*np.cos(z*.49-x*.34)+.31*np.sin(x*.77+z*.65)
    m.hgt[:] = ridge + (rough>.73) - (rough<-.89)
    m.blk[:] = np.where(rough>.28,SL_ASH,SL_GROUND)
    dist = np.full((m.d,m.w),999.,dtype=float)
    slope = np.zeros_like(dist)
    for path in (HIRUMA_TRAIL,*HIRUMA_SPURS):
        for (ax,az,ah),(bx,bz,bh) in zip(path,path[1:]):
            dx,dz = bx-ax,bz-az
            t = np.clip(((x-ax)*dx+(z-az)*dz)/(dx*dx+dz*dz),0.,1.)
            gap = (x-ax-t*dx)**2+(z-az-t*dz)**2
            closer = gap<dist
            slope[closer] = (ah+t*(bh-ah))[closer]
            dist[closer] = gap[closer]
    for bx,bz,sx,sz,tile in (
        (16,33,12,13,TARSTAIN),(37,23,5,9,POPPYF),(61,13,10,8,POPPYF),
        (78,39,10,11,TARSTAIN),(97,8,8,7,POPPYF),
    ):
        spot = ((x-bx)/sx)**2+((z-bz)/sz)**2<1+.13*rough
        m.blk[spot & (dist>13)] = tile
    # The high banks make the bends real, with room to explore on the low side.
    ridges = ((32,26,5.5,12,5),(53,21,7,9,5),(64,47,6,6,5),
              (75,34,4,11,5),(86,27,5,12,6),(106,28,4,9,5))
    for bx,bz,sx,sz,height in ridges:
        mask = ((x-bx)/sx)**2+((z-bz)/sz)**2<1+.14*rough
        mask &= dist>11
        m.hgt[mask] += height
        m.blk[mask] = STONE
    near = dist<22
    runway = dist<=8
    shoulder = np.rint(slope + np.clip((np.sqrt(dist)-2.8)*.55,0.,1.0))
    m.hgt[near] = shoulder[near]
    m.hgt[runway] = np.rint(slope[runway])
    m.blk[runway] = ROAD
    m.blk[near & ~runway] = SL_ASH
    m.hgt[0:5,0:5] = 3


def deep_road_3():
    m = MapSpec("M460","Shadowlands deep - the Hiruma road",112,54,base=SL_GROUND,y=3)
    hiruma_road_terrain(m)
    ev = Events(m)
    ev.talk(1,16,"CE000",[(None,[go("M458",106,16)])],trigger=5)
    ev.chest(26,6,"I130",3)
    ev.chest(70,24,"I131",3)
    waystone(m,ev,94,34)
    ev.talk(108,42,"CE000",[
        (None,[narrate("The trail rises into a wall of thorns. Natsuko pushes the branches apart."),
               setf("G1215"),
               narrate("Beyond the brush, a narrow climb. On the crest, the broken walls of a castle."),
               say("Natsuko","(very quietly) ...That's on Father's map."),
               choices(("Go on, to the castle.",DARK+[go("M461",5,16)]),
                       ("Not yet.",[step_back(-2.0,0)]))]),
        ([flag("G1215")],[choices(("On to Shiro Hiruma.",[go("M461",5,16)]),
                                  ("Not yet.",[step_back(-2.0,0)]))]),
    ],trigger=5)
    return m,ev
