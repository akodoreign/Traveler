"""Generate a continuous Japanese cedar source for the grove."""

from comfy_shinomen_gate import queue_meshes


PROMPTS={
    "scorpion_grove_cedar_v2":(
        "Realistic isolated asset photograph of one mature Cryptomeria japonica Japanese "
        "cedar. Dark green irregular conical crown, many soft hanging sprays of dense short "
        "needles hiding most lateral branches. A thin uneven cinnamon-dark bark trunk "
        "only exposed on the bottom quarter, a natural asymmetric living tree. Connected "
        "foliage, no stylized bars, no pruning platforms, no cages, no right angles. Fully "
        "visible raised three-quarter view on pure white, with no ground or other objects."
    ),
}


if __name__=="__main__":
    queue_meshes(PROMPTS,tuple(PROMPTS),"grove-cedar-v2",199081,877)
