from pathlib import Path

from pydantic import BaseModel
from yaml import full_load_all as load
from glom import glom

__all__ = ["config"]


class LoggingConfig(BaseModel):
    level: str
    file_level: str
    log_dir: str
    rotation: str
    retention: str


class SpiderConfig(BaseModel):
    max_concurrents: int | None = None
    max_retries: int | None = None
    features: str | None = None


class Config(BaseModel):
    telegram: str
    admins: list[int]

    database: str

    gemini_api: str
    logging_config: LoggingConfig
    spider_config: SpiderConfig


def load_config(config_path: str | Path = "configuration.yaml"):
    _config = {}
    with open(config_path, "r", encoding="utf-8") as f:
        for item in load(f):
            _config.update(item)

    return Config(
        telegram=glom(_config, "api.telegram"),
        admins=glom(_config, "api.admins"),
        database=glom(_config, "database.url"),
        gemini_api=glom(_config, "api.gemini_api"),
        logging_config=glom(_config, "logging"),
        spider_config=glom(_config, "spider"),
    )


config = load_config()
