"""Dataset adapters for cognitive risk screening models."""
from .oasis import load_oasis
from .lasi_dad import load_lasi_dad

__all__ = ["load_oasis", "load_lasi_dad"]
