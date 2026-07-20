import logging
from logging.handlers import RotatingFileHandler

from config import LOG_FILE, LOG_LEVEL, LOGS_PATH


LOGS_PATH.mkdir(parents=True, exist_ok=True)


def configurar_logger(nome: str) -> logging.Logger:
    """Configura um logger para terminal e arquivo.

    Args:
        nome: Nome do módulo que utilizará o logger.

    Returns:
        Logger configurado.
    """

    logger = logging.getLogger(nome)

    if logger.handlers:
        return logger

    nivel_log = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

    logger.setLevel(nivel_log)
    logger.propagate = False

    formato = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(nivel_log)
    console_handler.setFormatter(formato)

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(nivel_log)
    file_handler.setFormatter(formato)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger