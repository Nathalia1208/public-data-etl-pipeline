# Public Data ETL Pipeline

Pipeline ETL desenvolvido em Python para ingestão, transformação, integração e armazenamento de dados públicos brasileiros utilizando a API do IBGE, DuckDB e Parquet.

Este projeto foi desenvolvido com foco em demonstrar conhecimentos em Engenharia de Dados aplicando boas práticas de arquitetura, modularização, validação de dados, tratamento de erros, logging estruturado e armazenamento analítico.

---

# Objetivo

Construir um pipeline ETL completo capaz de:

- Extrair dados de múltiplas fontes públicas
- Transformar e padronizar os dados
- Integrar diferentes bases utilizando SQL
- Armazenar os dados em um banco analítico
- Exportar os dados em formato otimizado para Analytics
- Demonstrar boas práticas utilizadas em projetos reais de Engenharia de Dados

---

# Arquitetura do Pipeline

```text
                 API do IBGE (JSON)
                         │
                         │
                         ▼
                  ETAPA 1 - EXTRACT
                         │
                         │
CSV Complementar ─────────┘
                         │
                         ▼
                  Camada RAW
                         │
                         ▼
                ETAPA 2 - TRANSFORM
                         │
         ├────────────────────────────┐
         │                            │
 Normalização                Padronização
         │                            │
         └──────────────┬─────────────┘
                        ▼
                Camada PROCESSED
                        │
                        ▼
                 ETAPA 3 - LOAD
                        │
                        ▼
                   DuckDB
                        │
                 LEFT JOIN
                        │
                        ▼
             Tabela Consolidada
                        │
                        ▼
      Exportação Parquet Particionada
                        │
                        ▼
                Power BI / Analytics
```

---

# Estrutura do Projeto

```text
pipeline-etl-dados-publicos/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── curated/
│   └── etl.db
│
├── logs/
│   └── pipeline.log
│
├── src/
│   ├── config.py
│   ├── logging_config.py
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── main.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Fontes de Dados

## Fonte 1

**API Pública do IBGE**

Formato:

- JSON

Responsável por fornecer:

- Código do município
- Nome
- Região
- UF
- Região imediata
- Região intermediária

---

## Fonte 2

**CSV Público de Municípios Brasileiros**

Formato:

- CSV

Informações complementares:

- Código IBGE
- Capital
- Código UF
- Código SIAFI
- DDD
- Fuso horário

---

# Fluxo ETL

## Extract

- Consumo da API do IBGE
- Download da base complementar
- Validação das respostas
- Logging
- Tratamento de erros

---

## Transform

- Normalização do JSON
- Seleção das colunas
- Renomeação para padrão snake_case
- Validação dos arquivos
- Validação das colunas obrigatórias
- Conversão de tipos
- Validação de IDs

---

## Load

- Carregamento no DuckDB
- Criação das tabelas analíticas
- LEFT JOIN por `id_municipio`
- Validação da integridade do JOIN
- Exportação para Parquet
- Particionamento por UF

---

# Tecnologias Utilizadas

| Tecnologia | Finalidade |
|------------|------------|
| Python | Desenvolvimento do pipeline |
| Pandas | Manipulação de dados |
| Requests | Consumo da API |
| DuckDB | Banco analítico |
| SQL | Integração dos dados |
| Parquet | Armazenamento otimizado |
| Logging | Monitoramento da execução |

---

# Funcionalidades

- Extração de dados da API do IBGE
- Download automático da base complementar
- Tratamento robusto de erros
- Logging estruturado
- Validação dos dados
- Padronização dos esquemas
- Integração entre múltiplas fontes
- Banco analítico DuckDB
- Exportação em Parquet
- Particionamento por UF
- Métricas da execução

---

# Exemplo de Logs

```text
2026-07-20 12:07:22 | INFO | ETAPA 1/3 - EXTRAÇÃO | INÍCIO

2026-07-20 12:07:25 | INFO | ETAPA 2/3 - TRANSFORMAÇÃO | CONCLUÍDA

2026-07-20 12:07:26 | INFO | ETAPA 3/3 - CARGA | CONCLUÍDA

2026-07-20 12:07:26 | INFO | Pipeline ETL concluído com sucesso.
```

---

# Como executar

Clone o repositório

```bash
git clone https://github.com/Nathalia1208/public-data-etl-pipeline.git
```

Entre na pasta

```bash
cd public-data-etl-pipeline
```

Instale as dependências

```bash
pip install -r requirements.txt
```

Execute o pipeline

```bash
python src/main.py
```

---

# Saídas Geradas

Após a execução serão criados:

```text
data/raw/

data/processed/

data/etl.db

data/curated/

logs/pipeline.log
```

---

# Skills Demonstrated

## Engenharia de Dados

- ETL
- Data Integration
- Data Validation
- Data Modeling
- Data Quality
- SQL Analytics

## Desenvolvimento

- Python
- Modularização
- Logging
- Tratamento de Erros
- Organização de Código
- Configuração Centralizada

## Armazenamento

- DuckDB
- Parquet

---

# Roadmap

## ✅ v1.0

- Pipeline ETL funcional
- DuckDB
- Exportação Parquet

## ✅ v1.1

- Logging estruturado
- Tratamento robusto de erros
- Arquitetura modular
- Configuração centralizada
- Validação dos dados
- Métricas da execução
- Padronização dos logs

## 🚧 v1.2

- Configuração via `.env`
- `.env.example`
- Configuração desacoplada do código

## Planejamento futuro

- Testes automatizados com Pytest
- Docker
- GitHub Actions
- Incremental Load
- Data Quality
- Airflow
- Dashboard Power BI

---

# Licença

Projeto desenvolvido para fins de estudo, demonstração de portfólio e aprendizado em Engenharia de Dados.
