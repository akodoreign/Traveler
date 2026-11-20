"""Choreography for Support commands, performed by the calling Traveler."""
# ID, body cue, summoned mark, palette, release beat, effect size, shot duration
CALLS = [
    ("S143","command","spearline","lightning",.54,1.03,380),
    ("S144","cover","enclosure","void",.65,.89,0),
    ("S145","accuse","letter","shade",.58,.80,0),
    ("S146","veil","blankScroll","steel",.66,.84,0),
    ("S173","command","arrowRain","steel",.52,.96,414),
    ("S174","raise","basalt","earth",.65,1.01,360),
    ("S175","brace","barricade","wood",.69,1.04,0),
    ("S176","serve","ginseng","jade",.62,.78,0),
    ("S177","bridge","net","water",.63,.91,370),
    ("S178","hammer","impact","earth",.61,1.03,0),
    ("S183","crush","scree","earth",.66,1.13,255),
    ("S184","hail","jadeArrows","jade",.55,.93,390),
    ("S185","draw","cleanse","jade",.65,.85,0),
    ("S186","underhand","roller","wood",.56,.96,310),
    ("S187","bow","greenRibbon","jade",.67,.79,0),
    ("S188","close","lastCut","steel",.58,.91,0),
    ("S189","bridge","lanterns","fire",.62,.80,335),
    ("S191","command","boardingPike","steel",.54,.90,320),
    ("S192","bridge","tideBlessing","water",.68,.92,0),
    ("S193","watch","daikyu","steel",.59,1.00,450),
    ("S194","raise","stormGust","air",.61,.95,360),
    ("S400","accuse","evidence","lightning",.69,.87,0),
    ("S401","taunt","battleJoy","fire",.58,.98,0),
    ("S406","crush","trollStone","earth",.65,1.12,0),
    ("S427","bow","paperFan","steel",.68,.81,0),
    ("S428","underhand","lampOil","fire",.61,.83,330),
    ("S429","raise","lanternHalo","void",.71,1.07,350),
    ("S430","cover","wardCut","steel",.62,.89,0),
    ("S433","command","spearLine","steel",.54,.85,320),
    ("S434","bow","ancestorHalo","lightning",.69,.91,0),
    ("S439","veil","deathMask","earth",.73,.97,0),
    ("S441","accuse","jadePrayer","jade",.65,.91,325),
    ("S442","command","warSong","lightning",.65,.87,0),
    ("S443","watch","hunterArrow","steel",.55,.84,350),
    ("S444","hail","crookedSpear","steel",.52,.85,315),
    ("S448","dress","band","jade",.67,.73,0),
    ("S452","bridge","riverPrayer","water",.69,.87,0),
    ("S453","taunt","chorus","lightning",.63,.90,0),
    ("S454","command","matsuSpur","fire",.54,.88,320),
    ("S458","hail","acolyteSpark","fire",.53,.92,286),
    ("S459","crosscut","staffSweep","wood",.57,.88,0),
    ("S464","wheel","porterSweep","wood",.63,.94,0),
    ("S465","focus","memorial","air",.72,.84,0),
    ("S466","stop","templeStaff","wood",.57,.93,0),
    ("S467","serve","prayerBead","jade",.70,.82,0),
    ("S474","raise","stormHalo","air",.67,.88,0),
    ("S475","cover","gatePost","wood",.61,1.01,0),
    ("S478","watch","recall","void",.71,.88,0),
    ("S479","bridge","noviceStaff","wood",.61,.81,0),
    ("S480","dress","saltPoultice","jade",.66,.74,0),
    ("S487","raise","harpoon","water",.57,.94,350),
    ("S488","serve","shrineTea","jade",.67,.78,0),
    ("S494","command","cranePike","steel",.54,.85,322),
    ("S495","bow","smallBlessing","air",.69,.80,0),
    ("S500","watch","centipedeVolley","steel",.58,.94,422),
    ("S501","dress","medicWrap","jade",.67,.82,0),
    ("S502","copy","mirrors","shade",.65,.99,268),
    ("S503","crosscut","sweptClean","wood",.61,.90,0),
    ("S504","serve","foxHerbs","jade",.70,.76,0),
    ("S521","command","horseBow","steel",.56,.92,410),
    ("S522","crouch","shadowCut","shade",.58,.83,0),
    ("S528","command","picket","steel",.59,.87,320),
    ("S529","dress","midwifeRoot","jade",.69,.82,0),
    ("S539","raise","coolingRain","water",.64,.96,363),
    ("S540","bridge","twoSwords","steel",.63,.97,0),
    ("S551","raise","rollingRiver","water",.62,1.01,420),
    ("S552","watch","saddleVolley","steel",.61,.90,420),
    ("S559","accuse","jadeStrike","jade",.60,.96,347),
    ("S560","stop","wakeStaff","wood",.59,.90,0),
    ("S561","raise","agashaFlame","fire",.63,1.05,350),
    ("S565","underhand","powder","fire",.59,.98,342),
    ("S567","bridge","iuchiTide","water",.64,.97,405),
    ("S568","command","sergeantThrust","steel",.60,.97,335),
    ("S586","hail","hanabi","fire",.60,1.04,407),
    ("S587","watch","ferryShot","steel",.55,.85,394),
    ("S588","crosscut","wideSweep","steel",.65,1.03,0),
    ("S596","stop","lifeblood","ice",.64,.93,0),
    ("S600","accuse","laces","steel",.60,.82,0),
    ("S601","bridge","rememberedWind","air",.66,.92,385),
    ("S602","command","endlessStrike","steel",.57,1.01,0),
    ("S603","watch","bearArrow","steel",.58,.87,420),
    ("S604","hail","jadeDust","jade",.56,.86,322),
    ("S613","command","craterArrow","steel",.62,.91,402),
    ("S614","raise","craterWind","air",.59,1.00,357),
    ("S617","hammer","thunderclap","lightning",.64,1.06,204),
    ("S618","watch","hidaJade","jade",.56,.93,425),
    ("S633","close","fathersTanto","jade",.61,.93,0),
]

