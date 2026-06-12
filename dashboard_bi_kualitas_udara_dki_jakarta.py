import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

# ==========================================
# 1. DATA LOADER & PROCESSING
# ==========================================
# Membaca data clean (pastikan file df_clean2.csv berada di direktori yang sama)
df = pd.read_csv("df_clean2.csv")
df['tanggal'] = pd.to_datetime(df['tanggal'])

# Mapping kode stasiun ke wilayah administratif agar lebih dipahami Kepala Dinas
stasiun_mapping = {
    'DKI1 Bunderan HI': 'Jakarta Pusat',
    'DKI2 Kelapa Gading': 'Jakarta Utara',
    'DKI3 Jagakarsa': 'Jakarta Selatan',
    'DKI4 Lubang Buaya': 'Jakarta Timur',
    'DKI5 Kebon Jeruk': 'Jakarta Barat'
}
df['wilayah'] = df['stasiun'].map(stasiun_mapping)

# List tahun unik untuk filter/slicer
available_years = sorted(df['year'].unique(), reverse=True)

# ==========================================
# 2. DASHBOARD APP INITIALIZATION
# ==========================================
app = Dash(__name__)

# Mengatur tema global berbasis CSS inline demi kontrol desain penuh
APP_THEME = {
    'background': '#121214',
    'card-bg': '#1E1E24',
    'text': '#FFFFFF',
    'accent-red': '#FF4D4D',
    'accent-yellow': '#FFC107',
    'accent-green': '#2ECC71',
    'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
}

# ==========================================
# 3. DASHBOARD LAYOUT DEFINITION
# ==========================================
app.layout = html.Div(style={
    'backgroundColor': APP_THEME['background'],
    'color': APP_THEME['text'],
    'fontFamily': APP_THEME['font-family'],
    'padding': '24px',
    'margin': '0'
}, children=[
    
    # HEADER SECTION
    html.Div(style={
        'display': 'flex',
        'justifyContent': 'between',
        'alignItems': 'center',
        'borderBottom': '1px solid #2D2D35',
        'paddingBottom': '16px',
        'marginBottom': '24px'
    }, children=[
        html.Div([
            html.H1("KUALITAS UDARA DKI JAKARTA", style={'margin': '0', 'fontSize': '28px', 'fontWeight': '800', 'letterSpacing': '-0.5px'}),
            html.P("Dashboard Interaktif Pemantauan Eksploratif Kepala Dinas Lingkungan Hidup", style={'margin': '4px 0 0 0', 'color': '#A0A0AA', 'fontSize': '14px'})
        ], style={'flex': '1'}),
        
        # FILTER / SLICER TAHUN
        html.Div([
            html.Label("PERIODE TAHUN", style={'fontSize': '11px', 'fontWeight': '700', 'color': '#A0A0AA', 'display': 'block', 'marginBottom': '6px'}),
            dcc.Dropdown(
                id='year-picker',
                options=[{'label': str(yr), 'value': yr} for yr in available_years],
                value=available_years[0],
                clearable=False,
                style={
                    'width': '140px',
                    'backgroundColor': APP_THEME['card-bg'],
                    'color': '#000000', # Hitam untuk teks opsi dropdown agar terbaca saat diklik
                    'border': '1px solid #3D3D45'
                }
            )
        ])
    ]),
    
    # 4. KPI CARDS ROW (AT-A-GLANCE)
    html.Div(id='kpi-container', style={
        'display': 'grid',
        'gridTemplateColumns': 'repeat(auto-fit, minmax(220px, 1fr))',
        'gap': '16px',
        'marginBottom': '24px'
    }),
    
    # 5. MIDDLE VISUALIZATION SECTION (TWO COLUMNS)
    html.Div(style={
        'display': 'grid',
        'gridTemplateColumns': '1fr 1fr',
        'gap': '24px',
        'marginBottom': '24px'
    }, children=[
        
        # Kiri: Tren Kualitas Udara (Line Chart)
        html.Div(style={'backgroundColor': APP_THEME['card-bg'], 'padding': '20px', 'borderRadius': '8px'}, children=[
            html.H3("Tren Indeks Polusi Maksimal Bulanan", style={'margin': '0 0 12px 0', 'fontSize': '16px', 'fontWeight': '600'}),
            dcc.Graph(id='trend-line-chart', config={'displayModeBar': False})
        ]),
        
        # Kanan: Peringkat Wilayah Terpolutif (Bar Chart)
        html.Div(style={'backgroundColor': APP_THEME['card-bg'], 'padding': '20px', 'borderRadius': '8px'}, children=[
            html.H3("Peringkat Beban Polusi Per Wilayah (Rata-rata Nilai Max)", style={'margin': '0 0 12px 0', 'fontSize': '16px', 'fontWeight': '600'}),
            dcc.Graph(id='region-bar-chart', config={'displayModeBar': False})
        ])
    ]),
    
    # 6. BOTTOM VISUALIZATION SECTION (KOMPOSISI ZAT)
    html.Div(style={'backgroundColor': APP_THEME['card-bg'], 'padding': '20px', 'borderRadius': '8px'}, children=[
        html.H3("Komposisi Konsentrasi Zat Polutan Utama di Setiap Wilayah", style={'margin': '0 0 12px 0', 'fontSize': '16px', 'fontWeight': '600'}),
        dcc.Graph(id='pollutant-stacked-chart', config={'displayModeBar': False})
    ]),
    
    # AUTOMATED POLICY ACTION TRIGGER
    html.Div(id='policy-trigger-box', style={
        'marginTop': '24px',
        'padding': '16px',
        'borderRadius': '6px',
        'borderLeft': '4px solid',
        'fontSize': '14px',
        'fontWeight': '500'
    })
])

