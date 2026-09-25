"""
nicis-toolbox: A curated collection of handy Python utilities, tools, and helpers.
"""

from .pyklus import Pyklus, zyklus

__version__ = "0.2.0"
__all__ = ["Pyklus", "zyklus", "download_components", "find_jlc_executable"]


def download_components(*args, **kwargs):
    from .jlc_fetch import download_components as _dl
    return _dl(*args, **kwargs)


def find_jlc_executable(*args, **kwargs):
    from .jlc_fetch import find_jlc_executable as _find
    return _find(*args, **kwargs)
