import streamlit as tf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium
import folium

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Executive Air Quality Insight – DKI Jakarta",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. GENERATE MOCK DATA (Untuk keperluan demo)
@st.cache_data
def load_mock_data():
    np.random.seed(42)
    dates = pd.date_range(start="2024-01-01", end="2026-05-31", freq="D")
    stations = ["Bundaran HI", "Kelapa Gading", "Jagakarsa", "Kebon Jeruk", "Lubang Buaya"]
    pollutants = ["PM2.5", "PM10", "SO2", "CO", "O3", "NO2"]
    
    data = []
    for date in dates:
        for station in stations:
            ispu = np.random.randint(30, 180)  # Variasi nilai ISPU
            # Kategori berdasarkan PM2.5 standard KLHK
            if ispu <= 50: cat = "Baik"
            elif ispu <= 100: cat = "Sedang"
            elif ispu <= 150: cat = "Tidak Sehat"
            elif ispu <= 300: cat = "Sangat Tidak Sehat"
            else: cat = "Berbahaya"
            
            critical = np.random.choice(pollutants, p=[0.5, 0.2, 0.05, 0.05, 0.1, 0.1])
            data.append([date, station, ispu, cat, critical, date.year, date.strftime('%B')])
            
    df = pd.DataFrame(data, columns=["Tanggal", "Stasiun", "ISPU", "Kategori", "Critical_Param", "Tahun", "Bulan"])
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    
    # Koordinat Stasiun untuk Peta
    coords = {
        "Bundaran HI": [-6.195, 106.823],
        "Kelapa Gading": [-6.151, 106.905],
        "Jagakarsa": [-6.333, 106.812],
        "Kebon Jeruk": [-6.193, 106.764],
        "Lubang Buaya": [-6.291, 106.910]
    }
    df["Lat"] = df["Stasiun"].map(lambda x: coords[x][0])
    df["Lon"] = df["Stasiun"].map(lambda x: coords[x][1])
    return df

df_clean = load_mock_data()

# Palet warna standar ISPU KLHK
COLOR_MAP = {
    "Baik": "#2ecc71",          # Hijau
    "Sedang": "#3498db",        # Biru
    "Tidak Sehat": "#f1c40f",   # Kuning
    "Sangat Tidak Sehat": "#e74c3c", # Merah
    "Berbahaya": "#2c3e50"      # Hitam/Gelap
}

# 3. SIDEBAR / PANEL FILTER (Kriteria 1)
st.sidebar.header("📊 Filter Analisis")
st_date = st.sidebar.date_input("Pilih Rentang Tanggal", [df_clean["Tanggal"].min(), df_clean["Tanggal"].max()])
all_stations = df_clean["Stasiun"].unique().tolist()
selected_stations = st.sidebar.multiselect("Pilih Stasiun Pemantauan", all_stations, default=all_stations)

# Filter Data Berdasarkan Input
if len(st_date) == 2:
    start_date, end_date = pd.to_datetime(st_date[0]), pd.to_datetime(st_date[1])
    df_filtered = df_clean[(df_clean["Tanggal"] >= start_date) & (df_clean["Tanggal"] <= end_date)]
else:
    df_filtered = df_clean

if selected_stations:
    df_filtered = df_filtered[df_filtered["Stasiun"].isin(selected_stations)]

# DASHBOARD UTAMA
st.title("🏛️ Executive Air Quality Insight – DKI Jakarta")
st.markdown("Dashboard ringkasan eksekutif untuk Kepala Dinas Lingkungan Hidup Provinsi DKI Jakarta.")
st.write("---")

# 4. ROW 1: SCORECARDS & PETA KONDISI TERKINI (Kriteria 2)
col1, col2, col3, col4 = st.columns([1.5, 1.5, 1.5, 3.5])

# Hitung Metrik
avg_ispu = int(df_filtered["ISPU"].mean()) if not df_filtered.empty else 0
total_days = len(df_filtered)
bad_days = len(df_filtered[df_filtered["Kategori"].isin(["Tidak Sehat", "Sangat Tidak Sehat", "Berbahaya"])])
pct_bad_days = (bad_days / total_days * 100) if total_days > 0 else 0
dominant_param = df_filtered["Critical_Param"].mode()[0] if not df_filtered.empty else "-"

with col1:
    st.metric(label="Rata-rata ISPU Harian", value=avg_ispu)
with col2:
    st.metric(label="% Hari Tidak Sehat+", value=f"{pct_bad_days:.1f}%")
with col3:
    st.metric(label="Pencemar Dominan", value=dominant_param)

with col4:
    st.subheader("📍 Kondisi Terkini per Stasiun")
    # Mengambil data tanggal terakhir yang tersedia
    latest_date = df_filtered["Tanggal"].max()
    df_latest = df_filtered[df_filtered["Tanggal"] == latest_date]
    
    if not df_latest.empty:
        m = folium.Map(location=[-6.2088, 106.8456], zoom_start=11, tiles="CartoDB positron")
        for idx, row in df_latest.iterrows():
            folium.CircleMarker(
                location=[row['Lat'], row['Lon']],
                radius=10,
                popup=f"<b>{row['Stasiun']}</b><br>ISPU: {row['ISPU']}<br>Status: {row['Kategori']}",
                color=COLOR_MAP.get(row['Kategori'], '#grey'),
                fill=True,
                fill_color=COLOR_MAP.get(row['Kategori'], '#grey'),
                fill_opacity=0.7
            ).add_to(m)
        st_folium(m, height=200, use_container_width=True)
    else:
        st.write("Data tidak tersedia pada rentang tanggal tersebut.")

