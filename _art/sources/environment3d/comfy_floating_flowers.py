"""Generate small river-market props for Floating Flowers."""
from comfy_shinomen_gate import queue_meshes

PROMPTS={
    "floating_flowers_work_skiff":"A complete sixteenth-century Japanese River of Gold miniature work skiff, simple long shallow oiled chestnut plank hull with slightly upturned ends, three bench thwarts, a tied tan pole laid inside, no sail or cabin. Real physical model railroad diorama craft, dark readable plank seams, olive wear near waterline, not an illustration. Orthographic elevated three-quarter view, whole silhouette on pure white. No water, floor, people, stand, letters or shadow.",
    "floating_flowers_ribbon_wares":"Small late medieval Japanese riverside flower-market display, one low wicker tray packed with pastel pink plum blossoms and two pieces of brilliant vermilion and blue handmade silk ribbon folded across the lip and around a few cut stems. Handcrafted miniature diorama prop, whole isolated piece in elevated three-quarter view against solid white. No figure, market stall, ground, text or shadow.",
    "floating_flowers_paper_fish":"One little handmade folk-craft Japanese river shrine ornament, delicate origami-like koi cut from warm ivory paper with small indigo and red ink details; tail tipped upward, hanging from a thin cord loop by its back. Complete single object for a miniature diorama game prop against pure white, orthographic three-quarter view. No water, shrine, base, scenery, letters or shadow.",
}
if __name__=="__main__":
    queue_meshes(PROMPTS,tuple(PROMPTS),"floating-flowers-quay",816232,1830)
