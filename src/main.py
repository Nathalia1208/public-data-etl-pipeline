import sys
from time import perf_counter

from extract import (
    extrair_municipios_complementares,
    extrair_municipios_ibge,
)
from load import carregar_dados
from logging_config import configurar_logger
from transform import (
    transformar_municipios,
    transformar_municipios_complementares,
)
from config import (
    ETAPA_CARGA,
    ETAPA_EXTRACAO,
    ETAPA_TRANSFORMACAO,
)

logger = configurar_logger(__name__)


def executar_pipeline() -> None:
    """Executa todas as etapas do pipeline ETL.

    O pipeline realiza a extração, transformação, integração, carga no
    DuckDB e exportação dos dados consolidados em arquivos Parquet.

    Raises:
        RuntimeError: Quando alguma etapa do pipeline falha.
    """

    inicio_execucao = perf_counter()

    logger.info("=" * 70)
    logger.info("Iniciando pipeline ETL de municípios brasileiros.")
    logger.info("=" * 70)

    try:
        logger.info("%s | INÍCIO", ETAPA_EXTRACAO)

        extrair_municipios_ibge()
        extrair_municipios_complementares()

        logger.info("%s | CONCLUÍDA", ETAPA_EXTRACAO)

        logger.info("%s | INÍCIO", ETAPA_TRANSFORMACAO)

        transformar_municipios()
        transformar_municipios_complementares()

        logger.info("%s | CONCLUÍDA", ETAPA_TRANSFORMACAO)

        logger.info("%s | INÍCIO", ETAPA_CARGA)

        metricas = carregar_dados()

        logger.info("%s | CONCLUÍDA", ETAPA_CARGA)

        logger.info("Resumo da execução:")
        logger.info(
            "Municípios extraídos do IBGE: %s.",
            metricas["total_municipios_ibge"],
        )
        logger.info(
            "Registros da base complementar: %s.",
            metricas["total_municipios_complementares"],
        )
        logger.info(
            "Registros consolidados: %s.",
            metricas["total_registros_consolidados"],
        )
        logger.info(
            "Municípios sem correspondência: %s.",
            metricas["sem_correspondencia"],
        )
        logger.info(
            "IDs duplicados na base IBGE: %s.",
            metricas["duplicados_ibge"],
        )
        logger.info(
            "IDs duplicados na base complementar: %s.",
            metricas["duplicados_complementares"],
        )

    except KeyboardInterrupt:
        logger.warning("Execução interrompida manualmente pelo usuário.")
        raise

    except Exception as erro:
        logger.exception(
            "O pipeline foi interrompido devido a um erro: %s.",
            erro,
        )
        raise RuntimeError(
            "Não foi possível concluir o pipeline ETL."
        ) from erro

    finally:
        duracao_total = perf_counter() - inicio_execucao

        logger.info(
            "Tempo total de execução: %.2f segundos.",
            duracao_total,
        )

    logger.info("=" * 70)
    logger.info("Pipeline ETL concluído com sucesso.")
    logger.info("=" * 70)


if __name__ == "__main__":
    try:
        executar_pipeline()

    except KeyboardInterrupt:
        logger.warning("Pipeline encerrado pelo usuário.")
        sys.exit(130)

    except RuntimeError:
        logger.error("Pipeline finalizado com falha.")
        sys.exit(1)

    sys.exit(0)