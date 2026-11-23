"""A high-water counterpart to M212, connected by the manual tide choice."""


def tidal_bridge_banks(m):
    for left,width in ((0,8),(112,8)):
        m.rect(left,0,width,36,SAND,2)
    for z in (7,24):
        m.rect(8,z,2,4,SAND,2)
        m.rect(110,z+1,2,4,SAND,2)


def tide_submerged():
    m = MapSpec("M236","The land-bridge - high tide",120,36,base=WATER,y=2)
    tidal_bridge_banks(m)
    ev = Events(m)
    ev.portal(1,16,"M210",2,d=1)
    ev.portal(118,16,"M213",1,d=3)
    for x, shore, landing, retreat in ((6,"Crab",6,-1.5),(113,"Crane",113,1.5)):
        enter = go("M212",landing,16)
        ev.talk(x,16,"CE000",[(None,[
            narrate("The causeway to the %s side is under water." % shore),
            choices(("Wait for low tide.",[
                if_([flag("G363")],
                    [narrate("The Tide Chart says low water within the hour. Rensei waits on the bridgehead.")],
                    [narrate("Rensei waits on the bridgehead until the sand shows.")]),
                setf("G376"),enter,
            ]),("Not now.",[step_back(retreat,0)])),
        ])],trigger=5)
    return m,ev
