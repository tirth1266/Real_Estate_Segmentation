# Streamlit app following the PRD: 4 modules + 4 top filters (+ AI chat tab)
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Buyer Segmentation", page_icon="🏢", layout="wide",
                   initial_sidebar_state="collapsed")

SEG_COL = "segment"
ID_COL = "client_ref"
FILTER_COLS = ["country", "region", "acquisition_purpose", "client_type"]
FILTER_LABELS = {
    "country": "Country",
    "region": "Region",
    "acquisition_purpose": "Purpose",
    "client_type": "Client type",
}

# `use_container_width` was replaced by `width="stretch"` in newer Streamlit
_v = tuple(int(x) for x in st.__version__.split(".")[:2])
STRETCH = {"width": "stretch"} if _v >= (1, 50) else {"use_container_width": True}

# Apple system colors
PALETTE = ["#0071E3", "#34C759", "#FF9F0A", "#AF52DE", "#FF375F", "#5AC8FA", "#8E8E93"]
METRIC_LABELS = {
    "n_purchase": "Purchases per client",
    "avg_price": "Average price",
    "avg_price_per_sqft": "Average price per sq ft",
    "pct_office": "Share of office purchases",
}

# ---------- Styling ----------
st.markdown(
    """
<style>
/* base */
.stApp {background:#F5F5F7; color:#1D1D1F;
  font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","SF Pro Text","Inter","Segoe UI",Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased;}
.block-container {padding-top: 2.5rem; padding-bottom: 4rem; max-width: 1200px;}
[data-testid="stAppDeployButton"], #MainMenu, footer {display: none;}
[data-testid="stHeader"] {background: transparent;}
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {display: none;}

/* hero: plain, large type */
.hero {padding: .5rem 0 1.6rem;}
.hero h1 {margin:0; padding:0; font-size:2.9rem; font-weight:700; letter-spacing:-.035em;
  color:#1D1D1F; line-height:1.08;}
.hero p {margin:.6rem 0 0; color:#6E6E73; font-size:1.2rem; font-weight:400; letter-spacing:-.01em;}
.hero .count {display:inline-block; margin-top:1rem; color:#0071E3; font-size:.95rem; font-weight:500;}

/* filter card */
[data-testid="stVerticalBlockBorderWrapper"]:has(.fbar-marker) {
  background:#FFFFFF; border:none; border-radius:20px;
  box-shadow: 0 1px 2px rgba(0,0,0,.04), 0 8px 24px rgba(0,0,0,.05);
  padding: .6rem .8rem;
}
.fbar-title {font-weight:600; font-size:1.05rem; color:#1D1D1F; padding-top:.3rem; letter-spacing:-.01em;}
.fbar-label {font-size:.75rem; font-weight:500; color:#6E6E73; margin:.3rem 0 .35rem;}
.meter {height:4px; border-radius:999px; background:#E8E8ED; overflow:hidden; margin-top:.9rem;}
.meter > div {height:100%; border-radius:999px; background:#0071E3; transition: width .5s ease;}
.meter-text {font-size:.78rem; color:#6E6E73; margin-top:.35rem;}

/* popover buttons + pills: soft gray capsules, blue when active */
[data-testid="stPopover"] button, [data-testid="stPopoverButton"] {
  border-radius:999px; background:#F5F5F7; border:none; color:#1D1D1F;
  font-weight:500; font-size:.85rem; box-shadow:none;}
[data-testid="stPopover"] button:hover, [data-testid="stPopoverButton"]:hover {background:#E8E8ED;}
button[kind="pills"], [data-testid="stBaseButton-pills"] {
  border-radius:999px; background:#F5F5F7; border:none; color:#1D1D1F;
  font-size:.82rem; font-weight:500;}
button[kind="pillsActive"], [data-testid="stBaseButton-pillsActive"] {
  border-radius:999px; background:#0071E3; border:none; color:#fff;
  font-size:.82rem; font-weight:500;}

/* buttons */
.stButton > button, [data-testid="stBaseButton-secondary"] {
  border-radius:999px; font-weight:500; background:#F5F5F7; border:none; color:#0071E3;}
.stButton > button:hover {background:#E8E8ED; color:#0058B0;}

/* KPI cards */
.kpi {background:#fff; border-radius:20px; padding:1.2rem 1.4rem;
  box-shadow: 0 1px 2px rgba(0,0,0,.04), 0 6px 18px rgba(0,0,0,.04);}
.kpi .label {color:#6E6E73; font-size:.78rem; font-weight:500;}
.kpi .value {color:#1D1D1F; font-size:2rem; font-weight:600; line-height:1.15; margin-top:.35rem;
  letter-spacing:-.025em;}
.kpi .note {color:#86868B; font-size:.8rem; margin-top:.25rem;}

/* tabs: segmented control */
.stTabs [data-baseweb="tab-list"] {background:#E8E8ED; padding:3px; border-radius:12px; gap:2px;
  width:fit-content; border:none;}
.stTabs [data-baseweb="tab"] {height:2.1rem; padding:0 1.05rem; border-radius:9px;
  font-weight:500; font-size:.88rem; color:#515154; background:transparent;}
.stTabs [aria-selected="true"] {background:#fff; color:#1D1D1F; box-shadow:0 1px 3px rgba(0,0,0,.12);}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {display:none;}

/* section headings */
.section-title {font-size:1.35rem; font-weight:600; color:#1D1D1F; margin:1.2rem 0 .1rem; letter-spacing:-.02em;}
.section-sub {color:#6E6E73; font-size:.9rem; margin-bottom:.6rem;}

/* dataframes + charts as cards */
[data-testid="stDataFrame"] {border:none; border-radius:16px; overflow:hidden;
  box-shadow: 0 1px 2px rgba(0,0,0,.04), 0 6px 18px rgba(0,0,0,.04);}
[data-testid="stPlotlyChart"] {background:#fff; border-radius:20px; padding:.6rem;
  box-shadow: 0 1px 2px rgba(0,0,0,.04), 0 6px 18px rgba(0,0,0,.04);}
</style>
""",
    unsafe_allow_html=True,
)


