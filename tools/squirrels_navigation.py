"""Read or update the bot's learned walking choices using validated live observations."""
import ast
import math
from pathlib import Path
from pprint import pformat
import re
import tempfile

POLICY_FILE = Path(__file__).with_name("squirrels_walking_policy.py")
BOT_POSITION = re.compile(r"\[RT\] BOT at (M\d+) (-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?) y")
ASK_POSITION = re.compile(r"\| on (M\d+) at (-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)(?: |$)")
GOAL = re.compile(r"^M\d+ -?\d+(?:\.\d+)? -?\d+(?:\.\d+)?")
MAX_GOALS = 40


def observed_waypoints(mid, lines):
    """Convert visited player positions from the bot debug scale to map coordinates."""
    points = {}
    for line in reversed(lines[-500:]):
        if match := BOT_POSITION.search(line):
            if match[1] == mid:
                point = (float(match[2]) / 2, float(match[3]) / 2)
                points.setdefault(point, None)
    return list(points)


def read_hints():
    """Read the model's Python data without evaluating Python code."""
    try:
        stored = ast.parse(POLICY_FILE.read_text(encoding="utf-8")).body
        if (len(stored) == 1 and isinstance(stored[0], ast.Assign)
                and isinstance(stored[0].targets[0], ast.Name)
                and stored[0].targets[0].id == "WALKING_HINTS"):
            hints = ast.literal_eval(stored[0].value)
            if isinstance(hints, dict):
                return hints
    except (OSError, ValueError, SyntaxError):
        pass
    return {}


def store_hint(job, goal, mid, waypoint, observed):
    """Save one Ollama-selected waypoint, only when the game logged it as visited."""
    if not re.fullmatch(r"story_[0-7]_[a-z]+", job) or not GOAL.fullmatch(goal):
        raise ValueError("Expected a story job and a visible objective coordinate.")
    if not re.fullmatch(r"M\d+", mid) or waypoint not in observed:
        raise ValueError("The waypoint must have been visited on the current map.")
    hints = read_hints()
    key = (job, goal, mid)
    if hints.get(key) == waypoint:
        return False
    hints.pop(key, None)
    hints[key] = waypoint
    most_recent = dict(list(hints.items())[-MAX_GOALS:])
    source = "# Ollama's learned walking choices for the Squirrels.\nWALKING_HINTS = " + pformat(most_recent) + "\n"
    ast.parse(source)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=POLICY_FILE.parent,
                                     suffix=".tmp", delete=False) as temp:
        temp.write(source)
        filename = Path(temp.name)
    try:
        filename.replace(POLICY_FILE)
    finally:
        filename.unlink(missing_ok=True)
    return True


def walking_hint(job, question, tried):
    current = ASK_POSITION.search(question)
    goal = GOAL.match(question)
    if current is None or goal is None:
        return ""
    mid = current[1]
    point = read_hints().get((job, goal[0], mid))
    if (not isinstance(point, tuple) or len(point) != 2
            or any(type(value) not in (int, float) or not math.isfinite(value) for value in point)):
        return ""
    if max(abs(point[0] - float(current[2])), abs(point[1] - float(current[3]))) < 1.5:
        return ""
    command = f"goto {point[0]:g} {point[1]:g}"
    return command if command not in tried else ""