# ==========================================
# 4. INTERACTIVE CALLBACKS (REAKTIF-FILTER)
# ==========================================
@app.callback(
    [Output('kpi-container', 'children'),
     Output('trend-line-chart', 'figure'),
     Output('region-bar-chart', 'figure'),
     Output('pollutant-stacked-chart', 'figure'),
     Output('policy-trigger-box', 'children'),
     Output('policy-trigger-box', 'style')],
    [Input('year-picker', 'value')]
)
def update_dashboard(selected_year):
    # Menyaring data berdasarkan tahun yang dipilih user melalui filter
    filtered_df = df[df['year'] == selected_year]
    
    # --- HITUNG METRIK KPI ---
    avg_max = round(filtered_df['max'].mean(), 1)
    worst_row = filtered_df.loc[filtered_df['max'].idxmax()]
    worst_region = worst_row['wilayah']
    worst_value = worst_row['max']
    top_critical = filtered_df['critical'].mode()[0]
    
    # Hitung persentase hari tidak sehat
    total_days = len(filtered_df)
    unhealthy_days = len(filtered_df[filtered_df['categori'].isin(['TIDAK SEHAT', 'SANGAT TIDAK SEHAT', 'BERBAHAYA'])])
    pct_unhealthy = round((unhealthy_days / total_days) * 100, 1) if total_days > 0 else 0
    
    # Logika Penentuan Warna Sinyal Utama
    if avg_max > 100:
        alert_color = APP_THEME['accent-red']
        status_text = "SIAGA DARURAT"
        policy_recommendation = f"⚠️ REKOMENDASI KEBIJAKAN: Rata-rata indeks tahun {selected_year} berada di ambang batas buruk ({avg_max}). Disarankan instruksi pembatasan emisi industri sektor utara/selatan dan penerapan WFH parsial."
    elif avg_max > 50:
        alert_color = APP_THEME['accent-yellow']
        status_text = "SEDANG / WASPADA"
        policy_recommendation = f"⚡ REKOMENDASI KEBIJAKAN: Kualitas udara sedang ({avg_max}). Optimalkan razia uji emisi kendaraan bermotor di area publik stasiun terkait."
    else:
        alert_color = APP_THEME['accent-green']
        status_text = "AMAN / SEHAT"
        policy_recommendation = f"✅ REKOMENDASI KEBIJAKAN: Pertahankan performa hijau. Evaluasi regulasi ruang terbuka hijau dapat dilanjutkan secara berkala."

    # Komponen KPI Cards
    kpi_cards = [
        html.Div(style={'backgroundColor': '#25252D', 'padding': '16px', 'borderRadius': '6px'}, children=[
            html.Span("STATUS TAHUNAN", style={'fontSize': '11px', 'color': '#A0A0AA', 'fontWeight': '600'}),
            html.H2(status_text, style={'margin': '4px 0 0 0', 'color': alert_color, 'fontSize': '22px', 'fontWeight': '800'})
        ]),
        html.Div(style={'backgroundColor': '#25252D', 'padding': '16px', 'borderRadius': '6px'}, children=[
            html.Span("RATA-RATA INDEKS MAX", style={'fontSize': '11px', 'color': '#A0A0AA', 'fontWeight': '600'}),
            html.H2(f"{avg_max} ISPU", style={'margin': '4px 0 0 0', 'color': '#FFFFFF', 'fontSize': '24px', 'fontWeight': '800'})
        ]),
        html.Div(style={'backgroundColor': '#25252D', 'padding': '16px', 'borderRadius': '6px'}, children=[
            html.Span("ZONA TERTINGGI (CRITICAL)", style={'fontSize': '11px', 'color': '#A0A0AA', 'fontWeight': '600'}),
            html.H2(f"{worst_region} ({int(worst_value)})", style={'margin': '4px 0 0 0', 'color': APP_THEME['accent-red'], 'fontSize': '18px', 'fontWeight': '700'})
        ]),
        html.Div(style={'backgroundColor': '#25252D', 'padding': '16px', 'borderRadius': '6px'}, children=[
            html.Span("POLUTAN UTAMA DOMINAN", style={'fontSize': '11px', 'color': '#A0A0AA', 'fontWeight': '600'}),
            html.H2(top_critical, style={'margin': '4px 0 0 0', 'color': '#3498DB', 'fontSize': '24px', 'fontWeight': '800'})
        ]),
        html.Div(style={'backgroundColor': '#25252D', 'padding': '16px', 'borderRadius': '6px'}, children=[
            html.Span("HARI TIDAK SEHAT", style={'fontSize': '11px', 'color': '#A0A0AA', 'fontWeight': '600'}),
            html.H2(f"{pct_unhealthy}%", style={'margin': '4px 0 0 0', 'color': APP_THEME['accent-yellow'], 'fontSize': '24px', 'fontWeight': '800'})
        ])
    ]

    # --- VISUALISASI A: TREN BULANAN (LINE) ---
    df_trend = filtered_df.groupby('month')['max'].mean().reset_index()
    fig_line = px.line(df_trend, x='month', y='max', markers=True, template='plotly_dark')
    fig_line.update_traces(line_color='#FF4D4D', line_width=3, marker=dict(size=8))
    fig_line.add_hline(y=50, line_dash="dash", line_color="#2ECC71", annotation_text="Batas Aman (50)")
    fig_line.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=20, t=10, b=40), yaxis_title="Indeks ISPU", xaxis_title="Bulan"
    )

    # --- VISUALISASI B: PERINGKAT WILAYAH (BAR) ---
    df_region = filtered_df.groupby('wilayah')['max'].mean().reset_index().sort_values(by='max', ascending=True)
    fig_bar = px.bar(df_region, x='max', y='wilayah', orientation='h', template='plotly_dark', color='max',
                     color_continuous_scale=['#2ECC71', '#FFC107', '#FF4D4D'])
    fig_bar.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False,
        margin=dict(l=100, r=20, t=10, b=40), xaxis_title="Rata-rata Nilai Maksimum", yaxis_title=""
    )

    # --- VISUALISASI C: STACKED COMPOSITION BAR ---
    df_comp = filtered_df.groupby('wilayah')[['pm10', 'pm25', 'so2', 'co', 'o3', 'no2']].mean().reset_index()
    fig_stack = go.Figure(data=[
        go.Bar(name='PM2.5', x=df_comp['wilayah'], y=df_comp['pm25'], marker_color='#E74C3C'),
        go.Bar(name='PM10', x=df_comp['wilayah'], y=df_comp['pm10'], marker_color='#E67E22'),
        go.Bar(name='O3', x=df_comp['wilayah'], y=df_comp['o3'], marker_color='#F1C40F'),
        go.Bar(name='NO2', x=df_comp['wilayah'], y=df_comp['no2'], marker_color='#3498DB'),
        go.Bar(name='CO', x=df_comp['wilayah'], y=df_comp['co'], marker_color='#9B59B6'),
        go.Bar(name='SO2', x=df_comp['wilayah'], y=df_comp['so2'], marker_color='#95A5A6')
    ], template='plotly_dark')
    fig_stack.update_layout(
        barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=20, t=10, b=40), yaxis_title="Konsentrasi Rata-rata Zatz", xaxis_title=""
    )

    # Mengatur style box rekomendasi kebijakan dinamis
    policy_style = {
        'marginTop': '24px',
        'padding': '16px',
        'borderRadius': '6px',
        'borderLeft': f'4px solid {alert_color}',
        'backgroundColor': '#1E1E24',
        'color': '#FFFFFF'
    }

    return kpi_cards, fig_line, fig_bar, fig_stack, policy_recommendation, policy_style

# ==========================================
# 5. EXECUTION ENTRYPOINT
# ==========================================
if __name__ == '__main__':
    # Jalankan server lokal (Akses melalui http://127.0.0.1:8050 di browser Anda)
    app.run_server(debug=True)
