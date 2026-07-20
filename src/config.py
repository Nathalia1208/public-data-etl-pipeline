from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RAW_PATH = DATA_DIR / "raw"
PROCESSED_PATH = DATA_DIR / "processed"
CURATED_PATH = DATA_DIR / "curated"

LOGS_PATH = BASE_DIR / "logs"
LOG_FILE = LOGS_PATH / "pipeline.log"

DUCKDB_PATH = DATA_DIR / "etl.db"

MUNICIPIOS_IBGE_RAW_PATH = RAW_PATH / "municipios_ibge.json"

MUNICIPIOS_COMPLEMENTARES_RAW_PATH = (
    RAW_PATH / "municipios_complementares.csv"
)

MUNICIPIOS_IBGE_PROCESSED_PATH = (
    PROCESSED_PATH / "municipios_tratados.csv"
)

MUNICIPIOS_COMPLEMENTARES_PROCESSED_PATH = (
    PROCESSED_PATH / "municipios_complementares_tratados.csv"
)

MUNICIPIOS_CONSOLIDADOS_PARQUET_PATH = (
    CURATED_PATH / "municipios_consolidados"
)

IBGE_API_URL = (
    "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
)

MUNICIPIOS_COMPLEMENTARES_URL = (
    "https://raw.githubusercontent.com/"
    "kelvins/Municipios-Brasileiros/main/csv/municipios.csv"
)

TIMEOUT_REQUISICAO = 30
LOG_LEVEL = "INFO"

ETAPA_EXTRACAO = "ETAPA 1/3 - EXTRAÇÃO"
ETAPA_TRANSFORMACAO = "ETAPA 2/3 - TRANSFORMAÇÃO"
ETAPA_CARGA = "ETAPA 3/3 - CARGA"