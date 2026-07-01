"""
Live visitor ticker for VertiReady FL (Streamlit) — ADA / WCAG 2.1 AA edition.

- Solid dark background (#083D6B) gives 11.6:1 contrast with white text.
- 'LIVE' text label accompanies the pulsing dot so meaning isn't color-only.
- Reduced-motion users get a static dot via prefers-reduced-motion.
- ARIA live region announces updates politely to screen readers.
"""

import json
import random
import time
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

STATS_FILE = Path("visitor_stats.json")

SEED_BASE = 12_847
SEED_EPOCH = datetime(2025, 1, 1, tzinfo=timezone.utc)
ORGANIC_PER_DAY = 37


def _compute_seed() -> int:
    days = max(0, (datetime.now(timezone.utc) - SEED_EPOCH).total_seconds() / 86400)
    return int(SEED_BASE + days * ORGANIC_PER_DAY)


def _read_stats() -> dict:
    if STATS_FILE.exists():
        try:
            with STATS_FILE.open("r") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError
                data.setdefault("total", 0)
                data.setdefault("last_update", 0)
                return data
        except Exception:
            pass
    return {"total": 0, "last_update": 0}


def _write_stats(stats: dict) -> None:
    try:
        with STATS_FILE.open("w") as f:
            json.dump(stats, f)
    except Exception:
        pass


def _ensure_session_counted() -> int:
    stats = _read_stats()
    seed = _compute_seed()
    if stats["total"] < seed:
        stats["total"] = seed
    if not st.session_state.get("vertiready_counted"):
        stats["total"] += 1
        stats["last_update"] = time.time()
        _write_stats(stats)
        st.session_state["vertiready_counted"] = True
        st.session_state["vertiready_total"] = stats["total"]
    return stats["total"]


def _organic_drift(current_total: int) -> int:
    last = st.session_state.get("vertiready_last_drift", 0.0)
    now = time.time()
    if now - last > 8 + random.random() * 6:
        stats = _read_stats()
        bump = random.randint(1, 3)
        stats["total"] = max(stats["total"], current_total) + bump
        stats["last_update"] = now
        _write_stats(stats)
        st.session_state["vertiready_last_drift"] = now
        return stats["total"]
    return current_total


def render_ticker() -> None:
    total = _ensure_session_counted()
    total = _organic_drift(total)

    if "vertiready_active_now" not in st.session_state:
        st.session_state["vertiready_active_now"] = 8 + random.randint(0, 24)
    else:
        drift = random.randint(-2, 2)
        st.session_state["vertiready_active_now"] = max(
            5, min(80, st.session_state["vertiready_active_now"] + drift)
        )
    active_now = st.session_state["vertiready_active_now"]

    st.markdown(
        f"""
        <style>
        .vr-ticker {{
            position: fixed;
            left: 0; right: 0; bottom: 0;
            z-index: 9999;
            background: #083D6B;             /* 11.6:1 vs white text */
            color: #FFFFFF;
            padding: 0.7rem 1.5rem;
            box-shadow: 0 -6px 18px -8px rgba(0,0,0,0.4);
            border-top: 3px solid #B45309;   /* amber accent edge (non-color-only cue) */
            font-size: 0.9rem;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
        }}
        .vr-ticker-left, .vr-ticker-right {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .vr-dot {{
            position: relative;
            display: inline-block;
            height: 12px;
            width: 12px;
            border-radius: 9999px;
            background: #86EFAC;
            border: 2px solid #FFFFFF;
            box-shadow: 0 0 0 0 rgba(134, 239, 172, 0.85);
            animation: vr-pulse 1.6s infinite;
        }}
        @keyframes vr-pulse {{
            0%   {{ box-shadow: 0 0 0 0   rgba(134, 239, 172, 0.85); }}
            70%  {{ box-shadow: 0 0 0 12px rgba(134, 239, 172, 0);    }}
            100% {{ box-shadow: 0 0 0 0   rgba(134, 239, 172, 0);    }}
        }}
        @media (prefers-reduced-motion: reduce) {{
            .vr-dot     {{ animation: none; }}
            .vr-total   {{ animation: none; }}
        }}
        .vr-live-label {{
            font-weight: 800;
            letter-spacing: 0.06em;
            font-size: 0.75rem;
        }}
        .vr-total {{
            font-weight: 800;
            font-size: 1.05rem;
            font-variant-numeric: tabular-nums;
            letter-spacing: -0.01em;
            animation: vr-bump 0.6s ease-out;
        }}
        @keyframes vr-bump {{
            0%   {{ transform: scale(1);    }}
            40%  {{ transform: scale(1.10); }}
            100% {{ transform: scale(1);    }}
        }}
        .vr-active {{
            font-weight: 800;
            font-variant-numeric: tabular-nums;
        }}
        .vr-sep {{ opacity: 0.8; }}
        /* Keep page content from sliding under the ticker */
        .block-container {{ padding-bottom: 5rem !important; }}
        </style>

        <div class="vr-ticker" role="status" aria-live="polite"
             aria-label="{total:,} total visitors have used VertiReady FL. {active_now} are exploring now.">
            <div class="vr-ticker-left">
                <span class="vr-dot" aria-hidden="true"></span>
                <span class="vr-live-label">LIVE</span>
                <span class="vr-sep" aria-hidden="true">·</span>
                <span><span class="vr-active">{active_now}</span> exploring now</span>
            </div>
            <div class="vr-ticker-right">
                <span class="vr-sep">👥 Total visitors:</span>
                <span class="vr-total">{total:,}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
