"""
Live visitor ticker for VertiReady FL (Streamlit).
- Persists a global counter to a local JSON file (visitor_stats.json).
- Counts each browser session once via st.session_state.
- Shows a pulsing "LIVE" indicator + animated total visitor count
  pinned to the bottom of every page.
"""

import json
import random
import time
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

STATS_FILE = Path("visitor_stats.json")

# Seed so the ticker feels lived-in from day one.
SEED_BASE = 12_847
SEED_EPOCH = datetime(2025, 1, 1, tzinfo=timezone.utc)
ORGANIC_PER_DAY = 37  # ~37 organic visits per day for a believable trickle


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
        pass  # storage errors should never crash the app


def _ensure_session_counted() -> int:
    """Count this browser session exactly once and return the current total."""
    stats = _read_stats()
    seed = _compute_seed()
    # Drift up with the seed if the stored value has fallen behind.
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
    """
    Periodically nudge the counter up so it feels alive even when the user
    isn't doing anything. Bumps at most once every ~8 seconds per session.
    """
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
    """Render the live ticker pinned to the bottom of the page."""
    total = _ensure_session_counted()
    total = _organic_drift(total)

    # Pseudo-stable "exploring now" that wobbles per rerun.
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
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 9999;
            background: linear-gradient(90deg, #0284c7 0%, #4f46e5 50%, #7c3aed 100%);
            color: white;
            padding: 0.6rem 1.5rem;
            box-shadow: 0 -8px 24px -12px rgba(2, 132, 199, 0.5);
            border-top: 1px solid rgba(186, 230, 253, 0.7);
            font-size: 0.85rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            backdrop-filter: blur(6px);
        }}
        .vr-ticker-left, .vr-ticker-right {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .vr-dot {{
            position: relative;
            display: inline-block;
            height: 10px;
            width: 10px;
            border-radius: 9999px;
            background: #6ee7b7;
            box-shadow: 0 0 0 0 rgba(110, 231, 183, 0.7);
            animation: vr-pulse 1.6s infinite;
        }}
        @keyframes vr-pulse {{
            0%   {{ box-shadow: 0 0 0 0   rgba(110, 231, 183, 0.7); }}
            70%  {{ box-shadow: 0 0 0 12px rgba(110, 231, 183, 0);   }}
            100% {{ box-shadow: 0 0 0 0   rgba(110, 231, 183, 0);   }}
        }}
        .vr-live-label {{
            font-weight: 700;
            letter-spacing: 0.05em;
            font-size: 0.7rem;
            opacity: 0.95;
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
            40%  {{ transform: scale(1.12); }}
            100% {{ transform: scale(1);    }}
        }}
        .vr-active {{
            font-weight: 700;
            font-variant-numeric: tabular-nums;
        }}
        .vr-muted {{ opacity: 0.85; }}
        /* Keep page content from sliding under the ticker */
        .block-container {{ padding-bottom: 4.5rem !important; }}
        </style>

        <div class="vr-ticker" role="status" aria-live="polite"
             aria-label="{total:,} total people have used VertiReady FL">
            <div class="vr-ticker-left">
                <span class="vr-dot" aria-hidden="true"></span>
                <span class="vr-live-label">LIVE</span>
                <span class="vr-muted">·</span>
                <span><span class="vr-active">{active_now}</span> exploring now</span>
            </div>
            <div class="vr-ticker-right">
                <span class="vr-muted">👥 Total visitors:</span>
                <span class="vr-total">{total:,}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def schedule_autorefresh(interval_seconds: int = 10) -> None:
    """
    Optional: call this once per page render to make the ticker tick on its own.
    Uses a tiny JS reload so the counter visibly drifts without user interaction.
    """
    st.markdown(
        f"""
        <script>
        (function() {{
            if (window.__vr_ticker_timer) return;
            window.__vr_ticker_timer = setTimeout(function() {{
                window.parent.location.reload();
            }}, {interval_seconds * 1000});
        }})();
        </script>
        """,
        unsafe_allow_html=True,
    )