import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURASI HALAMAN STREMLIT ---
st.set_page_config(
    page_title="Dashboard ISPU DKI Jakarta",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- LOADING DATASET ---
@st.cache_data
def load_data():
    # Membaca data dan memastikan tipe data tanggal benar
    df = pd.read_csv("df_clean.csv")
    df['tanggal'] = pd.to_datetime(df['tanggal'])
    df['tahun'] = df['tanggal'].dt.year
    df['nama_bulan'] = df['tanggal'].dt.strftime('%B')
    df['bulan_num'] = df['tanggal'].dt.month
    return df

try:
    df_clean = load_data()
except Exception as e:
    st.error(f"Gagal memuat file 'df_clean.csv'. Pastikan file berada di direktori yang sama. Error: {e}")
    st.stop()

# --- SIDEBAR & FILTER GLOBAL ---
st.sidebar.image("https://img.icons8.com/external-flatart-icons-lineal-color-flatart-icons/64/external-ecology-environmentalism-flatart-icons-lineal-color-flatart-icons.png", width=60)
st.sidebar.title("Kontrol Dashboard")
st.sidebar.markdown("---")

# Filter Stasiun
stasiun_options = ["Semua Stasiun"] + list(df_clean['stasiun'].unique())
selected_stasiun = st.sidebar.selectbox("Pilih Stasiun SPKU:", stasiun_options)

# Filter Rentang Tahun (menyesuaikan dataset)
min_year = int(df_clean['tahun'].min())
max_year = int(df_clean['tahun'].max())
selected_years = st.sidebar.slider("Rentang Tahun Analisis:", min_year, max_year, (min_year, max_year))

# Menerapkan Filter ke Data
df_filtered = df_clean[(df_clean['tahun'] >= selected_years[0]) & (df_clean['tahun'] <= selected_years[1])]
if selected_stasiun != "Semua Stasiun":
    df_filtered = df_filtered[df_filtered['stasiun'] == selected_stasiun]

# --- STANDAR WARNA ISPU KEMENTERIAN LHK ---
ispu_colors = {
    'BAIK': '#2ecc71',            # Hijau
    'SEDANG': '#3498db',          # Biru
    'TIDAK SEHAT': '#f1c40f',     # Kuning
    'SANGAT TIDAK SEHAT': '#e74c3c', # Merah
    'BERBAHAYA': '#8B0000'        # Hitam/Gelap
}

# --- HEADER UTAMA ---
st.title("🌱 Pemantauan Kualitas Udara (ISPU) DKI Jakarta")
st.markdown(f"**Sasaran Analisis:** Kepala Dinas Lingkungan Hidup Provinsi DKI Jakarta | **Periode:** {selected_years[0]} - {selected_years[1]}")
st.markdown("---")

# --- MEMBUAT STRUKTUR TAB ---
tab1, tab2, tab3 = st.tabs([
    "📈 Ringkasan Eksekutif", 
    "🍂 Pola Musiman & Parameter", 
    "🏢 Komparasi Antar Stasiun"
])

# ==============================================================================
# TAB 1: EXECUTIVE SUMMARY
# ==============================================================================
with tab1:
    st.subheader("Indikator Kinerja Utama (KPI)")
    
    # Perhitungan KPI
    avg_ispu = round(df_filtered['max'].mean(), 1) if not df_filtered.empty else 0
    
    # Persentase Tidak Sehat atau lebih buruk
    total_hari = len(df_filtered)
    hari_buruk = len(df_filtered[df_filtered['categori'].isin(['TIDAK SEHAT', 'SANGAT TIDAK SEHAT', 'BERBAHAYA'])])
    pct_buruk = round((hari_buruk / total_hari) * 100, 1) if total_hari > 0 else 0
    
    # Polutan Dominan
    top_pollutant = df_filtered['critical'].mode().values[0] if not df_filtered.empty and df_filtered['critical'].notna().any() else "N/A"
    
    # Tampilan KPI Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Rata-rata Harian Nilai ISPU", value=f"{avg_ispu} Poin", help="Agregat nilai indeks standar pencemar udara di periode terpilih")
    with col2:
        st.metric(label="Rasio Hari Tidak Sehat (+)", value=f"{pct_buruk} %", delta=f"{hari_buruk} Hari", delta_color="inverse", help="Persentase hari dengan kualitas udara kategori Tidak Sehat hingga Berbahaya")
    with col3:
        st.metric(label="Pencemar Dominan (Kritis)", value=top_pollutant, help="Parameter polutan yang paling sering menjadi pemicu nilai ISPU tertinggi")

    st.markdown("---")
    st.subheader("Tren Nilai ISPU dari Waktu ke Waktu")
    
    # Kontrol Granularitas Waktu khusus untuk Grafik Garis
    granularity = st.radio("Pilih Struktur Waktu Grafik:", ["Harian", "Bulanan", "Tahunan"], horizontal=True)
    
    if granularity == "Harian":
        df_trend = df_filtered.groupby('tanggal')['max'].mean().reset_index()
        x_col = 'tanggal'
    elif granularity == "Bulanan":
        df_filtered['thn_bln'] = df_filtered['tanggal'].dt.to_period('M').astype(str)
        df_trend = df_filtered.groupby('thn_bln')['max'].mean().reset_index()
        x_col = 'thn_bln'
    else:
        df_trend = df_filtered.groupby('tahun')['max'].mean().reset_index()
        x_col = 'tahun'
        
    fig_trend = px.line(df_trend, x=x_col, y='max', title=f"Tren Nilai Maksimal ISPU ({granularity})",
                        labels={'max': 'Rata-rata Nilai ISPU', x_col: 'Waktu'},
                        color_discrete_sequence=['#2c3e50'])
    
    # Menambahkan garis ambang batas baku mutu (ISPU = 100 adalah batas Sehat/Tidak Sehat)
    fig_trend.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Batas Ambang Tidak Sehat (100)", annotation_position="top left")
    fig_trend.update_layout(hovermode="x unified")
    st.plotly_chart(fig_trend, use_container_width=True)


# ==============================================================================
# TAB 2: POLA MUSIMAN & PARAMETER CRITICAL
# ==============================================================================
with tab2:
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("🗓️ Pola Kualitas Udara Bulanan (Siklus Musiman)")
        st.markdown("*Membantu mendeteksi bulan-bulan kritis polusi tahunan (misal: Musim Kemarau).*")
    
        # 1. Groupby menyertakan 'bulan_num' agar angkanya tidak hilang
        df_season = df_filtered.groupby(['bulan_num', 'nama_bulan'])['max'].mean().reset_index()
    
        # 2. Urutkan hasil groupby berdasarkan angka bulannya
        df_season = df_season.sort_values('bulan_num')
    
        # 3. Buat grafik menggunakan data yang sudah urut
        fig_season = px.bar(df_season, x='nama_bulan', y='max', 
                            title="Rata-rata Nilai ISPU per Bulan",
                            labels={'max': 'Rata-rata ISPU', 'nama_bulan': 'Bulan'},
                            color='max', color_continuous_scale=px.colors.sequential.YlOrRd)
    
        # 4. Opsional: Paksa Plotly untuk mengikuti urutan DataFrame (tidak diurutkan abjad lagi oleh Plotly)
        fig_season.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': df_season['nama_bulan']})
    
        st.plotly_chart(fig_season, use_container_width=True)
        
   with col_right:
        st.subheader("🧪 Distribusi Parameter Kritis per Tahun")
        st.markdown("*Persentase parameter polutan yang bertanggung jawab memicu pemburukan kualitas udara setiap tahunnya.*")
        
        # 1. Pastikan data tidak kosong dan buat salinan data
        df_crit = df_filtered[df_filtered['critical'].notna()].copy()
        
        # 2. Ambil komponen tahun dari kolom tanggal (asumsi nama kolom adalah 'tanggal')
        # Jika Anda sudah punya kolom 'tahun', baris di bawah ini bisa dihapus/dikomentari
        if 'tahun' not in df_crit.columns:
            df_crit['tahun'] = pd.to_datetime(df_crit['tanggal']).dt.year
        
        # 3. Hitung frekuensi kemunculan polutan per tahun
        df_crit_count = df_crit.groupby(['tahun', 'critical']).size().reset_index(name='jumlah_kemunculan')
        
        # 4. Hitung total kemunculan per tahun untuk mencari persentase
        df_crit_count['total_tahunan'] = df_crit_count.groupby('tahun')['jumlah_kemunculan'].transform('sum')
        df_crit_count['persentase'] = (df_crit_count['jumlah_kemunculan'] / df_crit_count['total_tahunan']) * 100
        
        # 5. Buat Stacked Bar Chart (Sumbu X = Tahun, Sumbu Y = Persentase, Warna = Polutan)
        fig_crit = px.bar(df_crit_count, 
                          x='tahun', 
                          y='persentase', 
                          color='critical',
                          title="Tren Kontribusi Parameter Kritis Tahunan (%)",
                          labels={'persentase': 'Persentase (%)', 'tahun': 'Tahun', 'critical': 'Parameter Kritis'},
                          text=df_crit_count['persentase'].apply(lambda x: f'{x:.1f}%'), # Menampilkan teks % di dalam bar
                          color_discrete_sequence=px.colors.qualitative.Safe) # Menggunakan palet warna kategori yang aman
        
        # 6. Mengatur tampilan grafik agar menjadi 100% Stacked Bar dan merapikan teks
        fig_crit.update_layout(barmode='stack', yawaxis_ticksuffix="%")
        fig_crit.update_traces(textposition='inside', texttemplate='%{text}')
        
        # 7. Mengunci rentang sumbu Y dari 0 sampai 100%
        fig_crit.update_yaxes(range=[0, 100], title_text="Persentase Kontribusi")
        fig_crit.update_xaxes(type='category', title_text="Tahun") # Memaksa tahun dibaca sebagai kategori (bukan angka kontinu)
        
        st.plotly_chart(fig_crit, use_container_width=True)


# ==============================================================================
# TAB 3: PERBANDINGAN ANTAR STASIUN SPKU
# ==============================================================================
with tab3:
    st.subheader("🏢 Komparasi Kualitas Udara Antar Stasiun Pemantau (SPKU)")
    st.markdown("*Gunakan halaman ini untuk membandingkan performa kebersihan udara lintas wilayah Jakarta.*")
    
    # 1. Tabel Agregat per Stasiun
    df_stasiun_all = df_clean[(df_clean['tahun'] >= selected_years[0]) & (df_clean['tahun'] <= selected_years[1])]
    df_compare = df_stasiun_all.groupby('stasiun').agg(
        Rata_Rata_ISPU=('max', 'mean'),
        Hari_Pengamatan=('tanggal', 'count')
    ).reset_index()
    df_compare['Rata_Rata_ISPU'] = df_compare['Rata_Rata_ISPU'].round(1)
    
    col_tbl, col_cht = st.columns([1, 2])
    
    with col_tbl:
        st.write("📊 **Ringkasan Angka Per Stasiun**")
        st.dataframe(df_compare, use_container_width=True, hide_index=True)
        
    with col_cht:
        # 2. Horizontal Stacked Bar Kategori ISPU per Stasiun
        df_dist = df_stasiun_all.groupby(['stasiun', 'categori']).size().reset_index(name='hari')
        
        fig_dist = px.bar(df_dist, x='hari', y='stasiun', color='categori', title="Proporsi Kategori Kualitas Udara Kontinu",
                          orientation='h', labels={'hari': 'Jumlah Hari Berlangsung', 'stasiun': 'Stasiun SPKU'},
                          color_discrete_map=ispu_colors, barmode='stack')
        fig_dist.update_layout(legend_title_text='Kategori')
        st.plotly_chart(fig_dist, use_container_width=True)

# --- FOOTER ---
st.markdown("---")
st.caption("Dashboard dikembangkan menggunakan Streamlit & Plotly Engine. Hak Cipta Dinas Lingkungan Hidup DKI Jakarta 2026.")
