print("Script mulai...")
"""
INCI Ingredient Preprocessing Script
Dataset: cosmetic_p.csv
Output : cosmetic_cleaned.csv  — satu baris per produk, kolom ingredients berisi list JSON
         ingredients_master.csv — daftar unik semua ingredient
"""

import csv
import json
import re
from pathlib import Path

INPUT_FILE   = Path("data/raw/cosmetic_p.csv")
OUT_PRODUCTS = Path("data/processed/cosmetic_cleaned.csv")
OUT_MASTER   = Path("data/processed/ingredients_master.csv")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean_ingredient_name(raw: str) -> str:
    """Normalise satu nama ingredient."""
    name = raw.strip()

    # Hapus trailing tanda baca (titik, koma, titik koma)
    name = name.rstrip(".,;")

    # Hapus asterisk di awal / akhir (catatan kaki seperti *Avena Sativa**)
    name = name.strip("*")

    # Normalise spasi berlebih (termasuk "Caprylic/ Capric")
    name = re.sub(r"\s*/\s*", "/", name)   # "Caprylic/ Capric" → "Caprylic/Capric"
    name = re.sub(r"\s{2,}", " ", name)     # double space → single

    # Title-case sederhana untuk konsistensi (jaga huruf besar di tengah seperti "pH")
    # Hanya lowercase semua dulu lalu capitalize per kata
    name = name.strip()

    return name if name else None


def parse_ingredients(raw_string: str) -> list[str]:
    """
    Ubah raw INCI string menjadi list ingredient yang sudah dibersihkan.
    Menangani:
      - "May Contain: ..."  → dibuang
      - catatan kaki (*Hadasei-3., *Napiers...) → dibuang
      - spasi ekstra, asterisk, trailing punctuation
    """
    if not raw_string or not raw_string.strip():
        return []

    # 1. Buang bagian "May Contain: ..." (case-insensitive)
    text = re.split(r"(?i)\.\s*may contain\s*:", raw_string)[0]
    text = re.split(r"(?i),?\s*may contain\s*:", text)[0]

    # 2. Pisah berdasarkan koma
    parts = text.split(",")

    ingredients = []
    for part in parts:
        cleaned = clean_ingredient_name(part)

        if not cleaned:
            continue

        # 3. Buang catatan kaki: string yang diawali * dan tidak mengandung spasi
        #    atau yang merupakan keterangan singkat seperti "*Hadasei-3"
        if cleaned.startswith("*") or re.match(r"^\*+\S+$", cleaned):
            continue

        # 4. Buang entri yang terlalu pendek (1-2 karakter) atau hanya angka
        if len(cleaned) <= 2 or cleaned.isdigit():
            continue

        # 5. Buang keterangan dalam kurung yang berdiri sendiri
        #    misalnya "(Ci 77492)" yang tersisa setelah split
        if re.match(r"^\(.*\)$", cleaned):
            continue

        ingredients.append(cleaned)

    return ingredients


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    all_ingredients: set[str] = set()
    product_rows = []

    with open(INPUT_FILE, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            raw_inci   = row.get("Ingredients", "")
            parsed     = parse_ingredients(raw_inci)

            # Kumpulkan ke master set
            all_ingredients.update(parsed)

            product_rows.append({
                "label"       : row["Label"],
                "brand"       : row["Brand"],
                "name"        : row["Name"],
                "price"       : row["Price"],
                "rank"        : row["Rank"],
                "ingredients" : json.dumps(parsed),   # simpan sebagai JSON array
                "combination" : row["Combination"],
                "dry"         : row["Dry"],
                "normal"      : row["Normal"],
                "oily"        : row["Oily"],
                "sensitive"   : row["Sensitive"],
                "ingredient_count": len(parsed),
            })

    # --- Tulis cosmetic_cleaned.csv ---
    fieldnames = [
        "label", "brand", "name", "price", "rank",
        "ingredients", "combination", "dry", "normal", "oily", "sensitive",
        "ingredient_count",
    ]
    with open(OUT_PRODUCTS, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(product_rows)

    # --- Tulis ingredients_master.csv ---
    sorted_ingredients = sorted(all_ingredients, key=str.lower)
    with open(OUT_MASTER, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "inci_name"])
        for idx, name in enumerate(sorted_ingredients, start=1):
            writer.writerow([idx, name])

    # --- Ringkasan ---
    print("=" * 55)
    print("  INCI Preprocessing selesai!")
    print("=" * 55)
    print(f"  Produk diproses       : {len(product_rows)}")
    print(f"  Ingredient unik       : {len(all_ingredients)}")
    print(f"  Output produk         : {OUT_PRODUCTS.name}")
    print(f"  Output master INCI    : {OUT_MASTER.name}")
    print()

    # Contoh output 3 produk pertama
    print("  Contoh hasil parsing:")
    print("-" * 55)
    for row in product_rows[:3]:
        ingr_list = json.loads(row["ingredients"])
        print(f"  [{row['brand']}] {row['name'][:40]}")
        print(f"  → {len(ingr_list)} ingredients: {ingr_list[:4]} ...")
        print()


if __name__ == "__main__":
    main()