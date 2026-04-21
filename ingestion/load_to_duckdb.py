"""
📥 Olist Analytics — Carga no DuckDB
======================================
Carrega os 9 CSVs do Olist para um banco DuckDB local, criando
um schema 'raw' que servirá de fonte para as transformações dbt.

Uso:
    python ingestion/load_to_duckdb.py
    # ou
    make load
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import duckdb
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# ============================================================
# Configuração
# ============================================================

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_PATH = Path(os.getenv("RAW_DATA_PATH", PROJECT_ROOT / "data" / "raw"))

DUCKDB_PATH = Path(
    os.getenv("DUCKDB_PATH", PROJECT_ROOT / "data" / "warehouse" / "olist.duckdb")
)

RAW_SCHEMA: Final[str] = "raw"

console = Console()


# ============================================================
# Definição das tabelas
# ============================================================

@dataclass(frozen=True)
class TableSpec:
    csv_name: str
    table_name: str
    primary_key: str | None = None


TABLES: list[TableSpec] = [
    TableSpec("product_category_name_translation.csv",
              "product_category_translation"),
    TableSpec("olist_sellers_dataset.csv",
              "sellers",
              primary_key="seller_id"),
    TableSpec("olist_customers_dataset.csv",
              "customers",
              primary_key="customer_id"),
    TableSpec("olist_geolocation_dataset.csv",
              "geolocation"),
    TableSpec("olist_products_dataset.csv",
              "products",
              primary_key="product_id"),
    TableSpec("olist_orders_dataset.csv",
              "orders",
              primary_key="order_id"),
    TableSpec("olist_order_items_dataset.csv",
              "order_items"),
    TableSpec("olist_order_payments_dataset.csv",
              "order_payments"),
    TableSpec("olist_order_reviews_dataset.csv",
              "order_reviews",
              primary_key="review_id"),
]


# ============================================================
# Funções
# ============================================================

def print_header() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]🦆 Olist Analytics — Carga no DuckDB[/bold cyan]\n"
            f"[dim]Origem:[/dim] {RAW_DATA_PATH}\n"
            f"[dim]DuckDB:[/dim] {DUCKDB_PATH}\n"
            f"[dim]Schema:[/dim] {RAW_SCHEMA}",
            border_style="cyan",
        )
    )


def check_raw_files() -> None:
    missing = [
        spec.csv_name for spec in TABLES
        if not (RAW_DATA_PATH / spec.csv_name).exists()
    ]

    if missing:
        console.print("[bold red]❌ Arquivos CSV faltando:[/bold red]")
        for f in missing:
            console.print(f"   • {f}")
        console.print("\n   Execute primeiro: [yellow]make download[/yellow]")
        sys.exit(1)

    console.print("[green]✅ Todos os CSVs encontrados[/green]")


def ensure_warehouse_dir() -> None:
    DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_table(
    conn: duckdb.DuckDBPyConnection,
    spec: TableSpec,
) -> tuple[int, str | None]:
    csv_path = RAW_DATA_PATH / spec.csv_name
    full_table = f"{RAW_SCHEMA}.{spec.table_name}"

    conn.execute(f"DROP TABLE IF EXISTS {full_table}")

    conn.execute(
        f"""
        CREATE TABLE {full_table} AS
        SELECT * FROM read_csv_auto(
            '{csv_path}',
            header=true,
            sample_size=-1
        )
        """
    )

    row_count = conn.execute(
        f"SELECT COUNT(*) FROM {full_table}"
    ).fetchone()[0]

    pk_msg: str | None = None
    if spec.primary_key:
        nulls = conn.execute(
            f"SELECT COUNT(*) FROM {full_table} "
            f"WHERE {spec.primary_key} IS NULL"
        ).fetchone()[0]

        duplicates = conn.execute(
            f"""
            SELECT COUNT(*) - COUNT(DISTINCT {spec.primary_key})
            FROM {full_table}
            """
        ).fetchone()[0]

        if nulls == 0 and duplicates == 0:
            pk_msg = "✅"
        else:
            pk_msg = f"⚠️  {nulls} null, {duplicates} dup"

    return row_count, pk_msg


def load_all_tables() -> list[dict]:
    ensure_warehouse_dir()

    console.print(
        f"\n[cyan]📥 Carregando {len(TABLES)} tabelas no DuckDB...[/cyan]\n"
    )

    results = []

    with duckdb.connect(str(DUCKDB_PATH)) as conn:
        conn.execute(f"CREATE SCHEMA IF NOT EXISTS {RAW_SCHEMA}")

        for spec in TABLES:
            console.print(f"  → {spec.table_name}... ", end="")
            try:
                row_count, pk_msg = load_table(conn, spec)
                console.print(
                    f"[green]{row_count:>8,} linhas[/green]"
                    f" {'| PK ' + pk_msg if pk_msg else ''}"
                )
                results.append({
                    "table": spec.table_name,
                    "rows": row_count,
                    "pk_check": pk_msg or "—",
                    "status": "✅",
                })
            except Exception as e:
                console.print(f"[red]❌ {e}[/red]")
                results.append({
                    "table": spec.table_name,
                    "rows": 0,
                    "pk_check": "—",
                    "status": f"❌ {e}",
                })

    return results


def print_summary(results: list[dict]) -> None:
    console.print("\n[cyan]📊 Resumo da carga:[/cyan]\n")

    table = Table(title=f"🦆 DuckDB · Schema [{RAW_SCHEMA}]", show_lines=False)
    table.add_column("Tabela", style="cyan")
    table.add_column("Linhas", justify="right", style="green")
    table.add_column("PK Check", justify="center")
    table.add_column("Status", justify="center")

    total_rows = 0
    for r in results:
        table.add_row(
            r["table"],
            f"{r['rows']:,}",
            r["pk_check"],
            r["status"],
        )
        total_rows += r["rows"]

    console.print(table)

    db_size_mb = DUCKDB_PATH.stat().st_size / (1024 * 1024)

    all_ok = all(r["status"] == "✅" for r in results)
    border = "green" if all_ok else "red"
    icon = "🎉" if all_ok else "⚠️"

    console.print(
        Panel.fit(
            f"[bold]{icon} Carga finalizada[/bold]\n\n"
            f"[dim]Total de linhas:[/dim] [bold]{total_rows:,}[/bold]\n"
            f"[dim]Banco DuckDB:[/dim] {db_size_mb:.1f} MB em {DUCKDB_PATH.name}\n"
            f"[dim]Próximo passo:[/dim] [yellow]make validate[/yellow]",
            border_style=border,
        )
    )


# ============================================================
# Main
# ============================================================

def main() -> None:
    print_header()
    check_raw_files()
    results = load_all_tables()
    print_summary(results)

    if not all(r["status"] == "✅" for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
