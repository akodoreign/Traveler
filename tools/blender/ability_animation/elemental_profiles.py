"""Second pass of the spell catalog, with an explicit choreography for each ID.

The gesture, line of action, hold/release timing, and effect silhouette are arranged
as a single move. A shared rig or a common element does not imply a shared pose.
"""
# id, phase, element, gesture, shape, reach, sink, lean, twist, set/gather/release/follow, size, travel
SPELLS = [
    ("S035", "use", "water", "offer", "well", .64,.11,9,6, (.17,.37,.60,.84), .64, 0),
    ("S040", "use", "jade", "brush", "spring", .58,.08,8,17, (.15,.33,.57,.84), .69, 0),
    ("S043", "use", "air", "raise", "sunrise", .83,.18,14,4, (.24,.46,.69,.87), .92, 0),
    ("S073", "attack", "fire", "tap", "ember", .58,.08,12,-7, (.14,.32,.47,.75), .65, 260),
    ("S074", "attack", "fire", "heave", "comet", 1.21,.22,19,-20, (.22,.52,.66,.89), 1.11, 400),
    ("S076", "attack", "ice", "pinch", "icicles", .78,.14,12,-13, (.18,.39,.56,.79), .76, 310),
    ("S138", "attack", "fire", "raise", "sunwheel", 1.12,.19,17,-19, (.18,.50,.66,.88), 1.22, 405),
    ("S154", "use", "water", "press", "band", .45,.10,8,6, (.15,.39,.62,.84), .61, 0),
    ("S155", "use", "earth", "ward", "shingles", .93,.18,12,-17, (.15,.51,.67,.83), .81, 0),
    ("S156", "use", "fire", "brandish", "pennant", .82,.16,15,16, (.22,.39,.55,.85), .86, 0),
    ("S157", "use", "lightning", "cup", "motes", .49,.10,7,-6, (.22,.40,.68,.90), .73, 0),
    ("S158", "use", "jade", "heave", "wings", .96,.15,14,8, (.17,.45,.64,.83), .82, 0),
    ("S159", "use", "shadow", "coil", "thorn", .61,.15,12,-21, (.20,.49,.66,.82), .76, 0),
    ("S302", "use", "void", "draw", "vortex", .70,.15,9,15, (.16,.39,.72,.89), .81, 0),
    ("S307", "use", "jade", "bridge", "twins", .84,.12,11,17, (.19,.40,.64,.91), .81, 0),
    ("S311", "use", "water", "press", "pulse", .52,.11,13,-11, (.21,.46,.62,.80), .72, 0),
    ("S312", "use", "jade", "cup", "leaf", .72,.16,8,9, (.24,.44,.63,.87), .80, 0),
    ("S313", "use", "ice", "armsAcross", "frost", .61,.15,12,-17, (.18,.37,.60,.90), .78, 0),
    ("S316", "use", "lightning", "reachBelow", "thread", .89,.19,17,15, (.17,.39,.64,.87), 1.02, 0),
    ("S328", "use", "fire", "pat", "steps", 1.02,.18,15,14, (.13,.32,.47,.79), .85, 0),
    ("S329", "use", "fire", "unfurl", "crown", 1.07,.15,12,-21, (.16,.39,.62,.83), .88, 0),
    ("S333", "use", "fire", "tap", "sear", .53,.08,17,8, (.25,.45,.60,.89), .72, 0),
    ("S335", "attack", "fire", "fan", "breath", 1.18,.18,18,-26, (.25,.48,.57,.85), 1.19, 405),
    ("S337", "use", "shadow", "plant", "cinders", .77,.21,19,-13, (.20,.43,.72,.88), .87, 0),
    ("S338", "use", "fire", "step", "coals", .86,.22,12,20, (.13,.44,.61,.85), .82, 0),
    ("S341", "attack", "fire", "brandish", "pillars", 1.22,.23,22,25, (.17,.43,.58,.81), 1.25, 390),
    ("S343", "use", "shadow", "claw", "cloven", .77,.15,14,-25, (.21,.38,.67,.88), .94, 0),
    ("S349", "use", "shadow", "hush", "veil", .60,.11,6,20, (.25,.41,.66,.90), .79, 0),
    ("S350", "use", "air", "unfurl", "fogBank", .97,.18,15,16, (.17,.44,.69,.86), .98, 0),
    ("S351", "use", "air", "armsAcross", "shutter", .47,.10,11,-11, (.19,.36,.56,.81), .73, 0),
    ("S352", "attack", "air", "heave", "fogCurl", .92,.22,17,-16, (.19,.49,.65,.89), 1.13, 400),
    ("S353", "use", "void", "inspect", "iris", .59,.13,12,9, (.25,.43,.67,.88), .77, 0),
    ("S354", "use", "air", "tracer", "rune", .92,.13,9,-19, (.18,.43,.62,.90), .87, 0),
    ("S356", "attack", "shadow", "claw", "web", .81,.18,18,17, (.20,.46,.59,.84), .86, 365),
    ("S358", "attack", "air", "chop", "knives", .85,.17,17,-29, (.15,.40,.52,.79), .96, 286),
    ("S365", "use", "lightning", "bridge", "enclosure", .89,.17,13,13, (.20,.46,.63,.83), .86, 0),
    ("S367", "use", "earth", "brace", "tiles", .64,.22,22,-8, (.21,.46,.72,.89), .90, 0),
    ("S368", "use", "lightning", "brandish", "seven", .98,.12,15,21, (.18,.40,.63,.84), 1.04, 0),
    ("S372", "use", "earth", "claw", "basalt", .73,.22,19,12, (.22,.44,.62,.82), .86, 0),
    ("S373", "use", "jade", "ward", "fanLotus", .80,.11,8,-9, (.20,.50,.67,.91), .84, 0),
    ("S376", "use", "lightning", "raise", "crest", 1.00,.20,18,-12, (.27,.49,.68,.85), 1.04, 0),
    ("S377", "use", "earth", "chop", "rubble", .92,.25,20,14, (.19,.43,.58,.83), .92, 0),
    ("S380", "use", "earth", "step", "fault", 1.04,.29,23,-17, (.16,.53,.67,.87), 1.18, 0),
    ("S381", "use", "earth", "seal", "bars", .72,.21,18,20, (.25,.46,.66,.86), .98, 0),
    ("S386", "use", "void", "tracer", "switchback", .90,.12,13,-23, (.16,.37,.58,.90), .82, 0),
    ("S387", "use", "void", "still", "scales", .59,.12,8,10, (.28,.52,.66,.90), .81, 0),
    ("S392", "use", "water", "unfurl", "lotus", .99,.14,14,21, (.18,.50,.67,.90), 1.04, 0),
    ("S461", "use", "jade", "reachBelow", "root", .73,.21,18,13, (.24,.43,.65,.86), .73, 0),
    ("S499", "use", "fire", "offer", "hearth", .67,.13,10,-12, (.18,.45,.68,.89), .81, 0),
    ("S537", "attack", "fire", "push", "palm", 1.12,.14,19,-22, (.15,.42,.51,.82), .90, 280),
    ("S538", "use", "fire", "ward", "screen", .77,.19,14,20, (.19,.34,.60,.81), .87, 0),
    ("S615", "attack", "fire", "pinch", "spark", .63,.08,7,10, (.16,.34,.48,.79), .67, 240),
    ("S616", "use", "fire", "cup", "rekindle", .58,.11,12,-15, (.25,.48,.65,.86), .72, 0),
]


def spell_profiles():
    return {
        sid: dict(phase=phase, element=element, gesture=gesture, shape=shape,
                  body=[reach,sink,lean,twist], beats=list(beats), mark=size,
                  **({"travel":travel} if travel else {}))
        for sid,phase,element,gesture,shape,reach,sink,lean,twist,beats,size,travel in SPELLS
    }

