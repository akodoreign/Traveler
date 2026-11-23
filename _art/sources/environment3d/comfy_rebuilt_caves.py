"""Generate focal props and materials for the Snake Den and volcanic caves."""
from comfy_shinomen_gate import queue_meshes

PROMPTS={
    "snake_den_vein_cut_limestone":"Strict front-on square albedo material scan of natural damp blue-gray limestone cave rock with irregular aged pale calcite veins and subtle charcoal fractures. Fine visible color variation with exceptionally clean broad stone shapes and patchy dark patina. Even diffuse light with no glare. Edge to edge material only, no props, panels, building facade, background, frames, text or perspective.",
    "snake_den_coiled_guardian":"A single hand-carved dark blue-green limestone serpent for a late-medieval fantasy shrine, long thick body coiled on a low small stone plinth, raised quiet head, half-worn carved scales, muted mossy mineral seams and some amber age staining. Handbuilt 1:24 miniature diorama prop, smooth readable shape. Whole three-quarter view on pure white, no scenery, ground slab, lettering, shadows, text or people.",
    "snake_den_calcite_cluster":"One small natural damp limestone calcite cave cluster for a miniature diorama. Several joined broad warm gray stalagmites with just a few jade-green mineral veins, old blue shadows, strong organic silhouette, no snow. Entire isolated three-quarter front view on plain white, no ground sheet, background, people, symbols, text or shadow.",
    "volcano_red_crust_rock":"One hand-built miniature railroad diorama cluster of fractured obsidian and charcoal basalt with isolated deep red-orange hairline seams suggesting thermal activity, layered matte iron-red patina, no bright flame and no separate molten base. Isolated full elevated three-quarter game prop on pure white, no floor, background, writing, shadow or people.",
}
if __name__=="__main__":
    queue_meshes(PROMPTS,tuple(PROMPTS)[1:],"cave-rebuild-furnishings",816374,1856)
