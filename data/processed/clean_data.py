import pandas as pd
import os

# 1. Buat folder processed kalau belum ada
os.makedirs('data/processed', exist_ok=True)

# 2. Baca Data Kotor
df = pd.read_csv('data/raw/cosmetic_p.csv')
print(f"Data Kotor: {df.shape}")

# 3. PROSES CLEANING
# A. Hapus data yang duplikat (ternyata ada produk dobel)
df = df.drop_duplicates()

# B. Hapus baris yang kolom Ingredients-nya kosong
# (lebih aman daripada dropna() semua kolom sekaligus)
df = df.dropna(subset=['Ingredients'])

# C. Pastikan tipe data Price dan Rank angka
# errors='coerce' → kalau ada yang tidak bisa dikonversi, jadi NaN
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
df['Rank']  = pd.to_numeric(df['Rank'],  errors='coerce')

# D. Normalisasi teks Brand dan Label biar konsisten
df['Brand'] = df['Brand'].str.strip().str.upper()
df['Label'] = df['Label'].str.strip().str.title()

# E. Pastikan kolom skin type bertipe integer (0 atau 1)
skin_type_cols = ['Combination', 'Dry', 'Normal', 'Oily', 'Sensitive']
df[skin_type_cols] = df[skin_type_cols].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)

# F. Reset urutan baris (biar gak loncat-loncat angkanya)
df = df.reset_index(drop=True)

# 4. Ringkasan hasil
print(f"Data Bersih: {df.shape}")
print("\nJumlah kosong per kolom:")
print(df.isnull().sum())
print(f"\nContoh data:")
print(df[['Label', 'Brand', 'Name', 'Price', 'Rank']].head(3))

# 5. Simpan hasil yang rapih
# Simpan di folder processed, jangan timpa yang raw
df.to_csv('data/processed/cosmetic_clean.csv', index=False)

print("\nBERHASIL! Data bersih tersimpan di: data/processed/cosmetic_clean.csv")