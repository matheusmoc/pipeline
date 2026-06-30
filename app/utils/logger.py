"""
Utilitario de Logging.

Configura loggers com formatacao estruturada e saida em stdout.
A saida em stdout e o padrao para aplicacoes containerizadas,
pois o Docker captura automaticamente tudo que vai para stdout/stderr,
tornando os logs visiveis em ferramentas como Dozzle e docker logs.
"""

import logging
import sys

from app.config import settings


def get_logger(name: str) -> logging.Logger:
    """
    Cria e retorna um logger configurado para o modulo informado.

    Evita duplicacao de handlers caso o logger ja tenha sido
    inicializado anteriormente.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
