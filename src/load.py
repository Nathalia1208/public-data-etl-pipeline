import duckdb
from pathlib import Path

PROCESSED_PATH = Path("data/processed")
CURATED_PATH = Path("data/curated")

CURATED_PATH.mkdir(parents=True, exist_ok=True)


def carregar_dados():
    banco = duckdb.connect("data/etl.db")

    caminho_municipios = PROCESSED_PATH / "municipios_tratados.csv"
    caminho_populacao = PROCESSED_PATH / "populacao_tratada.csv"

    banco.execute(f"""
        CREATE OR REPLACE TABLE municipios AS
        SELECT *
        FROM read_csv_auto('{caminho_municipios}')
    """)

    print("Tabela municipios criada no DuckDB!")

    banco.execute(f"""
        CREATE OR REPLACE TABLE populacao AS
        SELECT *
        FROM read_csv_auto('{caminho_populacao}')
    """)

    print("Tabela populacao criada no DuckDB!")

    resultado_join = banco.execute("""
        SELECT
            m.id_municipio,
            m.municipio,
            m.sigla_uf,
            m.uf,
            p.capital,
            p.ddd,
            p.fuso_horario
        FROM municipios m
        LEFT JOIN populacao p
            ON m.id_municipio = p.id_municipio
        LIMIT 20
    """).fetchdf()

    print("\nResultado do JOIN:")
    print(resultado_join)

    banco.execute(f"""
        CREATE OR REPLACE TABLE municipios_com_populacao AS
        SELECT
            m.id_municipio,
            m.municipio,
            m.sigla_uf,
            m.uf,
            m.regiao,
            p.capital,
            p.codigo_uf,
            p.siafi_id,
            p.ddd,
            p.fuso_horario
        FROM municipios m
        LEFT JOIN populacao p
            ON m.id_municipio = p.id_municipio
    """)

    print("\nTabela municipios_com_populacao criada!")

    banco.execute(f"""
        COPY municipios_com_populacao
        TO '{CURATED_PATH}/municipios_com_populacao_particionado'
        (
            FORMAT PARQUET,
            PARTITION_BY (sigla_uf),
            OVERWRITE_OR_IGNORE TRUE
        )
    """)

    print("\nParquet particionado com JOIN criado com sucesso!")

    banco.close()


if __name__ == "__main__":
    carregar_dados()