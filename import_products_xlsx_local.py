"""
Reset local POS data (while keeping login-related tables) and import products from XLSX.

Usage example (PowerShell):
    .\\.venv\\Scripts\\python.exe import_products_xlsx_local.py `
      --xlsx "template_products_import.xlsx" `
      --host localhost --port 3306 --user root --password "YOUR_PASSWORD" --database stocks
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

import mysql.connector
import openpyxl


@dataclass
class ImportStats:
    rows_read: int = 0
    products_seen: int = 0
    products_upserted: int = 0
    suppliers_created: int = 0
    categories_created: int = 0
    inventory_updates: int = 0
    row_errors: int = 0


KEEP_TABLES_DEFAULT = [
    "users",
    "roles",
    "stores",
    "authorized_devices",
    "system_license",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reset local data (except login tables) and import products from XLSX."
    )
    parser.add_argument("--xlsx", required=True, help="Path to XLSX file")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=3306)
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="", help="MySQL password")
    parser.add_argument("--database", default="stocks")
    parser.add_argument(
        "--store-id",
        type=int,
        default=0,
        help="Target store for opening stock. 0 = auto-detect from users/stores.",
    )
    parser.add_argument(
        "--commit-every",
        type=int,
        default=1000,
        help="Commit interval during import.",
    )
    parser.add_argument(
        "--keep-tables",
        nargs="*",
        default=KEEP_TABLES_DEFAULT,
        help="Tables to preserve during reset.",
    )
    return parser.parse_args()


def to_int(value, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def to_decimal(value, default: str = "0") -> Decimal:
    try:
        if value is None or value == "":
            return Decimal(default)
        return Decimal(str(value))
    except Exception:
        return Decimal(default)


def to_text(value, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def fetch_existing_tables(cursor) -> List[str]:
    cursor.execute("SHOW TABLES")
    rows = cursor.fetchall()
    if not rows:
        return []
    first_key = next(iter(rows[0].keys()))
    return [str(row[first_key]) for row in rows]


def reset_database_except_login(cursor, conn, keep_tables: Iterable[str]) -> Tuple[int, int]:
    keep_set = {t.lower() for t in keep_tables}
    all_tables = fetch_existing_tables(cursor)
    to_truncate = [t for t in all_tables if t.lower() not in keep_set]

    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    try:
        for table in to_truncate:
            cursor.execute(f"TRUNCATE TABLE `{table}`")
    finally:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    return len(all_tables), len(to_truncate)


def detect_target_store_id(cursor, forced_store_id: int) -> int:
    if forced_store_id > 0:
        return forced_store_id

    cursor.execute("SELECT store_id FROM users WHERE is_active = TRUE ORDER BY id LIMIT 1")
    row = cursor.fetchone()
    if row and row.get("store_id"):
        return int(row["store_id"])

    cursor.execute("SELECT id FROM stores WHERE is_active = TRUE ORDER BY id LIMIT 1")
    row = cursor.fetchone()
    if row and row.get("id"):
        return int(row["id"])

    raise RuntimeError("No active store found. Cannot assign opening stock.")


def fetch_active_store_ids(cursor) -> List[int]:
    cursor.execute("SELECT id FROM stores WHERE is_active = TRUE ORDER BY id")
    rows = cursor.fetchall()
    return [int(r["id"]) for r in rows]


def ensure_category(cursor, category_id: int, category_cache: Set[int], stats: ImportStats) -> None:
    if category_id in category_cache:
        return

    cursor.execute("SELECT id FROM categories WHERE id = %s", (category_id,))
    if cursor.fetchone():
        category_cache.add(category_id)
        return

    cursor.execute(
        "INSERT INTO categories (id, category_name, description, is_active) VALUES (%s, %s, %s, TRUE)",
        (category_id, f"Category {category_id}", "Auto-created during XLSX import"),
    )
    category_cache.add(category_id)
    stats.categories_created += 1


def ensure_supplier_id(
    cursor,
    supplier_name: str,
    supplier_cache: Dict[str, int],
    stats: ImportStats,
) -> int:
    key = supplier_name.strip().lower()
    if key in supplier_cache:
        return supplier_cache[key]

    cursor.execute(
        "SELECT id FROM suppliers WHERE LOWER(name) = LOWER(%s) ORDER BY id LIMIT 1",
        (supplier_name,),
    )
    row = cursor.fetchone()
    if row:
        supplier_id = int(row["id"])
        supplier_cache[key] = supplier_id
        return supplier_id

    cursor.execute(
        """
        INSERT INTO suppliers (name, phone, address, tax_number, opening_balance, current_balance, notes, is_active)
        VALUES (%s, NULL, NULL, NULL, 0, 0, 'Auto-created during XLSX import', TRUE)
        """,
        (supplier_name,),
    )
    supplier_id = int(cursor.lastrowid)
    supplier_cache[key] = supplier_id
    stats.suppliers_created += 1
    return supplier_id


def upsert_product(cursor, code: str, name: str, category_id: int, buy_price: Decimal,
                   sell_price: Decimal, supplier_id: int, unit: str) -> int:
    cursor.execute(
        """
        INSERT INTO products (
            product_code, product_name, category_id, buy_price, sell_price,
            supplier_id, unit, barcode, is_active
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
        ON DUPLICATE KEY UPDATE
            product_name = VALUES(product_name),
            category_id = VALUES(category_id),
            buy_price = VALUES(buy_price),
            sell_price = VALUES(sell_price),
            supplier_id = VALUES(supplier_id),
            unit = VALUES(unit),
            is_active = TRUE
        """,
        (code, name, category_id, str(buy_price), str(sell_price), supplier_id, unit, code),
    )
    cursor.execute("SELECT id FROM products WHERE product_code = %s LIMIT 1", (code,))
    row = cursor.fetchone()
    if not row:
        raise RuntimeError(f"Failed to resolve product id for code: {code}")
    return int(row["id"])


def ensure_inventory_rows_for_all_stores(
    cursor,
    product_id: int,
    store_ids: List[int],
    target_store_id: int,
    opening_qty: int,
) -> None:
    for sid in store_ids:
        qty = opening_qty if sid == target_store_id else 0
        cursor.execute(
            """
            INSERT INTO product_inventory (product_id, store_id, quantity_in_stock)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE quantity_in_stock = quantity_in_stock + VALUES(quantity_in_stock)
            """,
            (product_id, sid, qty),
        )


def add_opening_qty_to_target_store(cursor, product_id: int, target_store_id: int, opening_qty: int) -> None:
    if opening_qty <= 0:
        return
    cursor.execute(
        """
        INSERT INTO product_inventory (product_id, store_id, quantity_in_stock)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE quantity_in_stock = quantity_in_stock + VALUES(quantity_in_stock)
        """,
        (product_id, target_store_id, opening_qty),
    )


def import_xlsx(cursor, conn, xlsx_path: Path, target_store_id: int, commit_every: int) -> ImportStats:
    stats = ImportStats()

    store_ids = fetch_active_store_ids(cursor)
    if not store_ids:
        raise RuntimeError("No active stores found. Cannot build product inventory.")

    wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    ws = wb.active

    category_cache: Set[int] = set()
    supplier_cache: Dict[str, int] = {}
    product_id_cache: Dict[str, int] = {}

    for row in ws.iter_rows(min_row=2, values_only=True):
        stats.rows_read += 1

        try:
            code = to_text(row[0] if len(row) > 0 else "", "")
            name = to_text(row[1] if len(row) > 1 else "", "")
            category_id = to_int(row[2] if len(row) > 2 else None, 1)
            buy_price = to_decimal(row[3] if len(row) > 3 else None, "0")
            sell_price = to_decimal(row[4] if len(row) > 4 else None, "0")
            unit = to_text(row[5] if len(row) > 5 else "", "piece") or "piece"
            supplier_name = to_text(row[6] if len(row) > 6 else "", "General Supplier") or "General Supplier"
            opening_qty = to_int(row[7] if len(row) > 7 else None, 0)

            if not code or not name:
                continue

            ensure_category(cursor, category_id, category_cache, stats)
            supplier_id = ensure_supplier_id(cursor, supplier_name, supplier_cache, stats)

            is_first_seen = code not in product_id_cache
            if is_first_seen:
                product_id = upsert_product(
                    cursor=cursor,
                    code=code,
                    name=name,
                    category_id=category_id,
                    buy_price=buy_price,
                    sell_price=sell_price,
                    supplier_id=supplier_id,
                    unit=unit,
                )
                product_id_cache[code] = product_id
                stats.products_upserted += 1
                ensure_inventory_rows_for_all_stores(
                    cursor=cursor,
                    product_id=product_id,
                    store_ids=store_ids,
                    target_store_id=target_store_id,
                    opening_qty=opening_qty,
                )
            else:
                product_id = product_id_cache[code]
                add_opening_qty_to_target_store(cursor, product_id, target_store_id, opening_qty)

            stats.inventory_updates += 1
        except Exception:
            stats.row_errors += 1

        if stats.rows_read % max(1, commit_every) == 0:
            conn.commit()

    conn.commit()
    stats.products_seen = len(product_id_cache)
    return stats


def main() -> int:
    args = parse_args()
    xlsx_path = Path(args.xlsx).expanduser().resolve()
    if not xlsx_path.exists():
        print(f"[ERROR] XLSX file not found: {xlsx_path}")
        return 1

    conn = None
    try:
        conn = mysql.connector.connect(
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.password,
            database=args.database,
            charset="utf8mb4",
            use_unicode=True,
            autocommit=False,
        )
        cursor = conn.cursor(dictionary=True)

        total_tables, truncated_tables = reset_database_except_login(cursor, conn, args.keep_tables)
        target_store_id = detect_target_store_id(cursor, args.store_id)
        stats = import_xlsx(cursor, conn, xlsx_path, target_store_id, args.commit_every)

        print("=== DONE ===")
        print(f"Database: {args.database}")
        print(f"XLSX: {xlsx_path}")
        print(f"Tables total: {total_tables}")
        print(f"Tables truncated: {truncated_tables}")
        print(f"Target store for opening stock: {target_store_id}")
        print(f"Rows read: {stats.rows_read}")
        print(f"Unique products: {stats.products_seen}")
        print(f"Products upserted: {stats.products_upserted}")
        print(f"Suppliers created: {stats.suppliers_created}")
        print(f"Categories created: {stats.categories_created}")
        print(f"Inventory updates: {stats.inventory_updates}")
        print(f"Row errors: {stats.row_errors}")
        return 0
    except Exception as exc:
        if conn:
            conn.rollback()
        print(f"[ERROR] {exc}")
        return 1
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
