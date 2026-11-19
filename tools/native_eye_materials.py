"""Keep Codex's existing eye polygons visible without changing the model data."""
import re


def iris_tint(iris, factor, lift=0):
    return tuple(int(min(255, max(0, c * factor + lift))) for c in iris)


def eye_materials(spec):
    iris = spec.get("eye", (98, 62, 42))
    colors = [(242, 225, 216), (31, 23, 26), (255, 244, 229), (45, 30, 33)]
    colors.extend(iris_tint(iris, factor, lift) for factor, lift in ((.55, 0), (.90, 0), (1.19, 13)))
    return {"c%02x%02x%02x" % rgb for rgb in colors}


def two_sided_eyes(text, spec):
    wanted = eye_materials(spec)
    found = set()

    def update(match):
        name, block = match[1], match[0]
        if name not in wanted:
            return block
        found.add(name)
        if re.search(r"(?m)^\t\tcullface = ", block):
            return re.sub(r"(?m)^\t\tcullface = [^\r\n]+", "\t\tcullface = SK_OFF", block)
        newline = "\r\n" if "\r\n" in block else "\n"
        line, rest = block.split(newline, 1)
        return newline.join((line, "\t\tcullface = SK_OFF", rest))

    out = re.sub(r'(?ms)^\t\tname = "(c[0-9a-f]{6})"\r?\n.*?^\t\}', update, text)
    if wanted != found:
        raise ValueError(f"{spec.get('model_key', 'body')}: missing eye materials {sorted(wanted - found)}")
    return out
