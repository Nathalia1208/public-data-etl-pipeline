import json
from pathlib import Path

import pandas as pd

from config import (
    MUNICIPIOS_COMPLEMENTARES_PROCESSED_PATH,
    MUNICIPIOS_COMPLEMENTARES_RAW_PATH,
    MUNICIPIOS_IBGE_PROCESSED_PATH,
    MUNICIPIOS_IBGE_RAW_PATH,
    PROCESSED_PATH,
)
from logging_config import configurar_logger


logger = configurar_logger(__name__)

PROCESSED_PATH.mkdir(parents=True, exist_ok=True)


def validar_arquivo(caminho_arquivo: Path, descricao: str) -> None:
    """Valida se um arquivo existe e possui conteúdo.

    Args:
        caminho_arquivo: Caminho do arquivo que será validado.
        descricao: Descrição do arquivo usada nas mensagens de log.

    Raises:
        FileNotFoundError: Quando o arquivo não existe.
        ValueError: Quando o arquivo está vazio.
    """

    if not caminho_arquivo.exists():
        raise FileNotFoundError(
            f"O arquivo de {descricao} não foi encontrado: {caminho_arquivo}"
        )

    if caminho_arquivo.stat().st_size == 0:
        raise ValueError(
            f"O arquivo de {descricao} está vazio: {caminho_arquivo}"
        )


def validar_colunas(
    dataframe: pd.DataFrame,
    colunas_obrigatorias: list[str],
    descricao: str,
) -> None:
    """Valida a presença das colunas obrigatórias em um DataFrame.

    Args:
        dataframe: DataFrame que será validado.
        colunas_obrigatorias: Lista de colunas esperadas.
        descricao: Descrição da base usada nas mensagens de log.

    Raises:
        ValueError: Quando uma ou mais colunas obrigatórias estão ausentes.
    """

    colunas_ausentes = [
        coluna
        for coluna in colunas_obrigatorias
        if coluna not in dataframe.columns
    ]

    if colunas_ausentes:
        raise ValueError(
            f"Colunas obrigatórias ausentes em {descricao}: "
            f"{colunas_ausentes}"
        )


def transformar_municipios() -> Path:
    caminho_json = MUNICIPIOS_IBGE_RAW_PATH
    caminho_saida = MUNICIPIOS_IBGE_PROCESSED_PATH

    logger.info("Iniciando transformação dos municípios do IBGE.")

    try:
        validar_arquivo(
            caminho_arquivo=caminho_json,
            descricao="municípios do IBGE",
        )

        with caminho_json.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        if not isinstance(dados, list):
            raise ValueError(
                "O JSON de municípios do IBGE não possui o formato esperado."
            )

        if not dados:
            raise ValueError(
                "O JSON de municípios do IBGE não contém registros."
            )

        dataframe = pd.json_normalize(dados)

        if dataframe.empty:
            raise ValueError(
                "A normalização do JSON do IBGE gerou um DataFrame vazio."
            )

        colunas_desejadas = {
            "id": "id_municipio",
            "nome": "municipio",
            "regiao-imediata.nome": "regiao_imediata",
            "regiao-imediata.regiao-intermediaria.nome": (
                "regiao_intermediaria"
            ),
            "regiao-imediata.regiao-intermediaria.UF.nome": "uf",
            "regiao-imediata.regiao-intermediaria.UF.sigla": "sigla_uf",
            "regiao-imediata.regiao-intermediaria.UF.regiao.nome": (
                "regiao"
            ),
        }

        validar_colunas(
            dataframe=dataframe,
            colunas_obrigatorias=list(colunas_desejadas.keys()),
            descricao="JSON de municípios do IBGE",
        )

        dataframe = dataframe[list(colunas_desejadas.keys())].copy()
        dataframe = dataframe.rename(columns=colunas_desejadas)

        dataframe["id_municipio"] = pd.to_numeric(
            dataframe["id_municipio"],
            errors="coerce",
        ).astype("Int64")

        ids_nulos = int(dataframe["id_municipio"].isna().sum())

        if ids_nulos > 0:
            raise ValueError(
                f"Foram encontrados {ids_nulos} códigos de município inválidos."
            )

        registros_duplicados = int(
            dataframe["id_municipio"].duplicated().sum()
        )

        if registros_duplicados > 0:
            logger.warning(
                "Foram encontrados %s códigos de município duplicados "
                "na base do IBGE.",
                registros_duplicados,
            )

        dataframe.to_csv(
            caminho_saida,
            index=False,
            encoding="utf-8",
        )

        logger.info(
            "Transformação dos municípios concluída. Registros tratados: %s.",
            len(dataframe),
        )
        logger.info("Arquivo salvo em: %s.", caminho_saida)

        return caminho_saida

    except FileNotFoundError as erro:
        logger.error("%s", erro)
        raise RuntimeError(
            "O arquivo de municípios do IBGE não está disponível para "
            "transformação."
        ) from erro

    except json.JSONDecodeError as erro:
        logger.exception(
            "O arquivo de municípios do IBGE não contém um JSON válido."
        )
        raise RuntimeError(
            "Não foi possível interpretar o JSON de municípios do IBGE."
        ) from erro

    except (ValueError, KeyError, OSError, TypeError) as erro:
        logger.exception(
            "Erro durante a transformação dos municípios do IBGE."
        )
        raise RuntimeError(
            "Não foi possível transformar os dados de municípios do IBGE."
        ) from erro


