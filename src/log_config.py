import logging.config


def configure_logging(
    loggers: dict[
        str,
        tuple[
            str,
            list[str],
        ],
    ]
) -> None:
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
        },
        "handlers": {
            "default_console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "standard",
            },
            "goolabs_service_file": {
                "level": "INFO",
                "class": "logging.FileHandler",
                "formatter": "standard",
                "filename": "goolabs_service.log",
                "mode": "a",
            },
        },
        "loggers": {
            logger_name: {
                "level": logger_config[0],
                "handlers": logger_config[1],
                "propagate": False,
            }
            for logger_name, logger_config in loggers.items()
        },
    }
    logging.config.dictConfig(logging_config)