st.write("---")

# 5. ROW 2: TREN NILAI ISPU & GRANULARITAS (Kriteria 3)
st.subheader("📈 Tren Akumulasi Nilai ISPU")
granularity = tf.radio("Pilih Granularitas Waktu:", ["Kritis (Harian)", "Mingguan (Akumulatif Hari)", "Bulanan", "Tahunan"], horizontal=True)

if not df_filtered.empty:
    if granularity == "Kritis (Harian)":
        df_trend = df_filtered.groupby("Tanggal")["ISPU"].max().reset_index()
        fig_trend = px.line(df_trend, x="Tanggal", y="ISPU", title="Tren ISPU Harian (Nilai Maksimal)")
    elif granularity == "Mingguan (Akumulatif Hari)":
        df_filtered['Minggu'] = df_filtered['Tanggal'].dt.to_period('W').astype(str)
        df_trend = df_filtered.groupby('Minggu')["ISPU"].sum().reset_index()
        fig_trend = px.line(df_trend, x="Minggu", y="ISPU", title="Tren Kumulatif ISPU Mingguan")
    elif granularity == "Bulanan":
        df_trend = df_filtered.groupby(["Tahun", "Bulan"])["ISPU"].mean().reset_index()
        fig_trend = px.line(df_trend, x="Bulan", y="ISPU", color="Tahun", title="Perbandingan Tren Bulanan antar Tahun")
    else:
        df_trend = df_filtered.groupby("Tahun")["ISPU"].mean().reset_index()
        fig_trend = px.bar(df_trend, x="Tahun", y="ISPU", title="Rata-rata ISPU Tahunan")

    # Kustomisasi Tooltip Tren
    fig_trend.update_traces(
        hovertemplate="<b>Waktu:</b> %{x}<br><b>Nilai ISPU:</b> %{y:.1f}<extra></extra>"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

st.write("---")

# 6. ROW 3: STACKED BAR CHART KATEGORI & CRITICAL (Kriteria 4 & 5)
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 % Kategori Udara per Stasiun")
    if not df_filtered.empty:
        # Hitung persentase kategori per stasiun
        df_cat = df_filtered.groupby(["Stasiun", "Kategori"]).size().reset_index(name="Jumlah")
        df_cat["Persentase"] = df_cat.groupby("Stasiun")["Jumlah"].transform(lambda x: (x / x.sum()) * 100)
        
        fig_cat = px.bar(
            df_cat, y="Stasiun", x="Persentase", color="Kategori", orientation="h",
            color_discrete_map=COLOR_MAP,
            title="Distribusi Kategori Udara (100% Stacked)"
        )
        # Kustomisasi Tooltip Kategori
        fig_cat.update_traces(
            hovertemplate="<b>Stasiun:</b> %{y}<br><b>Kategori:</b> %{customdata[0]}<br><b>Proporsi:</b> %{x:.1f}%<extra></extra>",
            customdata=np.stack((df_cat['Kategori'],), axis=-1)
        )
        st.plotly_chart(fig_cat, use_container_width=True)

with col_right:
    st.subheader("☢️ % Parameter Kritis per Stasiun & Tahun")
    if not df_filtered.empty:
        df_crit = df_filtered.groupby(["Stasiun", "Tahun", "Critical_Param"]).size().reset_index(name="Jumlah")
        df_crit["Persentase"] = df_crit.groupby(["Stasiun", "Tahun"])["Jumlah"].transform(lambda x: (x / x.sum()) * 100)
        
        # Menggunakan grafik facet per Tahun agar Kepala Dinas mudah membandingkannya
        fig_crit = px.bar(
            df_crit, y="Stasiun", x="Persentase", color="Critical_Param", orientation="h",
            facet_col="Tahun",
            title="Kontribusi Parameter Dominan per Tahun"
        )
        # Kustomisasi Tooltip Parameter Kritis
        fig_crit.update_traces(
            hovertemplate="<b>Stasiun:</b> %{y}<br><b>Polutan:</b> %{customdata[0]}<br><b>Kontribusi:</b> %{x:.1f}%<extra></extra>",
            customdata=np.stack((df_crit['Critical_Param'],), axis=-1)
        )
        st.plotly_chart(fig_crit, use_container_width=True)

st.write("---")

# 7. ROW 4: HEATMAP POLA MUSIMAN (Kriteria 6)
st.subheader("🌡️ Heatmap Pola Kualitas Udara Bulanan")
if not df_filtered.empty:
    months_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    
    # Pivot data untuk membuat matriks Heatmap (X: Bulan, Y: Tahun/Stasiun, Z: Avg ISPU)
    df_heat = df_filtered.groupby(["Tahun", "Bulan"])["ISPU"].mean().reset_index()
    df_heat_pivot = df_heat.pivot(index="Tahun", columns="Bulan", values="ISPU").reindex(columns=months_order)
    
    fig_heat = px.imshow(
        df_heat_pivot,
        labels=dict(x="Bulan", y="Tahun", color="Rata-rata ISPU"),
        x=df_heat_pivot.columns,
        y=df_heat_pivot.index,
        color_continuous_scale="YlOrRd", # Gradasi Kuning ke Merah Pekat
        title="Pola ISPU Bulanan (Mendeteksi Krisis Musim Kemarau)"
    )
    # Kustomisasi Tooltip Heatmap
    fig_heat.update_traces(
        hovertemplate="<b>Tahun:</b> %{y}<br><b>Bulan:</b> %{x}<br><b>Rata-rata ISPU:</b> %{z:.1f}<extra></extra>"
    )
    st.plotly_chart(fig_heat, use_container_width=True)