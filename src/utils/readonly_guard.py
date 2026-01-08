"""Helpers for enforcing read-only behavior in Streamlit historical mode.

This app uses an app-level mode switch (st.session_state.data_mode) to separate
"operacional" (2026+) from "historico" (2024/2025). In historical mode, we must
prevent *any* writes, even if a write-capable service method is called.

The guard intentionally becomes a no-op when Streamlit isn't available, so that
CLI/scripts (imports, maintenance jobs) can keep using the services.
"""

from __future__ import annotations

from typing import Optional


def get_data_mode(default: str = "operacional") -> str:
    try:
        import streamlit as st

        return str(st.session_state.get("data_mode", default))
    except Exception:
        return default


def ensure_writable(operation: Optional[str] = None) -> None:
    """Stops execution when running in Streamlit historical mode."""

    try:
        import streamlit as st
    except Exception:
        # Not running under Streamlit (e.g., scripts/) → don't block.
        return

    if get_data_mode() == "historico":
        op_text = f" ({operation})" if operation else ""
        st.error(f"🔒 Modo histórico (somente leitura){op_text}: operação bloqueada.")
        st.stop()
