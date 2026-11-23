# Kyuden Hida siege cellar

The native cellar now has shored stairs and warm-lit navy walls around its existing walkable route. The entry stair sits behind the original descent landing. The servants' exit has a cedar leaf tied to the original event and G275, with the upward steps beyond the transition volume. Existing cellar casks, cedar benches, lanterns, and the original arena registration are reused.

The original candidate stage verified 39 resources and changed only the M153 environment row. The full catalog and M153 collision file matched byte for byte. The original checkpoint stays visibly supported on its old ledge in this candidate. The separate repair moves its existing interaction and niche to the connected floor.

## Native route checks

- M541 event 15 is at padded x96,z13. In a direct fixture, start at x96,z16 with G1644,G271,G273, then walk toward z13. The event sends the party to M153 x34,z18. In play, the siege controller computes G1644 from active chapter state.
- The M153 ogre encounter uses M001 group 23 and arena M815. The original encounter touch is at x44,z18. Beyond it, take the southern detour. The original open floor passes x42,z30, x53,z34, x61,z36, x66,z26 and x77,z22 on the way to the story touch at x84,z18.
- M153 event 1 at x92,z18 sends the party to M501 x16,z34 when G275 is set. Test from x89,z18 with G271,G274,G275. The visual leaf follows the same condition.

~~~powershell
$py='C:/AI/comfy-3d/venv/Scripts/python.exe'
$work='C:/Users/akodo/Documents/Codex/2026-11-20/ok/work/hida-cave-rework/cellars'
$repo='C:/Users/akodo/.copilot/repos/copilot-worktrees/Traveler/akodoreign-laughing-chainsaw'
$slot='C:/Users/akodo/Documents/Codex/2026-11-20/ok/work/multi-window/profiles/slot-a'
& $py -B "$work/build_hida_cellar.py" stage $repo --profile $slot
& $py -B "$work/review_hida_cellar.py" $slot traverse --leg entry
& $py -B "$work/review_hida_cellar.py" $slot traverse --leg exit
& $py -B "$work/review_hida_cellar.py" $slot capture --view entry
& $py -B "$work/review_hida_cellar.py" $slot capture --view storeroom
& $py -B "$work/review_hida_cellar.py" $slot capture --view exit-locked
& $py -B "$work/review_hida_cellar.py" $slot capture --view exit-open
~~~

## Separate checkpoint relocation

Event 12 originally stood at x66,y10,z23 in block coordinates. The native floor is 1.5 m high, and nearby rock rises beyond the player's 1 m jump. The fixture keeps event 12, its facing, the same save/rest page and all original collision. It changes only the event's position to x68,y3,z24 and puts the shrine at the corresponding walkable alcove. The east approach from x69,z24 is 0.5 m away on the same floor, and x68,z25 connects the alcove to the existing cellar route.

The original and candidate catalog hashes are in `checkpoint-relocation/catalog-delta.json`. The build verified the patched generator's tile grid, height grid, object list and walls against the original. Its only event delta was the same three coordinates. The source patch is at `checkpoint-relocation/gen-maps-checkpoint.patch` and passed an apply check in a disposable copy.

~~~powershell
& $py -B "$work/checkpoint-relocation/relocate_cellar_checkpoint.py" stage $repo --profile $slot
& $py -B "$work/review_hida_cellar.py" $slot checkpoint
& $py -B "$work/review_hida_cellar.py" $slot capture --view checkpoint-relocated
~~~

The repair stage is repeatable and applies only the three coordinate values to the current catalog bytes. Use an isolated slot for these checks. The supervisor handles publication and the native playtest.
