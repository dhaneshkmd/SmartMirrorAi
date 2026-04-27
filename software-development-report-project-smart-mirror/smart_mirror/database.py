from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "smart_mirror.db"


PRODUCT_SEED = [
    {
        "barcode": "8901030970001",
        "name": "LumiWear Satin Foundation",
        "brand": "LumiWear",
        "shade": "Golden Beige 240",
        "ingredients": "Aqua, dimethicone, iron oxides, glycerin, mica",
        "cruelty_free": "Yes",
        "rating": 4.4,
        "undertone": "warm",
        "skin_tones": "medium,tan",
    },
    {
        "barcode": "5012345678900",
        "name": "Rose Cloud Lip Tint",
        "brand": "Aster Beauty",
        "shade": "Soft Rose",
        "ingredients": "Castor oil, beeswax, red 7 lake, vitamin E",
        "cruelty_free": "No",
        "rating": 4.1,
        "undertone": "cool",
        "skin_tones": "fair,light,medium",
    },
    {
        "barcode": "036000291452",
        "name": "Velvet Matte Blush",
        "brand": "Nira Studio",
        "shade": "Peach Bloom",
        "ingredients": "Talc, silica, mica, iron oxides, squalane",
        "cruelty_free": "Yes",
        "rating": 4.7,
        "undertone": "warm",
        "skin_tones": "light,medium,tan,deep",
    },
]


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                skin_tone TEXT NOT NULL,
                undertone TEXT NOT NULL,
                face_shape TEXT NOT NULL,
                body_shape TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS product_cache (
                barcode TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                brand TEXT NOT NULL,
                shade TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                cruelty_free TEXT NOT NULL,
                rating REAL NOT NULL,
                undertone TEXT NOT NULL,
                skin_tones TEXT NOT NULL,
                last_scanned TEXT
            );

            CREATE TABLE IF NOT EXISTS outfit_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                dominant_color TEXT NOT NULL,
                occasion TEXT NOT NULL,
                dress_cut TEXT NOT NULL,
                match_score INTEGER NOT NULL,
                suggestion TEXT NOT NULL
            );
            """
        )

        conn.execute(
            """
            INSERT OR IGNORE INTO user_profile
                (id, skin_tone, undertone, face_shape, body_shape)
            VALUES
                (1, 'medium', 'warm', 'round', 'pear')
            """
        )

        for product in PRODUCT_SEED:
            conn.execute(
                """
                INSERT OR IGNORE INTO product_cache
                    (barcode, name, brand, shade, ingredients, cruelty_free,
                     rating, undertone, skin_tones)
                VALUES
                    (:barcode, :name, :brand, :shade, :ingredients, :cruelty_free,
                     :rating, :undertone, :skin_tones)
                """,
                product,
            )


def fetch_user_profile() -> dict[str, Any]:
    with connect() as conn:
        row = conn.execute("SELECT * FROM user_profile WHERE id = 1").fetchone()
    return dict(row) if row else {}


def fetch_product_by_barcode(barcode: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM product_cache WHERE barcode = ?",
            (barcode,),
        ).fetchone()
        if row:
            conn.execute(
                "UPDATE product_cache SET last_scanned = CURRENT_TIMESTAMP WHERE barcode = ?",
                (barcode,),
            )
    return dict(row) if row else None


def search_product_by_text(query: str) -> dict[str, Any] | None:
    pattern = f"%{query.strip()}%"
    with connect() as conn:
        row = conn.execute(
            """
            SELECT * FROM product_cache
            WHERE name LIKE ? OR brand LIKE ? OR shade LIKE ?
            ORDER BY rating DESC
            LIMIT 1
            """,
            (pattern, pattern, pattern),
        ).fetchone()
    return dict(row) if row else None


def insert_outfit_result(
    dominant_color: str,
    occasion: str,
    dress_cut: str,
    match_score: int,
    suggestion: str,
) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO outfit_history
                (dominant_color, occasion, dress_cut, match_score, suggestion)
            VALUES
                (?, ?, ?, ?, ?)
            """,
            (dominant_color, occasion, dress_cut, match_score, suggestion),
        )


def fetch_outfit_history(limit: int = 8) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM outfit_history
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]