ALIASES = {"S553":"S528","S554":"S529","S634":"S439"}

# Wardrobe, Trickster, or a missing hero-specific presentation can reach the
# same IDs. The live signature hook takes precedence when its hero can perform it.
FALLBACKS = [
    ("S122","watch","evidence","lightning",.66,.81,0),
    ("S127","dress","medicWrap","jade",.65,.75,0),
    ("S142","hail","shuriken","steel",.55,.92,320),
    ("S573","serve","ginseng","jade",.66,.69,0),
    ("S574","serve","hearth","fire",.61,.78,0),
    ("S575","underhand","root","jade",.63,.73,0),
    ("S576","underhand","rekindle","fire",.67,.82,0),
    ("S577","bridge","hanabi","fire",.61,.93,0),
    ("S578","raise","powder","fire",.65,.98,0),
    ("S579","dress","greenRibbon","jade",.68,.82,0),
    ("S594","draw","lotus","ice",.69,.89,0),
    ("S595","serve","frost","ice",.67,.86,0),
]

SUPPORTIVE = {
    "S144","S146","S175","S176","S185","S187","S192","S434","S439","S442",
    "S448","S452","S453","S465","S467","S474","S480","S488","S495","S501",
    "S504","S529",
}

LEAD = {
    "command":"brandish","cover":"ward","accuse":"push","veil":"hush","raise":"raise",
    "brace":"brace","serve":"cup","bridge":"bridge","hammer":"chop","crush":"heave",
    "hail":"tap","draw":"draw","underhand":"reachBelow","bow":"offer","close":"seal",
    "watch":"inspect","taunt":"fan","dress":"press","crosscut":"tracer","wheel":"swirl",
    "focus":"still","stop":"ward","copy":"armsAcross","crouch":"plant",
}


def support_profiles():
    out = {}
    fallback_ids = {row[0] for row in FALLBACKS}
    for sid,style,shape,element,hit,mark,travel in CALLS + FALLBACKS:
        fallback = sid in fallback_ids
        phase = "use" if sid in SUPPORTIVE or (fallback and sid != "S142") else "attack"
        prep = .26 if style in {"focus","watch","veil","dress"} else .18
        wind = hit-(.17 if style in {"raise","crush","hammer"} else .13)
        out[sid] = dict(phase=phase,style=style,shape=shape,element=element,effort=mark,
                        mark=mark,beats=[prep,wind,hit,.89],movement="gesture",bank="support",
                        lead=LEAD[style], **({"travel":travel} if travel else {}))
        if fallback:
            out[sid]["fallback"] = True
    return out

