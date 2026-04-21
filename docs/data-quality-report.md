# 🛡️ Data Quality Report — Olist Analytics

![Quality Score](https://img.shields.io/badge/Quality%20Score-95.1%2F100-brightgreen)

> **Última execução:** 2026-04-21 17:12:32  
> **Total de testes:** 15  
> **Score geral:** 95.1 / 100

Este relatório é gerado automaticamente por `ingestion/validators.py`.
Não edite manualmente — execute `make validate` para atualizar.

---

## Coerência Temporal

| Teste | Severidade | Status | Detalhes |
|---|---|---|---|
| Aprovação antes da compra | MEDIUM | ✅ Pass | OK |
| Entrega antes da compra | HIGH | ✅ Pass | OK |
| Entrega ao cliente antes da transportadora | MEDIUM | ❌ Fail | 23 registros com problema |

## Completude

| Teste | Severidade | Status | Detalhes |
|---|---|---|---|
| Pedidos sem timestamp de compra | HIGH | ✅ Pass | OK |
| Clientes sem estado | MEDIUM | ✅ Pass | OK |

## Integridade Referencial

| Teste | Severidade | Status | Detalhes |
|---|---|---|---|
| Pedidos sem cliente associado | HIGH | ✅ Pass | OK |
| Itens de pedido sem produto cadastrado | HIGH | ✅ Pass | OK |
| Itens de pedido sem vendedor cadastrado | HIGH | ✅ Pass | OK |
| Itens de pedido sem pedido correspondente | HIGH | ✅ Pass | OK |
| Pagamentos sem pedido correspondente | HIGH | ✅ Pass | OK |

## Valores Anômalos

| Teste | Severidade | Status | Detalhes |
|---|---|---|---|
| Itens com preço negativo ou zerado | HIGH | ✅ Pass | OK |
| Itens com frete negativo | MEDIUM | ✅ Pass | OK |
| Pagamentos com valor negativo | HIGH | ✅ Pass | OK |
| Reviews com score fora de 1-5 | MEDIUM | ✅ Pass | OK |
| Produtos com peso negativo | LOW | ✅ Pass | OK |

---

## 📘 Como interpretar

- **HIGH**: problemas que invalidam análises (FKs quebradas, valores impossíveis).
- **MEDIUM**: inconsistências que merecem tratamento no dbt.
- **LOW**: avisos informativos, impacto mínimo.

Falhas não interrompem o pipeline — são documentadas aqui para serem
tratadas na camada de transformação (`dbt_olist/models/staging/`).
