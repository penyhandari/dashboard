# ==============================================================================
# 0. PERINTAH INSTALASI (Hapus tanda '#' di bawah ini jika dijalankan di Google Colab)
# ==============================================================================
# !pip install streamlit matplotlib seaborn pandas

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st  # <-- Menambahkan pustaka Streamlit

# Mengatur konfigurasi halaman Streamlit
st.set_page_config(page_title="Dashboard BI: Dampak GenAI Mahasiswa", layout="wide")

# Menampilkan judul utama di Dashboard Streamlit
st.title("📊 Analisis Dampak Penggunaan AI Generatif terhadap Performa Akademik & Kesejahteraan Mahasiswa")
st.markdown("Dashboard ini dirancang untuk konsultan pendidikan guna merumuskan kebijakan penggunaan AI yang tepat dan bertanggung jawab.")

# 1. Load Dataset
# Pastikan file CSV berada di direktori yang sama dengan script ini
@st.cache_data  # Optimasi Streamlit agar load data lebih cepat
def load_data():
    return pd.read_csv('ai_student_impact_dataset (1).csv')

df = load_data()

# Pengaturan Tema Visualisasi & Memaksa Latar Belakang Putih agar tidak error/hitam
sns.set_theme(style="whitegrid")
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['savefig.facecolor'] = 'white'

# Menghitung selisih IPK (Post - Pre)
df['GPA_Delta'] = df['Post_Semester_GPA'] - df['Pre_Semester_GPA']


# ==============================================================================
# VISUALISASI 1: Dampak Durasi Penggunaan GenAI terhadap Perubahan IPK & Retensi
# ==============================================================================
st.header("1. Analisis Dampak Akademik")

# Membuat subplots dengan latar belakang putih eksplisit
fig1, axes = plt.subplots(1, 2, figsize=(16, 6), facecolor='white')

# Plot A: Jam GenAI vs Perubahan IPK
sns.scatterplot(data=df, x='Weekly_GenAI_Hours', y='GPA_Delta', alpha=0.5, ax=axes[0], color='#1f77b4')
sns.regplot(data=df, x='Weekly_GenAI_Hours', y='GPA_Delta', scatter=False, ax=axes[0], color='red')
axes[0].set_title('Hubungan Durasi Penggunaan GenAI dengan Perubahan IPK', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Jam Penggunaan GenAI per Minggu')
axes[0].set_ylabel('Perubahan IPK (Post - Pre)')

# Plot B: Jam GenAI vs Skor Retensi Skill
sns.scatterplot(data=df, x='Weekly_GenAI_Hours', y='Skill_Retention_Score', alpha=0.5, ax=axes[1], color='#2ca02c')
sns.regplot(data=df, x='Weekly_GenAI_Hours', y='Skill_Retention_Score', scatter=False, ax=axes[1], color='red')
axes[1].set_title('Hubungan Durasi Penggunaan GenAI dengan Skor Retensi Skill', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Jam Penggunaan GenAI per Minggu')
axes[1].set_ylabel('Skor Retensi Skill')

plt.tight_layout()
st.pyplot(fig1)  # <-- Mengganti plt.show() menjadi st.pyplot()


# ==============================================================================
# VISUALISASI 2 & 3: Kesejahteraan Mahasiswa (Ditampilkan Berdampingan di Streamlit)
# ==============================================================================
st.header("2. Analisis Kesejahteraan Mahasiswa (Well-being)")

col1, col2 = st.columns(2)  # Membuat layout 2 kolom di Streamlit

with col1:
    fig2, ax2 = plt.subplots(figsize=(10, 6), facecolor='white')
    sns.boxplot(data=df, x='Institutional_Policy', y='Anxiety_Level_During_Exams', hue='Institutional_Policy', palette='Set2', legend=False, ax=ax2)
    plt.title('Tingkat Kecemasan Ujian Berdasarkan Kebijakan Institusi', fontsize=12, fontweight='bold')
    plt.xlabel('Kebijakan Institusi')
    plt.ylabel('Tingkat Kecemasan Saat Ujian (Skala 1-10)')
    plt.xticks(rotation=15)
    st.pyplot(fig2)

with col2:
    fig3, ax3 = plt.subplots(figsize=(10, 6), facecolor='white')
    burnout_order = ['Low', 'Medium', 'High']
    sns.barplot(data=df, x='Burnout_Risk_Level', y='Weekly_GenAI_Hours', order=burnout_order, palette='OrRd', errorbar=None, hue='Burnout_Risk_Level', legend=False, ax=ax3)
    plt.title('Rata-rata Jam GenAI / Minggu Berdasarkan Risiko Burnout', fontsize=12, fontweight='bold')
    plt.xlabel('Tingkat Risiko Burnout')
    plt.ylabel('Rata-rata Jam Kerja GenAI / Minggu')
    st.pyplot(fig3)


# ==============================================================================
# VISUALISASI 4: Matriks Korelasi Fitur Utama
# ==============================================================================
st.header("3. Matriks Korelasi (Ringkasan Eksekutif)")

fig4, ax4 = plt.subplots(figsize=(10, 7), facecolor='white')
numerical_cols = ['Weekly_GenAI_Hours', 'Pre_Semester_GPA', 'Post_Semester_GPA',
                  'Traditional_Study_Hours', 'Perceived_AI_Dependency',
                  'Anxiety_Level_During_Exams', 'Skill_Retention_Score']

corr_matrix = df[numerical_cols].corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5, ax=ax4)
plt.title('Korelasi Linear: Performa Akademik vs Kesejahteraan vs Penggunaan AI', fontsize=12, fontweight='bold')
plt.tight_layout()
st.pyplot(fig4)