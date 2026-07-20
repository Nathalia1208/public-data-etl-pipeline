import duckdb
from pathlib import Path

import duckdb

from config import (
    CURATED_PATH,
    DUCKDB_PATH,
    MUNICIPIOS_COMPLEMENTARES_PROCESSED_PATH,
    MUNICIPIOS_CONSOLIDADOS_PARQUET_PATH,
    MUNICIPIOS_IBGE_PROCESSED_PATH,
)
from logging_config import configurar_logger

logger = configurar_logger(__name__)

CURATED_PATH.mkdir(parents=True, exist_ok=True)

CURATED_PATH.mkdir(parents=True, exist_ok=True)


class LoadError(Exception):
    """Representa um erro ocorrido durante a etapa de carga."""


def validar_arquivo_entrada(
    caminho_arquivo: Path,
    descricao: str,
) -> None:
    """Valida se um arquivo de entrada existe e possui conteúdo.

    Args:
        caminho_arquivo: Caminho do arquivo que será validado.
        descricao: Descrição utilizada nas mensagens de erro.

    Raises:
        LoadError: Quando o arquivo não existe ou está vazio.
    """

    if not caminho_arquivo.exists():
        logger.error(
            "Arquivo de %s não encontrado: %s.",
            descricao,
            caminho_arquivo,
        )
        raise LoadError(
            f"O arquivo de {descricao} não foi encontrado: "
            f"{caminho_arquivo}"
        )

    if caminho_arquivo.stat().st_size == 0:
        logger.error(
            "Arquivo de %s está vazio: %s.",
            descricao,
            caminho_arquivo,
        )
        raise LoadError(
            f"O arquivo de {descricao} está vazio: {caminho_arquivo}"
        )


def converter_caminho_sql(caminho: Path) -> str:
    """Converte um caminho para um formato compatível com o DuckDB.

    Args:
        caminho: Caminho que será utilizado em uma instrução SQL.

    Returns:
        Caminho absoluto usando barras compatíveis com o DuckDB.
    """

    return caminho.resolve().as_posix()


