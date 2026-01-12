"""UI helpers shared across Streamlit pages."""

from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path
from typing import Optional

import streamlit as st


@lru_cache(maxsize=64)
def _image_to_data_uri_cached(resolved_path: str, mtime_ns: int) -> Optional[str]:
    path = Path(resolved_path)
    if not path.exists() or not path.is_file():
        return None

    suffix = path.suffix.lower().lstrip(".")
    mime = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
        "svg": "image/svg+xml",
    }.get(suffix, "application/octet-stream")

    try:
        data_b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    except OSError:
        return None

    _ = mtime_ns
    return f"data:{mime};base64,{data_b64}"


def _image_to_data_uri(image_path: str | Path) -> Optional[str]:
    path = Path(image_path)
    if not path.exists() or not path.is_file():
        return None

    resolved = str(path.resolve())
    try:
        mtime_ns = path.stat().st_mtime_ns
    except OSError:
        mtime_ns = 0

    return _image_to_data_uri_cached(resolved, mtime_ns)


def render_brand_header(
    *,
    title: str,
    subtitle: str,
    logo_path: str | Path,
    logo_width_px: int = 88,
    container_class: str = "brand-header",
) -> None:
    """Renders a centered header with logo inside the dark frame.

    Uses a data-uri so the logo is truly *inside* the HTML frame.
    """

    data_uri = _image_to_data_uri(logo_path)
    logo_html = (
        f'<img class="brand-logo" src="{data_uri}" style="width:{logo_width_px}px" />'
        if data_uri
        else ""
    )

    st.markdown(
        f"""
        <style>
        .{container_class} {{
            background: linear-gradient(90deg, #282828 0%, #000000 100%);
            padding: 1.25rem 1rem;
            border-radius: 12px;
            color: #F8F8F8;
            text-align: center;
            margin: 0.25rem 0 1.5rem;
            border-bottom: 3px solid #881818;
            box-shadow: 0 10px 30px rgba(0,0,0,0.18);
        }}
        .{container_class} .brand-logo {{
            display: block;
            margin: 0 auto 0.75rem;
            filter: drop-shadow(0 6px 10px rgba(0,0,0,0.35));
        }}
        .{container_class} h1 {{
            margin: 0;
            font-weight: 700;
            letter-spacing: 0.3px;
        }}
        .{container_class} p {{
            margin: 0.35rem 0 0;
            opacity: 0.9;
        }}
        </style>
        <div class="{container_class}">
            {logo_html}
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
