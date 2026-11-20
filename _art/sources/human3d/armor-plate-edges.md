# Clan upper-edge lacquer handoff

The accepted Hiruma pilot uses native_tailoring's two wearer albedos under edge-pilot/tex/crab. The shared kit is edge-catalog/tex. Copy all 208 relative PNG paths into project/resource/native_tailoring/tex. The three dedicated Soldier costume textures are in edge-mitsue/tex with the same destination. Back up the replaced relative files for rollback.

## Coverage

- Shared body armor. A101, A108, A109, A112, A116, A135, A141, A159, A166, A168 and A173. Authored paths follow exposed cuirasses, shoulder plates, tassets and rigid guards appropriate to the individual model.
- Shared rigid headgear. A102 Jingasa, A103 guard, A110 Kabuto, A113 scout shell and A160 legion helmet. Dome or shell edges and exposed hard neck plates receive the color where present. Fabric ties and soft rims use their existing material maps.
- Shosuro Mitsue. Soldier, reinforced Soldier and Soldier helmet each have a separately fitted upper-edge treatment in the costume's muted gold accent. Armor lames, shell and reinforced guards are separated from sleeves, wraps and garment panels.
- Soft/mixed equipment to review separately. A120 is robe and sash, A155 is flexible leather and cloth, and Mitsue's other costumes are mostly fabric. Specialty masks and accessory hardware need a visual material-by-material pass when requested.

## Authoring

paint_plate_edges.py and catalog_plate_courses.py read the installed native bind positions, UV0 and face topology. Front and rear depth passes give each visible panel its own authored top and half-side polyline. The mask tapers at the two ends, preserves the lower perimeter, and reads only on the selected visible surface. Existing crest sheets render through their normal routes. Geometry, base normal and layer weights stay on their current equipment assets. Approved rivet masks protect cap highlights along shared borders. Shared dye accents come from the gear palette's accent and lace roles. Undyed items use a dark copper edge or the authored costume gold.

Review in daylight from front and profile. Inspect panel contour registration, the halfway ends, and shoulder/hip movement in thrust, or kneel and rise for longer tassets.