def carregar_dados() -> dict[str, int]:
    """Carrega, integra e exporta os dados tratados.

    A função cria tabelas no DuckDB com os dados do IBGE e com os dados
    complementares, executa um LEFT JOIN por ``id_municipio``, cria uma
    tabela consolidada e exporta os dados em Parquet particionado por UF.

    Returns:
        Dicionário contendo as métricas da etapa de carga.

    Raises:
        LoadError: Quando ocorre falha na validação dos arquivos, conexão
            com o DuckDB, criação das tabelas, integração ou exportação.
    """

    caminho_municipios = MUNICIPIOS_IBGE_PROCESSED_PATH
    caminho_complementares = MUNICIPIOS_COMPLEMENTARES_PROCESSED_PATH

    logger.info("Iniciando etapa de carga dos dados.")
    logger.info("Banco DuckDB: %s.", DUCKDB_PATH)

    validar_arquivo_entrada(
        caminho_arquivo=caminho_municipios,
        descricao="municípios tratados do IBGE",
    )

    validar_arquivo_entrada(
        caminho_arquivo=caminho_complementares,
        descricao="municípios complementares tratados",
    )

    caminho_municipios_sql = converter_caminho_sql(caminho_municipios)
    caminho_complementares_sql = converter_caminho_sql(
        caminho_complementares
    )
    caminho_parquet_sql = converter_caminho_sql(MUNICIPIOS_CONSOLIDADOS_PARQUET_PATH)

    banco: duckdb.DuckDBPyConnection | None = None

    try:
        banco = duckdb.connect(str(DUCKDB_PATH))

        logger.info("Conexão com o DuckDB estabelecida com sucesso.")

        banco.execute(
            f"""
            CREATE OR REPLACE TABLE municipios_ibge AS
            SELECT *
            FROM read_csv_auto(
                '{caminho_municipios_sql}',
                HEADER = TRUE
            )
            """
        )

        total_municipios_ibge = banco.execute(
            """
            SELECT COUNT(*)
            FROM municipios_ibge
            """
        ).fetchone()[0]

        logger.info(
            "Tabela 'municipios_ibge' criada. Registros carregados: %s.",
            total_municipios_ibge,
        )

        banco.execute(
            f"""
            CREATE OR REPLACE TABLE municipios_complementares AS
            SELECT *
            FROM read_csv_auto(
                '{caminho_complementares_sql}',
                HEADER = TRUE
            )
            """
        )

        total_municipios_complementares = banco.execute(
            """
            SELECT COUNT(*)
            FROM municipios_complementares
            """
        ).fetchone()[0]

        logger.info(
            "Tabela 'municipios_complementares' criada. "
            "Registros carregados: %s.",
            total_municipios_complementares,
        )

        duplicados_ibge = banco.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT id_municipio
                FROM municipios_ibge
                GROUP BY id_municipio
                HAVING COUNT(*) > 1
            )
            """
        ).fetchone()[0]

        duplicados_complementares = banco.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT id_municipio
                FROM municipios_complementares
                GROUP BY id_municipio
                HAVING COUNT(*) > 1
            )
            """
        ).fetchone()[0]

        if duplicados_ibge > 0:
            logger.warning(
                "Foram encontrados %s IDs duplicados na tabela "
                "'municipios_ibge'.",
                duplicados_ibge,
            )

        if duplicados_complementares > 0:
            logger.warning(
                "Foram encontrados %s IDs duplicados na tabela "
                "'municipios_complementares'.",
                duplicados_complementares,
            )

        sem_correspondencia = banco.execute(
            """
            SELECT COUNT(*)
            FROM municipios_ibge AS ibge
            LEFT JOIN municipios_complementares AS complemento
                ON ibge.id_municipio = complemento.id_municipio
            WHERE complemento.id_municipio IS NULL
            """
        ).fetchone()[0]

        banco.execute(
            """
            CREATE OR REPLACE TABLE municipios_consolidados AS
            SELECT
                ibge.id_municipio,
                ibge.municipio,
                complemento.municipio_complementar,
                ibge.regiao_imediata,
                ibge.regiao_intermediaria,
                ibge.uf,
                ibge.sigla_uf,
                ibge.regiao,
                complemento.capital,
                complemento.codigo_uf,
                complemento.siafi_id,
                complemento.ddd,
                complemento.fuso_horario
            FROM municipios_ibge AS ibge
            LEFT JOIN municipios_complementares AS complemento
                ON ibge.id_municipio = complemento.id_municipio
            """
        )

        total_registros = banco.execute(
            """
            SELECT COUNT(*)
            FROM municipios_consolidados
            """
        ).fetchone()[0]

        logger.info(
            "Tabela 'municipios_consolidados' criada. "
            "Registros consolidados: %s.",
            total_registros,
        )

        if total_registros != total_municipios_ibge:
            logger.warning(
                "A quantidade de registros após o JOIN é diferente da "
                "quantidade original do IBGE. Antes: %s. Depois: %s.",
                total_municipios_ibge,
                total_registros,
            )

        if sem_correspondencia > 0:
            logger.warning(
                "%s município(s) do IBGE ficaram sem correspondência "
                "na base complementar.",
                sem_correspondencia,
            )
        else:
            logger.info(
                "Todos os municípios do IBGE possuem correspondência "
                "na base complementar."
            )

        banco.execute(
            f"""
            COPY municipios_consolidados
            TO '{caminho_parquet_sql}'
            (
                FORMAT PARQUET,
                PARTITION_BY (sigla_uf),
                OVERWRITE_OR_IGNORE TRUE
            )
            """
        )

        logger.info(
            "Arquivos Parquet exportados e particionados por UF em: %s.",
            MUNICIPIOS_CONSOLIDADOS_PARQUET_PATH,
        )

        logger.info("Etapa de carga concluída com sucesso.")

        return {
            "total_municipios_ibge": int(total_municipios_ibge),
            "total_municipios_complementares": int(
                total_municipios_complementares
            ),
            "total_registros_consolidados": int(total_registros),
            "sem_correspondencia": int(sem_correspondencia),
            "duplicados_ibge": int(duplicados_ibge),
            "duplicados_complementares": int(
                duplicados_complementares
            ),
        }

    except duckdb.Error as erro:
        logger.exception(
            "Erro durante uma operação no DuckDB."
        )
        raise LoadError(
            "Não foi possível concluir a carga dos dados no DuckDB."
        ) from erro

    except OSError as erro:
        logger.exception(
            "Erro de entrada ou saída durante a etapa de carga."
        )
        raise LoadError(
            "Não foi possível gravar o banco ou os arquivos Parquet."
        ) from erro

    except (TypeError, ValueError) as erro:
        logger.exception(
            "Erro de validação durante a etapa de carga."
        )
        raise LoadError(
            "Os dados não possuem o formato esperado para a carga."
        ) from erro

    finally:
        if banco is not None:
            banco.close()
            logger.info("Conexão com o DuckDB encerrada.")


if __name__ == "__main__":
    carregar_dados()