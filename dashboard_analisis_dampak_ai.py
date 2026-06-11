import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. KONFIGURASI HALAMAN & THEME
# ==========================================
st.set_page_config(
    page_title="Dashboard Dampak GenAI Mahasiswa",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk mempercantik UI Dashboard agar tampak premium dan bersih
st.markdown("""
    <style>
        /* Mengubah font global dan background */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        /* Desain Card KPI */
        .kpi-card {
            background-color: #F8FAFC;
            border-left: 5px solid #1E3A8A;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            margin-bottom: 10px;
        }
        .kpi-title {
            font-size: 14px;
            font-weight: 600;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .kpi-value {
            font-size: 28px;
            font-weight: 700;
            color: #0F172A;
            margin-top: 5px;
        }
        .kpi-sub {
            font-size: 12px;
            color: #10B981;
            font-weight: 500;
            margin-top: 5px;
        }
        .kpi-sub-danger {
            font-size: 12px;
            color: #EF4444;
            font-weight: 500;
            margin-top: 5px;
        }
        
        /* Desain Header Utama */
        .main-header {
            background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        .main-header h1 {
            color: #F8FAFC !important;
            font-weight: 700 !important;
            font-size: 28px !important;
            margin-bottom: 8px !important;
        }
        .main-header p {
            color: #94A3B8;
            font-size: 15px;
            margin: 0;
        }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# 2. MEMBACA & MEMPERSIAPKAN DATA
# ==========================================
@st.cache_data
def load_data():
    # Menggunakan dataset cleaned yang diunggah pengguna
    df = pd.read_xlsx("ai_student_impact_cleaned.xlsx")
    
    # Memastikan format kolom kategori bersih
    category_cols = ['Major_Category', 'Year_of_Study', 'Institutional_Policy', 'Burnout_Risk_Level', 'Primary_Use_Case']
    for col in category_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    # Buat kolom perbedaan GPA jika belum ada
    if 'GPA_Difference' not in df.columns and 'Post_Semester_GPA' in df.columns and 'Pre_Semester_GPA' in df.columns:
        df['GPA_Difference'] = df['Post_Semester_GPA'] - df['Pre_Semester_GPA']
        
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Gagal membaca dataset. Pastikan file 'ai_student_impact_cleaned.xlsx - Sheet1.csv' berada di folder yang sama. Error: {e}")
    st.stop()


# ==========================================
# 3. SIDEBAR - FILTER INTERAKTIF
# ==========================================
st.sidebar.image("https://img.icons8.com/fluency/96/education.png", width=80)
st.sidebar.title("Kontrol Analitik")
st.sidebar.write("Sesuaikan filter untuk menyaring data mahasiswa:")

# Filter 1: Major Category
all_majors = sorted(df['Major_Category'].unique())
selected_majors = st.sidebar.multiselect(
    "Rumpun Ilmu (Major Category)",
    options=all_majors,
    default=all_majors,
    help="Pilih satu atau beberapa jurusan akademik."
)

# Filter 2: Year of Study (Tingkat Angkatan)
all_years = sorted(df['Year_of_Study'].unique())
selected_years = st.sidebar.multiselect(
    "Tingkat Angkatan (Year of Study)",
    options=all_years,
    default=all_years,
    help="Pilih angkatan kuliah mahasiswa."
)

# Filter 3: Institutional Policy
all_policies = sorted(df['Institutional_Policy'].unique())
selected_policies = st.sidebar.multiselect(
    "Kebijakan Kampus (Institutional Policy)",
    options=all_policies,
    default=all_policies,
    help="Kebijakan regulasi AI di fakultas."
)

# Menerapkan Filter ke Dataset
df_filtered = df[
    (df['Major_Category'].isin(selected_majors)) &
    (df['Year_of_Study'].isin(selected_years)) &
    (df['Institutional_Policy'].isin(selected_policies))
]


# ==========================================
# 4. HEADER & RINGKASAN STRATEGIS
# ==========================================
st.markdown("""
    <div class="main-header">
        <h1>Analisis Dampak Penggunaan AI Generatif terhadap Performa Akademik dan Kesejahteraan Mahasiswa</h1>
        <p>Platform Intelijen Keputusan untuk merumuskan kebijakan penggunaan GenAI yang bertanggung jawab, aman, dan seimbang.</p>
    </div>
""", unsafe_allow_html=True)

# Antisipasi jika hasil filter kosong
if df_filtered.empty:
    st.warning("⚠️ Tidak ada data yang sesuai dengan kombinasi filter Anda. Silakan ubah filter pada sidebar.")
    st.stop()


# ==========================================
# 5. BARIS KPI UTAMA (3 KEY METRICS)
# ==========================================
# Hitung Nilai KPI secara dinamis
avg_post_gpa = df_filtered['Post_Semester_GPA'].mean()
avg_pre_gpa = df_filtered['Pre_Semester_GPA'].mean()
gpa_delta = avg_post_gpa - avg_pre_gpa

avg_retention = df_filtered['Skill_Retention_Score'].mean()

# Hitung Persentase High Burnout Risk
high_burnout_count = len(df_filtered[df_filtered['Burnout_Risk_Level'] == 'High'])
total_students = len(df_filtered)
burnout_pct = (high_burnout_count / total_students) * 100 if total_students > 0 else 0

kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

with kpi_col1:
    gpa_arrow = "▲" if gpa_delta >= 0 else "▼"
    gpa_color_class = "kpi-sub" if gpa_delta >= 0 else "kpi-sub-danger"
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Rata-Rata GPA (Post-Semester)</div>
            <div class="kpi-value">{avg_post_gpa:.3f}</div>
            <div class="{gpa_color_class}">{gpa_arrow} {abs(gpa_delta):.3f} vs Pre-Semester ({avg_pre_gpa:.3f})</div>
        </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Rata-Rata Retensi Pengetahuan</div>
            <div class="kpi-value">{avg_retention:.1f}%</div>
            <div class="kpi-sub">Kapasitas penguasaan konsep mandiri</div>
        </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    burnout_color_class = "kpi-sub-danger" if burnout_pct > 25 else "kpi-sub"
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Rasio Risiko Burnout Tinggi</div>
            <div class="kpi-value">{burnout_pct:.1f}%</div>
            <div class="{burnout_color_class}">Mengalami kejenuhan mental berat</div>
        </div>
    """, unsafe_allow_html=True)

st.write("---")


# ==========================================
# 6. VISUALISASI INTERAKTIF (5 PLOTS)
# ==========================================

# ------------------------------------------------------------
# GRID BARIS 1: Dampak Akademik & Pengaruh Kebijakan Kampus
# ------------------------------------------------------------
col_row1_left, col_row1_right = st.columns(2)

with col_row1_left:
    st.subheader("📊 1. Distribusi IPK Sebelum vs Sesudah Semester")
    st.caption("Membandingkan rata-rata IPK sebelum (Pre) dan sesudah (Post) adopsi AI di setiap rumpun ilmu.")
    
    # Kelompokkan data untuk perbandingan Pre vs Post GPA per Major
    gpa_comparison = df_filtered.groupby('Major_Category')[['Pre_Semester_GPA', 'Post_Semester_GPA']].mean().reset_index()
    gpa_comparison_melted = gpa_comparison.melt(
        id_vars='Major_Category', 
        value_vars=['Pre_Semester_GPA', 'Post_Semester_GPA'],
        var_name='Kategori_GPA', 
        value_name='Nilai_GPA'
    )
    # Mapping nama kategori agar lebih dipahami pengguna
    gpa_comparison_melted['Kategori_GPA'] = gpa_comparison_melted['Kategori_GPA'].map({
        'Pre_Semester_GPA': 'Sebelum Semester (Pre)',
        'Post_Semester_GPA': 'Sesudah Semester (Post)'
    })
    
    fig1 = px.bar(
        gpa_comparison_melted,
        x='Major_Category',
        y='Nilai_GPA',
        color='Kategori_GPA',
        barmode='group',
        color_discrete_map={
            'Sebelum Semester (Pre)': '#94A3B8',
            'Sesudah Semester (Post)': '#1E3A8A'
        },
        labels={'Nilai_GPA': 'Rata-Rata IPK', 'Major_Category': 'Rumpun Ilmu', 'Kategori_GPA': 'Waktu Evaluasi'}
    )
    fig1.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=10, b=20),
        yaxis_range=[2.0, 4.0]
    )
    st.plotly_chart(fig1, use_container_width=True)

