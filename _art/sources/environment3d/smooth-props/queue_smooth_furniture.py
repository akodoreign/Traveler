"""Queue Comfy source images and Hunyuan GLBs for the first smooth prop group."""
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from comfy_shinomen_gate import queue_meshes

PROMPTS={
    "smooth_iuchi_storm_shoji": (
        "One detached damaged low Japanese shoji screen panel lying on its bottom rail upright, "
        "a historical late medieval cypress wood and soft warm ivory paper screen from a windy hall. "
        "Broad panel a little wider than tall, nearly flat depth, smooth dark honey-brown cypress rails, "
        "clear continuous wood rails with hand-finished rounded edges, four columns and three rows. "
        "A few large torn paper shapes concentrated on the lower right and upper left, two empty rectangular cells "
        "show through the lattice, one splintered corner. Geometry reads as a single mostly rectangular panel. "
        "Use smooth continuous modeling, clean grain running along the wooden rails and softly mottled matte ivory paper. "
        "Orthographic front three-quarter view tilted only 12 degrees, entire single separate game mesh object in frame, "
        "plain solid white background, no floor, doorway, shadow, border, frame elsewhere, words, white cast base, "
        "voxel, pixel art, chunky noise or distressed chipped paint."
    ),
    "smooth_hoshi_trade_chest": (
        "One closed squat traditional sixteenth-century Japanese portable merchant tansu chest. Width twice height, "
        "depth about equal to height. Smooth restrained refined cypress joinery, dark reddish-brown lacquer "
        "showing soft straight wood grain, two simple bronze strap hinges and one dark iron pull. "
        "Flat feet and simple broad uninterrupted panels, slight pleasant edge bevel, no patterns on wood. "
        "Isolated single game prop, orthographic front three-quarter view on unbroken solid white, entire object. "
        "No scenery, floor, backdrop pedestal, shadow, texture noise, artifacting, voxel blocks, lettering or coins."
    ),
    "smooth_hoshi_storage_jar": (
        "One mostly round sixteenth-century Japanese low-fired stoneware storage jar, narrow foot, thick gently rolled "
        "rim and a tiny flat terracotta disc lid. Matte dark forest-brown ash glaze with restrained olive tones "
        "around the shoulder and plain rust-brown clay lower down. Smooth continuous curved pottery with broad calm "
        "color areas and only fine natural kiln marks. One isolated miniature game asset in orthographic three-quarter "
        "view on pure white. No shadow, floor plane, stand, adornment, text, black outlines, voxel steps or crushed grain."
    ),
    "smooth_coast_salt_crate": (
        "One small older Japanese coastal salt merchant's cedar packing crate, a square and slightly squat covered "
        "wooden crate with clean dark brown vertical battens and horizontal cedar boards, two subtle taut straw bindings "
        "and a small twisted straw side handle. Warm middle-brown, soft wood grain running along the boards, hand-worn "
        "edges with a slight bevel. Complete plain game prop isolated in orthographic three-quarter view against solid "
        "white, no display base, shadow, ground, salt contents, lettering, pixelated noise, voxel style or bright white trim."
    ),
}
if __name__=="__main__":
    queue_meshes(PROMPTS,tuple(PROMPTS),"smooth-furniture",815683,1791)
