"""Utility helpers for removing duplicate articles across sources."""
from __future__ import annotations

from hashlib import sha256
from typing import Iterable, List, Sequence, TypeVar

T = TypeVar("T")


def dedupe_by_key(items: Sequence[T], key: Iterable[str] | None = None, attr: str | None = None) -> List[T]:
    """Deduplicate sequence items using either explicit keys or an attribute."""

    seen = set()
    result: List[T] = []

    if key is not None:
        for item, key_value in zip(items, key, strict=False):
            digest = sha256(str(key_value).encode("utf-8")).hexdigest()
            if digest in seen:
                continue
            seen.add(digest)
            result.append(item)
        return result

    if attr is None:
        raise ValueError("Either key or attr must be provided")

    for item in items:
        value = getattr(item, attr)
        digest = sha256(str(value).encode("utf-8")).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        result.append(item)
    return result
