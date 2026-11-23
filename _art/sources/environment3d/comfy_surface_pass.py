"""Generate surface scans and a coastal pine source with the local Z-Image model."""

import json
from pathlib import Path
import time
from uuid import uuid4
from urllib.parse import urlencode

from comfy_coast import HTTP, response

HERE=Path(__file__).resolve().parent
OUT=HERE/"surface_sources"

PROMPTS={
    "sand_scan": "Seamless PBR texture scan for a video game. Strict straight-down orthographic view of pale warm-gray fine coastal sand grains. Small subtle ripple patterns and scattered fine gravel. Highly detailed even diffused light. The whole edge-to-edge square is sand. Nothing else.",
    "meadow_scan": "Seamless videogame diffuse material scan. Fixed orthographic top-down square of short dense dark olive coastal grass and tiny clover. Finely detailed natural patchwork with dull straw, olive leaves and dark earth. Consistent scale throughout. No horizon, no objects, no shadow patterns.",
    "cliff_scan": "Square flat tileable diffuse scan of a weathered horizontal coastal sandstone wall. Gray tan rough surface with many thin irregular sediment layers and sandy pores. Direct front-facing orthographic capture. Rock surface fills all four edges. No distant landscape, plants, borders, people or vehicles.",
    "coast_pine_v2": "One mature asymmetrical Japanese black pine tree, Pinus thunbergii, with leaning gnarled gray rough-barked trunk, exposed dark roots, broad flat cloud-shaped tiers of sparse weathered olive green needle foliage. Optimized asset photograph, full tree visible in a raised three quarter orthographic view, pure solid white background. No visible surface, no props, no text. No snowy branches, no Christmas shape.",
    "kaiu_masonry": "High fidelity photogrammetry albedo square. Direct flat front orthographic material scan of irregular rough boulders in late-1500s Japanese castle foundation dry stonework, with tightly stacked unshaped natural stones, mottled charcoal and bluish gray plus a little pale gray lichen. No mortar lines, no monuments, no horizon. Fills the square.",
    "kaiu_cedar": "Edge-to-edge flat tileable architectural material scan, dark weathered horizontal cedar cladding of a late medieval Japanese fortification. Plain narrow overlapping wood boards, visible shallow passes of grain, grey charcoal brown, muted color, smooth lighting.",
    "kaiu_plaster": "Only an edge-to-edge flat texture sample of warm off-white rough lime plaster used on Sengoku Japanese castle facades. Soft subtle stains, fine hairline creases, natural diffuse scan, texture uniform scale, no perspective, no scene, no furniture or trim.",
    "kawara_bluegrey": "Strict flat top-down game texture scan of a repeating Japanese kawara roof. Faded dark blue-gray ceramic cylindrical clay tiles and subtly lighter scuffed overlap, laid in parallel long straight aligned rows from top to bottom. PBR surface scanned in even light. Tile rows fill all four edges. No elements besides tile.",
    "watchtower_signal": "One isolated late Sengoku Japanese timber signal beacon basket, open round unlit iron fire bowl suspended from a short plain wood tripod, complete small gameplay prop orthographic three-quarter view, black wrought iron and aged dark cedar, pure white background, no floor plane and no other scenery.",
    "garrison_gate": "One compact rough late 1500s Japanese fortification main timber gate bay, full freestanding modular bay viewed in three quarter. Paired dark thick cedar doors with plain horizontal black iron brackets, heavy rectangular wooden posts with squared lintel and no roof, footings of individual uneven granite boulders. Pure white background, no surrounding building.",
}


def graph(name, text, seed):
    return {
        "1":{"class_type":"UNETLoader","inputs":{"unet_name":"z_image_turbo_nvfp4.safetensors","weight_dtype":"default"}},
        "2":{"class_type":"CLIPLoader","inputs":{"clip_name":"qwen_3_4b_fp8_mixed.safetensors","type":"lumina2","device":"default"}},
        "3":{"class_type":"VAELoader","inputs":{"vae_name":"ae.safetensors"}},
        "4":{"class_type":"CLIPTextEncode","inputs":{"text":text,"clip":["2",0]}},
        "5":{"class_type":"ConditioningZeroOut","inputs":{"conditioning":["4",0]}},
        "6":{"class_type":"EmptySD3LatentImage","inputs":{"width":768,"height":768,"batch_size":1}},
        "7":{"class_type":"ModelSamplingAuraFlow","inputs":{"model":["1",0],"shift":3.0}},
        "8":{"class_type":"KSampler","inputs":{"model":["7",0],"positive":["4",0],"negative":["5",0],
            "latent_image":["6",0],"seed":seed,"steps":9,"cfg":1.0,"sampler_name":"euler","scheduler":"simple","denoise":1.0}},
        "9":{"class_type":"VAEDecode","inputs":{"samples":["8",0],"vae":["3",0]}},
        "10":{"class_type":"SaveImage","inputs":{"images":["9",0],"filename_prefix":f"traveler_surface/{name}"}}
    }


def main():
    OUT.mkdir(exist_ok=True)
    path=HERE/"comfy-surfaces-receipts.json"
    jobs=json.loads(path.read_bytes()) if path.is_file() else {}
    for index,(name,prompt) in enumerate(PROMPTS.items()):
        if name not in jobs:
            res=json.loads(response(HTTP,"/prompt",{"prompt":graph(name,prompt,162388+index),"client_id":str(uuid4())}))
            jobs[name]=res["prompt_id"]
            path.write_text(json.dumps(jobs,indent=2),encoding="utf-8")
            print(name,jobs[name],flush=True)
    pending={key:job for key,job in jobs.items() if not (OUT/f"{key}.png").is_file()}
    deadline=time.monotonic()+650
    while pending:
        for key,job in list(pending.items()):
            result=json.loads(response(HTTP,f"/history/{job}")).get(job)
            if not result:
                continue
            if result["status"]["status_str"]!="success":
                raise RuntimeError(result["status"])
            pic,=result["outputs"]["10"]["images"]
            (OUT/f"{key}.png").write_bytes(response(HTTP,"/view?"+urlencode(pic)))
            del pending[key]
            print("downloaded",key,flush=True)
        if pending:
            if time.monotonic()>=deadline:
                raise TimeoutError(pending)
            time.sleep(4)
    queue=json.loads(response(HTTP,"/queue"))
    if not queue["queue_running"] and not queue["queue_pending"]:
        response(HTTP,"/free",{"unload_models":True,"free_memory":True})


if __name__=="__main__":
    main()
