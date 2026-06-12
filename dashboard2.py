import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from streamlit_folium import st_folium
import folium

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Executive Air Quality Insight – DKI Jakarta",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. LOAD & CLEAN DATA REAL
@st.cache_data
def load_real_data():
    # Membaca file data asli Anda
    df = pd.read_csv("df_clean.csv")
    
    # Konversi tanggal dan ekstrak komponen waktu
    df["tanggal"] = pd.to_datetime(df["tanggal"])
    df["Tahun"] = df["tanggal"].dt.year
    df["Bulan_Nama"] = df["tanggal"].dt.strftime('%B')
    
    # Sinkronisasi nama kolom agar rapi di visualisasi
    df = df.rename(columns={
        "max": "ISPU",
        "categori": "Kategori",
        "critical": "Critical_Param",
        "stasiun": "Stasiun"
    })
    
    # Membersihkan data kosong atau tidak valid
    df = df.dropna(subset=["ISPU", "Kategori", "Stasiun"])
    df["Kategori"] = df["Kategori"].str.title() # Menyeragamkan case (Sedang, Baik, dll)
    
    # Koordinat stasiun riil di DKI Jakarta untuk kebutuhan peta
    coords = {
        "DKI1 Bunderan HI": [-6.195, 106.823],
        "DKI2 Kelapa Gading": [-6.151, 106.905],
        "DKI3 Jagakarsa": [-6.333, 106.812],
        "DKI4 Lubang Buaya": [-6.291, 106.910],
        "DKI5 Kebon Jeruk": [-6.193, 106.764]
    }
    
    # Map koordinat, jika ada nama stasiun baru berikan koordinat default Jakarta Pusat
    df["Lat"] = df["Stasiun"].map(lambda x: coords.get(x, [-6.2088, 106.8456])[0])
    df["Lon"] = df["Stasiun"].map(lambda x: coords.get(x, [-6.2088, 106.8456])[1])
    
    return df

df_clean = load_real_data()

# Palet warna standar ISPU sesuai data kategori Anda
COLOR_MAP = {
    "Baik": "#2ecc71",
    "Sedang": "#3498db",
    "Tidak Sehat": "#f1c40f",
    "Sangat Tidak Sehat": "#e74c3c",
    "Berbahaya": "#2c3e50"
}

# 3. SIDEBAR / PANEL FILTER (Kriteria 1)
st.sidebar.header("📊 Filter Analisis")

# Filter Tanggal Berdasarkan Rentang Data Asli
min_date = df_clean["tanggal"].min().to_pydatetime()
max_date = df_clean["tanggal"].max().to_pydatetime()