def kpi(label, value, note=""):
    return (f'<div class="kpi"><div class="label">{label}</div>'
            f'<div class="value">{value}</div><div class="note">{note}</div></div>')


def section(title, sub=""):
    st.markdown(f'<div class="section-title">{title}</div>'
                f'<div class="section-sub">{sub}</div>', unsafe_allow_html=True)


def style(fig, height=380, legend=True):
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=24, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="-apple-system, SF Pro Text, Inter, Segoe UI, sans-serif",
                  color="#515154", size=13),
        legend=dict(title_text="", orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        showlegend=legend,
        hoverlabel=dict(bgcolor="white", font_size=13, bordercolor="#E8E8ED"),
    )
    fig.update_xaxes(gridcolor="#F0F0F3", zeroline=False, title_text=None, linecolor="#E8E8ED")
    fig.update_yaxes(gridcolor="#F0F0F3", zeroline=False, title_text=None, linecolor="#E8E8ED")
    return fig


# ---------- Data ----------
# Load segments and merge client attributes (country, region, etc.)
@st.cache_data
def load():
    base = Path(__file__).parent / "data" / "processed"
    seg = pd.read_csv(base / "client_segments.csv")
    cl = pd.read_csv(base / "clients_clean.csv").rename(columns={"client_id": ID_COL})
    return seg.merge(cl, on=ID_COL, how="left")


df = load()
COLOR_MAP = {s: PALETTE[i % len(PALETTE)]
             for i, s in enumerate(sorted(df[SEG_COL].dropna().unique()))}

# ---------- Header slot + filter card ----------
hero_slot = st.empty()   # hero is drawn here later, once the filtered count is known


def reset_filters():
    for c in FILTER_COLS:
        st.session_state[f"flt_{c}"] = []


def options(col):
    return sorted(df[col].dropna().unique())


with st.container(border=True):
    st.markdown("<span class='fbar-marker'></span>", unsafe_allow_html=True)
    h1, h2, h3 = st.columns([1, 3.2, 0.8])
    h1.markdown("<div class='fbar-title'>Filters</div>", unsafe_allow_html=True)
    meter_slot = h2.empty()          # filled in after the filters are applied
    h3.button("Reset", on_click=reset_filters, **STRETCH)

    c_country, c_region, c_purpose, c_type = st.columns([1, 1, 2, 2])

    # long lists -> popover with search
    for ui, col in ((c_country, "country"), (c_region, "region")):
        label = FILTER_LABELS[col]
        n = len(st.session_state.get(f"flt_{col}", []))
        ui.markdown(f"<div class='fbar-label'>{label}</div>", unsafe_allow_html=True)
        with ui.popover(f"{n} selected" if n else f"All {label.lower()}", **STRETCH):
            st.multiselect(label, options(col), key=f"flt_{col}",
                           placeholder=f"Search {label.lower()}",
                           label_visibility="collapsed")

    # short lists -> one-click pills
    for ui, col in ((c_purpose, "acquisition_purpose"), (c_type, "client_type")):
        ui.markdown(f"<div class='fbar-label'>{FILTER_LABELS[col]}</div>", unsafe_allow_html=True)
        with ui:
            st.pills(FILTER_LABELS[col], options(col), selection_mode="multi",
                     key=f"flt_{col}", label_visibility="collapsed")

    # apply filters (empty = no filtering)
    f = df.copy()
    for col in FILTER_COLS:
        pick = st.session_state.get(f"flt_{col}") or []
        if pick:
            f = f[f[col].isin(pick)]

    pct = len(f) / len(df) * 100
    meter_slot.markdown(
        f"<div class='meter'><div style='width:{max(pct, 1):.1f}%'></div></div>"
        f"<div class='meter-text'>{len(f):,} of {len(df):,} clients match ({pct:.0f}%)</div>",
        unsafe_allow_html=True,
    )

