"""Queue fixtures for the Dragon mountain town and Kyuden Togashi approaches."""

from comfy_shinomen_gate import queue_meshes


PROMPTS={
    "dragon_slate_waystation":(
        "A small single Japanese mountain path shelter of weathered dark cypress and a "
        "blue-gray slate roof, open on three sides, deep green sash tied to one post, "
        "separate slate footings. Whole isolated tabletop-scale game prop on white, "
        "three-quarter orthographic, open interior visible, no scene, shadows or text."
    ),
    "dragon_forest_torii":(
        "One Japanese mountain path gate in late-medieval timber craft, deep forest green "
        "aged lacquer with dark gold ties and low mossy granite feet. Traditional restrained "
        "silhouette and strong joinery. Isolated complete game object on pure white, "
        "orthographic three-quarter, no ground, text, shadow, people or scenery."
    ),
    "dragon_mountain_andon":(
        "One small Japanese mountain inn paper lantern, golden warm paper shade in "
        "dark green-black cypress lattice, slate square foot and two spare bronze fasteners. "
        "Complete isolated game prop on white, orthographic from three quarters, "
        "no shadows, lettering or scene."
    ),
    "dragon_togashi_stele":(
        "One quiet isolated late medieval Japanese mountain temple stone waymarker. "
        "Mottled green slate, tall narrow slightly irregular stone with simple carved "
        "cloud edgings and unmarked center, golden dead grasses beside its foot. Complete "
        "isolated game object centered on white, three-quarter orthographic, no scene or text."
    ),
    "dragon_slate_moss":(
        "Diffuse top-down square game material of rain-dark dark emerald moss scattered "
        "among blue-gray mountain slate and tiny angular pale gravel. Natural small grain, "
        "neutral overhead diffuse light, no perspective, repeating path, scenery, objects or text."
    ),
}


if __name__=="__main__":
    queue_meshes(PROMPTS,tuple(PROMPTS)[:-1],"dragon-mountains",201103,881)
