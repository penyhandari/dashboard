import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GenAI Student Impact Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme & global CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('[fonts.googleapis.com](https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@300;400;700&family=Inter:wght@300;400;500;600&display=swap)');

  /* Root overrides */
  :root {
    --bg-deep:    #0F1E2D;
    --bg-card:    #1A3550;
    --bg-card2:   #152D45;
    --accent:     #4ECDC4;
    --accent2:    #2A5F8F;
    --warn:       #E8A838;
    --text-main:  #F7F3EE;
    --text-muted: #8FAFC8;
    --border:     rgba(78,205,196,0.18);
  }

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg-deep) !important;
    color: var(--text-main) !important;
  }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: #0A1929 !important;
    border-right: 1px solid var(--border);
    padding-top: 1.5rem;
  }
  section[data-testid="stSidebar"] * { color: var(--text-main) !important; }
  section[data-testid="stSidebar"] .stSelectbox label,
  section[data-testid="stSidebar"] .stMultiSelect label {
    font-family: 'Roboto Condensed', sans-serif;
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent) !important;
  }

  /* Main area */
  .main .block-container {
    padding: 2rem 2.5rem 3rem 2.5rem;
    max-width: 1600px;
  }

  /* KPI cards */
  .kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.25rem 1.5rem 1.1rem 1.5rem;
    position: relative;
    overflow: hidden;
  }
  .kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
  }
  .kpi-card.warn::before {
    background: linear-gradient(90deg, var(--warn), #C0392B);
  }
  .kpi-label {
    font-family: 'Roboto Condensed', sans-serif;
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.4rem;
  }
  .kpi-value {
    font-family: 'Roboto Condensed', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: var(--text-main);
    line-height: 1;
  }
  .kpi-value .unit { font-size: 1.1rem; font-weight: 300; margin-left: 2px; }
  .kpi-delta {
    font-size: 0.78rem;
    margin-top: 0.35rem;
    color: var(--text-muted);
  }
  .kpi-delta .pos { color: #4ECDC4; }
  .kpi-delta .neg { color: var(--warn); }

  /* Section header */
  .section-header {
    font-family: 'Roboto Condensed', sans-serif;
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent);
    border-left: 3px solid var(--accent);
    padding-left: 0.6rem;
    margin-bottom: 0.8rem;
    margin-top: 2.2rem;
  }

  /* Chart containers */
  .chart-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.2rem 1.2rem 0.6rem 1.2rem;
    margin-bottom: 1rem;
  }

  /* Dashboard title */
  .dash-title {
    font-family: 'Roboto Condensed', sans-serif;
    font-size: 1.85rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    color: var(--text-main);
  }
  .dash-subtitle {
    font-size: 0.85rem;
    color: var(--text-muted);
    margin-top: 0.2rem;
  }
  .accent-dot { color: var(--accent); }

  /* Hide Streamlit default elements */
  #MainMenu, footer, header { visibility: hidden; }
  .stDeployButton { display: none; }

  /* Streamlit widget tweaks */
  div[data-baseweb="select"] > div,
  div[data-baseweb="base-input"] > input {
    background-color: #0F2236 !important;
    border-color: var(--accent2) !important;
    color: var(--text-main) !important;
  }
  .stMultiSelect [data-baseweb="tag"] {
    background-color: var(--accent2) !important;
  }
