"""Operational vs historical data scoping.

Business rule:
- The operational system starts in 2026.
- Legacy data (2024/2025) must only be visible in the historical dashboard.

Implementation rule:
- We apply scoping ONLY when running under Streamlit.
- In scripts/CLI contexts, services should keep seeing the full dataset.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional

OPERATIONAL_START_YEAR = 2026
OPERATIONAL_START_YM = f"{OPERATIONAL_START_YEAR:04d}-01"


def _in_streamlit_runtime() -> bool:
    """True only when code is running inside a Streamlit app run."""

    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        return get_script_run_ctx() is not None
    except Exception:
        return False


def get_active_data_mode(default: str = "operacional") -> str:
    if not _in_streamlit_runtime():
        return default

    try:
        import streamlit as st

        return str(st.session_state.get("data_mode", default))
    except Exception:
        return default


def should_apply_operational_scope() -> bool:
    return _in_streamlit_runtime() and get_active_data_mode() == "operacional"


def _extract_year(value: Any) -> Optional[int]:
    if value is None:
        return None

    if isinstance(value, str):
        try:
            return int(value[:4])
        except Exception:
            return None

    if isinstance(value, (date, datetime)):
        return int(value.year)

    # Firestore timestamps often behave like datetimes
    year = getattr(value, "year", None)
    if year is None:
        return None

    try:
        return int(year)
    except Exception:
        return None


def aluno_is_operational(aluno_data: Dict[str, Any]) -> bool:
    """Operational students are those that start in 2026+."""

    year = _extract_year(aluno_data.get("ativoDesde"))

    # If ativoDesde is missing/invalid, treat as legacy in operational mode.
    if year is None:
        return False

    return year >= OPERATIONAL_START_YEAR


def ym_is_operational(ym: Any) -> bool:
    """ym is expected as 'YYYY-MM'."""

    year = _extract_year(ym)
    if year is None:
        return False

    return year >= OPERATIONAL_START_YEAR


def pagamento_is_operational(pagamento: Dict[str, Any]) -> bool:
    ano = pagamento.get("ano")
    if isinstance(ano, int):
        return ano >= OPERATIONAL_START_YEAR

    return ym_is_operational(pagamento.get("ym"))


def presenca_is_operational(presenca: Dict[str, Any]) -> bool:
    return ym_is_operational(presenca.get("ym"))
