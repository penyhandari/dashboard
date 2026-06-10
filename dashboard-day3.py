import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# 1. KONFIGURASI HALAMAN
# =========================================================
st.set_page_config(
    page_title="Pantau Udara Jakarta",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. CSS PROFESIONAL
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(37, 99, 235, 0.12), transparent 30%),
            radial-gradient(circle at top right, rgba(20, 184, 166, 0.10), transparent 28%),
            #F6F8FB;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    section[data-testid="stSidebar"] {
        background: #0F172A;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #E5E7EB !important;
    }

    .hero {
        padding: 34px 36px;
        border-radius: 30px;
        background:
            linear-gradient(135deg, rgba(15, 23, 42, 0.97), rgba(30, 64, 175, 0.90));
        color: white;
        box-shadow: 0 24px 60px rgba(15, 23, 42, 0.24);
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }

    .hero:after {
        content: "";
        position: absolute;
        right: -100px;
        top: -100px;
        width: 280px;
        height: 280px;
        border-radius: 999px;
        border: 42px solid rgba(255,255,255,0.08);
    }

    .hero-eyebrow {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        font-weight: 800;
        color: #93C5FD;
        margin-bottom: 12px;
    }

    .hero-title {
        font-size: clamp(2.1rem, 5vw, 4.8rem);
        line-height: 0.95;
        font-weight: 900;
        letter-spacing: -0.065em;
        margin-bottom: 16px;
        max-width: 900px;
    }

    .hero-subtitle {
        font-size: 1.03rem;
        line-height: 1.7;
        color: #CBD5E1;
        max-width: 780px;
    }

    .kpi-card {
        padding: 22px 22px 20px 22px;
        border-radius: 24px;
        background: rgba(255,255,255,0.92);
        border: 1px solid rgba(226, 232, 240, 0.95);
        box-shadow: 0 16px 38px rgba(15, 23, 42, 0.07);
        min-height: 148px;
    }

    .kpi-card.good {
        border-left: 8px solid #22C55E;
    }

    .kpi-card.moderate {
        border-left: 8px solid #EAB308;
    }

    .kpi-card.unhealthy {
        border-left: 8px solid #F97316;
    }

    .kpi-card.bad {
        border-left: 8px solid #EF4444;
    }

    .kpi-card.unknown {
        border-left: 8px solid #94A3B8;
    }

    .kpi-label {
        color: #64748B;
        font-size: 0.72rem;
        font-weight: 850;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 9px;
    }

    .kpi-value {
        font-size: 2.1rem;
        line-height: 1.05;
        font-weight: 900;
        letter-spacing: -0.055em;
        color: #0F172A;
        margin-bottom: 10px;
    }

    .kpi-note {
        color: #64748B;
        font-size: 0.86rem;
        line-height: 1.45;
    }

    .panel {
        background: rgba(255,255,255,0.93);
        border: 1px solid rgba(226, 232, 240, 0.95);
        border-radius: 26px;
        padding: 20px 20px 12px 20px;
        box-shadow: 0 16px 38px rgba(15, 23, 42, 0.06);
        margin-bottom: 1rem;
    }

    .section-title {
        font-size: 1.12rem;
        font-weight: 850;
        letter-spacing: -0.03em;
        color: #0F172A;
        margin-bottom: 0.25rem;
    }

    .section-caption {
        color: #64748B;
        font-size: 0.88rem;
        margin-bottom: 0.8rem;
    }

    .mini-insight {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        color: #1E3A8A;
        padding: 15px 17px;
        border-radius: 20px;
        font-size: 0.92rem;
        line-height: 1.55;
        margin-bottom: 1rem;
    }

    .empty-state {
        padding: 42px;
        border-radius: 30px;
        text-align: center;
        background: white;
        border: 1px dashed #CBD5E1;
        box-shadow: 0 16px 38px rgba(15, 23, 42, 0.05);
    }

    div[data-testid="stMetricValue"] {
        font-weight: 900;
    }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stMultiSelect"] label,
    div[data-testid="stDateInput"] label {
        font-weight: 800 !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. KONSTANTA DAN HELPER
# =========================================================
REQUIRED_COLUMNS = ["tanggal", "lokasi_spku", "max", "categori", "critical"]

LOKASI_MAP = {
    "DKI1": "Jakarta Pusat",
    "DKI2": "Jakarta Utara",
    "DKI3": "Jakarta Selatan",
    "DKI4": "Jakarta Timur",
    "DKI5": "Jakarta Barat",
}

CATEGORY_COLOR = {
    "BAIK": "#22C55E",
    "SEDANG": "#EAB308",
    "TIDAK SEHAT": "#F97316",
    "SANGAT TIDAK SEHAT": "#EF4444",
    "BERBAHAYA": "#7F1D1D",
    "Tidak diketahui": "#94A3B8",
}

def normalize_category(value):
    if pd.isna(value):
        return "Tidak diketahui"

    text = str(value).strip().upper()

    if text in ["BAIK"]:
        return "BAIK"
    elif text in ["SEDANG"]:
        return "SEDANG"
    elif text in ["TIDAK SEHAT"]:
        return "TIDAK SEHAT"
    elif text in ["SANGAT TIDAK SEHAT"]:
        return "SANGAT TIDAK SEHAT"
    elif text in ["BERBAHAYA"]:
        return "BERBAHAYA"
    else:
        return str(value).strip()

def kpi_status_class(category):
    cat = str(category).upper()

    if cat == "BAIK":
        return "good"
    elif cat == "SEDANG":
        return "moderate"
    elif cat == "TIDAK SEHAT":
        return "unhealthy"
    elif cat in ["SANGAT TIDAK SEHAT", "BERBAHAYA"]:
        return "bad"
    else:
        return "unknown"

def format_number(value, digits=1):
    if pd.isna(value):
        return "-"
    return f"{value:,.{digits}f}".replace(",", ".")

def make_kpi_card(label, value, note, status="unknown"):
    st.markdown(
        f"""
        <div class="kpi-card {status}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def style_plotly(fig, height=420):
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=45, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#0F172A"),
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_family="Inter, sans-serif"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    fig.update_xaxes(
        showgrid=False,
        linecolor="#CBD5E1",
        tickfont=dict(color="#475569")
    )

    fig.update_yaxes(
        gridcolor="rgba(148, 163, 184, 0.22)",
        linecolor="#CBD5E1",
        tickfont=dict(color="#475569")
    )

    return fig

# =========================================================
# 4. LOAD DATA
# =========================================================
@st.cache_data(show_spinner=False)
def load_data(file):
    if file.name.lower().endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing_columns:
        raise ValueError(
            "Kolom berikut belum ada di file: "
            + ", ".join(missing_columns)
            + ". Kolom wajib: "
            + ", ".join(REQUIRED_COLUMNS)
        )

    df = df.copy()

    df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
    df["max"] = pd.to_numeric(df["max"], errors="coerce")

    df = df.dropna(subset=["tanggal", "max"])

    df["lokasi_spku"] = df["lokasi_spku"].astype(str).str.strip()
    df = df[~df["lokasi_spku"].isin(["0", "", "nan", "None", "NONE"])]

    df["lokasi_nama"] = df["lokasi_spku"].map(LOKASI_MAP).fillna(df["lokasi_spku"])

    df["categori"] = df["categori"].apply(normalize_category)
    df["critical"] = df["critical"].fillna("Tidak diketahui").astype(str).str.upper()

    df["tahun"] = df["tanggal"].dt.year
    df["bulan_tahun"] = df["tanggal"].dt.to_period("M").astype(str)

    df = df.sort_values("tanggal").reset_index(drop=True)

    return df

# =========================================================
# 5. SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## 🌫️ Pantau Udara")
    st.caption("Dashboard kualitas udara berbasis data ISPU/SPKU.")

    uploaded_file = st.file_uploader(
        "Upload data CSV atau XLSX",
        type=["csv", "xlsx"],
        help="File wajib memiliki kolom: tanggal, lokasi_spku, max, categori, critical."
    )

    st.divider()

# =========================================================
# 6. TAMPILAN AWAL SAAT FILE BELUM DIUPLOAD
# =========================================================
if uploaded_file is None:
    st.markdown("""
        <div class="hero">
            <div class="hero-eyebrow">Jakarta Air Quality Monitor</div>
            <div class="hero-title">Baca udara kota seperti membaca denyut nadi.</div>
            <div class="hero-subtitle">
                Upload data ISPU/SPKU untuk melihat indeks terkini, tren kualitas udara,
                peringkat wilayah, polutan dominan, distribusi kategori, dan pola bulanan.
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="empty-state">
            <h3 style="margin-bottom: 8px;">Upload file untuk mulai</h3>
            <p style="color:#64748B; margin:0;">
                Gunakan panel kiri untuk mengunggah file CSV/XLSX.
                Dashboard akan otomatis membuat filter, KPI, grafik tren, dan tabel data.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.stop()

# =========================================================
# 7. PROSES DATA
# =========================================================
try:
    df = load_data(uploaded_file)
except Exception as e:
    st.error(f"File belum bisa diproses: {e}")
    st.stop()

if df.empty:
    st.warning("Data kosong setelah proses pembersihan. Periksa kembali isi file.")
    st.stop()

# =========================================================
# 8. FILTER SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("### Filter Analisis")

    min_date = df["tanggal"].min().date()
    max_date = df["tanggal"].max().date()

    date_range = st.date_input(
        "Rentang tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    lokasi_opsi = sorted(df["lokasi_nama"].dropna().unique().tolist())
    selected_lokasi = st.multiselect(
        "Wilayah",
        options=lokasi_opsi,
        default=lokasi_opsi
    )

    polutan_opsi = sorted(df["critical"].dropna().unique().tolist())
    selected_polutan = st.multiselect(
        "Polutan utama",
        options=polutan_opsi,
        default=polutan_opsi
    )

    kategori_opsi = sorted(df["categori"].dropna().unique().tolist())
    selected_kategori = st.multiselect(
        "Kategori",
        options=kategori_opsi,
        default=kategori_opsi
    )

# =========================================================
# 9. APPLY FILTER
# =========================================================
filtered_df = df.copy()

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range

    filtered_df = filtered_df[
        (filtered_df["tanggal"].dt.date >= start_date) &
        (filtered_df["tanggal"].dt.date <= end_date)
    ]

if selected_lokasi:
    filtered_df = filtered_df[filtered_df["lokasi_nama"].isin(selected_lokasi)]

if selected_polutan:
    filtered_df = filtered_df[filtered_df["critical"].isin(selected_polutan)]

if selected_kategori:
    filtered_df = filtered_df[filtered_df["categori"].isin(selected_kategori)]

if filtered_df.empty:
    st.warning("Tidak ada data yang cocok dengan filter saat ini.")
    st.stop()

# =========================================================
# 10. HITUNG KPI
# =========================================================
latest = filtered_df.sort_values("tanggal").iloc[-1]

avg_ispu = filtered_df["max"].mean()
max_ispu = filtered_df["max"].max()
min_ispu = filtered_df["max"].min()

dominant_pollutant = (
    filtered_df["critical"].mode().iloc[0]
    if not filtered_df["critical"].mode().empty
    else "-"
)

dominant_category = (
    filtered_df["categori"].mode().iloc[0]
    if not filtered_df["categori"].mode().empty
    else "-"
)

worst_row = filtered_df.loc[filtered_df["max"].idxmax()]
best_row = filtered_df.loc[filtered_df["max"].idxmin()]

# =========================================================
# 11. HERO DASHBOARD
# =========================================================
st.markdown(f"""
    <div class="hero">
        <div class="hero-eyebrow">Jakarta Air Quality Command Center</div>
        <div class="hero-title">Pantau Udara Jakarta</div>
        <div class="hero-subtitle">
            Periode data <b>{filtered_df["tanggal"].min().strftime("%d %b %Y")}</b>
            sampai <b>{filtered_df["tanggal"].max().strftime("%d %b %Y")}</b>.
            Dashboard ini merangkum kondisi kualitas udara berdasarkan indeks maksimum,
            kategori ISPU, lokasi SPKU, dan polutan kritis.
        </div>
    </div>
""", unsafe_allow_html=True)

# =========================================================
# 12. KPI CARD
# =========================================================
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    make_kpi_card(
        "Indeks terkini",
        f"{int(latest['max'])}",
        f"{latest['lokasi_nama']} · {latest['tanggal'].strftime('%d %b %Y')}",
        kpi_status_class(latest["categori"])
    )

with kpi2:
    make_kpi_card(
        "Kategori terkini",
        latest["categori"],
        f"Polutan utama: {latest['critical']}",
        kpi_status_class(latest["categori"])
    )

with kpi3:
    make_kpi_card(
        "Rata-rata ISPU",
        format_number(avg_ispu, 1),
        f"Dari {len(filtered_df):,} baris data".replace(",", "."),
        kpi_status_class(dominant_category)
    )

with kpi4:
    make_kpi_card(
        "Nilai tertinggi",
        f"{int(max_ispu)}",
        f"Polutan dominan: {dominant_pollutant}",
        "bad" if max_ispu > 150 else "moderate"
    )

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# 13. INSIGHT RINGKAS
# =========================================================
st.markdown(
    f"""
    <div class="mini-insight">
        <b>Ringkasan cepat:</b>
        nilai ISPU tertinggi tercatat di <b>{worst_row['lokasi_nama']}</b>
        pada <b>{worst_row['tanggal'].strftime('%d %b %Y')}</b> dengan indeks
        <b>{int(worst_row['max'])}</b>. Nilai terendah tercatat di
        <b>{best_row['lokasi_nama']}</b> pada
        <b>{best_row['tanggal'].strftime('%d %b %Y')}</b> dengan indeks
        <b>{int(best_row['max'])}</b>.
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# 14. GRAFIK TREN DAN DONUT KATEGORI
# =========================================================
left, right = st.columns((1.7, 1))

with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Tren Kualitas Udara Harian</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Rata-rata indeks maksimum per tanggal berdasarkan filter aktif.</div>',
        unsafe_allow_html=True
    )

    trend_df = (
        filtered_df
        .groupby("tanggal", as_index=False)
        .agg(rata_rata_ispu=("max", "mean"))
        .sort_values("tanggal")
    )

    fig_trend = px.line(
        trend_df,
        x="tanggal",
        y="rata_rata_ispu",
        markers=True,
        labels={
            "tanggal": "Tanggal",
            "rata_rata_ispu": "Rata-rata ISPU"
        }
    )

    fig_trend.update_traces(
        line=dict(width=3, color="#2563EB"),
        marker=dict(size=7, color="#0F172A")
    )

    fig_trend.add_hrect(
        y0=0,
        y1=50,
        fillcolor="#22C55E",
        opacity=0.08,
        line_width=0
    )

    fig_trend.add_hrect(
        y0=51,
        y1=100,
        fillcolor="#EAB308",
        opacity=0.08,
        line_width=0
    )

    fig_trend.add_hrect(
        y0=101,
        y1=200,
        fillcolor="#F97316",
        opacity=0.07,
        line_width=0
    )

    fig_trend.add_hrect(
        y0=201,
        y1=max(300, filtered_df["max"].max() + 20),
        fillcolor="#EF4444",
        opacity=0.06,
        line_width=0
    )

    fig_trend = style_plotly(fig_trend, height=430)

    st.plotly_chart(
        fig_trend,
        use_container_width=True,
        config={"displayModeBar": False}
    )

    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Komposisi Kategori</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Proporsi kategori kualitas udara dalam data terfilter.</div>',
        unsafe_allow_html=True
    )

    cat_df = (
        filtered_df
        .groupby("categori", as_index=False)
        .size()
        .rename(columns={"size": "jumlah"})
    )

    if cat_df.empty:
        st.info("Belum ada data kategori untuk ditampilkan.")
    else:
        # PENTING:
        # Plotly Express tidak punya px.donut().
        # Donut chart dibuat dengan px.pie(..., hole=0.62).
        fig_cat = px.pie(
            cat_df,
            names="categori",
            values="jumlah",
            hole=0.62,
            color="categori",
            color_discrete_map=CATEGORY_COLOR
        )

        fig_cat.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(line=dict(color="white", width=3))
        )

        fig_cat = style_plotly(fig_cat, height=430)

        st.plotly_chart(
            fig_cat,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 15. RANKING WILAYAH DAN POLUTAN
# =========================================================
rank_col, pollutant_col = st.columns(2)

with rank_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Peringkat Wilayah</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Semakin tinggi nilai rata-rata, semakin perlu dipantau.</div>',
        unsafe_allow_html=True
    )

    loc_df = (
        filtered_df
        .groupby("lokasi_nama", as_index=False)
        .agg(rata_rata_ispu=("max", "mean"))
        .sort_values("rata_rata_ispu", ascending=True)
    )

    fig_bar = px.bar(
        loc_df,
        x="rata_rata_ispu",
        y="lokasi_nama",
        orientation="h",
        text="rata_rata_ispu",
        labels={
            "rata_rata_ispu": "Rata-rata ISPU",
            "lokasi_nama": "Wilayah"
        }
    )

    fig_bar.update_traces(
        marker_color="#1D4ED8",
        texttemplate="%{text:.1f}",
        textposition="outside",
        cliponaxis=False
    )

    fig_bar = style_plotly(fig_bar, height=390)

    st.plotly_chart(
        fig_bar,
        use_container_width=True,
        config={"displayModeBar": False}
    )

    st.markdown('</div>', unsafe_allow_html=True)

with pollutant_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Polutan Paling Sering Menjadi Kritis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Dihitung dari frekuensi kemunculan kolom critical.</div>',
        unsafe_allow_html=True
    )

    pol_df = (
        filtered_df
        .groupby("critical", as_index=False)
        .size()
        .rename(columns={"size": "jumlah"})
        .sort_values("jumlah", ascending=False)
    )

    fig_pol = px.bar(
        pol_df,
        x="critical",
        y="jumlah",
        text="jumlah",
        labels={
            "critical": "Polutan",
            "jumlah": "Frekuensi"
        }
    )

    fig_pol.update_traces(
        marker_color="#14B8A6",
        textposition="outside",
        cliponaxis=False
    )

    fig_pol = style_plotly(fig_pol, height=390)

    st.plotly_chart(
        fig_pol,
        use_container_width=True,
        config={"displayModeBar": False}
    )

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 16. HEATMAP BULANAN
# =========================================================
st.markdown('<div class="panel">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Pola Bulanan per Wilayah</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-caption">Rata-rata ISPU per bulan dan wilayah. Warna lebih pekat berarti nilai lebih tinggi.</div>',
    unsafe_allow_html=True
)

heat_df = (
    filtered_df
    .groupby(["bulan_tahun", "lokasi_nama"], as_index=False)
    .agg(rata_rata_ispu=("max", "mean"))
)

if heat_df.empty:
    st.info("Data belum cukup untuk membuat heatmap bulanan.")
else:
    pivot_heat = heat_df.pivot(
        index="lokasi_nama",
        columns="bulan_tahun",
        values="rata_rata_ispu"
    )

    fig_heat = go.Figure(
        data=go.Heatmap(
            z=pivot_heat.values,
            x=pivot_heat.columns,
            y=pivot_heat.index,
            colorscale="Blues",
            colorbar=dict(title="ISPU"),
            hovertemplate=
            "Bulan: %{x}<br>" +
            "Wilayah: %{y}<br>" +
            "Rata-rata ISPU: %{z:.1f}<extra></extra>"
        )
    )

    fig_heat.update_layout(
        height=420,
        margin=dict(l=20, r=20, t=35, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#0F172A")
    )

    fig_heat.update_xaxes(
        showgrid=False,
        linecolor="#CBD5E1",
        tickfont=dict(color="#475569")
    )

    fig_heat.update_yaxes(
        showgrid=False,
        linecolor="#CBD5E1",
        tickfont=dict(color="#475569")
    )

    st.plotly_chart(
        fig_heat,
        use_container_width=True,
        config={"displayModeBar": False}
    )

st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 17. TABEL DATA
# =========================================================
with st.expander("Lihat data terfilter"):
    display_cols = [
        "tanggal",
        "lokasi_spku",
        "lokasi_nama",
        "max",
        "categori",
        "critical"
    ]

    available_cols = [col for col in display_cols if col in filtered_df.columns]

    table_df = filtered_df[available_cols].sort_values("tanggal", ascending=False)
    table_df["tanggal"] = table_df["tanggal"].dt.strftime("%Y-%m-%d")

    st.dataframe(
        table_df,
        hide_index=True,
        use_container_width=True
    )

# =========================================================
# 18. FOOTER
# =========================================================
st.caption(
    "Dashboard ini menggunakan nilai rata-rata indeks maksimum untuk analisis agregat. "
    "Interpretasi akhir tetap perlu mempertimbangkan standar resmi dan konteks pengukuran lapangan."
)