# ---------- Header ----------
hero_slot.markdown(
    f"""
<div class="hero">
  <h1>Real Estate Buyer Segmentation</h1>
  <p>Who your clients are, how they invest, and where they come from.</p>
  <span class="count">{len(f):,} of {len(df):,} clients after filters</span>
</div>
""",
    unsafe_allow_html=True,
)

if f.empty:
    st.warning("No clients match these filters.")
    st.stop()

# KPI row
st.write("")
seg_counts = f[SEG_COL].value_counts()
top_seg, top_n = seg_counts.index[0], int(seg_counts.iloc[0])
k1, k2, k3, k4 = st.columns(4)
k1.markdown(kpi("Clients", f"{len(f):,}", f"{len(f) / len(df) * 100:.0f}% of all clients"),
            unsafe_allow_html=True)
k2.markdown(kpi("Segments", f"{f[SEG_COL].nunique()}", "in current selection"),
            unsafe_allow_html=True)
k3.markdown(kpi("Largest segment", top_seg, f"{top_n / len(f) * 100:.1f}% of clients"),
            unsafe_allow_html=True)
if "avg_price" in f.columns:
    k4.markdown(kpi("Avg price", f"{f['avg_price'].mean():,.0f}", "mean across clients"),
                unsafe_allow_html=True)
else:
    k4.markdown(kpi("Countries", f"{f['country'].nunique()}", "in current selection"),
                unsafe_allow_html=True)

st.write("")
t1, t2, t3, t4, t5 = st.tabs(["Segmentation overview", "Investor behavior",
                              "Geographic analysis", "Segment insights",
                              "Ask the data"])

# Module 1: cluster distribution
with t1:
    counts = seg_counts.rename_axis(SEG_COL).reset_index(name="clients")
    counts["pct"] = (counts["clients"] / len(f) * 100).round(1)
    counts["label"] = counts.apply(lambda r: f"{r.clients:,}  ({r.pct:.1f}%)", axis=1)

    c1, c2 = st.columns([3, 2])
    with c1:
        section("Clients per segment", "Count and share of the filtered client base")
        fig = px.bar(counts.sort_values("clients"), x="clients", y=SEG_COL, orientation="h",
                     color=SEG_COL, color_discrete_map=COLOR_MAP, text="label")
        fig.update_traces(textposition="outside", cliponaxis=False, marker_cornerradius=8,
                          hovertemplate="%{y}: %{x:,} clients<extra></extra>")
        fig.update_xaxes(range=[0, counts["clients"].max() * 1.3])
        st.plotly_chart(style(fig, 360, legend=False), **STRETCH)
    with c2:
        section("Segment mix", "Share of total clients")
        fig = px.pie(counts, names=SEG_COL, values="clients", hole=0.7,
                     color=SEG_COL, color_discrete_map=COLOR_MAP)
        fig.update_traces(textinfo="percent", sort=False,
                          marker=dict(line=dict(color="#FFFFFF", width=3)),
                          hovertemplate="%{label}: %{value:,} clients<extra></extra>")
        st.plotly_chart(style(fig, 360), **STRETCH)

    st.write("")
    st.dataframe(
        counts[[SEG_COL, "clients", "pct"]],
        hide_index=True,
        **STRETCH,
        column_config={
            SEG_COL: st.column_config.TextColumn("Segment"),
            "clients": st.column_config.NumberColumn("Clients", format="%d"),
            "pct": st.column_config.ProgressColumn("% of clients", format="%.1f%%",
                                                    min_value=0, max_value=100),
        },
    )

