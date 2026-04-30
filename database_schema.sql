-- ============================================================
--  Cosmetic Database Schema
--  Database : MySQL / MariaDB
--  Disesuaikan dengan dataset cosmetic_p.csv
-- ============================================================

CREATE DATABASE IF NOT EXISTS cosmetic_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE cosmetic_db;

-- ── 1. SKIN TYPES ─────────────────────────────────────────────
CREATE TABLE skin_types (
  id    TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name  VARCHAR(50) NOT NULL UNIQUE
);

-- Seed langsung dari kolom dataset
INSERT INTO skin_types (name) VALUES
  ('Combination'),
  ('Dry'),
  ('Normal'),
  ('Oily'),
  ('Sensitive');

-- ── 2. SKIN CONCERNS ──────────────────────────────────────────
CREATE TABLE skin_concerns (
  id    SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name  VARCHAR(100) NOT NULL UNIQUE
);

-- Seed awal (bisa ditambah sesuai kebutuhan)
INSERT INTO skin_concerns (name) VALUES
  ('Acne'),
  ('Anti-Aging'),
  ('Brightening'),
  ('Hydration'),
  ('Sensitivity'),
  ('Hyperpigmentation'),
  ('Pore Minimizing');

-- ── 3. PRODUCTS ───────────────────────────────────────────────
CREATE TABLE products (
  id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  label       VARCHAR(100)   NOT NULL,          -- kategori: Moisturizer, Cleanser, dll
  brand       VARCHAR(100)   NOT NULL,
  name        VARCHAR(255)   NOT NULL,
  price       DECIMAL(10,2)  DEFAULT NULL,
  rank        DECIMAL(3,1)   DEFAULT NULL,       -- rating 0.0 – 5.0
  inci_raw    TEXT           DEFAULT NULL,       -- raw string dari CSV (backup)
  created_at  TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,

  INDEX idx_brand (brand),
  INDEX idx_label (label)
);

-- ── 4. INGREDIENTS ────────────────────────────────────────────
CREATE TABLE ingredients (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  inci_name       VARCHAR(255)  NOT NULL UNIQUE,  -- nama INCI terstandar
  common_name     VARCHAR(255)  DEFAULT NULL,     -- nama umum (opsional)
  cas_number      VARCHAR(50)   DEFAULT NULL,     -- CAS Registry Number
  function        TEXT          DEFAULT NULL,     -- contoh: emollient, humectant
  comedogenic     TINYINT(1)    DEFAULT NULL,     -- 0–5 scale, NULL = belum diketahui

  INDEX idx_inci_name (inci_name)
);

-- ── 5. PRODUCT ↔ INGREDIENTS (many-to-many) ───────────────────
CREATE TABLE product_ingredients (
  product_id    INT UNSIGNED NOT NULL,
  ingredient_id INT UNSIGNED NOT NULL,
  position      SMALLINT UNSIGNED DEFAULT NULL,   -- urutan di label produk

  PRIMARY KEY (product_id, ingredient_id),
  FOREIGN KEY (product_id)    REFERENCES products(id)    ON DELETE CASCADE,
  FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
);

-- ── 6. PRODUCT ↔ SKIN TYPES (many-to-many) ───────────────────
CREATE TABLE product_skin_types (
  product_id    INT UNSIGNED    NOT NULL,
  skin_type_id  TINYINT UNSIGNED NOT NULL,

  PRIMARY KEY (product_id, skin_type_id),
  FOREIGN KEY (product_id)   REFERENCES products(id)    ON DELETE CASCADE,
  FOREIGN KEY (skin_type_id) REFERENCES skin_types(id)  ON DELETE CASCADE
);

-- ── 7. INGREDIENT ↔ SKIN CONCERNS (many-to-many) ─────────────
CREATE TABLE ingredient_concerns (
  ingredient_id INT UNSIGNED     NOT NULL,
  concern_id    SMALLINT UNSIGNED NOT NULL,
  effect        ENUM('beneficial', 'avoid', 'neutral') NOT NULL DEFAULT 'neutral',

  PRIMARY KEY (ingredient_id, concern_id),
  FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)    ON DELETE CASCADE,
  FOREIGN KEY (concern_id)    REFERENCES skin_concerns(id)  ON DELETE CASCADE
);