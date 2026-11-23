"""Queue small fixtures for the Ojatara testimony and Nihime scenes."""

from comfy_shinomen_gate import queue_meshes


PROMPTS={
    "ojatara_nihime_screen":(
        "One low three-panel late medieval Japanese folding screen, cream paper with a "
        "subtle painted branch of pale plum flowers, warm dark wood frame and plain "
        "back. Complete isolated object on pure white, elevated orthographic three-quarter "
        "angle, matte hand painted surface, no people, ground, shadows or text."
    ),
    "ojatara_incense_set":(
        "One small Japanese incense bowl and folded wisteria cloth on a low red cedar tray, "
        "a small blossom pressed beside it. Quiet matte late medieval household craft. "
        "Complete compact isolated game object on pure white, elevated orthographic angle, "
        "no smoke, scenery, surface or writing."
    ),
    "ojatara_court_ledger":(
        "Handmade pile of three folded late medieval Japanese testimony folios tied with "
        "faded brick-red cord, wrapped pale tan paper edges, a small black ink stone "
        "and bamboo brush sitting on a shallow wooden tray. Isolated completed game object "
        "on pure white, elevated orthographic view, no scene, ground, shadows or writing."
    ),
}


if __name__=="__main__":
    queue_meshes(PROMPTS,tuple(PROMPTS),"ojatara-rooms",189163,829)
