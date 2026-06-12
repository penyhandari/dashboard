import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Set Konfigurasi Halaman Streamlit (Tema Premium & Responsif)
st.set_page_config(
    page_title="Dashboard BI Kualitas Udara DKI Jakarta",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Kustomisasi CSS untuk Meningkatkan Kontras dan Tampilan Premium (Aesthetic & High Contrast)
st.markdown("""
<style>
    /* Styling Kartu KPI */
    .kpi-card {
        background-color: #1e293b;
        color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-left: 5px solid #3b82f6;
        margin-bottom: 10px;
    }
    .kpi-title {
        font-size: 14px;
        font-weight: 500;
        color: #94a3b8;
        margin-bottom: 5px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
    }
    /* Warna Dinamis untuk Kategori Kritis */
    .kpi-alert-red { border-left-color: #ef4444 !important; }
    .kpi-alert-yellow { border-left-color: #eab308 !important; }
    .kpi-alert-green { border-left-color: #22c55e !important; }
    
    /* Box Rekomendasi Kebijakan */
    .rec-box {
        background-color: #0f172a;
        color: #f1f5f9;
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. LOAD & PREPROCESS DATA
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    file_path = "df_clean.csv"
    if not os.path.exists(file_path):
        # Fallback dummy data jika dijalankan tanpa file df_clean.csv secara lokal
        st.error(f"File '{file_path}' tidak ditemukan di direktori saat ini. Silakan letakkan file tersebut bersama dengan file script ini.")
        st.stop()
        
    df = pd.read_csv(file_path)
    df['tanggal'] = pd.to_datetime(df['tanggal'])
    df['year'] = df['year'].astype(int)
    # Bersihkan nama kategori agar seragam (Kapital)
    df['categori'] = df['categori'].str.upper().str.strip()
    return df

try:
    df_raw = load_data()
except Exception as e:
    st.error(f"Gagal memuat data: {e}")
    st.stop()

# -----------------------------------------------------------------------------
# 2. PANEL NAVIGASI & FILTER (SIDEBAR)
# -----------------------------------------------------------------------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/b/b9/Coat_of_arms_of_Jakarta.svg", width=80)
st.sidebar.title("DLH Provinsi DKI Jakarta")
st.sidebar.subheader("Dashboard BI Kualitas Udara")
st.sidebar.markdown("---")

# Filter Tahun
available_years = sorted(df_raw['year'].unique())
selected_years = st.sidebar.multiselect(
    "Pilih Tahun Analisis:",
    options=available_years,
    default=available_years[-2:] if len(available_years) >= 2 else available_years
)

# Filter Stasiun (SPKU)
available_stations = sorted(df_raw['stasiun'].unique())
selected_stations = st.sidebar.multiselect(
    "Pilih Stasiun Pemantauan (SPKU):",
    options=available_stations,
    default=available_stations
)

# Filter Kategori Kualitas Udara
available_categories = sorted(df_raw['categori'].dropna().unique())
selected_categories = st.sidebar.multiselect(
    "Kategori Kualitas Udara:",
    options=available_categories,
    default=available_categories
)

# Terapkan Filter ke Dataset
df_filtered = df_raw.copy()
if selected_years:
    df_filtered = df_filtered[df_filtered['year'].isin(selected_years)]
if selected_stations:
    df_filtered = df_filtered[df_filtered['stasiun'].isin(selected_stations)]
if selected_categories:
    df_filtered = df_filtered[df_filtered['categori'].isin(selected_categories)]

# Jika data kosong setelah difilter
if df_filtered.empty:
    st.warning("⚠️ Tidak ada data yang cocok dengan kombinasi filter Anda. Silakan sesuaikan filter di sidebar.")
    st.stop()

# -----------------------------------------------------------------------------
# 3. KEPALA DASHBOARD (HEADER & KPI CARDS)
# -----------------------------------------------------------------------------
st.title("📊 PEMANTAUAN & KEPUTUSAN KUALITAS UDARA DKI JAKARTA")
st.markdown("Dokumentasi Analisis Strategis untuk **Kepala Dinas Lingkungan Hidup DKI Jakarta** guna merumuskan kebijakan taktis penanganan polusi udara.")
st.markdown("---")

# Mengolah metrik utama
max_aqi_value = int(df_filtered['max'].max())
dominant_pollutant = df_filtered['critical'].mode().values[0] if not df_filtered['critical'].empty else "N/A"

# Menghitung persentase hari tidak sehat
total_days = len(df_filtered)
unhealthy_days = len(df_filtered[df_filtered['categori'].isin(['TIDAK SEHAT', 'SANGAT TIDAK SEHAT', 'BERBAHAYA'])])
unhealthy_pct = round((unhealthy_days / total_days) * 100, 1) if total_days > 0 else 0

# Penentuan warna kelas alert untuk Max AQI harian
alert_class = "kpi-alert-green"
status_text = "BAIK/SEDANG"
if max_aqi_value > 150:
    alert_class = "kpi-alert-red"
    status_text = "SANGAT BURUK"
elif max_aqi_value > 100:
    alert_class = "kpi-alert-yellow"
    status_text = "TIDAK SEHAT"

# Render KPI Grid secara Horizontal
kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

with kpi_col1:
    st.markdown(f"""
    <div class="kpi-card {alert_class}">
        <div class="kpi-title">INDERS AQI MAKSIMUM (MAX)</div>
        <div class="kpi-value">{max_aqi_value} <span style="font-size:16px; font-weight:normal;">({status_text})</span></div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
    <div class="kpi-card kpi-alert-red">
        <div class="kpi-title">POLUTAN KRITIS DOMINAN</div>
        <div class="kpi-value">{dominant_pollutant.upper()}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
    <div class="kpi-card kpi-alert-yellow">
        <div class="kpi-title">HARI TIDAK SEHAT / SANGAT TIDAK SEHAT</div>
        <div class="kpi-value">{unhealthy_pct}% <span style="font-size:16px; font-weight:normal;">({unhealthy_days} Hari)</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. VISUALISASI UTAMA (GRID BARIS 1 & 2)
# -----------------------------------------------------------------------------
vis_col1, vis_col2 = st.columns([6, 4])

with vis_col1:
    st.subheader("📍 Peringkat Polusi dan Kondisi SPKU di Jakarta")
    # Urutkan SPKU berdasarkan rata-rata nilai max polutan
    df_spku = df_filtered.groupby('stasiun')['max'].mean().reset_index().sort_values('max', ascending=True)
    
    # Skema Warna Kontras Tinggi untuk Kebutuhan Presentasi
    fig_spku = px.bar(
        df_spku,
        x='max',
        y='stasiun',
        orientation='h',
        labels={'max': 'Rata-Rata AQI Maksimum', 'stasiun': 'Stasiun Pemantauan'},
        color='max',
        color_continuous_scale=px.colors.sequential.YlOrRd,
        text_auto='.1f'
    )
    
    # Tambahkan garis ambang batas Kategori Sehat/Sedang (AQI 100)
    fig_spku.add_vline(x=100, line_dash="dash", line_color="#ef4444", annotation_text="Batas Aman (100)", annotation_position="top right")
    
    fig_spku.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#f1f5f9',
        height=380,
        margin=dict(l=10, r=10, t=20, b=10)
    )
    st.plotly_chart(fig_spku, use_container_width=True)

with vis_col2:
    st.subheader("🎯 Komposisi Penyebab Polusi (Critical)")
    # Hitung kontribusi masing-masing parameter kritis
    df_crit_comp = df_filtered['critical'].value_counts().reset_index()
    df_crit_comp.columns = ['Parameter', 'Jumlah Kasus']
    
    fig_donut = px.pie(
        df_crit_comp,
        names='Parameter',
        values='Jumlah Kasus',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Dark24
    )
    fig_donut.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#f1f5f9',
        height=380,
        margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_donut, use_container_width=True)

