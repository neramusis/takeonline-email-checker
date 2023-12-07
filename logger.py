LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "default",
            "filename": "tradeonline.log",
            "when": "H",
            "interval": 1,
            "backupCount": 24,
        },
    },
    "loggers": {
        "": {
            "handlers": ["file"],
            "level": "INFO",
        },
    },
    "disable_existing_loggers": False,
}
