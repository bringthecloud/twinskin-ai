print("MULAI")

import json
import pandas as pd
import mysql.connector

# ── KONFIGURASI DATABASE ──────────────────────────────────────
DB_CONFIG = {
    'host'    : 'localhost',
    'user'    : 'root',
    'password': '',           # isi password MySQL kamu (XAMPP default kosong)
    'database': 'cosmetic_db',
    'charset' : 'utf8mb4',
}

# ── PATH FILE CSV ─────────────────────────────────────────────
PRODUCTS_CSV    = 'data/processed/cosmetic_cleaned.csv'
INGREDIENTS_CSV = 'data/processed/ingredients_master.csv'

# ─────────────────────────────────────────────────────────────

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def seed_ingredients(cursor, df_ingredients):
    """Masukkan semua ingredient unik ke tabel ingredients."""
    print("  Seeding ingredients...")
    sql = """
        INSERT IGNORE INTO ingredients (inci_name)
        VALUES (%s)
    """
    data = [(row['inci_name'],) for _, row in df_ingredients.iterrows()]
    cursor.executemany(sql, data)
    print(f"  → {cursor.rowcount} ingredient dimasukkan")


def seed_products(cursor, df_products):
    """Masukkan produk + relasi skin type + relasi ingredient."""

    # Ambil mapping skin_type name → id
    cursor.execute("SELECT id, name FROM skin_types")
    skin_type_map = {name.lower(): sid for sid, name in cursor.fetchall()}

    # Ambil mapping inci_name → id
    cursor.execute("SELECT id, inci_name FROM ingredients")
    ingredient_map = {name: iid for iid, name in cursor.fetchall()}

    print("  Seeding products...")
    total_products    = 0
    total_skin_types  = 0
    total_ingredients = 0

    for _, row in df_products.iterrows():

        # 1. Insert produk
        cursor.execute("""
            INSERT INTO products (label, brand, name, price, rank, inci_raw)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            row['label'],
            row['brand'],
            row['name'],
            row['price']  if pd.notna(row['price']) else None,
            row['rank']   if pd.notna(row['rank'])  else None,
            None,   # inci_raw tidak disimpan ulang untuk hemat space
        ))
        product_id = cursor.lastrowid
        total_products += 1

        # 2. Insert relasi skin type (kolom bernilai 1 = cocok)
        skin_cols = ['combination', 'dry', 'normal', 'oily', 'sensitive']
        for col in skin_cols:
            if int(row.get(col, 0)) == 1:
                st_id = skin_type_map.get(col)
                if st_id:
                    cursor.execute("""
                        INSERT IGNORE INTO product_skin_types (product_id, skin_type_id)
                        VALUES (%s, %s)
                    """, (product_id, st_id))
                    total_skin_types += 1

        # 3. Insert relasi ingredient
        try:
            ingredient_list = json.loads(row['ingredients'])
        except (json.JSONDecodeError, TypeError):
            ingredient_list = []

        for position, inci_name in enumerate(ingredient_list, start=1):
            ing_id = ingredient_map.get(inci_name)
            if ing_id:
                cursor.execute("""
                    INSERT IGNORE INTO product_ingredients (product_id, ingredient_id, position)
                    VALUES (%s, %s, %s)
                """, (product_id, ing_id, position))
                total_ingredients += 1

    print(f"  → {total_products} produk dimasukkan")
    print(f"  → {total_skin_types} relasi skin type dimasukkan")
    print(f"  → {total_ingredients} relasi ingredient dimasukkan")


def main():
    print("=" * 50)
    print("  SEED DATABASE - cosmetic_db")
    print("=" * 50)

    # Baca CSV
    print("\nMembaca file CSV...")
    df_products    = pd.read_csv(PRODUCTS_CSV)
    df_ingredients = pd.read_csv(INGREDIENTS_CSV)
    print(f"  Produk    : {len(df_products)} baris")
    print(f"  Ingredient: {len(df_ingredients)} baris")

    # Koneksi ke MySQL
    print("\nKoneksi ke MySQL...")
    conn   = get_connection()
    cursor = conn.cursor()
    print("  Berhasil terhubung!")

    try:
        print()
        seed_ingredients(cursor, df_ingredients)
        conn.commit()

        print()
        seed_products(cursor, df_products)
        conn.commit()

        print()
        print("=" * 50)
        print("  SEEDING SELESAI!")
        print("=" * 50)

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] {e}")
        print("Rollback dilakukan, tidak ada data yang tersimpan.")

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()