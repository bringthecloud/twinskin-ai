import pandas as pd

# Rapikan tampilan output
pd.set_option('display.max_colwidth', 50)
pd.set_option('display.width', None)
pd.set_option('display.max_columns', None)

df = pd.read_csv('data/raw/cosmetic_p.csv')

# ── 1. Info Umum ──────────────────────────────────────
print("=" * 50)
print("  INFO UMUM")
print("=" * 50)
print(f"  Jumlah baris    : {df.shape[0]}")
print(f"  Jumlah kolom    : {df.shape[1]}")
print(f"  Kolom           : {df.columns.tolist()}")

# ── 2. Tipe Data ──────────────────────────────────────
print("\n" + "=" * 50)
print("  TIPE DATA")
print("=" * 50)
print(df.dtypes.to_string())

# ── 3. Data Kosong ────────────────────────────────────
print("\n" + "=" * 50)
print("  DATA KOSONG (NaN)")
print("=" * 50)
missing = df.isnull().sum()
if missing.sum() == 0:
    print("  Tidak ada data kosong!")
else:
    print(missing[missing > 0].to_string())

# ── 4. Nilai Unik Label ───────────────────────────────
print("\n" + "=" * 50)
print("  KATEGORI PRODUK (Label)")
print("=" * 50)
for label in df['Label'].unique():
    count = len(df[df['Label'] == label])
    print(f"  {label:<20} : {count} produk")

# ── 5. Preview Data ───────────────────────────────────
print("\n" + "=" * 50)
print("  PREVIEW 3 BARIS PERTAMA")
print("=" * 50)
print(df[['Label', 'Brand', 'Name', 'Price', 'Rank']].head(3).to_string(index=False))

print("TES! SCRIPT INI JALAN LHO!")