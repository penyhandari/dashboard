import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Membaca Dataset
# Pastikan file 'ai_student_impact_dataset (1).csv' berada di folder yang sama dengan skrip ini
df = pd.read_csv('ai_student_impact_dataset (1).csv')

# ==============================================================================
# PERBAIKAN UTAMA: Mengatur Tema Dasar & Memaksa Latar Belakang Berwarna Putih
# ==============================================================================
sns.set_theme(style="whitegrid")
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['savefig.facecolor'] = 'white'

# Menghitung selisih IPK (Post - Pre) untuk analisis dampak akademik
df['GPA_Delta'] = df['Post_Semester_GPA'] - df['Pre_Semester_GPA']


# ==============================================================================
# VISUALISASI 1: Dampak Durasi Penggunaan GenAI terhadap Perubahan IPK & Retensi
# ==============================================================================
# Menambahkan facecolor='white' pada subplots
fig, axes = plt.subplots(1, 2, figsize=(16, 6), facecolor='white')

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
plt.show()


# ==============================================================================
# VISUALISASI 2: Tingkat Kecemasan Ujian Berdasarkan Kebijakan Kampus
# ==============================================================================
plt.figure(figsize=(12, 6), facecolor='white')

# Boxplot untuk melihat distribusi kecemasan berdasarkan regulasi institusi
sns.boxplot(data=df, x='Institutional_Policy', y='Anxiety_Level_During_Exams', hue='Institutional_Policy', palette='Set2', legend=False)
plt.title('Distribusi Tingkat Kecemasan Ujian Berdasarkan Kebijakan Institusi', fontsize=14, fontweight='bold')
plt.xlabel('Kebijakan Institusi')
plt.ylabel('Tingkat Kecemasan Saat Ujian (Skala 1-10)')
plt.xticks(rotation=15)
plt.show()


# ==============================================================================
# VISUALISASI 3: Risiko Burnout Berdasarkan Jam Penggunaan GenAI Mingguan
# ==============================================================================
plt.figure(figsize=(10, 6), facecolor='white')

# Mengurutkan kategori burnout agar rapi
burnout_order = ['Low', 'Medium', 'High']

sns.barplot(data=df, x='Burnout_Risk_Level', y='Weekly_GenAI_Hours', order=burnout_order, palette='OrRd', errorbar=None, hue='Burnout_Risk_Level', legend=False)
plt.title('Rata-rata Jam Penggunaan GenAI per Minggu Berdasarkan Risiko Burnout', fontsize=14, fontweight='bold')
plt.xlabel('Tingkat Risiko Burnout')
plt.ylabel('Rata-rata Jam Kerja GenAI / Minggu')
plt.show()


# ==============================================================================
# VISUALISASI 4: Matriks Korelasi Fitur Utama (Insight untuk Manajemen)
# ==============================================================================
plt.figure(figsize=(10, 8), facecolor='white')

# Memilih kolom numerik krusial untuk melihat hubungan linear
numerical_cols = ['Weekly_GenAI_Hours', 'Pre_Semester_GPA', 'Post_Semester_GPA', 
                  'Traditional_Study_Hours', 'Perceived_AI_Dependency', 
                  'Anxiety_Level_During_Exams', 'Skill_Retention_Score']

corr_matrix = df[numerical_cols].corr()

sns.heatmap(corr_matrix, annot=True, cmap='Coolwarm', fmt=".2f", linewidths=0.5)
plt.title('Matriks Korelasi: Performa Akademik vs Kesejahteraan vs Penggunaan AI', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()