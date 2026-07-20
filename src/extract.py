import json
from pathlib import Path

import pandas as pd
import requests

from config import (
    IBGE_API_URL,
    MUNICIPIOS_COMPLEMENTARES_RAW_PATH,
    MUNICIPIOS_COMPLEMENTARES_URL,
    MUNICIPIOS_IBGE_RAW_PATH,
    RAW_PATH,
    TIMEOUT_REQUISICAO,
)
from logging_config import configurar_logger


logger = configurar_logger(__name__)

RAW_PATH.mkdir(parents=True, exist_ok=True)

def extrair_municipios_ibge() -> Path:
    

    url = IBGE_API_URL
    caminho_arquivo = MUNICIPIOS_IBGE_RAW_PATH
    logger.info("Iniciando extração dos municípios pela API do IBGE.")

    try:
        resposta = requests.get(url, timeout=TIMEOUT_REQUISICAO)
        resposta.raise_for_status()

        if not resposta.content:
            raise ValueError("A API do IBGE retornou uma resposta vazia.")

        dados = resposta.json()

        if not isinstance(dados, list):
            raise ValueError(
                "A resposta da API do IBGE não possui o formato esperado."
            )

        if not dados:
            raise ValueError("A API do IBGE não retornou municípios.")

        with caminho_arquivo.open("w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=4)

        logger.info(
            "Extração dos municípios concluída. Registros recebidos: %s.",
            len(dados),
        )
        logger.info("Arquivo salvo em: %s.", caminho_arquivo)

        return caminho_arquivo

    except requests.Timeout as erro:
        logger.error("Tempo limite excedido ao acessar a API do IBGE.")
        raise RuntimeError(
            "A API do IBGE demorou mais que o esperado para responder."
        ) from erro

    except requests.ConnectionError as erro:
        logger.error("Não foi possível conectar à API do IBGE.")
        raise RuntimeError(
            "Falha de conexão ao acessar a API do IBGE."
        ) from erro

    except requests.HTTPError as erro:
        logger.error("Erro HTTP ao acessar a API do IBGE: %s.", erro)
        raise RuntimeError(
            "A API do IBGE retornou um erro HTTP."
        ) from erro

    except requests.RequestException as erro:
        logger.exception("Erro inesperado durante a requisição ao IBGE.")
        raise RuntimeError(
            "Erro inesperado durante a extração dos municípios."
        ) from erro

    except json.JSONDecodeError as erro:
        logger.exception("A resposta da API do IBGE não contém JSON válido.")
        raise RuntimeError(
            "A API do IBGE retornou um JSON inválido."
        ) from erro

    except (ValueError, OSError) as erro:
        logger.exception("Erro ao processar ou salvar os dados do IBGE.")
        raise RuntimeError(
            "Não foi possível processar ou salvar os dados do IBGE."
        ) from erro


def baixar_csv(url: str, caminho_arquivo: Path, descricao: str) -> Path:
    """Baixa um arquivo CSV e realiza validações básicas.

    Args:
        url: Endereço público do arquivo CSV.
        caminho_arquivo: Caminho onde o arquivo será salvo.
        descricao: Nome descritivo utilizado nas mensagens de log.

    Returns:
        Caminho do arquivo CSV salvo na camada raw.

    Raises:
        RuntimeError: Quando ocorre falha no download, leitura ou gravação.
    """

    logger.info("Iniciando download: %s.", descricao)

    try:
        resposta = requests.get(url, timeout=TIMEOUT_REQUISICAO)
        resposta.raise_for_status()

        if not resposta.content:
            raise ValueError(f"O download de {descricao} retornou vazio.")

        caminho_arquivo.write_bytes(resposta.content)

        dataframe_validacao = pd.read_csv(caminho_arquivo)

        if dataframe_validacao.empty:
            raise ValueError(
                f"O arquivo de {descricao} não contém registros."
            )

        if len(dataframe_validacao.columns) == 0:
            raise ValueError(
                f"O arquivo de {descricao} não contém colunas válidas."
            )

        logger.info(
            "%s concluído. Registros recebidos: %s.",
            descricao,
            len(dataframe_validacao),
        )
        logger.info(
            "Colunas identificadas em %s: %s.",
            descricao,
            list(dataframe_validacao.columns),
        )
        logger.info("Arquivo salvo em: %s.", caminho_arquivo)

        return caminho_arquivo

    except requests.Timeout as erro:
        logger.error(
            "Tempo limite excedido durante o download de %s.",
            descricao,
        )
        raise RuntimeError(
            f"Tempo limite excedido durante o download de {descricao}."
        ) from erro

    except requests.ConnectionError as erro:
        logger.error(
            "Erro de conexão durante o download de %s.",
            descricao,
        )
        raise RuntimeError(
            f"Não foi possível conectar à fonte de {descricao}."
        ) from erro

    except requests.HTTPError as erro:
        logger.error(
            "Erro HTTP durante o download de %s: %s.",
            descricao,
            erro,
        )
        raise RuntimeError(
            f"A fonte de {descricao} retornou um erro HTTP."
        ) from erro

    except requests.RequestException as erro:
        logger.exception(
            "Erro inesperado durante o download de %s.",
            descricao,
        )
        raise RuntimeError(
            f"Erro inesperado durante o download de {descricao}."
        ) from erro

    except pd.errors.EmptyDataError as erro:
        logger.exception(
            "O arquivo de %s está vazio ou não possui conteúdo válido.",
            descricao,
        )
        raise RuntimeError(
            f"O arquivo de {descricao} está vazio."
        ) from erro

    except pd.errors.ParserError as erro:
        logger.exception(
            "O arquivo de %s não possui um formato CSV válido.",
            descricao,
        )
        raise RuntimeError(
            f"O arquivo de {descricao} não pôde ser interpretado como CSV."
        ) from erro

    except (ValueError, OSError) as erro:
        logger.exception("Erro ao validar ou salvar %s.", descricao)
        raise RuntimeError(
            f"Não foi possível validar ou salvar {descricao}."
        ) from erro


def extrair_municipios_complementares() -> Path:
    
    url = MUNICIPIOS_COMPLEMENTARES_URL
    caminho_arquivo = MUNICIPIOS_COMPLEMENTARES_RAW_PATH

    return baixar_csv(
        url=url,
        caminho_arquivo=caminho_arquivo,
        descricao="base complementar de municípios brasileiros",
    )


if __name__ == "__main__":
    extrair_municipios_ibge()
    extrair_municipios_complementares()