st_date = st.sidebar.date_input(
    "Pilih Rentang Tanggal", 
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Filter Stasiun Berdasarkan Data Asli
all_stations = sorted(df_clean["Stasiun"].unique().tolist())
selected_stations = st.sidebar.multiselect("Pilih Stasiun Pemantauan", all_stations, default=all_stations)

# Memfilter Data
if len(st_date) == 2:
    start_date, end_date = pd.to_datetime(st_date[0]), pd.to_datetime(st_date[1])
    df_filtered = df_clean[(df_clean["tanggal"] >= start_date) & (df_clean["tanggal"] <= end_date)]
else:
    df_filtered = df_clean

if selected_stations:
    df_filtered = df_filtered[df_filtered["Stasiun"].isin(selected_stations)]

# DASHBOARD UTAMA
st.title("🏛️ Executive Air Quality Insight – DKI Jakarta")
st.markdown("Dashboard ringkasan eksekutif berbasis data historis resmi untuk Kepala Dinas Lingkungan Hidup.")
st.write("---")

# 4. ROW 1: SCORECARDS & PETA KONDISI TERKINI (Kriteria 2)
col1, col2, col3, col4 = st.columns([1.5, 1.5, 1.5, 3.5])

if not df_filtered.empty:
    # Hitung Metrik Rata-rata dan Persentase
    avg_ispu = int(df_filtered["ISPU"].mean())
    total_days = len(df_filtered)
    bad_days = len(df_filtered[df_filtered["Kategori"].isin(["Tidak Sehat", "Sangat Tidak Sehat", "Berbahaya"])])
    pct_bad_days = (bad_days / total_days * 100) if total_days > 0 else 0
    
    # Mencari parameter dominan (handling jika ada nilai nan)
    valid_critical = df_filtered.dropna(subset=["Critical_Param"])
    dominant_param = valid_critical["Critical_Param"].mode()[0] if not valid_critical.empty else "-"

    with col1:
        st.metric(label="Rata-rata ISPU Harian", value=avg_ispu)
    with col2:
        st.metric(label="% Hari Tidak Sehat+", value=f"{pct_bad_days:.1f}%")
    with col3:
        st.metric(label="Pencemar Dominan", value=dominant_param)

    with col4:
        st.subheader("📍 Kondisi Terkini per Stasiun")
        # Ambil data hari terakhir yang tercatat di filter
        latest_date = df_filtered["tanggal"].max()
        df_latest = df_filtered[df_filtered["tanggal"] == latest_date]
        
        m = folium.Map(location=[-6.2088, 106.8456], zoom_start=11, tiles="CartoDB positron")
        for idx, row in df_latest.iterrows():
            folium.CircleMarker(
                location=[row['Lat'], row['Lon']],
                radius=11,
                popup=f"<b>{row['Stasiun']}</b><br>Tanggal: {row['tanggal'].strftime('%Y-%m-%d')}<br>ISPU: {row['ISPU']}<br>Status: {row['Kategori']}",
                color=COLOR_MAP.get(row['Kategori'], '#grey'),
                fill=True,
                fill_color=COLOR_MAP.get(row['Kategori'], '#grey'),
                fill_opacity=0.8
            ).add_to(m)
        st_folium(m, height=180, use_container_width=True)
else:
    st.warning("Tidak ada data yang tersedia pada filter ini.")

st.write("---")

# 5. ROW 2: TREN NILAI ISPU & GRANULARITAS (Kriteria 3)
st.subheader("📈 Tren Akumulasi Nilai ISPU")
granularity = st.radio("Pilih Granularitas Waktu:", ["Kritis (Harian)", "Mingguan (Akumulatif Hari)", "Bulanan", "Tahunan"], horizontal=True)

if not df_filtered.empty:
    if granularity == "Kritis (Harian)":
        df_trend = df_filtered.groupby("tanggal")["ISPU"].max().reset_index()
        fig_trend = px.line(df_trend, x="tanggal", y="ISPU", title="Tren ISPU Harian (Nilai Maksimal)")
        fig_trend.update_traces(hovertemplate="<b>Tanggal:</b> %{x|%d %B %Y}<br><b>Max ISPU:</b> %{y}<extra></extra>")
        
    elif granularity == "Mingguan (Akumulatif Hari)":
        # Ambil kolom minggu bawaan data atau kalkulasi ulang
        df_filtered['Minggu_Grup'] = df_filtered['tanggal'].dt.to_period('W').astype(str)
        df_trend = df_filtered.groupby('Minggu_Grup')["ISPU"].sum().reset_index()
        fig_trend = px.line(df_trend, x="Minggu_Grup", y="ISPU", title="Tren Kumulatif ISPU Mingguan")
        fig_trend.update_traces(hovertemplate="<b>Periode Minggu:</b> %{x}<br><b>Total Kumulatif ISPU:</b> %{y}<extra></extra>")
        
    elif granularity == "Bulanan":
        df_trend = df_filtered.groupby(["Tahun", "Bulan_Nama"])["ISPU"].mean().reset_index()
        months_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        df_trend["Bulan_Nama"] = pd.Categorical(df_trend["Bulan_Nama"], categories=months_order, ordered=True)
        df_trend = df_trend.sort_values("Bulan_Nama")
        
        fig_trend = px.line(df_trend, x="Bulan_Nama", y="ISPU", color="Tahun", title="Perbandingan Tren Bulanan antar Tahun")
        fig_trend.update_traces(hovertemplate="<b>Bulan:</b> %{x}<br><b>Rata-rata ISPU:</b> %{y:.1f}<extra></extra>")
        
    else:
        df_trend = df_filtered.groupby("Tahun")["ISPU"].mean().reset_index()
        fig_trend = px.bar(df_trend, x="Tahun", y="ISPU", title="Rata-rata ISPU Tahunan")
        fig_trend.update_traces(hovertemplate="<b>Tahun:</b> %{x}<br><b>Rata-rata ISPU:</b> %{y:.1f}<extra></extra>")

    st.plotly_chart(fig_trend, use_container_width=True)

st.write("---")

# 6. ROW 3: STACKED BAR CHART KATEGORI & CRITICAL (Kriteria 4 & 5)
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 % Kategori Udara per Stasiun")
    if not df_filtered.empty:
        df_cat = df_filtered.groupby(["Stasiun", "Kategori"]).size().reset_index(name="Jumlah")
        df_cat["Persentase"] = df_cat.groupby("Stasiun")["Jumlah"].transform(lambda x: (x / x.sum()) * 100)
        
        fig_cat = px.bar(
            df_cat, y="Stasiun", x="Persentase", color="Kategori", orientation="h",
            color_discrete_map=COLOR_MAP,
            title="Proporsi Kategori Kualitas Udara (100% Stacked)"
        )
        fig_cat.update_traces(
            hovertemplate="<b>Stasiun:</b> %{y}<br><b>Kategori:</b> %{customdata[0]}<br><b>Proporsi:</b> %{x:.1f}%<extra></extra>",
            customdata=np.stack((df_cat['Kategori'],), axis=-1)
        )
        st.plotly_chart(fig_cat, use_container_width=True)

with col_right:
    st.subheader("☢️ % Parameter Kritis per Stasiun & Tahun")
    if not df_filtered.empty:
        # Filter parameter kosong khusus chart ini
        df_crit_clean = df_filtered.dropna(subset=["Critical_Param"])
        df_crit = df_crit_clean.groupby(["Stasiun", "Tahun", "Critical_Param"]).size().reset_index(name="Jumlah")
        df_crit["Persentase"] = df_crit.groupby(["Stasiun", "Tahun"])["Jumlah"].transform(lambda x: (x / x.sum()) * 100)
        
        fig_crit = px.bar(
            df_crit, y="Stasiun", x="Persentase", color="Critical_Param", orientation="h",
            facet_col="Tahun",
            title="Distribusi Parameter Dominan per Tahun"
        )
        fig_crit.update_traces(
            hovertemplate="<b>Stasiun:</b> %{y}<br><b>Polutan Kritis:</b> %{customdata[0]}<br><b>Kontribusi:</b> %{x:.1f}%<extra></extra>",
            customdata=np.stack((df_crit['Critical_Param'],), axis=-1)
        )
        st.plotly_chart(fig_crit, use_container_width=True)

st.write("---")

# 7. ROW 4: HEATMAP POLA MUSIMAN (Kriteria 6)
st.subheader("🌡️ Heatmap Pola Kualitas Udara Bulanan")
if not df_filtered.empty:
    months_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    
    df_heat = df_filtered.groupby(["Tahun", "Bulan_Nama"])["ISPU"].mean().reset_index()
    df_heat_pivot = df_heat.pivot(index="Tahun", columns="Bulan_Nama", values="ISPU").reindex(columns=months_order)
    
    fig_heat = px.imshow(
        df_heat_pivot,
        labels=dict(x="Bulan", y="Tahun", color="Rata-rata ISPU"),
        x=df_heat_pivot.columns,
        y=df_heat_pivot.index,
        color_continuous_scale="YlOrRd",
        title="Matriks Pola ISPU Bulanan Berdasarkan Tahun"
    )
    fig_heat.update_traces(
        hovertemplate="<b>Tahun:</b> %{y}<br><b>Bulan:</b> %{x}<br><b>Rata-rata ISPU:</b> %{z:.1f}<extra></extra>"
    )
    st.plotly_chart(fig_heat, use_container_width=True)
