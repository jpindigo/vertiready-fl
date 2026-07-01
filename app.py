"""
VertiReady FL — Florida Vertiport Readiness Play Tool (Streamlit)
A play tool that assesses Florida jurisdictions' readiness for Vertiports
based on Comprehensive Plan, Zoning Ordinance, and Development Procedures,
using FDOT Advanced Air Mobility guidance as reference.

Contact: John Patrick, AICP — john.patrick@burgessniple.com
"""

import streamlit as st
import plotly.graph_objects as go

from jurisdictions import (
    JURISDICTIONS,
    florida_averages,
    overall_score,
    readiness_tier,
)
from fdot_references import FDOT_REFERENCES
from ticker import render_ticker  # NEW

# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="VertiReady FL — Vertiport Readiness Play Tool",
    page_icon="🛩️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# Custom CSS — Florida sky-blue / sunshine palette
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* ---------- ADA / WCAG 2.1 AA compliant palette ---------- */
    :root {
        --ada-bg:            #F8FAFC;
        --ada-surface:       #FFFFFF;
        --ada-text:          #0B2545;
        --ada-text-muted:    #334155;
        --ada-primary:       #0B5FA5;
        --ada-primary-dark:  #083D6B;
        --ada-accent:        #B45309;
        --ada-success:       #166534;
        --ada-warning-bg:    #FEF3C7;
        --ada-warning-fg:    #78350F;
        --ada-danger:        #991B1B;
        --ada-border:        #CBD5E1;
        --ada-focus:         #1D4ED8;
    }

    /* Solid background (no low-contrast gradient behind body text) */
    .stApp { background: var(--ada-bg); color: var(--ada-text); }
    body, .stMarkdown, p, li, span, label { color: var(--ada-text); }

    /* Hero panel — dark solid ensures 4.5:1 for white text everywhere */
    .hero {
        background: var(--ada-primary-dark);
        color: #FFFFFF;
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 1.5rem;
        border: 1px solid var(--ada-primary);
    }
    .hero h1 { font-size: 2.25rem !important; font-weight: 800; margin: 0.5rem 0; color: #FFFFFF; }
    .hero p  { color: #FFFFFF; opacity: 1; font-size: 1rem; max-width: 700px; }

    .badge-pill {
        display: inline-block;
        background: #FFFFFF;
        color: var(--ada-primary-dark);
        border: 1px solid #FFFFFF;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Cards */
    .score-card {
        background: var(--ada-surface);
        border-radius: 0.75rem;
        padding: 1.25rem;
        border: 2px solid var(--ada-border);
    }
    .pillar-title { font-weight: 700; font-size: 1rem; margin-bottom: 0.5rem; color: var(--ada-text); }
    .score-big    { font-size: 2rem; font-weight: 800; color: var(--ada-primary); }

    /* Warnings — 6.9:1 dark orange on cream */
    .disclaimer-box {
        background: var(--ada-warning-bg);
        border-left: 6px solid var(--ada-accent);
        padding: 1rem 1.25rem;
        border-radius: 0.5rem;
        color: var(--ada-warning-fg);
        margin: 1rem 0;
        font-weight: 500;
    }
    .disclaimer-box a { color: var(--ada-warning-fg); text-decoration: underline; }

    /* Reference cards */
    .reference-card {
        background: var(--ada-surface);
        border: 2px solid var(--ada-border);
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }
    .reference-card p { color: var(--ada-text-muted); font-size: 0.9rem; }

    /* Pillar tag — 6.8:1 white on ocean blue */
    .pillar-tag {
        display: inline-block;
        background: var(--ada-primary);
        color: #FFFFFF;
        padding: 0.2rem 0.55rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: 700;
        margin-right: 0.35rem;
        margin-top: 0.35rem;
    }

    /* Contact card */
    .contact-card {
        background: var(--ada-surface);
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 2px solid var(--ada-border);
        margin-top: 1rem;
    }
    .contact-card a { color: var(--ada-primary); text-decoration: underline; }

    /* Links everywhere — always underlined, always high-contrast */
    a { color: var(--ada-primary); text-decoration: underline; }
    a:hover { color: var(--ada-primary-dark); }

    /* Buttons — Streamlit primary */
    .stButton > button[kind="primary"] {
        background: var(--ada-primary) !important;
        color: #FFFFFF !important;
        border: 2px solid var(--ada-primary-dark) !important;
        font-weight: 700 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: var(--ada-primary-dark) !important;
    }

    /* Visible keyboard focus (WCAG 2.4.7) */
    *:focus-visible {
        outline: 3px solid var(--ada-focus) !important;
        outline-offset: 2px !important;
        border-radius: 4px;
    }

    /* Streamlit metric widget */
    div[data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 800;
        color: var(--ada-primary);
    }
    div[data-testid="stMetricLabel"] { color: var(--ada-text); font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)
# ----------------------------------------------------------------------------
# Session state — disclaimer gate
# ----------------------------------------------------------------------------
if "disclaimer_accepted" not in st.session_state:
    st.session_state.disclaimer_accepted = False


def show_disclaimer_gate():
    st.markdown(
        """
        <div class="hero">
            <span class="badge-pill">⚠️ Play Tool Disclosure</span>
            <h1>Welcome to VertiReady FL</h1>
            <p>A notional readiness assessment for Florida jurisdictions' Comprehensive Plans,
            Zoning Ordinances, and Development Procedures for Vertiports.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.warning(
        "**This application is a PLAY TOOL only.** "
        "Results are illustrative and reference FDOT Advanced Air Mobility guidance for context."
    )
    st.markdown("### Before you continue, please acknowledge:")
    st.markdown(
        """
        - 🛡️ Results **must not be relied upon** for any policy, planning, investment, regulatory, or business decision.
        - 🛩️ Always consult the jurisdiction's adopted Comprehensive Plan, Land Development Code, and official FAA / FDOT guidance.
        - ⚠️ Scores are derived from a notional rubric and do not represent the official position of any agency or employer.
        """
    )
    agree = st.checkbox(
        "I acknowledge that **VertiReady FL is a play tool** and that I will not use its "
        "results for decision-making.",
        key="agree_check",
    )
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("I understand", type="primary", disabled=not agree, use_container_width=True):
            st.session_state.disclaimer_accepted = True
            st.rerun()
    with col2:
        st.caption("Questions? Contact **John Patrick, AICP** — john.patrick@burgessniple.com")


def sidebar_nav():
    st.sidebar.markdown("# 🛩️ VertiReady FL")
    st.sidebar.caption("Florida Vertiport Readiness Play Tool")
    page = st.sidebar.radio(
        "Navigate",
        ["✨ Assessment", "📖 Methodology", "✉️ Contact"],
        label_visibility="collapsed",
    )
    st.sidebar.markdown("---")
    st.sidebar.info(
        "⚠️ **Play Tool** — Do not use results for real decisions.\n\n"
        "Discuss with **John Patrick, AICP** — john.patrick@burgessniple.com"
    )
    return page


# --- Charts (unchanged) -----------------------------------------------------
def radar_chart(plan_score, zoning_score, proc_score):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[plan_score, zoning_score, proc_score, plan_score],
        theta=["Comp. Plan", "Zoning", "Procedures", "Comp. Plan"],
        fill="toself",
        fillcolor="rgba(11, 95, 165, 0.30)",   # ADA primary, 30% opacity
        line=dict(color="#0B5FA5", width=3),
        marker=dict(size=10, color="#0B2545", symbol="circle"),  # dark markers for shape+color redundancy
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10],
                            tickfont=dict(size=12, color="#0B2545"),
                            gridcolor="#CBD5E1"),
            angularaxis=dict(tickfont=dict(size=13, color="#0B2545", family="Arial Black"),
                             gridcolor="#CBD5E1"),
            bgcolor="#FFFFFF",
        ),
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=20),
        height=320,
        paper_bgcolor="#FFFFFF",
    )
    return fig


def comparison_chart(jurisdiction_scores, fl_avg):
    pillars = ["Comp. Plan", "Zoning", "Procedures"]
    fig = go.Figure(data=[
        go.Bar(
            name="Selected Jurisdiction",
            x=pillars, y=jurisdiction_scores,
            marker=dict(color="#4477AA", line=dict(color="#0B2545", width=1.5)),
            text=[f"{s:.1f}" for s in jurisdiction_scores],
            textposition="outside",
            textfont=dict(color="#0B2545", size=13, family="Arial Black"),
        ),
        go.Bar(
            name="Florida Average",
            x=pillars, y=fl_avg,
            marker=dict(
                color="#CCBB44",
                line=dict(color="#0B2545", width=1.5),
                pattern=dict(shape="/", fgcolor="#0B2545", size=8),   # diagonal stripes for non-color redundancy
            ),
            text=[f"{s:.1f}" for s in fl_avg],
            textposition="outside",
            textfont=dict(color="#0B2545", size=13, family="Arial Black"),
        ),
    ])
    fig.update_layout(
        barmode="group",
        yaxis=dict(range=[0, 10.5], title="Score (1–10)",
                   tickfont=dict(color="#0B2545"), gridcolor="#CBD5E1"),
        xaxis=dict(tickfont=dict(color="#0B2545", size=13)),
        height=340,
        margin=dict(l=40, r=20, t=30, b=40),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        legend=dict(orientation="h", y=1.15, font=dict(color="#0B2545", size=13)),
    )
    return fig


def overall_gauge(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Overall Readiness", "font": {"size": 16, "color": "#0B2545"}},
        number={"font": {"color": "#0B2545", "size": 40}},
        gauge={
            "axis": {"range": [0, 10], "tickwidth": 1, "tickcolor": "#0B2545",
                     "tickfont": {"color": "#0B2545"}},
            "bar": {"color": "#0B5FA5"},
            "bgcolor": "#FFFFFF",
            "borderwidth": 2,
            "bordercolor": "#0B2545",
            # Sequential ramp (dark → light of a single hue family) is CB-safe
            "steps": [
                {"range": [0, 4],  "color": "#F1F5F9"},
                {"range": [4, 6],  "color": "#CBD5E1"},
                {"range": [6, 8],  "color": "#94A3B8"},
                {"range": [8, 10], "color": "#64748B"},
            ],
            "threshold": {"line": {"color": "#991B1B", "width": 4},
                          "thickness": 0.85, "value": 10},
        },
    ))
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=20),
                      paper_bgcolor="#FFFFFF")
    return fig


# --- Pages (unchanged content) ----------------------------------------------
def page_assessment():
    st.markdown(
        """
        <div class="hero">
            <span class="badge-pill">✨ Play Tool • Notional Assessment</span>
            <h1>Is your Florida jurisdiction ready for Vertiports?</h1>
            <p>Explore a notional 1–10 readiness score across each jurisdiction's Comprehensive Plan,
            Zoning Ordinance, and Development Procedures — with rationale informed by FDOT Advanced
            Air Mobility guidance. A perfect 10 is reserved for jurisdictions that are fully ready
            across all three pillars.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 📍 Select a Florida jurisdiction")
    names = [f"{j['name']} ({j['type']}) — {j['region']}" for j in JURISDICTIONS]
    selection = st.selectbox(
        "Choose a county or city",
        options=["— Select a jurisdiction —"] + names,
        label_visibility="collapsed",
    )
    st.caption(
        f"Includes all 67 Florida counties plus a broad set of incorporated cities "
        f"({len(JURISDICTIONS)} total jurisdictions)."
    )

    if selection == "— Select a jurisdiction —":
        st.info("👆 Pick a county or city from the dropdown above to see its readiness scores.")
        return

    idx = names.index(selection)
    j = JURISDICTIONS[idx]
    overall = overall_score(j)
    tier = readiness_tier(overall)
    fl_avg = florida_averages()

    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"## {j['name']}")
        st.markdown(
            f"**Type:** {j['type']}  |  **Region:** {j['region']}  |  **Tier:** :blue[{tier['label']}]"
        )
        if overall < 10:
            st.caption(
                "ℹ️ A score of 10 is only awarded when the Comprehensive Plan, Zoning Ordinance, "
                "and Development Procedures are all fully ready for Vertiports."
            )
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Comp. Plan", f"{j['comprehensive_plan']['score']}/10")
        m2.metric("Zoning", f"{j['zoning_ordinance']['score']}/10")
        m3.metric("Procedures", f"{j['development_procedures']['score']}/10")
        m4.metric("Overall", f"{overall}/10")
    with col2:
        st.plotly_chart(overall_gauge(overall), use_container_width=True)

    st.markdown("### Pillar Scores & Rationale")
    p1, p2, p3 = st.columns(3)
    pillars = [
        ("📄 Comprehensive Plan", j["comprehensive_plan"], p1),
        ("🗺️ Zoning Ordinance", j["zoning_ordinance"], p2),
        ("📋 Development Procedures", j["development_procedures"], p3),
    ]
    for title, pillar, col in pillars:
        with col:
            st.markdown(
                f"""<div class="score-card"><div class="pillar-title">{title}</div>
                <div class="score-big">{pillar['score']}/10</div></div>""",
                unsafe_allow_html=True,
            )
            st.progress(pillar["score"] / 10)
            for bullet in pillar["rationale"]:
                st.markdown(f"- {bullet}")

    st.markdown("### 📊 Visualizations")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Pillar Profile (Radar)**")
        st.plotly_chart(
            radar_chart(j["comprehensive_plan"]["score"], j["zoning_ordinance"]["score"], j["development_procedures"]["score"]),
            use_container_width=True,
        )
    with c2:
        st.markdown("**Compared to Florida Average**")
        st.plotly_chart(
            comparison_chart(
                [j["comprehensive_plan"]["score"], j["zoning_ordinance"]["score"], j["development_procedures"]["score"]],
                [fl_avg["plan"], fl_avg["zoning"], fl_avg["proc"]],
            ),
            use_container_width=True,
        )

    with st.expander("📚 FDOT AAM Reference Framework used for this assessment", expanded=False):
        for ref in FDOT_REFERENCES:
            tags = "".join([f'<span class="pillar-tag">{p}</span>' for p in ref["pillars"]])
            st.markdown(
                f"""<div class="reference-card"><strong>{ref['title']}</strong>
                <p style="color:#475569; font-size:0.85rem; margin: 0.35rem 0;">{ref['description']}</p>
                {tags}</div>""",
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <div class="disclaimer-box">
        ⚠️ <strong>Reminder:</strong> VertiReady FL is a play tool. The scores shown are illustrative
        only and must not be relied upon for any decision.
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_methodology():
    st.markdown("# 📖 Methodology")
    st.markdown(
        "VertiReady FL assigns a notional 1–10 readiness score across three pillars informed by "
        "FDOT Advanced Air Mobility (AAM) guidance. A perfect 10 is reserved for jurisdictions "
        "that are ready across all three pillars simultaneously."
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 📄 Comprehensive Plan")
        st.markdown("- AAM-supportive Future Land Use language\n- Transportation Element references vertiports\n- Capital Improvements anticipates AAM\n- Intergovernmental coordination with FAA/FDOT")
    with c2:
        st.markdown("#### 🗺️ Zoning Ordinance")
        st.markdown("- 'Vertiport' defined as a permitted use\n- Use table entries in C/I/T districts\n- Noise, lighting, safety performance standards\n- Overlay or SUP pathway for vertiports")
    with c3:
        st.markdown("#### 📋 Development Procedures")
        st.markdown("- Pre-application pathway for vertiports\n- Site plan: TLOF, FATO, charging\n- FAA 7480-1 / FDOT Aviation coordination\n- Tailored public engagement")

    st.markdown("---")
    st.markdown("## 📚 FDOT AAM References")
    for ref in FDOT_REFERENCES:
        tags = "".join([f'<span class="pillar-tag">{p}</span>' for p in ref["pillars"]])
        st.markdown(
            f"""<div class="reference-card"><strong>{ref['title']}</strong>
            <p style="color:#475569; font-size:0.9rem; margin: 0.5rem 0;">{ref['description']}</p>
            {tags}</div>""",
            unsafe_allow_html=True,
        )


def page_contact():
    st.markdown("# ✉️ Let's talk Vertiports")
    st.markdown(
        "Interested in discussing Florida Vertiport readiness, FDOT Advanced Air Mobility guidance, "
        "or how local Comprehensive Plans, Zoning Ordinances, and Development Procedures can prepare?"
    )
    st.markdown(
        """
        <div class="contact-card">
            <h2 style="margin:0; color:#0c4a6e;">🛩️ John Patrick, AICP</h2>
            <p style="color:#475569; margin: 0.25rem 0 1rem 0;">Planner • Tampa, FL</p>
            <p>📧 mailto:john.patrick@burgessniple.com<strong>john.patrick@burgessniple.com</strong></a></p>
            <p>💼 AICP — Certified Planner</p>
            <p>📍 Tampa, Florida</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.link_button(
        "📧 Email John Patrick, AICP",
        "mailto:john.patrick@burgessniple.com?subject=Discussion%3A%20VertiReady%20FL%20%26%20Florida%20Vertiport%20Readiness",
        type="primary",
    )


# ----------------------------------------------------------------------------
# Main routing
# ----------------------------------------------------------------------------
def main():
    if not st.session_state.disclaimer_accepted:
        show_disclaimer_gate()
    else:
        page = sidebar_nav()
        if page == "✨ Assessment":
            page_assessment()
        elif page == "📖 Methodology":
            page_methodology()
        elif page == "✉️ Contact":
            page_contact()

    # Render the live visitor ticker on EVERY page (including the disclaimer gate).
    render_ticker()


if __name__ == "__main__":
    main()
