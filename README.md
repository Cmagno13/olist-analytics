<h1 align="center">
  🛒 Olist Analytics — Full Cycle BI Platform
</h1>

<p align="center">
  <b>Da ingestão à decisão executiva: um case completo de Business Intelligence<br/>
  em cima de 100k pedidos reais de e-commerce brasileiro.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Em%20desenvolvimento-yellow?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Dataset-Olist%20%7C%20100k%20pedidos-20A6C9?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Stack-Python%20%7C%20dbt%20%7C%20DuckDB%20%7C%20Superset-FF4B4B?style=for-the-badge"/>
</p>

<p align="center">
  <a href="#-o-problema-de-negócio">Problema</a> •
  <a href="#-perguntas-que-esse-projeto-responde">Perguntas</a> •
  <a href="#️-arquitetura">Arquitetura</a> •
  <a href="#-principais-insights">Insights</a> •
  <a href="#-como-executar">Executar</a> •
  <a href="#-sobre-o-autor">Autor</a>
</p>

---

## 🎯 O problema de negócio

> *"Tenho uma loja online com milhares de pedidos, vendedores espalhados pelo Brasil e clientes que muitas vezes não voltam. Preciso entender **onde está meu dinheiro, onde está meu problema e onde está minha oportunidade** — mas só tenho planilhas desencontradas e relatórios que ninguém lê."*

Esse é o cenário típico de qualquer e-commerce de pequeno ou médio porte no Brasil.

**Este projeto simula uma consultoria completa de BI** para um marketplace real (Olist, fundado no Paraná, vendido à VTEX em 2024), mostrando como transformar **dados brutos em decisão executiva** — do pipeline de ingestão ao PDF de recomendação estratégica.

---

## 🧩 Perguntas que esse projeto responde

| # | Pergunta de negócio | Impacto potencial |
|---|---|---|
| 1 | **Quais estados e regiões geram mais faturamento e qual o ticket médio por região?** | Orientar investimento em logística e mídia regional |
| 2 | **Qual categoria de produto combina alto volume + alta margem + boa avaliação?** | Definir o mix de produtos a priorizar |
| 3 | **Qual o tempo médio entre pedido e entrega — e como isso impacta a nota do cliente?** | Identificar gargalos logísticos que geram churn |
| 4 | **Quantos clientes voltam a comprar? Qual a taxa real de retenção?** | Redirecionar verba de aquisição → retenção |
| 5 | **Quais vendedores (sellers) são mais eficientes e quais arrastam a reputação?** | Curadoria e gestão de parceiros |

> 💡 Cada pergunta é respondida no dashboard executivo **com dado real**, não mock.

---

## 🏗️ Arquitetura

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│   Olist     │    │   Python     │    │   DuckDB    │    │     dbt      │    │   Superset   │
│   Dataset   │──▶│  Ingestion   │──▶│ Data Warehouse│──▶│ Transformation│──▶│  Dashboards  │
│  (9 CSVs)   │    │  + Validação │    │  (Star Schema)│    │staging ▶ marts│    │  + Looker    │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘    └──────────────┘
                                                                                       │
                                                                                       ▼
                                                                              ┌──────────────┐
                                                                              │   📊 PDF     │
                                                                              │  Executivo   │
                                                                              └──────────────┘
