"""
nicis-toolbox: A curated collection of handy Python utilities, tools, and helpers.
"""

from .pyklus import Pyklus, zyklus
from .cpy_snooze import CpySnooze, SleepManager

__version__ = "0.5.0"
__all__ = [
    "Pyklus",
    "zyklus",
    "CpySnooze",
    "SleepManager",
    "DocForge",
    "download_components",
    "find_jlc_executable",
    "type_text",
]


def download_components(*args, **kwargs):
    from .jlc_fetch import download_components as _dl
    return _dl(*args, **kwargs)


def find_jlc_executable(*args, **kwargs):
    from .jlc_fetch import find_jlc_executable as _find
    return _find(*args, **kwargs)


def type_text(*args, **kwargs):
    from .ghostwriter import type_text as _tt
    return _tt(*args, **kwargs)


def DocForge(*args, **kwargs):
    from .doc_forge import DocForge as _DF
    return _DF(*args, **kwargs)
