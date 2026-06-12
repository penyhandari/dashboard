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

# === UPDATE KODE DI SINI ===
# Menambahkan garis ambang batas horizontal 100 (Putus-putus Merah)
fig_trend.add_hline(
    y=100, 
    line_dash="dash", 
    line_color="#ef4444", 
    line_width=2,
    annotation_text="Batas Aman (100)", 
    annotation_position="top left",
    annotation_font=dict(color="#ef4444")
)
# ===========================

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