```

**Decisões arquiteturais (ADRs resumidos):**

- **DuckDB** como Data Warehouse local → performance OLAP sem custo de cloud, ideal para datasets até dezenas de GB
- **dbt** para transformação → camadas `staging → intermediate → marts`, testes e lineage automáticos
- **Star Schema** como modelagem → facilita consumo por BI e melhora performance de queries analíticas
- **Superset** como camada principal de visualização → aproveita expertise do autor e permite personalização via CSS
- **Looker Studio** como camada secundária → link público que qualquer cliente abre sem login

> 📄 Documentação detalhada em [`docs/arquitetura.md`](./docs/arquitetura.md)

---

## 🛠️ Stack Técnica

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/DuckDB-FFF000?style=flat-square&logo=duckdb&logoColor=black"/>
  <img src="https://img.shields.io/badge/dbt-FF694B?style=flat-square&logo=dbt&logoColor=white"/>
  <img src="https://img.shields.io/badge/Apache%20Superset-20A6C9?style=flat-square&logo=apachesuperset&logoColor=white"/>
  <img src="https://img.shields.io/badge/Looker%20Studio-4285F4?style=flat-square&logo=looker&logoColor=white"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white"/>
  <img src="https://img.shields.io/badge/SQL-003B57?style=flat-square&logo=postgresql&logoColor=white"/>
</p>

---

## 📸 Preview do projeto

> 🔧 *Imagens/GIFs serão adicionados conforme os dashboards forem construídos.*

<p align="center">
  <em>[ Em breve: GIF do dashboard executivo em Superset ]</em>
</p>

<p align="center">
  <em>[ Em breve: print do Looker Studio público ]</em>
</p>

---

## 📊 Principais insights

> 🔧 *Esta seção será preenchida ao final do Sprint 3, com os achados reais da análise.*

- 💡 **[Placeholder]** — Descoberta sobre concentração geográfica de faturamento
- 💡 **[Placeholder]** — Análise de margem × volume × avaliação por categoria
- 💡 **[Placeholder]** — Correlação entre tempo de entrega e nota do cliente
- 💡 **[Placeholder]** — Taxa de recompra e perfil do cliente recorrente
- 💡 **[Placeholder]** — Ranking de eficiência de vendedores

📄 Análise executiva completa no PDF: [`docs/insights-executivos.pdf`](./docs/insights-executivos.pdf)

---

## 📂 Estrutura do projeto

```
olist-analytics/
├── 📄 README.md                          ← Este arquivo
├── 📁 docs/
│   ├── arquitetura.md                    ← Decisões arquiteturais (ADRs)
│   ├── insights-executivos.pdf           ← Relatório de consultoria
│   ├── dicionario-de-dados.md            ← Metadados das tabelas
│   └── images/                           ← Prints, GIFs e diagramas
├── 📁 data/
│   ├── raw/                              ← CSVs originais do Olist
│   └── warehouse/                        ← Arquivo DuckDB (.db)
├── 📁 ingestion/
│   ├── download_data.py                  ← Download automatizado do dataset
│   ├── load_to_duckdb.py                 ← Carga inicial CSV → DuckDB
│   └── validators.py                     ← Testes de integridade
├── 📁 dbt_olist/
│   ├── dbt_project.yml
│   ├── models/
│   │   ├── staging/                      ← Limpeza e padronização
│   │   ├── intermediate/                 ← Junções e agregações
│   │   └── marts/                        ← Star schema final
│   ├── tests/                            ← Testes de qualidade
│   └── macros/                           ← Funções reutilizáveis
├── 📁 dashboards/
│   ├── superset/
│   │   ├── export.zip                    ← Dashboards exportados
│   │   └── preview.gif                   ← Demo animada
│   └── looker_studio.md                  ← Link público + instruções
├── 📁 notebooks/
│   ├── 01_eda.ipynb                      ← Análise exploratória
│   ├── 02_rfm_analysis.ipynb             ← Segmentação de clientes
│   └── 03_cohort_retention.ipynb         ← Retenção por coorte
└── 📁 infra/
    ├── docker-compose.yml                ← Superset + dependências
    ├── requirements.txt                  ← Pacotes Python
    └── Makefile                          ← Atalhos de execução
```

---

## 🚀 Como executar

> 🔧 *Instruções detalhadas serão finalizadas ao fim do desenvolvimento.*

### Pré-requisitos

- Python 3.11+
- Docker & Docker Compose
- Git

### Passo a passo (rápido)

```bash
# 1. Clone o repositório
git clone https://github.com/Cmagno13/olist-analytics.git
cd olist-analytics

# 2. Instale dependências Python
pip install -r infra/requirements.txt

# 3. Baixe o dataset e carregue no DuckDB
python ingestion/download_data.py
python ingestion/load_to_duckdb.py

# 4. Rode as transformações dbt
cd dbt_olist
dbt deps
dbt build

# 5. Suba o Superset (opcional — para dashboards locais)
cd ../infra
docker compose up -d
# Superset disponível em http://localhost:8088
```

---

## 🗺️ Roadmap

- [x] **Sprint 0** — Planejamento e definição de escopo
- [x] **Sprint 1** — Ingestão, modelagem dimensional e carga no DuckDB
- [ ] **Sprint 2** — Transformações dbt (staging → marts) + testes de qualidade
- [ ] **Sprint 3** — Dashboards (Superset + Looker) e PDF executivo

---

## 📚 Sobre o dataset

**Fonte oficial:** [Brazilian E-Commerce Public Dataset by Olist — Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

- **~100.000 pedidos** realizados entre 2016 e 2018
- **9 tabelas relacionais**: pedidos, itens, produtos, vendedores, clientes, pagamentos, avaliações, geolocalização e categorias
- Dados **reais e anonimizados**, disponibilizados pela própria Olist sob licença CC BY-NC-SA 4.0

---

## 👤 Sobre o autor

<p>
  <b>Carlos Magno Ribeiro</b><br/>
  Senior Business Intelligence & Data Analytics Specialist<br/>
  <a href="https://github.com/Cmagno13">GitHub</a> ·
  <a href="https://www.linkedin.com/in/carlos-magnoribeiro-a6b7b043">LinkedIn</a> ·
  <a href="mailto:carlos.magno23@hotmail.com">E-mail</a> ·
  <a href="https://www.cmagnoribeiro.com/">Blog</a>
</p>

> 💼 Estou **aberto a projetos freelance** e **consultoria remota** em Apache Superset, modelagem analítica, pipelines ETL e dashboards executivos.
> Se esse case é o tipo de trabalho que faria sentido para o seu negócio, me chama no LinkedIn.

---

<p align="center">
  <i>"Dados sem contexto são ruído. Dados com contexto são decisão."</i>
</p>
