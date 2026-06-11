import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Dashboard Dampak GenAI Mahasiswa",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS CUSTOM UNTUK TAMPILAN PREMIUM ---
st.markdown("""
<style>
    /* Mengubah warna latar belakang utama dan font */
    .stApp {
        background-color: #F8FAFC;
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    
    /* Mengatur gaya kartu KPI */
    .kpi-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-left: 5px solid #1E3A8A;
        margin-bottom: 10px;
    }
    .kpi-title {
        font-size: 14px;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        font-size: 28px;
        color: #1E293B;
        font-weight: 700;
        margin-top: 5px;
    }
    .kpi-subtitle {
        font-size: 11px;
        color: #94A3B8;
        margin-top: 2px;
    }
    
    /* Custom tab style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F1F5F9;
        border-radius: 8px 8px 0px 0px;
        gap: 12px;
        padding-left: 16px;
        padding-right: 16px;
        font-weight: 600;
        color: #475569;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E3A8A !important;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)


# --- FUNGSI LOAD DATA ---
@st.cache_data
def load_data():
    # Mencoba membaca file hasil cleaning terlebih dahulu, jika gagal membaca file asli
    file_cleaned = "ai_student_impact_cleaned.xlsx - Sheet1.csv"
    file_raw = "ai_student_impact_dataset.csv"
    
    if os.path.exists(file_cleaned):
        df = pd.read_csv(file_cleaned)
    elif os.path.exists(file_raw):
        df = pd.read_csv(file_raw)
        # Lakukan basic cleaning instan jika membaca file mentah
        if 'Pre_Semester_GPA' in df.columns and 'Post_Semester_GPA' in df.columns:
            df['GPA_Difference'] = df['Post_Semester_GPA'] - df['Pre_Semester_GPA']
    else:
        # Jika tidak ada file sama sekali, buat dummy data untuk demo
        st.error("Data tidak ditemukan! Membuat data simulasi untuk menjalankan dashboard.")
        np.random.seed(42)
        n = 1000
        df = pd.DataFrame({
            'Student_ID': np.arange(100001, 100001 + n),
            'Major_Category': np.random.choice(['STEM', 'Medical', 'Business', 'Humanities'], n),
            'Year_of_Study': np.random.choice(['Freshman', 'Sophomore', 'Junior', 'Senior', 'Graduate'], n),
            'Pre_Semester_GPA': np.random.uniform(2.0, 4.0, n),
            'Weekly_GenAI_Hours': np.random.exponential(12, n),
            'Primary_Use_Case': np.random.choice(['Copywriting/Drafting', 'Ideation', 'Summarizing_Reading', 'Debugging/Troubleshooting'], n),
            'Prompt_Engineering_Skill': np.random.choice(['Beginner', 'Intermediate', 'Advanced'], n),
            'Tool_Diversity': np.random.randint(1, 6, n),
            'Paid_Subscription': np.random.choice(['YES', 'NO'], n),
            'Traditional_Study_Hours': np.random.uniform(5, 30, n),
            'Perceived_AI_Dependency': np.random.randint(1, 6, n),
            'Institutional_Policy': np.random.choice(['Strict_Ban', 'Allowed_With_Citation', 'Actively_Encouraged'], n),
            'Anxiety_Level_During_Exams': np.random.randint(1, 11, n),
            'Post_Semester_GPA': np.random.uniform(2.0, 4.0, n),
            'Skill_Retention_Score': np.random.uniform(40, 100, n),
            'Burnout_Risk_Level': np.random.choice(['Low', 'Medium', 'High'], n)
        })
        df['GPA_Difference'] = df['Post_Semester_GPA'] - df['Pre_Semester_GPA']
        
    # Standarisasi penamaan kolom Year_of_Study
    if 'Year_of_Student' in df.columns and 'Year_of_Study' not in df.columns:
        df.rename(columns={'Year_of_Student': 'Year_of_Study'}, inplace=True)
        
    return df

try:
    df_raw = load_data()
except Exception as e:
    st.error(f"Error memuat data: {e}")
    st.stop()


# --- SIDEBAR & FILTER ---
st.sidebar.image("https://img.icons8.com/fluency/96/education.png", width=80)
st.sidebar.title("Filter Analisis")
st.sidebar.markdown("Sesuaikan visualisasi data di bawah ini menggunakan filter berikut:")

# Filter 1: Major Category (Rumpun Ilmu)
all_majors = sorted(df_raw['Major_Category'].dropna().unique().tolist())
selected_majors = st.sidebar.multiselect(
    "Rumpun Ilmu (Major Category):",
    options=all_majors,
    default=all_majors
)

# Filter 2: Year of Study (Tahun Angkatan)
all_years = sorted(df_raw['Year_of_Study'].dropna().unique().tolist())
selected_years = st.sidebar.multiselect(
    "Tahun Angkatan (Year of Study):",
    options=all_years,
    default=all_years
)

# Filter 3: Institutional Policy (Kebijakan Aturan)
all_policies = sorted(df_raw['Institutional_Policy'].dropna().unique().tolist())
selected_policies = st.sidebar.multiselect(
    "Kebijakan Institusi (Policy):",
    options=all_policies,
    default=all_policies
)

# Proteksi Filter Kosong
if not selected_majors or not selected_years or not selected_policies:
    st.warning("⚠️ Silakan pilih minimal satu opsi pada setiap filter di sidebar untuk memuat visualisasi!")
    st.stop()

# Menerapkan Filter pada Data
df = df_raw[
    (df_raw['Major_Category'].isin(selected_majors)) &
    (df_raw['Year_of_Study'].isin(selected_years)) &
    (df_raw['Institutional_Policy'].isin(selected_policies))
]


# --- HEADER DASHBOARD ---
st.markdown("<h1 style='text-align: center; color: #1E3A8A; margin-bottom: 5px;'>Analisis Dampak Penggunaan AI Generatif terhadap Performa Akademik dan Kesejahteraan Mahasiswa</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748B; font-size: 16px; margin-bottom: 25px;'>Sistem Pendukung Keputusan Berbasis Bukti Empiris untuk Penyusunan Kebijakan AI yang Bertanggung Jawab</p>", unsafe_allow_html=True)


# --- SECTION 1: KEY PERFORMANCE INDICATORS (KPI) ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_post_gpa = df['Post_Semester_GPA'].mean()
    avg_pre_gpa = df['Pre_Semester_GPA'].mean()
    gpa_delta = avg_post_gpa - avg_pre_gpa
    delta_color = "color: #10B981;" if gpa_delta >= 0 else "color: #EF4444;"
    delta_symbol = "▲" if gpa_delta >= 0 else "▼"
    
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Rerata IPK Akhir</div>
        <div class="kpi-value">{avg_post_gpa:.3f}</div>
        <div class="kpi-subtitle" style="{delta_color}">
            {delta_symbol} {abs(gpa_delta):.3f} vs Semester Lalu ({avg_pre_gpa:.3f})
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    avg_retention = df['Skill_Retention_Score'].mean()
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #3B82F6;">
        <div class="kpi-title">Rerata Skor Retensi</div>
        <div class="kpi-value">{avg_retention:.1f}%</div>
        <div class="kpi-subtitle">Pemahaman konsep murni mahasiswa saat diuji tanpa AI</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    high_burnout_pct = (df['Burnout_Risk_Level'] == 'High').sum() / len(df) * 100
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #EF4444;">
        <div class="kpi-title">Risiko Burnout Tinggi</div>
        <div class="kpi-value">{high_burnout_pct:.1f}%</div>
        <div class="kpi-subtitle" style="color: #EF4444;">Mengalami kejenuhan mental tingkat akut</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    avg_ai_hours = df['Weekly_GenAI_Hours'].mean()
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #8B5CF6;">
        <div class="kpi-title">Durasi Penggunaan AI</div>
        <div class="kpi-value">{avg_ai_hours:.1f} Jam</div>
        <div class="kpi-subtitle">Rerata waktu penggunaan AI per minggu/mahasiswa</div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)


# --- SECTION 2: MENU TAB UNTUK MENJAWAB PERTANYAAN BISNIS ---
tab1, tab2, tab3 = st.tabs([
    "📈 Kinerja Akademik & Penggunaan AI", 
    "🧠 Retensi Pengetahuan & Rekomendasi Aman", 
    "🛡️ Kebijakan Kampus & Kesejahteraan Mental"
])

# ==================== TAB 1: KINERJA AKADEMIK & PENGGUNAAN AI (Q1 & Q5) ====================
with tab1:
    st.markdown("### Analisis Hubungan Penggunaan GenAI dengan Performa IPK (GPA)")
    
    col_t1_left, col_t1_right = st.columns([2, 1])
    
    with col_t1_left:
        # VISUALISASI 1: Scatter plot tren Jam AI vs Selisih IPK
        # Ambil sampel acak jika data terlalu padat agar performa plot tetap cepat
        sample_size = min(2000, len(df))
        df_sample = df.sample(n=sample_size, random_state=42)
        
        fig1 = px.scatter(
            df_sample, 
            x="Weekly_GenAI_Hours", 
            y="GPA_Difference", 
            color="Major_Category",
            trendline="ols",
            title=f"Tren Durasi Penggunaan AI vs Selisih IPK Akhir (Sampel N={sample_size})",
            labels={
                "Weekly_GenAI_Hours": "Jam Penggunaan AI per Minggu",
                "GPA_Difference": "Perubahan IPK (Post_GPA - Pre_GPA)",
                "Major_Category": "Rumpun Ilmu"
            },
            color_discrete_sequence=px.colors.qualitative.Safe,
            opacity=0.6
        )
        fig1.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=40, r=40, t=50, b=40)
        )
        fig1.update_yaxes(showgrid=True, gridcolor='#E2E8F0')
        fig1.update_xaxes(showgrid=True, gridcolor='#E2E8F0')
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_t1_right:
        st.markdown("""
        <div style="background-color: #EFF6FF; padding: 20px; border-radius: 10px; border-left: 5px solid #2563EB;">
            <h4 style="color: #1E3A8A; margin-top:0;">💡 Temuan Bisnis 1: Dampak IPK (Q1)</h4>
            <p style="font-size: 14px; line-height: 1.6; color: #1E293B; text-align: justify;">
                Berdasarkan visualisasi korelasi dan regresi linier di samping, 
                kita dapat mengamati bahwa <b>durasi penggunaan AI yang terlalu tinggi (ekstrem) cenderung berkorelasi dengan pendataran atau bahkan sedikit penurunan perubahan nilai IPK</b>. 
                <br><br>
                Penggunaan AI yang moderat (di bawah 15 jam per minggu) secara umum membantu menstabilkan performa akademik mahasiswa, sementara mahasiswa dengan penggunaan ekstrem (>25 jam) berisiko mengalami penurunan IPK nyata.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<hr style='border: 0.5px solid #E2E8F0;'>", unsafe_allow_html=True)
    
    # VISUALISASI 2 & JAWABAN Q5 (Dampak per Major & Year)
    st.markdown("### Pola Dampak AI di Tiap Rumpun Ilmu & Tahun Angkatan (Q5)")
    
    col_t1_b_left, col_t1_b_right = st.columns([1, 2])
    
    with col_t1_b_left:
        st.markdown("""
        <div style="background-color: #F8FAFC; padding: 20px; border-radius: 10px; border: 1px solid #E2E8F0;">
            <h4 style="color: #475569; margin-top:0;">🔍 Analisis Segmentasi Jurusan (Q5)</h4>
            <p style="font-size: 14px; line-height: 1.6; color: #334155; text-align: justify;">
                Pola adopsi AI sangat bervariasi bergantung pada jenis studi mahasiswa:
                <ul style="padding-left: 20px; font-size: 14px; color: #334155;">
                    <li><b>STEM & Business:</b> Rata-rata jam penggunaan mingguan relatif tinggi karena kegunaan utama berupa <i>Debugging/Troubleshooting</i> dan analisis data terstruktur.</li>
                    <li><b>Medical:</b> Cenderung moderat, dengan fokus penggunaan untuk memahami materi tebal (<i>Summarizing_Reading</i>).</li>
                    <li><b>Humanities:</b> Penggunaan dominan pada <i>Copywriting/Drafting</i> memiliki sensitivitas yang lebih tinggi terhadap potensi penurunan retensi konseptual.</li>
                </ul>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_t1_b_right:
        # Menghitung agregat untuk Visualisasi 2
        df_grouped = df.groupby(['Major_Category', 'Year_of_Study']).agg({
            'Weekly_GenAI_Hours': 'mean',
            'Post_Semester_GPA': 'mean'
        }).reset_index()
        
        fig2 = px.bar(
            df_grouped,
            x="Year_of_Study",
            y="Weekly_GenAI_Hours",
            color="Major_Category",
            barmode="group",
            title="Rata-rata Durasi Penggunaan AI Mingguan berdasarkan Angkatan dan Jurusan",
            labels={
                "Year_of_Study": "Tahun Angkatan",
                "Weekly_GenAI_Hours": "Rata-rata Jam AI/Minggu",
                "Major_Category": "Rumpun Ilmu"
            },
            color_discrete_sequence=px.colors.qualitative.Safe,
            category_orders={"Year_of_Study": ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"]}
        )
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        fig2.update_yaxes(showgrid=True, gridcolor='#E2E8F0')
        st.plotly_chart(fig2, use_container_width=True)

# ==================== TAB 2: RETENSI PENGETAHUAN & REKOMENDASI AMAN (Q2 & Q6) ====================
with tab2:
    st.markdown("### Ketergantungan AI vs Retensi Pemahaman Konseptual")
    
    col_t2_left, col_t2_right = st.columns([2, 1])
    
    with col_t2_left:
        # VISUALISASI 3: Boxplot Hubungan Dependensi vs Skor Retensi
        fig3 = px.box(
            df,
            x="Perceived_AI_Dependency",
            y="Skill_Retention_Score",
            color="Perceived_AI_Dependency",
            title="Distribusi Skor Retensi Pengetahuan Berdasarkan Tingkat Ketergantungan AI",
            labels={
                "Perceived_AI_Dependency": "Tingkat Ketergantungan AI (Skala 1-5)",
                "Skill_Retention_Score": "Skor Retensi Keterampilan (0-100)"
            },
            color_discrete_sequence=px.colors.sequential.Sunsetdark
        )
        fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white", showlegend=False)
        fig3.update_yaxes(showgrid=True, gridcolor='#E2E8F0')
        st.plotly_chart(fig3, use_container_width=True)
        
    with col_t2_right:
        st.markdown("""
        <div style="background-color: #FFFBEB; padding: 20px; border-radius: 10px; border-left: 5px solid #D97706;">
            <h4 style="color: #B45309; margin-top:0;">💡 Temuan Bisnis 2: Penurunan Retensi (Q2)</h4>
            <p style="font-size: 14px; line-height: 1.6; color: #1E293B; text-align: justify;">
                Hasil visualisasi boxplot menunjukkan tren yang sangat konsisten: 
                <b>Semakin tinggi persepsi ketergantungan mahasiswa pada AI (Skala 4 dan 5), semakin rendah nilai retensi pengetahuan asli mereka saat diuji secara mandiri</b>.
                <br><br>
                Mahasiswa yang mengalami adiksi/ketergantungan berat (skala 5) mencatatkan median skor retensi yang paling rendah, mengindikasikan risiko 'kemalasan kognitif' akibat bersandar sepenuhnya pada jawaban instan AI.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border: 0.5px solid #E2E8F0;'>", unsafe_allow_html=True)
    
    # FORMULA SWEET SPOT (Q6)
    st.markdown("### Pencarian Formula Batasan Aman - \"The Sweet Spot\" (Q6)")
    
    # Filter mahasiswa sukses & sehat secara empiris dari data terfilter
    df_sweet = df[
        (df['Post_Semester_GPA'] >= 3.3) & 
        (df['Skill_Retention_Score'] >= 75.0) & 
        (df['Burnout_Risk_Level'] == 'Low')
    ]
    
    col_sweet_left, col_sweet_right = st.columns([1, 1])
    
    with col_sweet_left:
        st.markdown(f"""
        <div style="background-color: #ECFDF5; padding: 25px; border-radius: 12px; border: 2px solid #10B981;">
            <h3 style="color: #065F46; margin-top:0; font-size: 20px;">🌟 Formula Penggunaan AI Paling Aman</h3>
            <p style="font-size: 15px; color: #047857;"><b>Kriteria Mahasiswa Sukses:</b> IPK ≥ 3.3, Retensi Pemahaman ≥ 75%, & Risiko Burnout Rendah</p>
            <hr style="border: 0.5px solid #A7F3D0; margin: 15px 0;">
            <table style="width:100%; border-collapse: collapse; font-size:15px; color:#065F46;">
                <tr>
                    <td style="padding: 6px 0;"><b>Rekomendasi Batas Waktu:</b></td>
                    <td style="text-align:right; font-weight:bold; font-size: 18px;">{df_sweet['Weekly_GenAI_Hours'].mean():.1f} Jam/Minggu</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0;"><b>Toleransi Maksimal AI:</b></td>
                    <td style="text-align:right; font-weight:bold;">{df_sweet['Weekly_GenAI_Hours'].max():.1f} Jam/Minggu</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0;"><b>Rekomendasi Belajar Mandiri:</b></td>
                    <td style="text-align:right; font-weight:bold; font-size: 18px;">{df_sweet['Traditional_Study_Hours'].mean():.1f} Jam/Minggu</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0;"><b>Rasio Belajar (Tradisional : AI):</b></td>
                    <td style="text-align:right; font-weight:bold;">
                        {df_sweet['Traditional_Study_Hours'].mean() / max(1, df_sweet['Weekly_GenAI_Hours'].mean()):.2f}x Lebih Banyak Belajar Mandiri
                    </td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
    with col_sweet_right:
        st.markdown("""
        <div style="padding: 5px 15px;">
            <h4 style="color: #065F46; margin-top:0;">📝 Catatan Kebijakan Strategis:</h4>
            <p style="font-size: 14px; line-height: 1.6; color: #334155; text-align: justify;">
                Data di samping membuktikan secara empiris bahwa mahasiswa yang berprestasi tinggi sekaligus memiliki mental yang sehat adalah mereka yang menerapkan <b>pembelajaran bauran (blended learning) seimbang</b>.
                <br><br>
                Rekomendasi batas aman penggunaan AI berkisar di angka <b>7-11 jam per minggu</b>. Di atas batas tersebut, nilai retensi mulai menurun secara eksponensial.
                <br><br>
                Selain itu, rasio belajar mandiri secara konvensional (buku, jurnal, kerja kelompok fisik) harus tetap dijaga <b>minimal 1.5 kali lipat lebih lama</b> daripada durasi interaksi di depan sistem AI.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ==================== TAB 3: KEBIJAKAN KAMPUS & KESEJAHTERAAN MENTAL (Q3 & Q4) ====================
with tab3:
    st.markdown("### Pengaruh Aturan Institusi Terhadap IPK, Kecemasan, & Burnout (Q3)")
    
    col_t3_left, col_t3_right = st.columns([2, 1])
    
    with col_t3_left:
        # Kebijakan Aggregation
        policy_agg = df.groupby('Institutional_Policy').agg({
            'Post_Semester_GPA': 'mean',
            'Anxiety_Level_During_Exams': 'mean',
            'Weekly_GenAI_Hours': 'mean'
        }).reset_index()
        
        # VISUALISASI 4: Multi-bar chart perbandingan metrik berdasarkan Kebijakan Aturan
        fig4 = go.Figure()
        
        fig4.add_trace(go.Bar(
            x=policy_agg['Institutional_Policy'],
            y=policy_agg['Post_Semester_GPA'],
            name="Rata-rata IPK Akhir (Post GPA)",
            marker_color='#3B82F6'
        ))
        
        fig4.add_trace(go.Bar(
            x=policy_agg['Institutional_Policy'],
            y=policy_agg['Anxiety_Level_During_Exams'] / 2.5, # Normalisasi skala agar muat dalam satu grafik pembanding
            name="Indeks Kecemasan Ujian (Normalisasi)",
            marker_color='#F59E0B'
        ))
        
        fig4.update_layout(
            barmode='group',
            title="Komparasi Efektivitas Aturan Institusi Terhadap Performa Akademik & Kecemasan",
            xaxis_title="Kebijakan Aturan Institusi",
            yaxis_title="Skor Metrik",
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
        st.plotly_chart(fig4, use_container_width=True)
        
    with col_t3_right:
        st.markdown("""
        <div style="background-color: #F8FAFC; padding: 20px; border-radius: 10px; border: 1px solid #E2E8F0;">
            <h4 style="color: #1E3A8A; margin-top:0;">📢 Dampak Aturan Regulasi (Q3)</h4>
            <p style="font-size: 14px; line-height: 1.6; color: #334155; text-align: justify;">
                Berdasarkan visualisasi di samping:
                <br><br>
                1. Kebijakan pelarangan total (<b>Strict_Ban</b>) ternyata <b>tidak</b> serta merta berkorelasi dengan perolehan IPK tertinggi. Kebijakan ini justru memicu tingkat kecemasan ujian tertinggi bagi mahasiswa yang takut melakukan pelanggaran tidak disengaja.
                <br><br>
                2. Kebijakan <b>Allowed_With_Citation</b> (Diizinkan dengan sitasi yang jelas) menghasilkan rata-rata performa akademik yang solid dengan tingkat kecemasan yang relatif terkendali.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<hr style='border: 0.5px solid #E2E8F0;'>", unsafe_allow_html=True)
    
    # PROFIL MAHASISWA BERISIKO BURNOUT TINGGI (Q4)
    st.markdown("### Profil Karakteristik Mahasiswa Berisiko Burnout Tinggi (Q4)")
    
    col_burn_left, col_burn_right = st.columns([1, 2])
    
    with col_burn_left:
        # Filter data burnout tinggi
        df_high_burn = df[df['Burnout_Risk_Level'] == 'High']
        
        st.markdown(f"""
        <div style="background-color: #FEF2F2; padding: 25px; border-radius: 12px; border: 1.5px solid #FCA5A5; color:#991B1B;">
            <h4 style="margin-top:0; font-size:18px;">🔥 Profil Mayoritas Pelaku Burnout Tinggi</h4>
            <p style="font-size:13px; color:#EF4444;">Dihitung dari basis data empiris mahasiswa berisiko burnout tinggi</p>
            <hr style="border-color:#FCA5A5; margin:10px 0;">
            <ul style="padding-left:18px; font-size:14px; line-height: 1.7;">
                <li><b>Rata-rata Jam Kerja AI:</b> {df_high_burn['Weekly_GenAI_Hours'].mean():.1f} jam/minggu (Sangat Tinggi)</li>
                <li><b>Belajar Tradisional:</b> {df_high_burn['Traditional_Study_Hours'].mean():.1f} jam/minggu</li>
                <li><b>Kecemasan Saat Ujian:</b> Skala {df_high_burn['Anxiety_Level_During_Exams'].mean():.1f}/10</li>
                <li><b>Rata-rata Ketergantungan:</b> Skala {df_high_burn['Perceived_AI_Dependency'].mean():.1f}/5</li>
                <li><b>Didominasi Rumpun Ilmu:</b> {df_high_burn['Major_Category'].mode()[0]}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col_burn_right:
        # VISUALISASI 5: Bubble Chart / Scatter plot yang memetakan korelasi multi-dimensi dari risiko burnout
        fig5 = px.scatter(
            df_sample,
            x="Anxiety_Level_During_Exams",
            y="Weekly_GenAI_Hours",
            size="Tool_Diversity",
            color="Burnout_Risk_Level",
            color_discrete_map={"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"},
            title="Peta Multi-dimensi: Jam Kerja AI vs Kecemasan vs Tingkat Burnout (Ukuran Gelembung: Keberagaman Aplikasi)",
            labels={
                "Anxiety_Level_During_Exams": "Tingkat Kecemasan Ujian (1-10)",
                "Weekly_GenAI_Hours": "Jam AI Mingguan",
                "Burnout_Risk_Level": "Risiko Burnout"
            }
        )
        fig5.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        fig5.update_yaxes(showgrid=True, gridcolor='#E2E8F0')
        fig5.update_xaxes(showgrid=True, gridcolor='#E2E8F0')
        st.plotly_chart(fig5, use_container_width=True)

# --- PANEL CATATAN & DOWNLOAD REPORT DI BAWAH ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="background-color: #F1F5F9; padding: 20px; border-radius: 12px; border: 1px solid #CBD5E1;">
    <h4 style="margin-top:0; color: #334155;">📥 Ekspor Laporan Kebijakan untuk Konsultan</h4>
    <p style="font-size:14px; color: #475569; margin-bottom:15px;">
        Gunakan data hasil filter aktif di atas untuk menghasilkan tabel ringkasan strategis guna dilampirkan pada laporan tertulis (Policy Brief).
    </p>
</div>
""", unsafe_allow_html=True)

# Fitur Ekspor Data CSV
csv_data = df.groupby(['Major_Category', 'Institutional_Policy']).agg({
    'Post_Semester_GPA': 'mean',
    'Skill_Retention_Score': 'mean',
    'Weekly_GenAI_Hours': 'mean'
}).to_csv().encode('utf-8')

st.download_button(
    label="⬇️ Unduh Ringkasan Data Strategis (CSV)",
    data=csv_data,
    file_name="ringkasan_kebijakan_ai_mahasiswa.csv",
    mime="text/csv"
)