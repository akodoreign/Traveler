return {
modeldata = "m212_landbridge.mdl"
bnd = [43.0, 1.2745000123977661, 13.0, 43.0, 0.2745000123977661, 13.0]
material = [
  {
    name = "tidal_sand"
    tec = "pbr.basic"
    mtype = 0
    basecol = 0xffffffff
    rough = 0.9300
    metal = 0.0
    mparam = 0xff000000
    texmap = 0
    texture0 = "tex/sand.png"
    texture1 = null
    texture2 = null
  }
  {
    name = "tidal_wet"
    tec = "pbr.basic"
    mtype = 0
    basecol = 0xffffffff
    rough = 0.8500
    metal = 0.0
    mparam = 0xff000000
    texmap = 0
    texture0 = "tex/tidal_wet.png"
    texture1 = null
    texture2 = null
  }
  {
    name = "cliff"
    tec = "pbr.basic"
    mtype = 0
    basecol = 0xffffffff
    rough = 0.9700
    metal = 0.0
    mparam = 0xff000000
    texmap = 0
    texture0 = "tex/cliff.png"
    texture1 = null
    texture2 = null
  }
]
}
