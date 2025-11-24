from typing import Any, List
import re


def _zon_safe_str(s: Any) -> str:
    if s is None:
        return "null"
    s = str(s)
    if s == "":
        return '""'
    lower = s.lower()
    if lower in ("true", "false", "null"):
        return lower
    # numbers
    try:
        int(s)
        return s
    except Exception:
        try:
            float(s)
            return s
        except Exception:
            pass
    # if contains whitespace or special chars, quote
    if any(c.isspace() for c in s) or any(c in s for c in '"#[]{}'):
        return '"' + s.replace('"', '\\"') + '"'
    return s


def zon_serialize(obj: Any, indent: int = 0) -> str:
    pad = "  " * indent
    if isinstance(obj, dict):
        lines: List[str] = []
        for k, v in obj.items():
            key = str(k)
            if isinstance(v, (dict, list)):
                lines.append(f"{pad}{key}")
                lines.append(zon_serialize(v, indent + 1))
            else:
                lines.append(f"{pad}{key} { _zon_safe_str(v) }")
        return "\n".join(lines)
    if isinstance(obj, list):
        items = []
        complex_item = False
        for v in obj:
            if isinstance(v, (dict, list)):
                complex_item = True
                items.append("\n" + zon_serialize(v, indent + 1))
            else:
                items.append(_zon_safe_str(v))
        if complex_item:
            return "\n".join(items)
        return f"[ {', '.join(items)} ]"
    return pad + _zon_safe_str(obj)


def _parse_literal(token: str):
    t = token.strip()
    if t == "null":
        return None
    if t == "true":
        return True
    if t == "false":
        return False
    # quoted string
    if len(t) >= 2 and (
        (t[0] == '"' and t[-1] == '"') or (t[0] == "'" and t[-1] == "'")
    ):
        return t[1:-1].replace('\\"', '"')
    # list inline
    if t.startswith("[") and t.endswith("]"):
        inner = t[1:-1].strip()
        if inner == "":
            return []
        parts = [p.strip() for p in inner.split(",")]
        return [_parse_literal(p) for p in parts]
    # numbers
    try:
        if "." in t:
            return float(t)
        return int(t)
    except Exception:
        return t


def zon_parse(text: str):
    """A tolerant ZON parser: supports comments (#), inline lists, quoted strings,
    and nested block objects via indentation.
    Returns Python dict/list/primitives.
    """
    # Preprocess: remove comments
    lines = []
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if line.strip() == "":
            continue
        lines.append(line)

    if not lines:
        return {}

    root = {}
    stack = [(-1, root)]  # (indent_level, container)

    for raw in lines:
        # count leading spaces as indent (2 spaces per indent level)
        stripped = raw.lstrip()
        indent = len(raw) - len(stripped)
        level = indent // 2

        # key [value] or key value or key
        parts = stripped.split(None, 1)
        key = parts[0]
        val = None
        if len(parts) > 1:
            val = parts[1].strip()

        # find parent container for this level
        while stack and stack[-1][0] >= level:
            stack.pop()
        parent = stack[-1][1]

        if val is None:
            # start nested object
            new = {}
            parent[key] = new
            stack.append((level, new))
        else:
            # parse literal or inline list
            parsed = _parse_literal(val)
            parent[key] = parsed

    return root
