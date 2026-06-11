import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Dashboard Pemantauan Kualitas Udara DKI Jakarta",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Kustomisasi CSS untuk Font & Elemen UI agar terkesan Clean & Corporate
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        .stMetric {
            background-color: #F8FAFC;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #E2E8F0;
        }
        .tooltip-icon {
            color: #64748B;
            cursor: help;
            font-size: 0.85em;
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. IDENTITAS VISUAL & PALETTE WARNA ---
COLOR_PRIMARY = "#1E293B"      # Deep Navy
COLOR_SECONDARY = "#10B981"    # Emerald Green

# Warna Standar Resmi Kementerian LHK
MAP_WARNA_ISPU = {
    'BAIK': '#22C55E',               # Hijau
    'SEDANG': '#3B82F6',             # Biru
    'TIDAK SEHAT': '#EAB308',        # Kuning
    'SANGAT TIDAK SEHAT': '#EF4444',  # Merah
    'BERBAHAYA': '#0F172A'           # Hitam/Gelap
}

# Kamus penjelasan parameter polutan untuk Fitur UX Glosarium
GLOSARIUM_POLUTAN = {
    'PM10': "Partikel udara dengan ukuran < 10 mikrometer. Sumber: Debu jalan raya, konstruksi.",
    'PM2.5': "Partikel udara halus berukuran < 2.5 mikrometer. Berbahaya bagi pernapasan, bersumber dari asap kendaraan & industri.",
    'O3': "Ozon permukaan. Terbentuk akibat reaksi kimia polutan kendaraan dengan sinar matahari.",
    'CO': "Karbon Monoksida. Gas tidak berbau dari pembakaran kendaraan bermotor yang tidak sempurna.",
    'SO2': "Sulfur Dioksida. Gas bersumber dari pembakaran batu bara/bensin di industri atau pembangkit listrik.",
    'NO2': "Nitrogen Dioksida. Polutan gas hasil pembakaran bersuhu tinggi seperti mesin kendaraan."
}

# --- 3. LOADING & PREPROCESSING DATASET ---
@st.cache_data
def load_data():
    # Membaca data lokal df_clean.csv
    df = pd.read_csv("df_clean.csv")
    df['tanggal'] = pd.to_datetime(df['tanggal'])
    df['tahun'] = df['tanggal'].dt.year
    df['bulan_num'] = df['tanggal'].dt.month
    
    # Standarisasi teks kategori ke uppercase untuk menjaga sinkronisasi warna
    if 'categori' in df.columns:
        df['categori'] = df['categori'].str.upper().str.strip()
    if 'critical' in df.columns:
        df['critical'] = df['critical'].str.upper().str.strip()
        
    return df

try:
    df_orig = load_data()
except Exception as e:
    st.error(f"Gagal memuat file dataset 'df_clean.csv'. Pastikan file berada di direktori yang sama. Error: {e}")
    st.stop()

# --- 4. SIDEBAR & FILTER GLOBAL ---
with st.sidebar:
    st.image("https://img.icons8.com/external-flatart-icons-lineal-color-flatart-icons/64/000000/external-ecology-environmentalism-flatart-icons-lineal-color-flatart-icons.png", width=50)
    st.title("Kontrol Analisis")
    st.markdown("---")
    
    # Filter 1: Dropdown Pilih Stasiun SPKU (Menggunakan istilah kedinasan)
    list_stasiun = sorted(list(df_orig['stasiun'].unique()))
    opsi_stasiun = ["Semua Stasiun"] + list_stasiun
    selected_stasiun = st.selectbox("Pilih Stasiun SPKU:", opsi_stasiun, index=0)
    
    # Filter 2: Rentang Waktu (Date Range Picker)
    min_date = df_orig['tanggal'].min().to_pydatetime()
    max_date = df_orig['tanggal'].max().to_pydatetime()
    
    st.markdown("**Rentang Waktu Pengukuran:**")
    date_range = st.date_input(
        "Pilih Rentang Tanggal:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

# Menerapkan Filter Global ke Dataset
df_filtered = df_orig.copy()
if selected_stasiun != "Semua Stasiun":
    df_filtered = df_filtered[df_filtered['stasiun'] == selected_stasiun]

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_dt, end_dt = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    df_filtered = df_filtered[(df_filtered['tanggal'] >= start_dt) & (df_filtered['tanggal'] <= end_dt)]

# --- 5. HEADER DASHBOARD ---
col_header, col_download = st.columns([4, 1])
with col_header:
    st.title("🌱 Kualitas Udara (ISPU) Provinsi DKI Jakarta")
    st.markdown(f"**Sasaran Pengamatan:** Kepala Dinas Lingkungan Hidup | **Wilayah:** {selected_stasiun} | **Periode:** {date_range[0]} s/d {date_range[1]}")
with col_download:
    st.markdown("<br>", unsafe_allow_html=True)
    # Fitur UX: Tombol Unduh Laporan Eksekutif (Simulasi Siap Cetak/Rapat)
    st.download_button(
        label="📥 Unduh Laporan Eksekutif",
        data=df_filtered.to_csv(index=False),
        file_name=f"Laporan_ISPU_DKI_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True,
        help="Klik untuk mengunduh kompilasi data aktif dalam format CSV siap lampir."
    )

st.markdown("---")

# --- 6. STRUKTUR DESAIN TAB ---
tab1, tab2, tab3 = st.tabs([
    "📈 Executive Summary", 
    "🍂 Analisis Parameter & Musiman", 
    "🏢 Perbandingan Antar Stasiun SPKU"
])

# ==============================================================================
# TAB 1: EXECUTIVE SUMMARY
# ==============================================================================
with tab1:
    st.subheader("Indikator Kinerja Utama (KPI)")
    
    # Perhitungan Metrik Utama
    if not df_filtered.empty:
        avg_ispu = round(df_filtered['max'].mean(), 1)
        
        # Penentuan status warna berjalan rata-rata ISPU harian
        status_kategori = "BAIK" if avg_ispu <= 50 else ("SEDANG" if avg_ispu <= 100 else "TIDAK SEHAT")
        
        # Persentase hari Tidak Sehat atau lebih buruk
        total_hari = len(df_filtered)
        hari_buruk = len(df_filtered[df_filtered['categori'].isin(['TIDAK SEHAT', 'SANGAT TIDAK SEHAT', 'BERBAHAYA'])])
        pct_hari_buruk = round((hari_buruk / total_hari) * 100, 1) if total_hari > 0 else 0
        
        # Polutan dominan (Critical Pollutant)
        polutan_valid = df_filtered[df_filtered['critical'].notna() & (df_filtered['critical'] != '')]
        top_pollutant = polutan_valid['critical'].mode().values[0] if not polutan_valid.empty else "N/A"
    else:
        avg_ispu, pct_hari_buruk, top_pollutant, status_kategori = 0, 0, "N/A", "N/A"

    # Penayangan Widget KPI
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    with kpi_col1:
        st.metric(
            label="Rata-Rata Nilai ISPU Harian",
            value=f"{avg_ispu} Poin",
            delta=f"Kategori: {status_kategori}",
            delta_color="off" if status_kategori in ["BAIK","SEDANG"] else "inverse",
            help="Nilai agregat indeks standar pencemar udara tertinggi lintas seluruh parameter utama."
        )
    with kpi_col2:
        st.metric(
            label="Tingkat Risiko Kesehatan (% Hari Tidak Sehat+)",
            value=f"{pct_hari_buruk} %",
            delta=f"{hari_buruk} Hari Terdeteksi",
            delta_color="inverse",
            help="Rasio jumlah hari dengan kategori kualitas udara Tidak Sehat hingga Berbahaya. Target Visual: Mendekati 0%."
        )
    with kpi_col3:
        penjelasan_pop = GLOSARIUM_POLUTAN.get(top_pollutant, "Parameter kritis penentu.")
        st.metric(
            label="Polutan Utama (Critical Pollutant)",
            value=top_pollutant,
            help=f"Polutan yang paling sering menjadi pemicu nilai ISPU tertinggi di periode ini. Info: {penjelasan_pop}"
        )

    st.markdown("---")
    
    # Bagian 2: Tren Real-Time & Historis ISPU
    st.subheader("Tren Historis & Fluktuasi Nilai ISPU")
    
    # Fitur Non-Teknis: Toggle Granularitas Waktu
    granularitas = st.radio(
        "Pilih Struktur Waktu Grafik Tren:",
        options=["Harian", "Bulanan", "Tahunan"],
        horizontal=True
    )
    
    if not df_filtered.empty:
        if granularitas == "Harian":
            df_trend = df_filtered.groupby('tanggal')['max'].mean().reset_index()
            x_axis_field = 'tanggal'
        elif granularitas == "Bulanan":
            df_filtered['thn_bln'] = df_filtered['tanggal'].dt.to_period('M').astype(str)
            df_trend = df_filtered.groupby('thn_bln')['max'].mean().reset_index()
            x_axis_field = 'thn_bln'
        else:
            df_trend = df_filtered.groupby('tahun')['max'].mean().reset_index()
            x_axis_field = 'tahun'
            
        fig_trend = px.line(
            df_trend, x=x_axis_field, y='max',
            labels={x_axis_field: 'Waktu Analisis', 'max': 'Rata-rata Maksimum ISPU'},
            color_discrete_sequence=[COLOR_PRIMARY]
        )
        
        # Rekomendasi UX: Garis Ambang Batas Baku Mutu (Threshold Line > 100)
        fig_trend.add_hline(
            y=100, line_dash="dash", line_color="#EF4444", line_width=2,
            annotation_text="Ambang Batas Baku Mutu Lingkungan (100)", 
            annotation_position="top left"
        )
        
        fig_trend.update_layout(
            hovermode="x unified",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#E2E8F0")
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("Tidak ada data tersedia pada rentang filter ini.")

# ==============================================================================
# TAB 2: ANALISIS PARAMETER & ANALISIS MUSIMAN
# ==============================================================================
with tab2:
    col_musiman, col_kritis = st.columns([1, 1])
    
    with col_musiman:
        st.subheader("🗓️ Pola Kualitas Udara Musiman (Bulanan)")
        st.markdown("*Deteksi dini kecenderungan kenaikan polusi udara pada siklus bulan tahunan.*")
        
        if not df_filtered.empty:
            # Pivot data untuk membuat Heatmap Matriks (Sumbu X: Bulan, Sumbu Y: Tahun)
            df_filtered['nama_bulan'] = df_filtered['tanggal'].dt.strftime('%b')
            df_filtered['bulan_index'] = df_filtered['tanggal'].dt.month
            
            df_matrix = df_filtered.groupby(['tahun', 'bulan_index', 'nama_bulan'])['max'].mean().reset_index()
            df_matrix = df_matrix.sort_values('bulan_index')
            
            # Pivot table
            df_pivot = df_matrix.pivot(index='tahun', columns='nama_bulan', values='max')
            # Urutan bulan yang logis
            order_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            df_pivot = df_pivot.reindex(columns=[m for m in order_months if m in df_pivot.columns])
            
            fig_heatmap = px.imshow(
                df_pivot,
                labels=dict(x="Bulan dalam Setahun", y="Tahun", color="Nilai Rata ISPU"),
                x=df_pivot.columns,
                y=df_pivot.index,
                color_continuous_scale="YlOrRd" # Gradasi merah-kuning sesuai brief
            )
            fig_heatmap.update_layout(coloraxis_colorbar=dict(title="Skala ISPU"))
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("Data tidak cukup untuk menyusun pola musiman.")
            
    with col_kritis:
        st.subheader("🧪 Distribusi Proporsi Parameter Kritis")
        st.markdown("*Komposisi zat pencemar utama yang bertanggung jawab menurunkan kebersihan udara.*")
        
        df_crit_clean = df_filtered[df_filtered['critical'].notna() & (df_filtered['critical'] != "")]
        if not df_crit_clean.empty:
            df_prop = df_crit_clean.groupby(['stasiun', 'critical']).size().reset_index(name='jumlah_hari')
            
            # Stacked Bar Chart (100%)
            fig_stack = px.bar(
                df_prop, x="stasiun", y="jumlah_hari", color="critical",
                title="Perbandingan Polutan Dominan Lintas Stasiun SPKU",
                labels={'jumlah_hari': 'Aktivitas Hari Pengukuran', 'stasiun': 'Stasiun Pemantau'},
                barmode="stack",
                color_discrete_scheme=px.colors.qualitative.Safe
            )
            fig_stack.update_layout(yaxis=dict(range=[0, 1000])) # Rentang 0-1000 sesuai parameter brief
            st.plotly_chart(fig_stack, use_container_width=True)
        else:
            st.info("Data parameter kritis kosong.")

    st.markdown("---")
    st.subheader("🔄 Tren Pergeseran Jenis Polutan Utama (Tahun ke Tahun)")
    
    if not df_filtered.empty:
        # Analisis tahun ke tahun untuk mendeteksi pergeseran polutan utama
        df_yearly_crit = df_filtered[df_filtered['critical'].notna() & (df_filtered['critical'] != "")].groupby(['tahun', 'critical']).size().reset_index(name='hari')
        fig_year_comp = px.bar(
            df_yearly_crit, x='tahun', y='hari', color='critical',
            title="Evolusi Komposisi Pencemar Kritis Tahunan di Jakarta",
            barmode='group',
            labels={'hari': 'Akumulasi Hari Pengukuran', 'tahun': 'Tahun Periode'}
        )
        st.plotly_chart(fig_year_comp, use_container_width=True)

# ==============================================================================
# TAB 3: PERBANDINGAN ANTAR STASIUN SPKU
# ==============================================================================
with tab3:
    st.subheader("🏢 Komparasi Komprehensif Kualitas Udara Antar Stasiun SPKU")
    st.markdown("*Identifikasi area prioritas lokal guna perencanaan rekayasa lalu lintas atau pengawasan industri.*")
    
    # Menggunakan keseluruhan data (bukan filter stasiun tunggal) agar perbandingan 5 stasiun tetap komprehensif
    df_compare_base = df_orig.copy()
    if isinstance(date_range, tuple) and len(date_range) == 2:
        df_compare_base = df_compare_base[(df_compare_base['tanggal'] >= start_dt) & (df_compare_base['tanggal'] <= end_dt)]
        
    if not df_compare_base.empty:
        # Bagian 1: Matriks Perbandingan Ringkasan Eksekutif (Tabel)
        st.write("📊 **Matriks Perbandingan Kondisi Rata-Rata Wilayah**")
        
        # Proses agregasi per stasiun
        df_table_agg = df_compare_base.groupby('stasiun').agg(
            Rata_Rata_ISPU=('max', 'mean'),
            Hari_Terpantau=('tanggal', 'count')
        ).reset_index()
        
        df_table_agg['Rata_Rata_ISPU'] = df_table_agg['Rata_Rata_ISPU'].round(1)
        
        # Mencari parameter kritis utama untuk masing-masing stasiun
        list_crit_mode = []
        for stn in df_table_agg['stasiun']:
            subset = df_compare_base[(df_compare_base['stasiun'] == stn) & (df_compare_base['critical'].notna())]
            if not subset.empty:
                list_crit_mode.append(subset['critical'].mode().values[0])
            else:
                list_crit_mode.append("N/A")
                
        df_table_agg['Parameter_Kritis_Utama'] = list_crit_mode
        
        # Mengubah penamaan kolom ke bahasa kedinasan operasional yang scannable
        df_table_agg.columns = ['Nama Stasiun SPKU', 'Rata-Rata Nilai ISPU', 'Total Hari Pengamatan', 'Parameter Kritis Utama']
        
        # Tampilkan tabel representatif dengan pengayaan visual internal Streamlit
        st.dataframe(
            df_table_agg.style.background_gradient(cmap="YlOrRd", subset=['Rata-Rata Nilai ISPU']),
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Bagian 2: Distribusi Kategori Udara Per Stasiun (Horizontal Stacked Bar Chart 100%)
        st.write("📈 **Distribusi Kategori Mutu Udara per Wilayah Pengamatan**")
        
        df_dist_stasiun = df_compare_base.groupby(['stasiun', 'categori']).size().reset_index(name='jumlah_hari')
        
        # Menghitung persentase kontribusi agar menjadi Stacked Bar 100%
        df_total_stn = df_compare_base.groupby('stasiun').size().reset_index(name='total_hari_stn')
        df_dist_stasiun = pd.merge(df_dist_stasiun, df_total_stn, on='stasiun')
        df_dist_stasiun['Persentase_Hari'] = (df_dist_stasiun['jumlah_hari'] / df_dist_stasiun['total_hari_stn']) * 100
        df_dist_stasiun['Persentase_Hari'] = df_dist_stasiun['Persentase_Hari'].round(1)
        
        fig_horiz_share = px.bar(
            df_dist_stasiun, x='Persentase_Hari', y='stasiun', color='categori',
            orientation='h',
            title="Proporsi Kategori Udara Standar LHK Lintas Stasiun SPKU",
            labels={'Persentase_Hari': 'Persentase Proporsi Waktu Harian (%)', 'stasiun': 'Stasiun SPKU'},
            color_discrete_map=MAP_WARNA_ISPU,
            category_orders={"categori": ["BAIK", "SEDANG", "TIDAK SEHAT", "SANGAT TIDAK SEHAT", "BERBAHAYA"]}
        )
        
        fig_horiz_share.update_layout(
            legend_title_text='Kategori Mutu Udara',
            xaxis=dict(ticksuffix="%")
        )
        st.plotly_chart(fig_horiz_share, use_container_width=True)
        
    else:
        st.info("Data komparasi stasiun tidak tersedia pada filter ini.")

# --- 7. FOOTER & KAMUS POP-UP GLOSARIUM PENDUKUNG ---
st.markdown("---")
col_foot1, col_foot2 = st.columns([3, 2])
with col_foot1:
    st.caption("Dashboard Monitoring Kualitas Udara v2.1 • Dikembangkan Menggunakan Streamlit Engine & Plotly Analytics • Hak Cipta Dinas Lingkungan Hidup DKI Jakarta.")
with col_foot2:
    # Solusi UX: Kamus Data Pop-up ekspander interaktif di bagian bawah agar tidak mengganggu layout utama
    with st.expander("❓ Glosarium Singkat Parameter Polutan (Kamus Data pimpinan)"):
        for param, desc in GLOSARIUM_POLUTAN.items():
            st.markdown(f"**{param}** : {desc}")
