"""Shared parser for the canonical VERIFIED.md ledger."""
from __future__ import annotations

import re
from pathlib import Path

ROW_RE = re.compile(r"^\|(.+)\|(.+)\|(.+)\|(.+)\|(.+)\|\s*$")
CODE_RE = re.compile(r"`([^`]+)`")


def strip_md(value: str) -> str:
    value = value.strip().replace("**", "")
    value = value.strip("`")
    value = value.replace("¹", "").replace("²", "")
    return value.strip()


def extract_files(root: Path, cell: str) -> list[str]:
    """Resolve full and basename-only .lean references in one ledger file cell."""
    tokens: list[str] = []
    for expanded in expand_braces(cell):
        tokens.extend(
            re.findall(r"(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.lean", expanded)
        )
    result: list[str] = []
    parent: Path | None = None
    for token in tokens:
        path = Path(token)
        if len(path.parts) > 1:
            candidate = path
            parent = path.parent
        elif parent is not None:
            candidate = parent / path
        else:
            matches = list(root.rglob(path.name))
            candidate = matches[0].relative_to(root) if len(matches) == 1 else path
        posix = candidate.as_posix()
        if posix not in result:
            result.append(posix)
    return result


def extract_name_patterns(cell: str) -> list[str]:
    """Extract declaration-like code spans, expanding namespace shorthand."""
    spans = CODE_RE.findall(cell)
    if not spans:
        spans = [strip_md(cell)]
    result: list[str] = []
    namespace: str | None = None
    previous: str | None = None
    for raw in spans:
        name = raw.strip().rstrip(".,;")
        if not name or name.startswith("instance :"):
            continue
        if any(char.isspace() for char in name):
            continue
        if not re.fullmatch(r"[\w'.!?₀-₉*{},]+", name, flags=re.UNICODE):
            continue
        shorthand_suffix = name.startswith("_")
        if shorthand_suffix and previous:
            name = previous + name
        elif "." not in name and namespace:
            name = f"{namespace}.{name}"
        if "." in name and "*" not in name and "{" not in name:
            namespace = name.rsplit(".", 1)[0]
            if not shorthand_suffix:
                previous = name
        result.append(name)
    return result


def expand_braces(pattern: str) -> list[str]:
    match = re.search(r"\{([^{}]+)\}", pattern)
    if not match:
        return [pattern]
    return [
        pattern[:match.start()] + choice + pattern[match.end():]
        for choice in match.group(1).split(",")
    ]


def parse_ledger(root: Path) -> list[dict]:
    rows: list[dict] = []
    seen_header = False
    text = (root / "VERIFIED.md").read_text(encoding="utf-8")
    for line in text.splitlines():
        match = ROW_RE.match(line)
        if not match:
            continue
        cells = [cell.strip() for cell in match.groups()]
        if cells[0].lower() == "claim_id":
            seen_header = True
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        if not seen_header:
            continue
        claim, names, files, method, status = cells
        index = len(rows)
        rows.append(
            {
                "id": f"ledger-{index:03d}",
                "claim": strip_md(claim),
                "theorem_cell": names,
                "name": strip_md(names),
                "file_cell": files,
                "files": extract_files(root, files),
                "name_patterns": extract_name_patterns(names),
                "method": strip_md(method),
                "status": strip_md(status),
            }
        )
    return rows