with col_row1_right:
    st.subheader("🛡️ 2. Hubungan Kebijakan Kampus dengan Risiko Burnout")
    st.caption("Melihat apakah larangan ketat (Strict Ban) sukses mengurangi kelelahan mental atau sebaliknya.")
    
    # Kelompokkan proporsi burnout per kebijakan institusi
    burnout_policy = df_filtered.groupby(['Institutional_Policy', 'Burnout_Risk_Level']).size().reset_index(name='Jumlah_Mahasiswa')
    
    fig2 = px.bar(
        burnout_policy,
        x='Institutional_Policy',
        y='Jumlah_Mahasiswa',
        color='Burnout_Risk_Level',
        barmode='percent',  # Menampilkan dalam bentuk persentase 100%
        color_discrete_map={
            'Low': '#10B981',
            'Medium': '#F59E0B',
            'High': '#EF4444'
        },
        category_orders={"Burnout_Risk_Level": ["Low", "Medium", "High"]},
        labels={'Jumlah_Mahasiswa': 'Persentase Mahasiswa (%)', 'Institutional_Policy': 'Aturan Kampus', 'Burnout_Risk_Level': 'Tingkat Burnout'}
    )
    fig2.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=10, b=20)
    )
    st.plotly_chart(fig2, use_container_width=True)


# ------------------------------------------------------------
# GRID BARIS 2: Tren Penggunaan AI & Profil Risiko Kesejahteraan
# ------------------------------------------------------------
col_row2_left, col_row2_right = st.columns(2)

