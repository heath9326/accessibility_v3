from fastapi import FastAPI
from pydantic_settings import BaseSettings
import logging
import logging.config

from starlette.templating import Jinja2Templates


class Settings(BaseSettings):
    text_complexity_index: int = 30
    word_complexity_index: int = 4


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "app.log",
            "formatter": "detailed",
        },
    },
    "loggers": {
        "fastapi": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
        "my_app": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

app = FastAPI()
templates = Jinja2Templates(directory="templates")
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("my_app")
settings = Settings()
