"""Compatibility loader for ``load_source("dom_patterns")``.

The pattern table and detector live in blueprobe. This module re-exports
them so a checkout can still be loaded by module name.
"""

from blueprobe import (
    CATEGORIES,
    DOM_PATTERNS,
    SCHEMA,
    detect_pattern,
    get_pattern,
    get_selector_for_pattern,
    list_categories,
    list_patterns,
)

__all__ = [
    "CATEGORIES",
    "DOM_PATTERNS",
    "SCHEMA",
    "detect_pattern",
    "get_pattern",
    "get_selector_for_pattern",
    "list_categories",
    "list_patterns",
]