with col_row2_left:
    st.subheader("💡 3. Komposisi Pemanfaatan AI Berdasarkan Angkatan")
    st.caption("Memantau tujuan utama penggunaan GenAI (Use Cases) yang dominan di setiap tingkat angkatan mahasiswa.")
    
    usecase_year = df_filtered.groupby(['Year_of_Study', 'Primary_Use_Case']).size().reset_index(name='Count')
    
    fig3 = px.bar(
        usecase_year,
        x='Year_of_Study',
        y='Count',
        color='Primary_Use_Case',
        title="",
        color_discrete_sequence=px.colors.qualitative.Prism,
        labels={'Count': 'Jumlah Pengguna', 'Year_of_Study': 'Angkatan', 'Primary_Use_Case': 'Tujuan Utama AI'}
    )
    fig3.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=10, b=20)
    )
    st.plotly_chart(fig3, use_container_width=True)

with col_row2_right:
    st.subheader("🧠 4. Profil Risiko: Ketergantungan AI vs Tingkat Burnout")
    st.caption("Memetakan korelasi antara skala ketergantungan AI dengan tingkat stres burnout yang dialami mahasiswa.")
    
    # Kelompokkan rata-rata ketergantungan AI berdasarkan tingkat burnout risiko
    dependency_profile = df_filtered.groupby(['Perceived_AI_Dependency', 'Burnout_Risk_Level']).size().reset_index(name='Jumlah_Mahasiswa')
    
    fig4 = px.line(
        dependency_profile,
        x='Perceived_AI_Dependency',
        y='Jumlah_Mahasiswa',
        color='Burnout_Risk_Level',
        markers=True,
        color_discrete_map={
            'Low': '#10B981',
            'Medium': '#F59E0B',
            'High': '#EF4444'
        },
        labels={'Perceived_AI_Dependency': 'Persepsi Ketergantungan AI (Skala 1-5)', 'Jumlah_Mahasiswa': 'Jumlah Mahasiswa'}
    )
    fig4.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=10, b=20)
    )
    st.plotly_chart(fig4, use_container_width=True)


# ------------------------------------------------------------
# GRID BARIS 3: Pencarian Titik Seimbang (Sweet Spot)
# ------------------------------------------------------------
st.write("---")
st.subheader("🎯 5. Analisis Hubungan Durasi Penggunaan AI dengan Retensi Pengetahuan")
st.caption("Grafik interaktif ini membantu mendeteksi batas aman ('Sweet Spot') jam pemakaian AI per minggu terhadap tingkat pemahaman konsep kuliah mahasiswa.")

# Karena data berjumlah besar (50k baris), kita ambil sampel representatif 2.500 baris agar rendering grafik lancar
sample_size = min(2500, len(df_filtered))
df_sample = df_filtered.sample(n=sample_size, random_state=42)

fig5 = px.scatter(
    df_sample,
    x='Weekly_GenAI_Hours',
    y='Skill_Retention_Score',
    color='Prompt_Engineering_Skill',
    size='Tool_Diversity',
    color_discrete_sequence=px.colors.sequential.Viridis,
    hover_data=['Major_Category', 'Post_Semester_GPA'],
    labels={
        'Weekly_GenAI_Hours': 'Durasi Pakai AI (Jam/Minggu)',
        'Skill_Retention_Score': 'Skor Retensi Keterampilan (0-100)',
        'Prompt_Engineering_Skill': 'Kemahiran Prompt'
    },
    opacity=0.6
)
fig5.update_layout(
    margin=dict(l=20, r=20, t=10, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig5, use_container_width=True)


# ==========================================
# 7. FOOTER / INSIGHT SINGKAT UNTUK KONSULTAN
# ==========================================
st.write("---")
with st.expander("💡 Catatan Insight Strategis untuk Konsultan Pendidikan"):
    st.markdown("""
        1. **Sweet Spot Penggunaan AI:** Perhatikan visualisasi ke-5. Penggunaan AI yang produktif biasanya berkisar di bawah 15 jam per minggu. Mahasiswa dengan jam pemakaian berlebih cenderung mengalami kemerosotan pada skor retensi materi kuliah (*Skill Retention*).
        2. **Dampak Kebijakan (Policy Effectiveness):** Bandingkan performa kebijakan 'Strict Ban' versus 'Allowed With Citation'. Seringkali kebijakan pelarangan total tidak menghentikan penggunaan, melainkan menaikkan tingkat kecemasan ujian secara signifikan akibat ketakutan melanggar aturan.
        3. **Intervensi Burnout:** Mahasiswa dengan risiko burnout tinggi didominasi oleh kelompok yang memiliki dependensi AI di tingkat tinggi (Skala 4-5) yang diiringi dengan jam belajar tradisional yang sangat rendah.
    """)

st.caption("Dikembangkan sebagai Alat Bantu Pengambilan Keputusan Strategis Pendidikan Tinggi | Data Aktual Semester Aktif.")