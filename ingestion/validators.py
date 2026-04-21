"""
🛡️  Olist Analytics — Validadores de Qualidade de Dados
=========================================================
Executa testes de qualidade contra o DuckDB e gera relatório executivo.

Categorias de testes:
    1. Integridade referencial (FKs órfãs)
    2. Coerência temporal (ordem de timestamps)
    3. Valores anômalos (negativos, ranges inválidos)
    4. Completude (% de nulos por coluna crítica)

Uso:
    python ingestion/validators.py
    # ou
    make validate
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

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
DUCKDB_PATH = Path(
    os.getenv("DUCKDB_PATH", PROJECT_ROOT / "data" / "warehouse" / "olist.duckdb")
)
REPORT_PATH = PROJECT_ROOT / "docs" / "data-quality-report.md"

console = Console()


# ============================================================
# Definição dos testes
# ============================================================

@dataclass
class TestResult:
    category: str
    name: str
    passed: bool
    details: str
    severity: str = "medium"  # low | medium | high
    affected_rows: int = 0


@dataclass
class QualitySuite:
    results: list[TestResult] = field(default_factory=list)

    def add(self, result: TestResult) -> None:
        self.results.append(result)

    def score(self) -> float:
        """Score de 0 a 100 baseado na proporção de testes passados,
        ponderados pela severidade."""
        if not self.results:
            return 0.0

        weights = {"low": 1, "medium": 3, "high": 5}
        total_weight = sum(weights[r.severity] for r in self.results)
        passed_weight = sum(
            weights[r.severity] for r in self.results if r.passed
        )
        return round(100 * passed_weight / total_weight, 1)


# ============================================================
# Definição dos testes de qualidade
# ============================================================

# Cada teste é uma tupla: (categoria, nome, query, severidade)
# Query deve retornar a contagem de REGISTROS COM PROBLEMA.
# Se retornar 0, o teste passou.

QUALITY_TESTS: list[tuple[str, str, str, str]] = [

    # ----- Integridade Referencial (FKs) -----
    (
        "Integridade Referencial",
        "Pedidos sem cliente associado",
        """
        SELECT COUNT(*) FROM raw.orders o
        LEFT JOIN raw.customers c ON o.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
        """,
        "high"
    ),
    (
        "Integridade Referencial",
        "Itens de pedido sem produto cadastrado",
        """
        SELECT COUNT(*) FROM raw.order_items oi
        LEFT JOIN raw.products p ON oi.product_id = p.product_id
        WHERE p.product_id IS NULL
        """,
        "high"
    ),
    (
        "Integridade Referencial",
        "Itens de pedido sem vendedor cadastrado",
        """
        SELECT COUNT(*) FROM raw.order_items oi
        LEFT JOIN raw.sellers s ON oi.seller_id = s.seller_id
        WHERE s.seller_id IS NULL
        """,
        "high"
    ),
    (
        "Integridade Referencial",
        "Itens de pedido sem pedido correspondente",
        """
        SELECT COUNT(*) FROM raw.order_items oi
        LEFT JOIN raw.orders o ON oi.order_id = o.order_id
        WHERE o.order_id IS NULL
        """,
        "high"
    ),
    (
        "Integridade Referencial",
        "Pagamentos sem pedido correspondente",
        """
        SELECT COUNT(*) FROM raw.order_payments op
        LEFT JOIN raw.orders o ON op.order_id = o.order_id
        WHERE o.order_id IS NULL
        """,
        "high"
    ),

    # ----- Coerência Temporal -----
    (
        "Coerência Temporal",
        "Aprovação antes da compra",
        """
        SELECT COUNT(*) FROM raw.orders
        WHERE order_approved_at < order_purchase_timestamp
        """,
        "medium"
    ),
    (
        "Coerência Temporal",
        "Entrega antes da compra",
        """
        SELECT COUNT(*) FROM raw.orders
        WHERE order_delivered_customer_date < order_purchase_timestamp
        """,
        "high"
    ),
    (
        "Coerência Temporal",
        "Entrega ao cliente antes da transportadora",
        """
        SELECT COUNT(*) FROM raw.orders
        WHERE order_delivered_customer_date < order_delivered_carrier_date
        """,
        "medium"
    ),

    # ----- Valores Anômalos -----
    (
        "Valores Anômalos",
        "Itens com preço negativo ou zerado",
        """
        SELECT COUNT(*) FROM raw.order_items
        WHERE price <= 0
        """,
        "high"
    ),
    (
        "Valores Anômalos",
        "Itens com frete negativo",
        """
        SELECT COUNT(*) FROM raw.order_items
        WHERE freight_value < 0
        """,
        "medium"
    ),
    (
        "Valores Anômalos",
        "Pagamentos com valor negativo",
        """
        SELECT COUNT(*) FROM raw.order_payments
        WHERE payment_value < 0
        """,
        "high"
    ),
    (
        "Valores Anômalos",
        "Reviews com score fora de 1-5",
        """
        SELECT COUNT(*) FROM raw.order_reviews
        WHERE review_score NOT BETWEEN 1 AND 5
        """,
        "medium"
    ),
    (
        "Valores Anômalos",
        "Produtos com peso negativo",
        """
        SELECT COUNT(*) FROM raw.products
        WHERE product_weight_g < 0
        """,
        "low"
    ),

    # ----- Completude -----
    (
        "Completude",
        "Pedidos sem timestamp de compra",
        """
        SELECT COUNT(*) FROM raw.orders
        WHERE order_purchase_timestamp IS NULL
        """,
        "high"
    ),
    (
        "Completude",
        "Clientes sem estado",
        """
        SELECT COUNT(*) FROM raw.customers
        WHERE customer_state IS NULL OR customer_state = ''
        """,
        "medium"
    ),
]


# ============================================================
# Execução
# ============================================================

def print_header() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]🛡️  Olist Analytics — Data Quality Suite[/bold cyan]\n"
            f"[dim]DuckDB:[/dim] {DUCKDB_PATH}\n"
            f"[dim]Testes a executar:[/dim] {len(QUALITY_TESTS)}",
            border_style="cyan",
        )
    )


def run_tests(conn: duckdb.DuckDBPyConnection) -> QualitySuite:
    """Executa todos os testes e coleta os resultados."""
    suite = QualitySuite()

    current_category = ""
    for category, name, query, severity in QUALITY_TESTS:
        if category != current_category:
            console.print(f"\n[bold cyan]▸ {category}[/bold cyan]")
            current_category = category

        try:
            affected = conn.execute(query).fetchone()[0]
            passed = affected == 0

            if passed:
                console.print(f"  [green]✅ {name}[/green]")
                details = "OK"
            else:
                icon = "❌" if severity == "high" else "⚠️ "
                color = "red" if severity == "high" else "yellow"
                console.print(
                    f"  [{color}]{icon} {name}: {affected:,} registros[/{color}]"
                )
                details = f"{affected:,} registros com problema"

            suite.add(TestResult(
                category=category,
                name=name,
                passed=passed,
                details=details,
                severity=severity,
                affected_rows=affected,
            ))
        except Exception as e:
            console.print(f"  [red]💥 {name}: erro - {e}[/red]")
            suite.add(TestResult(
                category=category,
                name=name,
                passed=False,
                details=f"Erro de execução: {e}",
                severity=severity,
            ))

    return suite


def print_summary(suite: QualitySuite) -> None:
    """Mostra resumo final no terminal."""
    console.print("\n[cyan]📊 Resumo por severidade:[/cyan]\n")

    table = Table(show_lines=False)
    table.add_column("Severidade", style="cyan")
    table.add_column("Total", justify="right")
    table.add_column("Passou", justify="right", style="green")
    table.add_column("Falhou", justify="right", style="red")

    for sev in ["high", "medium", "low"]:
        subset = [r for r in suite.results if r.severity == sev]
        passed = sum(1 for r in subset if r.passed)
        failed = len(subset) - passed
        table.add_row(
            sev.upper(),
            str(len(subset)),
            str(passed),
            str(failed) if failed else "0",
        )

    console.print(table)

    score = suite.score()
    if score >= 90:
        border, icon = "green", "🎉"
    elif score >= 70:
        border, icon = "yellow", "⚠️ "
    else:
        border, icon = "red", "❌"

    console.print(
        Panel.fit(
            f"[bold]{icon} Data Quality Score: {score} / 100[/bold]\n\n"
            f"[dim]Relatório exportado em:[/dim] {REPORT_PATH.relative_to(PROJECT_ROOT)}",
            border_style=border,
        )
    )


def export_markdown_report(suite: QualitySuite) -> None:
    """Exporta um relatório em Markdown pra versionar no Git."""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    score = suite.score()
    badge_color = "brightgreen" if score >= 90 else "yellow" if score >= 70 else "red"

    lines = [
        "# 🛡️ Data Quality Report — Olist Analytics",
        "",
        f"![Quality Score](https://img.shields.io/badge/Quality%20Score-{score}%2F100-{badge_color})",
        "",
        f"> **Última execução:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"> **Total de testes:** {len(suite.results)}  ",
        f"> **Score geral:** {score} / 100",
        "",
        "Este relatório é gerado automaticamente por `ingestion/validators.py`.",
        "Não edite manualmente — execute `make validate` para atualizar.",
        "",
        "---",
        "",
    ]

    # Agrupa por categoria
    categories = sorted(set(r.category for r in suite.results))
    for cat in categories:
        lines.append(f"## {cat}")
        lines.append("")
        lines.append("| Teste | Severidade | Status | Detalhes |")
        lines.append("|---|---|---|---|")

        for r in suite.results:
            if r.category != cat:
                continue
            status = "✅ Pass" if r.passed else "❌ Fail"
            lines.append(
                f"| {r.name} | {r.severity.upper()} | {status} | {r.details} |"
            )
        lines.append("")

    # Interpretação
    lines.extend([
        "---",
        "",
        "## 📘 Como interpretar",
        "",
        "- **HIGH**: problemas que invalidam análises (FKs quebradas, valores impossíveis).",
        "- **MEDIUM**: inconsistências que merecem tratamento no dbt.",
        "- **LOW**: avisos informativos, impacto mínimo.",
        "",
        "Falhas não interrompem o pipeline — são documentadas aqui para serem",
        "tratadas na camada de transformação (`dbt_olist/models/staging/`).",
        "",
    ])

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


# ============================================================
# Main
# ============================================================

def main() -> None:
    print_header()

    if not DUCKDB_PATH.exists():
        console.print(
            f"[bold red]❌ DuckDB não encontrado em {DUCKDB_PATH}[/bold red]\n"
            "   Execute primeiro: [yellow]make load[/yellow]"
        )
        sys.exit(1)

    with duckdb.connect(str(DUCKDB_PATH), read_only=True) as conn:
        suite = run_tests(conn)

    export_markdown_report(suite)
    print_summary(suite)

    # Falha apenas se houver erro HIGH não resolvido
    high_failures = [r for r in suite.results if not r.passed and r.severity == "high"]
    if high_failures:
        console.print(
            f"\n[bold red]⚠️  {len(high_failures)} problema(s) HIGH detectado(s). "
            "Revise antes de prosseguir.[/bold red]"
        )
        # Não faz sys.exit aqui pois queremos o relatório mesmo com falhas


if __name__ == "__main__":
    main()
