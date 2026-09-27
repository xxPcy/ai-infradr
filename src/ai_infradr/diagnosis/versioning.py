from __future__ import annotations

import re

_VERSION_RE = re.compile(r"^(\d+)(?:\.(\d+))?(?:\.(\d+))?")


def version_tuple(value: str | None) -> tuple[int, int, int] | None:
    if not value:
        return None
    match = _VERSION_RE.match(str(value).strip())
    if not match:
        return None
    return tuple(int(part or 0) for part in match.groups())  # type: ignore[return-value]


def version_lt(left: str | None, right: str | None) -> bool:
    a = version_tuple(left)
    b = version_tuple(right)
    return bool(a is not None and b is not None and a < b)
