"""
📥 Olist Analytics — Download do Dataset
==========================================
Baixa o Brazilian E-Commerce Public Dataset da Olist direto do Kaggle,
extrai os 9 CSVs e valida a integridade dos arquivos.

Uso:
    python ingestion/download_data.py
    # ou
    make download
"""

from __future__ import annotations

import os
import sys
import zipfile
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# ============================================================
# Configuração
# ============================================================

# Carrega variáveis de ambiente do .env (se existir)
load_dotenv()

# Raiz do projeto (dois níveis acima deste arquivo)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Pasta onde os CSVs brutos serão salvos
RAW_DATA_PATH = Path(os.getenv("RAW_DATA_PATH", PROJECT_ROOT / "data" / "raw"))

# Identificador do dataset no Kaggle (formato: "owner/dataset-slug")
KAGGLE_DATASET = "olistbr/brazilian-ecommerce"

# Lista dos 9 CSVs esperados após extração
EXPECTED_FILES = [
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
]

# Console do Rich para output colorido e estruturado
console = Console()


# ============================================================
# Funções
# ============================================================

def print_header() -> None:
    """Imprime cabeçalho bonito no terminal."""
    console.print(
        Panel.fit(
            "[bold cyan]🛒 Olist Analytics — Download do Dataset[/bold cyan]\n"
            f"[dim]Dataset:[/dim] {KAGGLE_DATASET}\n"
            f"[dim]Destino:[/dim] {RAW_DATA_PATH}",
            border_style="cyan",
        )
    )


def check_kaggle_credentials() -> None:
    """Verifica se a credencial do Kaggle existe e está acessível."""
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"

    if not kaggle_json.exists():
        console.print(
            "[bold red]❌ Credencial do Kaggle não encontrada![/bold red]\n"
            f"   Esperado em: [yellow]{kaggle_json}[/yellow]\n\n"
            "   Como configurar:\n"
            "   1. Acesse https://www.kaggle.com/settings/account\n"
            "   2. Na seção 'Legacy API Credentials', clique em 'Create Legacy API Key'\n"
            "   3. Copie o kaggle.json para ~/.kaggle/\n"
            "   4. Execute: chmod 600 ~/.kaggle/kaggle.json"
        )
        sys.exit(1)

    # Valida permissão (deve ser 600)
    mode = oct(kaggle_json.stat().st_mode)[-3:]
    if mode != "600":
        console.print(
            f"[yellow]⚠️  Permissão de {kaggle_json} é {mode}, ajustando para 600...[/yellow]"
        )
        kaggle_json.chmod(0o600)

    console.print("[green]✅ Credencial do Kaggle validada[/green]")


def download_dataset() -> Path:
    """Baixa o dataset do Kaggle e retorna o caminho do ZIP."""
    # Import dentro da função para só autenticar quando necessário
    import kaggle

    console.print(f"\n[cyan]⬇️  Baixando [bold]{KAGGLE_DATASET}[/bold]...[/cyan]")

    # Garante que a pasta de destino existe
    RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)

    # Autentica e baixa
    kaggle.api.authenticate()
    kaggle.api.dataset_download_files(
        dataset=KAGGLE_DATASET,
        path=str(RAW_DATA_PATH),
        unzip=False,  # vamos extrair manualmente pra ter mais controle
        quiet=False,
    )

    # Nome do ZIP baixado (formato padrão do Kaggle)
    zip_filename = KAGGLE_DATASET.split("/")[-1] + ".zip"
    zip_path = RAW_DATA_PATH / zip_filename

    if not zip_path.exists():
        console.print(f"[bold red]❌ ZIP não encontrado em {zip_path}[/bold red]")
        sys.exit(1)

    size_mb = zip_path.stat().st_size / (1024 * 1024)
    console.print(f"[green]✅ Download concluído:[/green] {zip_path.name} ({size_mb:.1f} MB)")

    return zip_path


def extract_zip(zip_path: Path) -> None:
    """Extrai o ZIP na pasta data/raw/."""
    console.print(f"\n[cyan]📦 Extraindo [bold]{zip_path.name}[/bold]...[/cyan]")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(RAW_DATA_PATH)

    # Remove o ZIP após extração para não ocupar espaço
    zip_path.unlink()
    console.print("[green]✅ Extração concluída e ZIP removido[/green]")


def validate_files() -> bool:
    """Valida que todos os 9 CSVs esperados existem e lista detalhes."""
    console.print("\n[cyan]🔍 Validando integridade dos arquivos...[/cyan]\n")

    table = Table(title="📂 Arquivos Baixados", show_lines=False)
    table.add_column("Arquivo", style="cyan")
    table.add_column("Tamanho", justify="right", style="green")
    table.add_column("Status", justify="center")

    all_ok = True

    for filename in EXPECTED_FILES:
        file_path = RAW_DATA_PATH / filename

        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            size_str = f"{size_mb:.2f} MB" if size_mb >= 0.01 else f"{file_path.stat().st_size / 1024:.1f} KB"
            table.add_row(filename, size_str, "[green]✅[/green]")
        else:
            table.add_row(filename, "—", "[red]❌[/red]")
            all_ok = False

    console.print(table)
    return all_ok


def print_summary(success: bool) -> None:
    """Imprime resumo final."""
    if success:
        console.print(
            Panel.fit(
                "[bold green]🎉 Download concluído com sucesso![/bold green]\n\n"
                f"[dim]Os CSVs estão em:[/dim] {RAW_DATA_PATH}\n"
                "[dim]Próximo passo:[/dim] [yellow]make load[/yellow] (carregar no DuckDB)",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel.fit(
                "[bold red]❌ Alguns arquivos estão faltando.[/bold red]\n"
                "Execute o script novamente ou verifique manualmente a pasta data/raw/.",
                border_style="red",
            )
        )
        sys.exit(1)


# ============================================================
# Main
# ============================================================

def main() -> None:
    print_header()
    check_kaggle_credentials()
    zip_path = download_dataset()
    extract_zip(zip_path)
    success = validate_files()
    print_summary(success)


if __name__ == "__main__":
    main()
