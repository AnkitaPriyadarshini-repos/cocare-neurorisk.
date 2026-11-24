"""LASI-DAD (Longitudinal Aging Study in India - Diagnostic Assessment of Dementia) Adapter.

=============================================================================
STUB ADAPTER - AWAITING CODEBOOK & APPROVED ACCESS
=============================================================================
PRIME DIRECTIVE COMPLIANCE:
Never invent variable names. LASI-DAD is access-controlled and governed by
a Data Use Agreement (DUA). This adapter is a strictly typed stub that outlines
the ingestion contract. When the official codebook and data dictionary are placed
in `ml/docs/`, this adapter must be updated with the exact verified variable IDs.
=============================================================================
"""
import os
from typing import Tuple, Optional
import pandas as pd


def load_lasi_dad(
    data_path: Optional[str] = None,
    codebook_path: Optional[str] = None
) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Stub loader for LASI-DAD dataset.

    Raises:
        NotImplementedError: Always raised until codebook and authorized data
        are provided by the data owner.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    expected_doc = os.path.join(base_dir, "docs", "feature_inventory.csv")

    raise NotImplementedError(
        "LASI-DAD data adapter is a stub awaiting the official LASI-DAD codebook "
        "and participant-level data. Never invent variable names or simulate unverified "
        "harmonization. Place codebook in ml/docs/ and contact data owner for DUA approval.\n"
        "To run the verified pipeline, use the OASIS adapter: `ml.src.datasets.oasis`."
    )