# Module 2: investment patterns by segment
with t2:
    behav = [c for c in ["n_purchase", "avg_price", "avg_price_per_sqft",
                         "pct_office"] if c in f.columns]
    if not behav:
        st.info("No investor-behavior columns found in the data.")
    else:
        section("Average per segment", "Pick a metric to compare segments")
        m = st.selectbox("Metric", behav, format_func=lambda c: METRIC_LABELS.get(c, c),
                         label_visibility="collapsed")
        g = f.groupby(SEG_COL)[m].mean().reset_index().sort_values(m)
        g["label"] = g[m].map(lambda v: f"{v:,.2f}")
        fig = px.bar(g, x=m, y=SEG_COL, orientation="h", color=SEG_COL,
                     color_discrete_map=COLOR_MAP, text="label")
        fig.update_traces(textposition="outside", cliponaxis=False, marker_cornerradius=8,
                          hovertemplate="%{y}: %{x:,.2f}<extra></extra>")
        fig.update_xaxes(range=[0, g[m].max() * 1.25])
        st.plotly_chart(style(fig, 340, legend=False), **STRETCH)

    section("Acquisition purpose by segment (%)", "Each row sums to 100%")
    ct = (pd.crosstab(f[SEG_COL], f["acquisition_purpose"], normalize="index") * 100).round(1)
    fig = px.imshow(ct, text_auto=".1f", aspect="auto",
                    color_continuous_scale=[[0, "#F5F5F7"], [1, "#0071E3"]])
    fig.update_layout(coloraxis_showscale=False)
    fig.update_traces(hovertemplate="%{y} / %{x}: %{z:.1f}%<extra></extra>")
    fig.update_xaxes(side="top")
    st.plotly_chart(style(fig, 120 + 60 * len(ct), legend=False), **STRETCH)

# Module 3: segments by region / country
with t3:
    section("Clients per region", "Split by segment")
    reg = pd.crosstab(f["region"], f[SEG_COL])
    reg = reg.loc[reg.sum(axis=1).sort_values(ascending=False).index].head(15)
    fig = px.bar(reg.iloc[::-1], orientation="h", barmode="stack",
                 color_discrete_map=COLOR_MAP, labels={"value": "Clients"})
    fig.update_traces(hovertemplate="%{y} / %{fullData.name}: %{x:,}<extra></extra>")
    st.plotly_chart(style(fig, 520), **STRETCH)

    section("Top 10 countries", "Split by segment")
    top = (pd.crosstab(f["country"], f[SEG_COL])
           .assign(t=lambda d: d.sum(axis=1))
           .nlargest(10, "t").drop(columns="t"))
    fig = px.bar(top.iloc[::-1], orientation="h", barmode="stack",
                 color_discrete_map=COLOR_MAP, labels={"value": "Clients"})
    fig.update_traces(hovertemplate="%{y} / %{fullData.name}: %{x:,}<extra></extra>")
    st.plotly_chart(style(fig, 420), **STRETCH)

# Module 4: descriptive stats per segment + client lookup
with t4:
    section("Segment profile", "Descriptive statistics for the selected segment")
    seg_pick = st.selectbox("Segment", sorted(f[SEG_COL].unique()),
                            label_visibility="collapsed")
    st.dataframe(f[f[SEG_COL] == seg_pick].describe().T.round(2), **STRETCH)

    st.write("")
    section("Client lookup", "Search any client, regardless of the filters")
    cid = st.text_input("Client ID (e.g. C0001)")
    if cid:
        row = df[df[ID_COL].astype(str) == cid.strip()]
        if row.empty:
            st.warning("Not found.")
        else:
            st.dataframe(row.T, **STRETCH)

# Module 5: chat with the AI agent (Gemini + the five tools)
with t5:
    section("Ask the data", "Answers come from the tools only. Filters don't apply here.")

    # Import the agent once; show a clear message if the API key is missing
    try:
        import agent
    except KeyError:
        st.error("GEMINI_API_KEY is not set. Set it and restart the app.")
        st.stop()

    # Keep the visible conversation across Streamlit reruns
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if st.button("Clear chat"):
        st.session_state.messages = []
        agent.reset_chat()   # also resets Gemini's memory (added below)
        st.rerun()

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if q := st.chat_input("e.g. Compare Budget Buyers and Portfolio Investors"):
        st.session_state.messages.append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.markdown(q)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    reply = agent.ask(q)
                except Exception as e:
                    reply = f"Sorry, the request failed: {e}"
            st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})