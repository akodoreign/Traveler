"""Regenerate two remaining modular spirit foes in the coastal encounter lists."""
from comfy_shinomen_gate import queue_meshes

PROMPTS = {
    "foe_ink_pot_spirit": (
        "Original Rokugan game creature. A very old, round black-gray Japanese stoneware ink pot come to life, "
        "a crooked mouth carved into its dark varnished pot, two watchful indigo eyes, several curling glossy "
        "black ink tendrils below the bowl and two little brushlike limbs to either side. Cobalt reflections, "
        "reddish patina on the chipped rim and shallow decorative rings on the clay. One compact expressive "
        "creature body with connected forms, rendered as a textured stylized RPG miniature. Full isolated "
        "three-quarter on white, no ground, cast shadow, real person, text, scenery or lettering."
    ),
    "foe_paper_lantern_spirit": (
        "Original Rokugan game creature. Animated Japanese paper lantern with rich orange-red, ribbed rice paper, "
        "dark lacquer wooden rims, deep black slit grin with a single pointed long vermilion tongue curling out. "
        "One clear blue-black pupil under the top rim, warm honey interior colors, slightly torn paper edge, "
        "slender black tassels and a brass handle above. One compact creature silhouette, connected forms for "
        "a textured stylized RPG diorama mesh. Whole isolated object on flat white, no scenery, human body, "
        "typography, floor or shadows."
    ),
}
if __name__=="__main__":
    queue_meshes(PROMPTS, tuple(PROMPTS), "coastal-spirit-foes", 872636, 7626)
