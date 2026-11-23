"""The marker chaser's local model (tools/markerchase.py starts it; runs in D:\\RokuganTraveler\\.venv-npu).
Phi-3.5-mini (OpenVINO int4, channel-wise) on the Intel NPU (falls back to GPU, then CPU). One JSON request per stdin
line, one JSON answer per stdout line:
    {"task": "supervise", "job": ..., "tail": "<the last log lines>", "idle_s": 180}
        -> {"action": "continue" | "restart" | "close", "why": "..."}
    {"task": "summarise", "job": ..., "notes": "<the run's notes>"}
        -> {"text": "findings, in plain sentences"}
It only reads what it is sent and answers; it opens no files and changes nothing (the user's rule: read only)."""
import json
import os
import sys
import time

MODEL = os.environ.get("CHASE_MODEL", r"D:\RokuganTraveler\models\phi35-mini-int4-cw-ov")
CACHE = os.environ.get("CHASE_CACHE", r"D:\RokuganTraveler\models\npu_cache")

SUPERVISE = """You supervise a test bot playing a role-playing game. The bot follows the quest marker, talks to
people and walks through exits. Below are the last lines of its log and how long it has made no progress.
Answer with exactly one word first - CONTINUE (it is still moving on, or a long scene is playing), RESTART (it is
looping, stuck in place, or the game looks frozen), or CLOSE (the run ended or cannot go further) - then one short
sentence saying why.

Job: {job}
Seconds without progress: {idle}
Log:
{tail}

Answer:"""

SUMMARISE = """You are writing a playtester's notes for a game designer. Below is what a bot did while playing one
part of a role-playing game: the goals the quest marker gave it, the people it talked to, what they said, menus,
battles, and where it got stuck. Write 3 to 8 short bullet points of FINDINGS a designer should act on: places the
marker led nowhere, events that could not be triggered, dialogue that repeats or reads wrong, errors, and anything
that took unusually long. Every point must name something that appears in the notes (a map, a person, a line, an error). If the notes show nothing wrong, write exactly: - No problems found. Never give general advice.

Job: {job}
Notes:
{notes}

Findings:"""


def load():
    import openvino_genai as og
    os.makedirs(CACHE, exist_ok=True)
    for dev in ("NPU", "GPU", "CPU"):
        try:
            t = time.time()
            cfg = {"CACHE_DIR": CACHE} if dev == "NPU" else {}
            p = og.LLMPipeline(MODEL, dev, **cfg)
            sys.stderr.write("chase_llm: %s ready in %.1f s\n" % (dev, time.time() - t))
            return p, dev
        except Exception as e:                                         # noqa: BLE001 (try the next device)
            sys.stderr.write("chase_llm: %s failed: %s\n" % (dev, e))
    return None, None


def main():
    pipe, dev = load()
    print(json.dumps({"ready": bool(pipe), "device": dev}), flush=True)
    for line in sys.stdin:
        try:
            req = json.loads(line)
        except ValueError:
            continue
        try:
            if req.get("task") == "supervise":
                prompt = SUPERVISE.format(job=req.get("job", ""), idle=int(req.get("idle_s", 0)),
                                          tail=req.get("tail", "")[-3500:])
                out = pipe.generate(prompt, max_new_tokens=40) if pipe else "CONTINUE (no model)"
                word = out.strip().split()[0].strip(".:,").upper() if out.strip() else "CONTINUE"
                action = {"RESTART": "restart", "CLOSE": "close"}.get(word, "continue")
                print(json.dumps({"action": action, "why": out.strip()[:300]}), flush=True)
            elif req.get("task") == "summarise":
                prompt = SUMMARISE.format(job=req.get("job", ""), notes=req.get("notes", "")[-7000:])
                out = pipe.generate(prompt, max_new_tokens=300) if pipe else ""
                print(json.dumps({"text": out.strip()}), flush=True)
            else:
                print(json.dumps({"error": "unknown task"}), flush=True)
        except Exception as e:                                         # noqa: BLE001
            print(json.dumps({"error": str(e)[:300]}), flush=True)


if __name__ == "__main__":
    main()
