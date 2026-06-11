import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# CONFIGURATION & PAGE SETUP
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Dampak AI Mahasiswa",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk tampilan premium, clean, dan profesional
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .kpi-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #1E3A8A;
        text-align: center;
    }
    .kpi-title { font-size: 14px; color: #6B7280; font-weight: 600; text-transform: uppercase; }
    .kpi-value { font-size: 28px; color: #111827; font-weight: bold; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DATA LOADING (Diubah ke Excel dengan Caching)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    # Mengubah pembacaan data langsung ke file Excel asli (.xlsx)
    # Gunakan sheet pertama secara default. Memerlukan library 'openpyxl'
    df = pd.read_excel("ai_student_impact_cleaned.xlsx", sheet_name=0, engine="openpyxl")
    return df

try:
    df_raw = load_data()
except Exception as e:
    st.error(f"❌ Gagal memuat file Excel. Pastikan file bernama 'ai_student_impact_cleaned.xlsx' berada di folder yang sama dengan script ini. Error: {e}")
    st.stop()

# -----------------------------------------------------------------------------
# SIDEBAR FILTERS (Kontrol Navigasi Konsultan)
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ Filter Konsultan")
st.sidebar.markdown("Sesuaikan parameter di bawah untuk memetakan kelompok mahasiswa tertentu.")

# 1. Filter Major Category
all_majors = sorted(df_raw['Major_Category'].dropna().unique())
selected_majors = st.sidebar.multiselect("Bidang Studi (Major):", options=all_majors, default=all_majors)

# 2. Filter Year of Study
all_years = sorted(df_raw['Year_of_Study'].dropna().unique())
selected_years = st.sidebar.multiselect("Tahun Angkatan (Year of Study):", options=all_years, default=all_years)

# 3. Filter Institutional Policy
all_policies = sorted(df_raw['Institutional_Policy'].dropna().unique())
selected_policies = st.sidebar.multiselect("Kebijakan Kampus:", options=all_policies, default=all_policies)

# Menerapkan Filter ke Dataset
df_filtered = df_raw[
    (df_raw['Major_Category'].isin(selected_majors)) &
    (df_raw['Year_of_Study'].isin(selected_years)) &
    (df_raw['Institutional_Policy'].isin(selected_policies))
]

# Proteksi jika kombinasi filter menghasilkan data kosong
if df_filtered.empty:
    st.warning("⚠️ Tidak ada data yang cocok dengan kombinasi filter Anda. Silakan ubah pilihan pada sidebar.")
    st.stop()

# -----------------------------------------------------------------------------
# HEADER SECTION
# -----------------------------------------------------------------------------
st.title("Analisis Dampak Penggunaan AI Generatif terhadap Performa Akademik dan Kesejahteraan Mahasiswa")
st.markdown("""
    *Dashboard Pembuat Keputusan untuk Konsultan Pendidikan — Memantau korelasi integrasi kecerdasan buatan, 
    kebijakan akademik, capaian indeks prestasi (GPA), dan risiko burnout praktis.*
""")
st.write("---")

# -----------------------------------------------------------------------------
# KPI METRICS SECTION (Informasi Utama)
# -----------------------------------------------------------------------------
# Perhitungan metrik berdasarkan filter aktif
avg_pre_gpa = df_filtered['Pre_Semester_GPA'].mean()
avg_post_gpa = df_filtered['Post_Semester_GPA'].mean()
gpa_delta = avg_post_gpa - avg_pre_gpa

avg_skill_retention = df_filtered['Skill_Retention_Score'].mean()

total_students = len(df_filtered)
high_burnout_count = len(df_filtered[df_filtered['Burnout_Risk_Level'].str.upper() == 'HIGH'])
pct_high_burnout = (high_burnout_count / total_students) * 100 if total_students > 0 else 0

# Tampilan Grid 3 Kolom KPI
kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

with kpi_col1:
    st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-title">Rata-Rata GPA (Post-Semester)</div>
            <div class="kpi-value">{avg_post_gpa:.2f}</div>
            <div style="font-size: 12px; color: {'#10B981' if gpa_delta >= 0 else '#EF4444'}; font-weight: bold;">
                {'▲' if gpa_delta >= 0 else '▼'} {abs(gpa_delta):.3f} vs Pre-Semester
            </div>
        </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-title">Rata-Rata Skill Retention</div>
            <div class="kpi-value">{avg_skill_retention:.1f}%</div>
            <div style="font-size: 12px; color: #6B7280;">Skor retensi pemahaman mandiri</div>
        </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
        <div class="kpi-box" style="border-left: 5px solid #EF4444;">
            <div class="kpi-title">High Burnout Risk</div>
            <div class="kpi-value" style="color: #EF4444;">{pct_high_burnout:.1f}%</div>
            <div style="font-size: 12px; color: #6B7280;">{high_burnout_count} dari {total_students} Mahasiswa Aktif</div>
        </div>
    """, unsafe_allow_html=True)

st.write("---")

# -----------------------------------------------------------------------------
# VISUALISASI 1 & 2 (Baris Pertama)
# -----------------------------------------------------------------------------
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("1. Distribusi Perubahan GPA (Pre vs Post) per Bidang Studi")
    
    df_gpa = df_filtered.groupby('Major_Category')[['Pre_Semester_GPA', 'Post_Semester_GPA']].mean().reset_index()
    df_gpa_melted = df_gpa.melt(id_vars='Major_Category', value_vars=['Pre_Semester_GPA', 'Post_Semester_GPA'],
                                var_name='Periode', value_name='GPA')
    df_gpa_melted['Periode'] = df_gpa_melted['Periode'].map({'Pre_Semester_GPA': 'Pre-Semester', 'Post_Semester_GPA': 'Post-Semester'})
    
    fig1 = px.bar(
        df_gpa_melted, 
        x='Major_Category', 
        y='GPA', 
        color='Periode',
        barmode='group',
        color_discrete_sequence=['#93C5FD', '#1E3A8A'], # Light Ice Blue & Deep Navy
        labels={'Major_Category': 'Bidang Studi', 'GPA': 'Rata-rata Nilai GPA'}
    )
    fig1.update_layout(margin=dict(l=20, r=20, t=10, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig1, use_container_width=True)

with row1_col2:
    st.subheader("2. Distribusi Tingkat Burnout berdasarkan Kebijakan Kampus")
    
    df_burnout = df_filtered.groupby(['Institutional_Policy', 'Burnout_Risk_Level']).size().reset_index(name='Jumlah Mahasiswa')
    
    fig2 = px.bar(
        df_burnout,
        x='Institutional_Policy',
        y='Jumlah Mahasiswa',
        color='Burnout_Risk_Level',
        barmode='stack',
        color_discrete_map={'Low': '#10B981', 'Medium': '#FBBF24', 'High': '#EF4444'}, # Skema warna indikator risiko yang jelas
        labels={'Institutional_Policy': 'Kebijakan Institusi', 'Jumlah Mahasiswa': 'Total Mahasiswa'}
    )
    fig2.update_layout(margin=dict(l=20, r=20, t=10, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------------------------------------------------------
# VISUALISASI 3 & 4 (Baris Kedua)
# -----------------------------------------------------------------------------
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("3. Tren Durasi Penggunaan AI Mingguan per Angkatan")
    
    # Box plot untuk memperlihatkan sebaran data, rentang interkuartil, dan tren penggunaan AI
    fig3 = px.box(
        df_filtered,
        x='Year_of_Study',
        y='Weekly_GenAI_Hours',
        color='Year_of_Study',
        color_discrete_sequence=px.colors.qualitative.Safe,
        labels={'Year_of_Study': 'Tahun Angkatan', 'Weekly_GenAI_Hours': 'Jam Penggunaan GenAI/Minggu'}
    )
    fig3.update_layout(showlegend=False, margin=dict(l=20, r=20, t=10, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig3, use_container_width=True)

with row2_col2:
    st.subheader("4. Profil Risiko: Ketergantungan AI vs Risiko Burnout")
    
    # Matriks kepadatan (Heatmap) untuk mendeteksi klaster mahasiswa yang rentan
    df_profile = df_filtered.groupby(['Perceived_AI_Dependency', 'Burnout_Risk_Level']).size().unstack(fill_value=0)
    all_levels = [1, 2, 3, 4, 5]
    df_profile = df_profile.reindex(index=[lvl for lvl in all_levels if lvl in df_profile.index], columns=['Low', 'Medium', 'High'], fill_value=0)
    
    fig4 = px.imshow(
        df_profile,
        text_auto=True,
        color_continuous_scale='Reds',
        labels=dict(x="Tingkat Burnout", y="Ketergantungan AI (Skala 1-5)", color="Jumlah Mhs")
    )
    fig4.update_layout(margin=dict(l=20, r=20, t=10, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig4, use_container_width=True)

# -----------------------------------------------------------------------------
# VISUALISASI 5 (Baris Ketiga - Eksklusif & Interaktif)
# -----------------------------------------------------------------------------
st.write("---")
st.subheader("5. Analisis Korelasi Khusus: Durasi AI vs Skor Retensi Keahlian")
st.markdown("> **Catatan Analisis:** Ukuran gelembung mewakili pencapaian nilai awal (*Pre-Semester GPA*). Perhatikan kecenderungan penurunan retensi materi jika durasi AI melampaui batas tertentu