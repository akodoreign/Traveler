"""Run the live field, follower, and battle-factory clothing regression."""
from pathlib import Path

import playbot


def main():
    name, mid = "native_gear", "M202"
    fixture = r"evalf ..\..\tools\test_native_gear.sk"
    steps = ["wait 600", fixture, "wait 400", fixture, "wait 300", "shot native_gear_clans",
             fixture, "wait 400", fixture, "shot native_gear_unequipped"]
    _, timeout = playbot.launch(name, mid, *playbot.block(mid, 49, 15), steps,
                                lead="P100", party="P104", secs=50)
    log = Path(__file__).resolve().parents[1] / f"_art/preview/bot/{name}/log.txt"
    contents = log.read_text(encoding="utf-8", errors="replace")
    stages = [line for line in contents.splitlines() if line.startswith("[NATIVE GEAR]")]
    if timeout or len(stages) != 4 or "Exception in thread" in contents:
        raise RuntimeError(f"Native gear regression failed. See {log}")
    print("\n".join(stages))


if __name__ == "__main__":
    main()
