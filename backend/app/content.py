"""Loads game content (pictures + labels) for the two study conditions."""
import json
import os
from functools import lru_cache

CONTENT_DIR = os.path.join(os.path.dirname(__file__), "..", "content")
VERSIONS = ("localized", "generic")


@lru_cache(maxsize=None)
def load_items(version: str) -> list[dict]:
    if version not in VERSIONS:
        raise ValueError(f"unknown content version: {version}")
    with open(os.path.join(CONTENT_DIR, f"items_{version}.json"), encoding="utf-8") as f:
        return json.load(f)["items"]
