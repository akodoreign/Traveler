return {
modeldata = "hoshi_andon.mdl"
bnd = [0.0, 0.30000001192092896, 0.0, 0.19499999284744263, 0.30000001192092896, 0.19499999284744263]
material = [
  {
    name = "frame"
    tec = "pbr.basic"
    mtype = 0
    basecol = 0xffffffff
    rough = 0.9100
    metal = 0.0
    mparam = 0xff000000
    texmap = 0
    texture0 = "tex/storehouse_frame.png"
    texture1 = null
    texture2 = null
  }
  {
    name = "glow"
    tec = "pbr.basic"
    mtype = 0
    basecol = 0xffffffff
    rough = 0.9200
    metal = 0.0
    mparam = 0xff160000
    texmap = 0
    texture0 = "tex/andon_paper.png"
    texture1 = null
    texture2 = null
  }
]
}