def transformar_municipios_complementares() -> Path:
    

    caminho_csv = MUNICIPIOS_COMPLEMENTARES_RAW_PATH
    caminho_saida = MUNICIPIOS_COMPLEMENTARES_PROCESSED_PATH

    logger.info(
        "Iniciando transformação da base complementar de municípios."
    )

    try:
        validar_arquivo(
            caminho_arquivo=caminho_csv,
            descricao="base complementar de municípios",
        )

        dataframe = pd.read_csv(caminho_csv)

        if dataframe.empty:
            raise ValueError(
                "A base complementar de municípios não contém registros."
            )

        colunas_desejadas = {
            "codigo_ibge": "id_municipio",
            "nome": "municipio_complementar",
            "capital": "capital",
            "codigo_uf": "codigo_uf",
            "siafi_id": "siafi_id",
            "ddd": "ddd",
            "fuso_horario": "fuso_horario",
        }

        validar_colunas(
            dataframe=dataframe,
            colunas_obrigatorias=list(colunas_desejadas.keys()),
            descricao="base complementar de municípios",
        )

        dataframe = dataframe[list(colunas_desejadas.keys())].copy()
        dataframe = dataframe.rename(columns=colunas_desejadas)

        dataframe["id_municipio"] = pd.to_numeric(
            dataframe["id_municipio"],
            errors="coerce",
        ).astype("Int64")

        ids_nulos = int(dataframe["id_municipio"].isna().sum())

        if ids_nulos > 0:
            raise ValueError(
                f"Foram encontrados {ids_nulos} códigos de município inválidos "
                "na base complementar."
            )

        registros_duplicados = int(
            dataframe["id_municipio"].duplicated().sum()
        )

        if registros_duplicados > 0:
            logger.warning(
                "Foram encontrados %s códigos de município duplicados "
                "na base complementar.",
                registros_duplicados,
            )

        dataframe.to_csv(
            caminho_saida,
            index=False,
            encoding="utf-8",
        )

        logger.info(
            "Transformação da base complementar concluída. "
            "Registros tratados: %s.",
            len(dataframe),
        )
        logger.info("Arquivo salvo em: %s.", caminho_saida)

        return caminho_saida

    except FileNotFoundError as erro:
        logger.error("%s", erro)
        raise RuntimeError(
            "O arquivo complementar de municípios não está disponível "
            "para transformação."
        ) from erro

    except pd.errors.EmptyDataError as erro:
        logger.exception(
            "O CSV complementar está vazio ou não possui colunas válidas."
        )
        raise RuntimeError(
            "Não foi possível ler a base complementar de municípios."
        ) from erro

    except pd.errors.ParserError as erro:
        logger.exception(
            "O CSV complementar não possui um formato válido."
        )
        raise RuntimeError(
            "Não foi possível interpretar o CSV complementar."
        ) from erro

    except (ValueError, KeyError, OSError, TypeError) as erro:
        logger.exception(
            "Erro durante a transformação da base complementar "
            "de municípios."
        )
        raise RuntimeError(
            "Não foi possível transformar a base complementar "
            "de municípios."
        ) from erro


if __name__ == "__main__":
    transformar_municipios()
    transformar_municipios_complementares()