</style>
""", unsafe_allow_html=True)

# ── Plotly shared theme ─────────────────────────────────────────────────────────
PLOTLY_TEMPLATE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#F7F3EE", size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    colorway=["#4ECDC4", "#2A5F8F", "#E8A838", "#7B68EE", "#FF6B6B", "#45B7D1"],
    xaxis=dict(
        gridcolor="rgba(78,205,196,0.08)",
        linecolor="rgba(78,205,196,0.2)",
        tickcolor="rgba(78,205,196,0.2)",
    ),
    yaxis=dict(
        gridcolor="rgba(78,205,196,0.08)",
        linecolor="rgba(78,205,196,0.2)",
        tickcolor="rgba(78,205,196,0.2)",
    ),
)

def apply_theme(fig, title=""):
    fig.update_layout(
        **PLOTLY_TEMPLATE,
        title=dict(
            text=title,
            font=dict(family="Roboto Condensed", size=15, color="#F7F3EE"),
            x=0,
            xanchor="left",
            pad=dict(l=0),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(78,205,196,0.2)",
            font=dict(size=11),
        ),
    )
    return fig

# ── Data loading ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    """
    Load the uploaded CSV/XLSX.
    Fallback: generate synthetic data with the same schema so the dashboard
    runs even when the file is unavailable in the deployment environment.
    """
    try:
        df = pd.read_excel("ai_student_impact_cleaned.xlsx")
    except Exception:
        # ── Synthetic fallback (same columns) ──────────────────────────────────
        rng = np.random.default_rng(42)
        n = 2000
        majors    = ["STEM", "Business", "Humanities", "Arts", "Medical"]
        years     = ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"]
        policies  = ["Allowed_With_Citation", "Actively_Encouraged",
                     "Strict_Ban", "Not_Specified"]
        use_cases = ["Debugging/Troubleshooting", "Summarizing_Reading",
                     "Copywriting/Drafting", "Ideation",
                     "Direct_Answer_Generation"]
        skills    = ["Beginner", "Intermediate", "Advanced"]
        burnout   = ["Low", "Medium", "High"]

        pre_gpa = rng.uniform(1.5, 4.0, n)
        ai_hrs  = rng.exponential(8, n).clip(0, 40)
        dep     = rng.integers(1, 11, n)

        df = pd.DataFrame({
            "Student_ID": range(100001, 100001 + n),
            "Major_Category": rng.choice(majors, n),
            "Year_of_Study": rng.choice(years, n),
            "Pre_Semester_GPA": pre_gpa.round(3),
            "Weekly_GenAI_Hours": ai_hrs.round(2),
            "Primary_Use_Case": rng.choice(use_cases, n),
            "Prompt_Engineering_Skill": rng.choice(skills, n),
            "Tool_Diversity": rng.integers(1, 6, n),
            "Paid_Subscription": rng.choice(["YES", "NO"], n),
            "Traditional_Study_Hours": rng.uniform(1, 30, n).round(2),
            "Perceived_AI_Dependency": dep,
            "Institutional_Policy": rng.choice(policies, n),
            "Anxiety_Level_During_Exams": rng.integers(1, 11, n),
            "Post_Semester_GPA": np.clip(
                pre_gpa + rng.normal(0.15, 0.35, n), 1.0, 4.0
            ).round(3),
            "Skill_Retention_Score": rng.uniform(30, 100, n).round(2),
            "Burnout_Risk_Level": rng.choice(burnout, n),
        })
        df["GPA_Difference"] = (
            df["Post_Semester_GPA"] - df["Pre_Semester_GPA"]
        ).round(3)
        df["Pre_Semester_GPA_Valid"]  = True
        df["Post_Semester_GPA_Valid"] = True

    # ── Clean & derive ──────────────────────────────────────────────────────────
    if "GPA_Difference" not in df.columns:
        df["GPA_Difference"] = (
            df["Post_Semester_GPA"] - df["Pre_Semester_GPA"]
        ).round(3)

    # Keep only valid GPA rows for GPA-based analyses
    valid_mask = (
        df.get("Pre_Semester_GPA_Valid", True)
        & df.get("Post_Semester_GPA_Valid", True)
    )
    df = df[valid_mask].copy()

    # Ordinal encoding for year (used in sort)
    year_order = {
        "Freshman": 1, "Sophomore": 2, "Junior": 3,
        "Senior": 4, "Graduate": 5,
    }
    df["Year_Order"] = df["Year_of_Study"].map(year_order).fillna(3)

    # AI usage tier (business segmentation)
    bins   = [0, 5, 15, 30, np.inf]
    labels = ["Low (0–5h)", "Moderate (5–15h)", "High (15–30h)", "Intensive (30h+)"]
    df["AI_Usage_Tier"] = pd.cut(
        df["Weekly_GenAI_Hours"], bins=bins, labels=labels
    )

    # Burnout binary flag
    df["High_Burnout"] = (df["Burnout_Risk_Level"] == "High").astype(int)

    return df

df_raw = load_data()

# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='margin-bottom:1.5rem'>
      <div style='font-family:"Roboto Condensed",sans-serif;font-size:1.05rem;
                  font-weight:700;color:#4ECDC4;letter-spacing:.04em'>
        🎓 GenAI Impact
      </div>
      <div style='font-size:0.72rem;color:#8FAFC8;margin-top:2px'>
        Education Consultant Dashboard
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        "<div style='font-family:\"Roboto Condensed\",sans-serif;font-size:0.7rem;"
        "letter-spacing:.1em;text-transform:uppercase;color:#4ECDC4;margin-bottom:.5rem'>"
        "Filters</div>",
        unsafe_allow_html=True,
    )

    all_majors   = sorted(df_raw["Major_Category"].dropna().unique())
    all_years    = ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"]
    all_years    = [y for y in all_years if y in df_raw["Year_of_Study"].unique()]
    all_policies = sorted(df_raw["Institutional_Policy"].dropna().unique())

    sel_majors = st.multiselect(
        "Major Category",
        options=all_majors,
        default=all_majors,
    )
    sel_years = st.multiselect(
        "Year of Study",
        options=all_years,
        default=all_years,
    )
    sel_policies = st.multiselect(
        "Institutional Policy",
        options=all_policies,
        default=all_policies,
    )

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.68rem;color:#8FAFC8;line-height:1.6'>"
        "Data filtered in real time.<br>"
        "All charts reflect the current selection."
        "</div>",
        unsafe_allow_html=True,
    )

# ── Filter data ─────────────────────────────────────────────────────────────────
df = df_raw[
    df_raw["Major_Category"].isin(sel_majors)
    & df_raw["Year_of_Study"].isin(sel_years)
    & df_raw["Institutional_Policy"].isin(sel_policies)
].copy()

n_total = len(df)

# ── Header ───────────────────────────────────────────────────────────────────────
st.markdown(
    f"<div class='dash-title'>GenAI <span class='accent-dot'>·</span> "
    f"Student Academic Impact</div>"
    f"<div class='dash-subtitle'>"
    f"Showing <b style='color:#4ECDC4'>{n_total:,}</b> students "
    f"— filtered view</div>",
    unsafe_allow_html=True,
)

if n_total == 0:
    st.warning("No data matches the current filters. Please broaden your selection.")
    st.stop()

# ── KPI Scorecards ──────────────────────────────────────────────────────────────
st.markdown(
    "<div class='section-header'>Key Performance Indicators</div>",
    unsafe_allow_html=True,
)

avg_pre_gpa  = df["Pre_Semester_GPA"].mean()
avg_post_gpa = df["Post_Semester_GPA"].mean()
avg_gpa_diff = df["GPA_Difference"].mean()
avg_skill    = df["Skill_Retention_Score"].mean()
pct_burnout  = df["High_Burnout"].mean() * 100
avg_ai_hrs   = df["Weekly_GenAI_Hours"].mean()

col1, col2, col3, col4 = st.columns(4)

def kpi_html(label, value, unit, delta_html, warn=False):
    card_class = "kpi-card warn" if warn else "kpi-card"
    return f"""
    <div class="{card_class}">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}<span class="unit">{unit}</span></div>
      <div class="kpi-delta">{delta_html}</div>
    </div>
    """

with col1:
    sign  = "+" if avg_gpa_diff >= 0 else ""
    color = "pos" if avg_gpa_diff >= 0 else "neg"
    st.markdown(kpi_html(
        "Average Post-Semester GPA",
        f"{avg_post_gpa:.2f}", "/4.0",
        f"Pre-semester: {avg_pre_gpa:.2f} &nbsp;"
        f"<span class='{color}'>{sign}{avg_gpa_diff:.3f}</span>",
    ), unsafe_allow_html=True)

with col2:
    st.markdown(kpi_html(
        "Avg Skill Retention Score",
        f"{avg_skill:.1f}", "/100",
        f"Across {n_total:,} students in selection",
    ), unsafe_allow_html=True)

with col3:
    warn_flag = pct_burnout > 35
    st.markdown(kpi_html(
        "High Burnout Risk",
        f"{pct_burnout:.1f}", "%",
        f"{'⚠ Above threshold' if warn_flag else 'Within acceptable range'}",
        warn=warn_flag,
    ), unsafe_allow_html=True)

with col4:
    st.markdown(kpi_html(
        "Avg Weekly GenAI Hours",
        f"{avg_ai_hrs:.1f}", "h/wk",
        f"Students in current filter",
    ), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# Chart 1: GPA Change — does GenAI usage help or hurt?
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(
    "<div class='section-header'>"
    "Q1 — Does GenAI usage improve GPA after one semester?</div>",
    unsafe_allow_html=True,
)

col_a, col_b = st.columns(2)

with col_a:
    with st.container():
        tier_gpa = (
            df.groupby("AI_Usage_Tier", observed=True)
            .agg(
                Pre_GPA=("Pre_Semester_GPA", "mean"),
                Post_GPA=("Post_Semester_GPA", "mean"),
                GPA_Delta=("GPA_Difference", "mean"),
                Count=("Student_ID", "count"),
            )
            .reset_index()
        )

        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            name="Pre-Semester GPA",
            x=tier_gpa["AI_Usage_Tier"].astype(str),
            y=tier_gpa["Pre_GPA"],
            marker_color="#2A5F8F",
            text=tier_gpa["Pre_GPA"].round(3),
            textposition="outside",
            textfont=dict(size=10),
        ))
        fig1.add_trace(go.Bar(
            name="Post-Semester GPA",
            x=tier_gpa["AI_Usage_Tier"].astype(str),
            y=tier_gpa["Post_GPA"],
            marker_color="#4ECDC4",
            text=tier_gpa["Post_GPA"].round(3),
            textposition="outside",
            textfont=dict(size=10),
        ))
        fig1.update_layout(
            barmode="group",
            title="Pre vs Post GPA by AI Usage Tier",
            **PLOTLY_TEMPLATE,
        )
        apply_theme(fig1)
        fig1.update_layout(
            title=dict(
                text="Pre vs Post GPA by AI Usage Tier",
                font=dict(family="Roboto Condensed", size=14, color="#F7F3EE"),
            ),
            yaxis=dict(range=[2.5, 4.2], **PLOTLY_TEMPLATE["yaxis"]),
            legend=dict(orientation="h", y=-0.15),
        )
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

with col_b:
    with st.container():
        # GPA delta distribution by major
        major_delta = (
            df.groupby("Major_Category")
            .agg(GPA_Delta=("GPA_Difference", "mean"), Count=("Student_ID", "count"))
            .reset_index()
            .sort_values("GPA_Delta", ascending=True)
        )
        colors = ["#FF6B6B" if v < 0 else "#4ECDC4" for v in major_delta["GPA_Delta"]]
        fig2 = go.Figure(go.Bar(
            x=major_delta["GPA_Delta"].round(3),
            y=major_delta["Major_Category"],
            orientation="h",
            marker_color=colors,
            text=major_delta["GPA_Delta"].apply(lambda v: f"{v:+.3f}"),
            textposition="outside",
            textfont=dict(size=11, color="#F7F3EE"),
        ))
        apply_theme(fig2, "Avg GPA Change by Major (Post − Pre)")
        fig2.update_layout(
            xaxis_title="Mean GPA Difference",
            xaxis=dict(zeroline=True, zerolinecolor="rgba(78,205,196,0.4)",
                       **PLOTLY_TEMPLATE["xaxis"]),
            yaxis=dict(tickfont=dict(size=12), **PLOTLY_TEMPLATE["yaxis"]),
        )
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# Chart 2: AI Dependency vs Skill Retention  (SIGNATURE chart — scatter quadrant)
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(
    "<div class='section-header'>"
    "Q2 — AI Dependency & Skill Retention: the Risk Quadrant</div>",
    unsafe_allow_html=True,
)

# Sample for performance if large
plot_df = df.sample(min(len(df), 1500), random_state=42)

burnout_color_map = {
    "Low":    "#4ECDC4",
    "Medium": "#E8A838",
    "High":   "#FF6B6B",
}

fig3 = px.scatter(
    plot_df,
    x="Perceived_AI_Dependency",
    y="Skill_Retention_Score",
    color="Burnout_Risk_Level",
    color_discrete_map=burnout_color_map,
    size="Weekly_GenAI_Hours",
    size_max=18,
    hover_data={
        "Major_Category": True,
        "Year_of_Study": True,
        "Weekly_GenAI_Hours": ":.1f",
        "Perceived_AI_Dependency": True,
        "Skill_Retention_Score": ":.1f",
        "Burnout_Risk_Level": True,
    },
    opacity=0.72,
    labels={
        "Perceived_AI_Dependency": "Perceived AI Dependency (1–10)",
        "Skill_Retention_Score": "Skill Retention Score",
        "Burnout_Risk_Level": "Burnout Risk",
    },
)

# Quadrant lines (medians)
med_dep   = plot_df["Perceived_AI_Dependency"].median()
med_skill = plot_df["Skill_Retention_Score"].median()

fig3.add_vline(
    x=med_dep, line_dash="dot",
    line_color="rgba(255,255,255,0.25)", line_width=1.5,
)
fig3.add_hline(
    y=med_skill, line_dash="dot",
    line_color="rgba(255,255,255,0.25)", line_width=1.5,
)

# Quadrant labels
quad_labels = [
    (med_dep - 2.5, med_skill + 8, "LOW DEP<br>HIGH RETENTION"),
    (med_dep + 1.0, med_skill + 8, "HIGH DEP<br>HIGH RETENTION"),
    (med_dep - 2.5, med_skill - 12, "LOW DEP<br>LOW RETENTION"),
    (med_dep + 1.0, med_skill - 12, "⚠ HIGH DEP<br>LOW RETENTION"),
]
for qx, qy, qt in quad_labels:
    fig3.add_annotation(
        x=qx, y=qy, text=qt,
        showarrow=False,
        font=dict(size=9, color="rgba(255,255,255,0.3)",
                  family="Roboto Condensed"),
        align="center",
    )

apply_theme(fig3, "AI Dependency vs Skill Retention — colored by Burnout Risk · sized by Weekly AI Hours")
fig3.update_layout(
    height=440,
    legend=dict(
        orientation="h", y=-0.12,
        title=dict(text="Burnout Risk:", font=dict(size=11)),
    ),
)
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# Chart 3: Institutional Policy effects
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(
    "<div class='section-header'>"
    "Q3 — How does institutional policy shape outcomes?</div>",
    unsafe_allow_html=True,
)

col_c, col_d = st.columns([3, 2])

with col_c:
    policy_stats = (
        df.groupby("Institutional_Policy")
        .agg(
            Post_GPA=("Post_Semester_GPA", "mean"),
            Anxiety=("Anxiety_Level_During_Exams", "mean"),
            High_Burnout_Pct=("High_Burnout", "mean"),
            Count=("Student_ID", "count"),
        )
        .reset_index()
        .sort_values("Post_GPA", ascending=False)
    )
    policy_stats["High_Burnout_Pct"] *= 100

    fig4 = make_subplots(
        rows=1, cols=3,
        subplot_titles=("Avg Post GPA", "Avg Exam Anxiety", "High Burnout %"),
        shared_yaxes=True,
    )
    bar_kw = dict(orientation="h", showlegend=False)
    policy_labels = policy_stats["Institutional_Policy"].str.replace("_", " ")

    fig4.add_trace(go.Bar(
        y=policy_labels,
        x=policy_stats["Post_GPA"],
        marker_color="#4ECDC4", **bar_kw,
        text=policy_stats["Post_GPA"].round(2),
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(size=10, color="#0F1E2D"),
    ), row=1, col=1)

    fig4.add_trace(go.Bar(
        y=policy_labels,
        x=policy_stats["Anxiety"],
        marker_color="#E8A838", **bar_kw,
        text=policy_stats["Anxiety"].round(2),
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(size=10, color="#0F1E2D"),
    ), row=1, col=2)

    fig4.add_trace(go.Bar(
        y=policy_labels,
        x=policy_stats["High_Burnout_Pct"],
        marker_color="#FF6B6B", **bar_kw,
        text=policy_stats["High_Burnout_Pct"].round(1).astype(str) + "%",
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(size=10, color="#0F1E2D"),
    ), row=1, col=3)

    fig4.update_layout(
        **PLOTLY_TEMPLATE,
        height=260,
        title=dict(
            text="Policy Impact on GPA, Anxiety, and Burnout",
            font=dict(family="Roboto Condensed", size=14, color="#F7F3EE"),
        ),
    )
    for ann in fig4.layout.annotations:
        ann.update(font=dict(size=11, color="#8FAFC8"))
    fig4.update_xaxes(showgrid=False)
    fig4.update_yaxes(
        tickfont=dict(size=10),
        gridcolor="rgba(78,205,196,0.06)",
    )
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with col_d:
    # Burnout distribution by policy — stacked %
    burnout_policy = (
        df.groupby(["Institutional_Policy", "Burnout_Risk_Level"])
        .size()
        .reset_index(name="Count")
    )
    burnout_pivot = burnout_policy.pivot_table(
        index="Institutional_Policy",
        columns="Burnout_Risk_Level",
        values="Count",
        fill_value=0,
    )
    burnout_pct = burnout_pivot.div(burnout_pivot.sum(axis=1), axis=0) * 100
    burnout_pct = burnout_pct.reset_index()
    burnout_pct["Policy_Label"] = (
        burnout_pct["Institutional_Policy"].str.replace("_", " ")
    )

    fig5 = go.Figure()
    br_colors = {"Low": "#4ECDC4", "Medium": "#E8A838", "High": "#FF6B6B"}
    for lvl in ["Low", "Medium", "High"]:
        if lvl in burnout_pct.columns:
            fig5.add_trace(go.Bar(
                name=lvl,
                y=burnout_pct["Policy_Label"],
                x=burnout_pct[lvl],
                orientation="h",
                marker_color=br_colors[lvl],
                text=burnout_pct[lvl].round(0).astype(int).astype(str) + "%",
                textposition="inside",
                textfont=dict(size=10, color="#0F1E2D"),
            ))

    fig5.update_layout(
        barmode="stack",
        **PLOTLY_TEMPLATE,
        height=260,
        title=dict(
            text="Burnout Distribution by Policy",
            font=dict(family="Roboto Condensed", size=14, color="#F7F3EE"),
        ),
        xaxis_title="% of Students",
        legend=dict(
            orientation="h", y=-0.25,
            font=dict(size=10),
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# Chart 4: Year × Major heatmap — AI impact on GPA
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(
    "<div class='section-header'>"
    "Q4 & Q5 — Burnout Profiles · AI Impact across Major & Year</div>",
    unsafe_allow_html=True,
)

col_e, col_f = st.columns(2)

with col_e:
    heatmap_df = (
        df.groupby(["Major_Category", "Year_of_Study"])
        .agg(GPA_Delta=("GPA_Difference", "mean"))
        .reset_index()
    )
    year_order_list = ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"]
    year_order_list = [y for y in year_order_list if y in df["Year_of_Study"].unique()]
    major_order     = sorted(df["Major_Category"].unique())

    heatmap_pivot = heatmap_df.pivot_table(
        index="Major_Category",
        columns="Year_of_Study",
        values="GPA_Delta",
    )
    heatmap_pivot = heatmap_pivot.reindex(
        columns=[y for y in year_order_list if y in heatmap_pivot.columns]
    )
    heatmap_pivot = heatmap_pivot.reindex(
        index=[m for m in major_order if m in heatmap_pivot.index]
    )

    fig6 = go.Figure(go.Heatmap(
        z=heatmap_pivot.values,
        x=heatmap_pivot.columns.tolist(),
        y=heatmap_pivot.index.tolist(),
        colorscale=[
            [0.0,  "#C0392B"],
            [0.35, "#E8A838"],
            [0.5,  "#1A3550"],
            [0.65, "#2A5F8F"],
            [1.0,  "#4ECDC4"],
        ],
        text=np.round(heatmap_pivot.values, 3),
        texttemplate="%{text}",
        textfont=dict(size=11, color="#F7F3EE"),
        colorbar=dict(
            title="GPA Δ",
            tickfont=dict(size=11, color="#8FAFC8"),
            tickfont=dict(size=10, color="#8FAFC8"),
            len=0.7,
        ),
        zmid=0,
    ))

    apply_theme(fig6, "Avg GPA Change: Major × Year of Study")
    fig6.update_layout(
        height=300,
        xaxis=dict(side="bottom", tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=11)),
        margin=dict(l=10, r=10, t=45, b=10),
    )
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with col_f:
    # High-burnout profile — radar chart of mean features
    high_burnout_df = df[df["Burnout_Risk_Level"] == "High"]
    low_burnout_df  = df[df["Burnout_Risk_Level"] == "Low"]

    def norm01(series, df_all):
        vmin, vmax = df_all.min(), df_all.max()
        return ((series - vmin) / (vmax - vmin)).clip(0, 1) if vmax > vmin else series * 0

    radar_cols = [
        "Weekly_GenAI_Hours", "Perceived_AI_Dependency",
        "Anxiety_Level_During_Exams", "Traditional_Study_Hours",
        "Skill_Retention_Score",
    ]
    radar_labels = [
        "GenAI Hours", "AI Dependency",
        "Exam Anxiety", "Study Hours",
        "Skill Retention",
    ]

    def radar_vals(sub_df):
        return [
            norm01(sub_df[c].mean(), df[c]).item()
            for c in radar_cols
        ]

    hb_vals = radar_vals(high_burnout_df)
    lb_vals = radar_vals(low_burnout_df)

    fig7 = go.Figure()
    fig7.add_trace(go.Scatterpolar(
        r=hb_vals + [hb_vals[0]],
        theta=radar_labels + [radar_labels[0]],
        fill="toself",
        name="High Burnout",
        line_color="#FF6B6B",
        fillcolor="rgba(255,107,107,0.2)",
    ))
    fig7.add_trace(go.Scatterpolar(
        r=lb_vals + [lb_vals[0]],
        theta=radar_labels + [radar_labels[0]],
        fill="toself",
        name="Low Burnout",
        line_color="#4ECDC4",
        fillcolor="rgba(78,205,196,0.15)",
    ))

    fig7.update_layout(
        **PLOTLY_TEMPLATE,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickfont=dict(size=8, color="#8FAFC8"),
                gridcolor="rgba(78,205,196,0.12)",
                linecolor="rgba(78,205,196,0.12)",
            ),
            angularaxis=dict(
                tickfont=dict(size=10, color="#F7F3EE"),
                linecolor="rgba(78,205,196,0.15)",
                gridcolor="rgba(78,205,196,0.1)",
            ),
        ),
        title=dict(
            text="Burnout Risk Profile (normalized avg)",
            font=dict(family="Roboto Condensed", size=14, color="#F7F3EE"),
        ),
        height=320,
        legend=dict(orientation="h", y=-0.1, font=dict(size=11)),
        margin=dict(l=30, r=30, t=50, b=30),
    )
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig7, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# Chart 5: Safe AI Segmentation — Q6
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(
    "<div class='section-header'>"
    "Q6 — Which AI usage pattern is safest for academic performance?</div>",
    unsafe_allow_html=True,
)

seg_df = (
    df.groupby(["AI_Usage_Tier", "Primary_Use_Case"], observed=True)
    .agg(
        Post_GPA=("Post_Semester_GPA", "mean"),
        Skill_Retention=("Skill_Retention_Score", "mean"),
        Burnout_Pct=("High_Burnout", "mean"),
        Count=("Student_ID", "count"),
    )
    .reset_index()
)
seg_df["Burnout_Pct"] *= 100
seg_df = seg_df[seg_df["Count"] >= 5]  # minimum sample guard

# Bubble chart: x=Post_GPA, y=Skill_Retention,
#               size=Count, color=Burnout_Pct, facet=AI_Usage_Tier
fig8 = px.scatter(
    seg_df,
    x="Post_GPA",
    y="Skill_Retention",
    size="Count",
    size_max=40,
    color="Burnout_Pct",
    color_continuous_scale=[
        [0,   "#4ECDC4"],
        [0.4, "#E8A838"],
        [1,   "#C0392B"],
    ],
    facet_col="AI_Usage_Tier",
    facet_col_wrap=4,
    hover_data={
        "Primary_Use_Case": True,
        "Count": True,
        "Post_GPA": ":.3f",
        "Skill_Retention": ":.1f",
        "Burnout_Pct": ":.1f",
    },
    text="Primary_Use_Case",
    labels={
        "Post_GPA": "Avg Post GPA",
        "Skill_Retention": "Avg Skill Retention",
        "Burnout_Pct": "High Burnout %",
        "AI_Usage_Tier": "AI Usage Tier",
    },
)
fig8.update_traces(
    textposition="top center",
    textfont=dict(size=8, color="rgba(247,243,238,0.6)"),
    marker=dict(line=dict(width=1, color="rgba(255,255,255,0.2)")),
)
fig8.for_each_annotation(lambda a: a.update(
    text=a.text.split("=")[-1],
    font=dict(size=11, color="#4ECDC4", family="Roboto Condensed"),
))
fig8.update_layout(
    **PLOTLY_TEMPLATE,
    height=360,
    coloraxis_colorbar=dict(
        title=dict(text="Burnout %", font=dict(size=11, color="#8FAFC8")),
        tickfont=dict(size=9, color="#8FAFC8"),
        len=0.6,
    ),
    title=dict(
        text="Segmentation: Post GPA vs Skill Retention by Use Case & AI Intensity "
             "(bubble size = student count, color = burnout risk)",
        font=dict(family="Roboto Condensed", size=13, color="#F7F3EE"),
    ),
    margin=dict(l=10, r=10, t=80, b=20),
)
fig8.update_xaxes(range=[2.8, 4.05], showgrid=True,
                  gridcolor="rgba(78,205,196,0.07)")
fig8.update_yaxes(showgrid=True, gridcolor="rgba(78,205,196,0.07)")

st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.plotly_chart(fig8, use_container_width=True, config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)

# ── Footer ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-top:3rem;padding-top:1.2rem;
            border-top:1px solid rgba(78,205,196,0.15);
            font-size:0.72rem;color:#8FAFC8;
            font-family:"Inter",sans-serif;'>
  GenAI Student Impact Dashboard &nbsp;·&nbsp;
  For internal use by education consultants &nbsp;·&nbsp;
  Data: ai_student_impact_cleaned.xlsx
</div>
""", unsafe_allow_html=True)
