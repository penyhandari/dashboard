import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# ==========================================
# 1. KONFIGURASI HALAMAN & THEME
# ==========================================
st.set_page_config(
    page_title="Napas Sehat - Dashboard Kualitas Udara",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injeksi CSS Khusus untuk Tampilan Premium & Non-Templated
st.markdown("""
    <style>
        /* Import Font Modern */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap');
        
        * {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        
        /* Ganti Warna Background Sidebar & Main Content */
        .stApp {
            background-color: #F8FAFC;
        }
        
        [data-testid="stSidebar"] {
            background-color: #0F172A;
            color: #FFFFFF;
        }
        
        /* Modifikasi Card Metrik */
        .metric-card {
            background-color: #FFFFFF;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
            border: 1px solid #E2E8F0;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
        }
        
        /* Status Badges */
        .badge {
            padding: 6px 12px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            display: inline-block;
            text-transform: uppercase;
        }
        
        .badge-healthy { background-color: #DCFCE7; color: #15803D; }
        .badge-moderate { background-color: #FEF3C7; color: #B45309; }
        .badge-unhealthy { background-color: #FEE2E2; color: #991B1B; }
        .badge-hazardous { background-color: #F3E8FF; color: #6B21A8; }
        
        /* Tipografi Kustom */
        h1, h2, h3 {
            color: #0F172A !important;
            font-weight: 700 !important;
        }
        
        .hero-text {
            font-size: 1.1rem;
            color: #475569;
            margin-bottom: 24px;
        }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# 2. PENGAMBILAN & PENYIAPAN DATA (CACHE)
# ==========================================
@st.cache_data
def load_cleaned_data():
    # Daftar prioritas file yang akan dimuat
    possible_files = [
        'India_Air_Quality_Cleaned.xlsx - Cleaned Data.csv',
        'India Air Quality Analysis.csv'
    ]
    
    df = None
    for file in possible_files:
        if os.path.exists(file):
            try:
                # Menggunakan delimiter ';' jika mendeteksi file mentah asli
                delim = ';' if 'Analysis' in file else ','
                df = pd.read_csv(file, delimiter=delim, na_values=["NA", "na", "Null", " ", "NA\r"])
                break
            except Exception:
                continue
                
    # Jika tidak ada file fisik, buat data simulasi representatif agar dashboard tetap menyala
    if df is None:
        dates = pd.date_range(start="2015-01-01", end="2015-12-31", freq="D")
        locations = ['Hyderabad', 'Chittoor', 'Guntur', 'Kurnool', 'Vijayawada', 'Visakhapatnam']
        types = ['Residential, Rural and other Areas', 'Industrial Area', 'Sensitive Area']
        
        np.random.seed(42)
        n_rows = 2000
        
        df = pd.DataFrame({
            'stn_code': np.random.choice([150, 151, 152], n_rows),
            'state': ['Andhra Pradesh'] * n_rows,
            'location': np.random.choice(locations, n_rows),
            'type': np.random.choice(types, n_rows),
            'so2': np.random.uniform(2, 25, n_rows),
            'no2': np.random.uniform(5, 55, n_rows),
            'rspm': np.random.uniform(30, 220, n_rows),
            'spm': np.random.uniform(80, 380, n_rows),
            'pm2_5': [36.0] * n_rows,
            'date': np.random.choice(dates, n_rows)
        })

    # Standardisasi nama kolom (mengubah menjadi lowercase dan strip spasi)
    df.columns = df.columns.str.strip().str.lower()
    
    # Standardisasi format tanggal dan waktu
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    else:
        df['date'] = pd.to_datetime(df['sampling_date'], errors='coerce')
        
    # Isi tanggal kosong jika ada kegagalan parsing
    df['date'] = df['date'].fillna(pd.Timestamp('2015-01-01'))
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.strftime('%B')
    df['month_num'] = df['date'].dt.month
    
    # Konversi kolom numerik yang kritis
    numeric_cols = ['so2', 'no2', 'rspm', 'spm']
    for col in numeric_cols:
        if col in df.columns:
            # Hilangkan karakter non-numerik jika ada typo input
            df[col] = df[col].astype(str).str.replace(r'[^\d\.]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # Imputasi jika masih ada NaN sisa menggunakan nilai median
            df[col] = df[col].fillna(df[col].median())
        else:
            # Buat kolom dengan median default jika kolom tidak ada sama sekali
            df[col] = 40.0
            
    # Pastikan kolom kategorikal bersih dari NA/kosong
    categorical_cols = ['state', 'location', 'type']
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str).str.strip()
        else:
            df[col] = "Unknown"
            
    return df

df = load_cleaned_data()


# ==========================================
# 3. SIDEBAR CONTROLS (FILTER INTERAKTIF)
# ==========================================
st.sidebar.markdown("<h2 style='color: #FFFFFF !important; font-size: 20px; margin-bottom: 20px;'>🔍 Filter Wilayah</h2>", unsafe_allow_html=True)

# Filter 1: Negara Bagian (State)
available_states = sorted(df['state'].unique())
selected_state = st.sidebar.selectbox("Pilih Negara Bagian", available_states)

# Filter 2: Kota (Location) - Diperbarui dinamis berdasarkan State yang dipilih
filtered_by_state = df[df['state'] == selected_state]
available_cities = sorted(filtered_by_state['location'].unique())
selected_city = st.sidebar.selectbox("Pilih Kota / Lokasi", ["Semua Kota"] + list(available_cities))

# Filter 3: Tipe Area (Peruntukan Lahan)
available_types = sorted(df['type'].unique())
selected_types = st.sidebar.multiselect("Tipe Area", available_types, default=available_types)

# Pemrosesan Filter Akhir pada DataFrame utama
df_filtered = filtered_by_state[filtered_by_state['type'].isin(selected_types)]
if selected_city != "Semua Kota":
    df_filtered = df_filtered[df_filtered['location'] == selected_city]


# ==========================================
# 4. LOGIKA AQI & STATUS KESEHATAN (EDUKATIF)
# ==========================================
# Menggunakan RSPM (PM10) sebagai representasi indeks utama kualitas udara di publik
avg_rspm = df_filtered['rspm'].mean() if not df_filtered.empty else 0
avg_no2 = df_filtered['no2'].mean() if not df_filtered.empty else 0
avg_so2 = df_filtered['so2'].mean() if not df_filtered.empty else 0
avg_spm = df_filtered['spm'].mean() if not df_filtered.empty else 0

# Penentuan status kesehatan masyarakat
if avg_rspm < 60:
    status_label = "BAIK / SEHAT"
    status_class = "badge-healthy"
    status_color = "#15803D"
    advice = "Kondisi udara sangat baik untuk beraktivitas di luar ruangan. Hirup napas dalam-dalam dan nikmati hari Anda!"
elif avg_rspm < 100:
    status_label = "SEDANG"
    status_class = "badge-moderate"
    status_color = "#B45309"
    advice = "Kualitas udara dapat diterima. Namun, bagi kelompok yang sangat sensitif (penderita asma/lansia) sebaiknya membatasi aktivitas fisik berat di luar ruang."
elif avg_rspm < 150:
    status_label = "TIDAK SEHAT"
    status_class = "badge-unhealthy"
    status_color = "#991B1B"
    advice = "Udara mulai berbahaya bagi kelompok sensitif. Disarankan mengurangi waktu berlama-lama di luar atau gunakan masker standar medis jika bepergian."
else:
    status_label = "BERBAHAYA"
    status_class = "badge-hazardous"
    status_color = "#6B21A8"
    advice = "Peringatan Kesehatan! Seluruh warga berisiko mengalami dampak negatif. Hindari aktivitas luar ruangan yang tidak mendesak. Gunakan selalu masker N95."


# ==========================================
# 5. HEADER & HERO SECTION
# ==========================================
st.markdown("<h1 style='font-size: 38px; margin-bottom: 10px;'>🍃 Napas Sehat India</h1>", unsafe_allow_html=True)
st.markdown(
    f"<p class='hero-text'>Membantu masyarakat mengenali kebersihan udara di lingkungan sekitar demi paru-paru yang lebih sehat. Saat ini mengamati wilayah <b>{selected_state}</b> - <b>{selected_city}</b>.</p>", 
    unsafe_allow_html=True
)

st.markdown("---")


# ==========================================
# 6. DYNAMIC KPI CARDS (DASHBOARD GRID)
# ==========================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-card" style="border-top: 5px solid {status_color};">
            <div class="kpi-title">Indeks Udara Saat Ini</div>
            <div class="kpi-value" style="color: {status_color}; font-size: 24px; margin: 10px 0;">{status_label}</div>
            <span class="badge {status_class}">RSPM: {avg_rspm:.1f} µg/m³</span>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card" style="border-top: 5px solid #005B60;">
            <div class="kpi-title">Polusi Debu (RSPM)</div>
            <div class="kpi-value" style="color: #0F172A; margin: 10px 0;">{avg_rspm:.1f} <span style="font-size:14px;color:#64748B;">µg/m³</span></div>
            <p style="font-size: 11px; color: #64748B;">Ambang Aman WHO: <font color="#15803D"><b>50 µg/m³</b></font></p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card" style="border-top: 5px solid #1E3A8A;">
            <div class="kpi-title">Gas Kendaraan (NO2)</div>
            <div class="kpi-value" style="color: #0F172A; margin: 10px 0;">{avg_no2:.1f} <span style="font-size:14px;color:#64748B;">µg/m³</span></div>
            <p style="font-size: 11px; color: #64748B;">Batas Aman Emisi: <font color="#15803D"><b>40 µg/m³</b></font></p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card" style="border-top: 5px solid #B45309;">
            <div class="kpi-title">Zat Padat Melayang (SPM)</div>
            <div class="kpi-value" style="color: #0F172A; margin: 10px 0;">{avg_spm:.1f} <span style="font-size:14px;color:#64748B;">µg/m³</span></div>
            <p style="font-size: 11px; color: #64748B;">Partikel debu kasar di atmosfer</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ==========================================
# 7. VISUALISASI UTAMA (PLOTLY INTEGRATION)
# ==========================================
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("### 📈 Tren Polusi Bulanan")
    st.markdown("<p style='font-size:13px; color:#64748B;'>Mendeteksi musim kritis kapan polusi udara melonjak tinggi agar masyarakat dapat melakukan antisipasi.</p>", unsafe_allow_html=True)
    
    if not df_filtered.empty:
        # Agregasi data tren bulanan
        monthly_data = df_filtered.groupby(['month_num', 'month'])[['rspm', 'no2']].mean().reset_index()
        monthly_data = monthly_data.sort_values('month_num')
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=monthly_data['month'], y=monthly_data['rspm'],
            mode='lines+markers', name='Debu Halus (RSPM)',
            line=dict(color='#DC2626', width=3),
            marker=dict(size=8)
        ))
        fig_trend.add_trace(go.Scatter(
            x=monthly_data['month'], y=monthly_data['no2'],
            mode='lines+markers', name='Gas Kendaraan (NO2)',
            line=dict(color='#2563EB', width=3),
            marker=dict(size=8)
        ))
        
        fig_trend.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=True, gridcolor='#E2E8F0'),
            yaxis=dict(showgrid=True, gridcolor='#E2E8F0', title="Konsentrasi (µg/m³)")
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("Pilih tipe area yang sesuai pada sidebar untuk memunculkan grafik.")

with chart_col2:
    st.markdown("### 🏢 Tingkat Polusi Berdasarkan Tipe Area")
    st.markdown("<p style='font-size:13px; color:#64748B;'>Membandingkan kualitas udara antara wilayah perumahan, industri, dan kawasan lindung/sensitif.</p>", unsafe_allow_html=True)
    
    if not df_filtered.empty:
        # Agregasi data berdasarkan Tipe Area
        area_data = df_filtered.groupby('type')['rspm'].mean().reset_index()
        
        fig_area = px.bar(
            area_data, x='rspm', y='type',
            orientation='h',
            color='rspm',
            color_continuous_scale=['#2E7D32', '#F9A825', '#C62828'],
            labels={'rspm': 'Rata-rata RSPM', 'type': 'Tipe Area'}
        )
        
        fig_area.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=20, b=20),
            coloraxis_showscale=False,
            xaxis=dict(showgrid=True, gridcolor='#E2E8F0', title="Rata-rata RSPM (µg/m³)")
        )
        st.plotly_chart(fig_area, use_container_width=True)
    else:
        st.info("Data area tidak tersedia.")

st.markdown("<br>", unsafe_allow_html=True)


# ==========================================
# 8. ANALISIS SPASIAL & TABULAR (KOTA TERPOLUSI)
# ==========================================
st.markdown("### 🏆 Peringkat Kualitas Udara Kota Terbaik vs Terburuk")
st.markdown("<p style='font-size:13px; color:#64748B;'>Daftar kota diurutkan berdasarkan konsentrasi debu halus (RSPM) untuk memudahkan pencarian zona aman.</p>", unsafe_allow_html=True)

col_table, col_edu = st.columns([2, 1])

with col_table:
    # Urutkan kota-kota berdasarkan rata-rata RSPM
    city_leaderboard = filtered_by_state.groupby('location')[['rspm', 'no2', 'so2']].mean().round(1).reset_index()
    city_leaderboard = city_leaderboard.sort_values('rspm', ascending=True) # Dari paling bersih
    
    # Gunakan st.column_config untuk format visual yang responsif dan aman tanpa error applymap
    st.dataframe(
        city_leaderboard,
        column_config={
            "location": st.column_config.TextColumn(
                "Nama Kota / Lokasi",
                help="Kota stasiun pengamatan resmi",
                width="medium"
            ),
            "rspm": st.column_config.NumberColumn(
                "Debu Halus (RSPM)",
                help="Batas aman standar: < 60",
                format="%.1f µg/m³"
            ),
            "no2": st.column_config.NumberColumn(
                "Gas Kendaraan (NO2)",
                help="Batas aman standar: < 40",
                format="%.1f µg/m³"
            ),
            "so2": st.column_config.NumberColumn(
                "Zat Asam Industri (SO2)",
                help="Batas aman standar: < 80",
                format="%.1f µg/m³"
            )
        },
        hide_index=True,
        use_container_width=True
    )

with col_edu:
    st.markdown("""
        <div style="background-color: #0F172A; color: #FFFFFF; padding: 24px; border-radius: 16px; height: 100%;">
            <h4 style="color: #FFFFFF !important; margin-bottom: 12px; font-size: 16px;">🌱 Mari Ambil Aksi Nyata</h4>
            <p style="font-size: 13px; line-height: 1.6; color: #E2E8F0; margin-bottom: 16px;">
                Polutan mikroskopis (seperti RSPM dan PM2.5) dapat dengan mudah menembus masker kain biasa dan masuk ke paru-paru Anda.
            </p>
            <ul style="font-size: 12px; line-height: 1.6; color: #CBD5E1; padding-left: 16px;">
                <li>Gunakan filter udara HEPA di dalam rumah Anda jika polusi di luar masuk kategori buruk.</li>
                <li>Tanam tanaman penyerap polutan alami seperti Lidah Mertua (Sansevieria) atau Palem Kuning.</li>
                <li>Dukung pemakaian transportasi publik demi mengurangi emisi NO2 harian.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)


# ==========================================
# 9. EDUKASI AKSI NYATA (RECOMMENDATION SECTION)
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"""
    <div style="background-color: {status_color}12; border-left: 6px solid {status_color}; padding: 20px; border-radius: 8px;">
        <h4 style="color: {status_color} !important; margin-bottom: 5px;">📍 Rekomendasi Kesehatan untuk Anda di {selected_city if selected_city != 'Semua Kota' else selected_state}:</h4>
        <p style="color: #334155; font-size: 14px; font-weight: 500;">{advice}</p>
    </div>
""", unsafe_allow_html=True)