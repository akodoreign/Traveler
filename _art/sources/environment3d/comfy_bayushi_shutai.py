"""Generate Bayushi castle-town and Shutai fixtures with distinct materials."""

from comfy_shinomen_gate import queue_meshes


PROMPTS={
    "bayushi_household_well":(
        "One late medieval Japanese street well, dark mottled stone circular curb, black "
        "cedar posts supporting a small dark blue ceramic awning, straight timber windlass "
        "with a rough hanging rope and bucket. Near-black wood, warm pale rope and slate "
        "stone. Full isolated voxel game prop on white, orthographic three quarter."
    ),
    "bayushi_scarlet_lantern":(
        "One Japanese standing welcome lantern on a tall deep lacquered post, rich oxblood "
        "red mulberry paper shade held in small black cypress frame, subtle brass latch and "
        "one straight narrow awning. Complete isolated game prop on white, orthographic "
        "three-quarter, no floor, person, text, shadows or scenery."
    ),
    "shutai_willow_cart":(
        "One simple weathered open Japanese wooden handcart, dark rain-stained cedar, two "
        "large spoke wheels and one dark-blue cloth-wrapped sack. Distinct open silhouette "
        "and broad visible handles. Isolated complete voxel game prop on white, elevated "
        "orthographic three-quarter angle, no figure, scenery, ground, text or shadows."
    ),
    "bayushi_shrine_lattice":(
        "Freestanding Japanese small roadside shrine in deep old red-brown lacquer and "
        "black cypress, slim dark navy tiled roof, dark shadow between two open lattice "
        "leaves, one bronze hanging bell and pale rope. Single isolated complete game prop "
        "on pure white in three-quarter orthographic view, no people, text or scenery."
    ),
    "bayushi_rain_dark_lacquer":(
        "Strict overhead square diffuse texture scan of weathered deep oxblood Japanese "
        "lacquer over cedar grain from an outdoor late medieval building. Near-black red "
        "seams, fine matte chips and warm rust undertones. High color depth, neutral diffuse "
        "flat light, edge to edge with no scene, props, shadow or lettering."
    ),
}


if __name__=="__main__":
    queue_meshes(PROMPTS,tuple(PROMPTS)[:-1],"bayushi-shutai",196771,853)
