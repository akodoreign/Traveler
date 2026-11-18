"""Exercise native weapon replacement and victory animation in RPG-Cobo."""
from pathlib import Path

import playbot


def main():
    name, mid = "native_victory", "M202"
    fixture = r"evalf ..\..\tools\test_native_victory.sk"
    steps = ["wait 650", fixture, "wait 400", "shot native_victory_1", "wait 450",
             "shot native_victory_2", fixture, "wait 400", fixture, "wait 400", fixture]
    _, timeout = playbot.launch(name, mid, *playbot.block(mid, 49, 15), steps,
                                lead="P100", party="P104,P102", secs=50)
    log = Path(__file__).resolve().parents[1] / f"_art/preview/bot/{name}/log.txt"
    contents = log.read_text(encoding="utf-8", errors="replace")
    checks = [line for line in contents.splitlines() if line.startswith("[NATIVE VICTORY]")]
    if timeout or len(checks) != 4 or "Exception in thread" in contents:
        raise RuntimeError(f"Native victory regression failed. See {log}")
    print("\n".join(checks))


if __name__ == "__main__":
    main()