st.markdown("---")

# BARIS 3: TREN TEMPORAL (LINE CHART)
st.subheader("📈 Tren Perkembangan Polusi Udara Harian & Bulanan")
# Kelompokkan data harian untuk line chart yang mulus
df_trend = df_filtered.groupby('tanggal')['max'].mean().reset_index()

# Tambahkan Moving Average (Rata-rata Bergerak 7 Hari) untuk meminimalkan 'noise' data harian
df_trend['7-Day MA'] = df_trend['max'].rolling(window=7, min_periods=1).mean()

fig_trend = go.Figure()
# Line Harian (Transparan/Tipis)
fig_trend.add_trace(go.Scatter(
    x=df_trend['tanggal'], y=df_trend['max'],
    mode='lines',
    name='Harian',
    line=dict(color='#64748b', width=1)
))
# Line Moving Average (Tebal & Kontras Tinggi)
fig_trend.add_trace(go.Scatter(
    x=df_trend['tanggal'], y=df_trend['7-Day MA'],
    mode='lines',
    name='Rata-Rata Bergerak 7 Hari',
    line=dict(color='#f43f5e', width=3)
))

fig_trend.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color='#f1f5f9',
    xaxis=dict(showgrid=True, gridcolor='#334155'),
    yaxis=dict(showgrid=True, gridcolor='#334155', title="Indeks Polutan (AQI Max)"),
    height=350,
    margin=dict(l=10, r=10, t=10, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. REKOMENDASI TAKTIS & DETAIL DATA (BARIS BAWAH)
# -----------------------------------------------------------------------------
action_col1, action_col2 = st.columns([5, 5])

with action_col1:
    st.subheader("📋 Rekomendasi Kebijakan Taktis (Data-Driven)")
    
    # Algoritma Kecerdasan Sederhana berbasis Parameter Kritis Terbanyak
    dominant_clean = str(dominant_pollutant).strip().upper()
    
    st.markdown('<div class="rec-box">', unsafe_allow_html=True)
    if 'PM2' in dominant_clean or 'PM25' in dominant_clean or 'PM2.5' in dominant_clean:
        st.error("🚨 **FOKUS UTAMA: Partikulat PM2.5 Tinggi**")
        st.markdown("""
        * **Penyebab Utama:** Sektor transportasi (asap knalpot), debu aspal, dan pembangkit listrik/industri pembakaran.
        * **Rekomendasi Kebijakan Segera:**
            1. **Optimalisasi Uji Emisi:** Lakukan razia tilang uji emisi di koridor wilayah stasiun dengan rata-rata tertinggi (terutama SPKU paling polutif).
            2. **Aturan Pembatasan Truk:** Batasi jam operasi kendaraan berat / truk logistik non-kritis di kawasan padat lalu lintas pada jam-jam sibuk.
            3. **Water Mist & Penyiraman Jalan:** Aktifkan penyemprotan kabut air (*water mist*) dari gedung tinggi dan penyiraman jalan protokol.
        """)
    elif 'O3' in dominant_clean:
        st.warning("⚠️ **FOKUS UTAMA: Polusi Ozon Permukaan (O3) Tinggi**")
        st.markdown("""
        * **Penyebab Utama:** Reaksi fotokimia antara sinar matahari terik dengan emisi hidrokarbon (VOC) dan NOx dari knalpot kendaraan.
        * **Rekomendasi Kebijakan Segera:**
            1. **Pengendalian Kemacetan:** Perluas cakupan ganjil-genap untuk menurunkan beban total kendaraan di jalur utama.
            2. **Uji Emisi Industri:** Tingkatkan sidak kepatuhan cerobong pabrik di sekitar area terdampak.
            3. **Insentif Transportasi Publik:** Dorong tarif ramah bagi warga komuter untuk beralih menggunakan MRT/LRT/Transjakarta.
        """)
    else:
        st.info("ℹ️ **FOKUS UTAMA: Polutan Gas (CO / SO2 / NO2)**")
        st.markdown("""
        * **Penyebab Utama:** Aktivitas pembakaran industri manufaktur, PLTU batu bara, dan kendaraan bermotor.
        * **Rekomendasi Kebijakan Segera:**
            1. **Sidak Sektor Industri:** Kerahkan tim DLH untuk melakukan pemantauan emisi cerobong pabrik manufaktur di wilayah penyangga secara acak.
            2. **Katalis Konverter:** Wajibkan sertifikasi kelaikan katalis konverter pada kendaraan angkutan umum massal.
        """)
    st.markdown('</div>', unsafe_allow_html=True)

with action_col2:
    st.subheader("🔍 Sampel Data Historis Terdampak")
    st.markdown("Berikut adalah tabel data yang sesuai dengan filter Anda untuk validasi silang:")
    
    # Menampilkan tabel data ringkas yang mudah diexport ke Excel/CSV
    df_table_show = df_filtered[['tanggal', 'stasiun', 'max', 'critical', 'categori']].sort_values('max', ascending=False)
    st.dataframe(
        df_table_show.head(100), 
        use_container_width=True, 
        height=280
    )
    st.caption("Menampilkan hingga 100 baris data teratas yang diurutkan dari indeks polusi tertinggi.")

# Footer Dashboard
st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 12px;'>Sistem Informasi Manajemen Kualitas Udara - Dinas Lingkungan Hidup DKI Jakarta © 2026</p>", unsafe_allow_html=True)