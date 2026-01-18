from pathlib import Path

from pydantic import BaseModel
from yaml import full_load_all as load
from glom import glom

__all__ = [
    "config"
]

class LoggingConfig(BaseModel):
    level: str
    file_level: str
    log_dir: str
    rotation: str 
    retention: str

class Config(BaseModel):
    telegram: str
    admins: list[int]
    
    database: str
    features: str
    
    logging_config: LoggingConfig

def load_config(config_path: str | Path = "configuration.yaml"):
    _config = {}
    with open(config_path, "r", encoding="utf-8") as f:
        for item in load(f):
            _config.update(item)
    
    return Config(
        telegram = glom(_config, 'api.telegram'),
        admins = glom(_config, 'api.admins'),
        database = glom(_config, 'database.url'),
        features = glom(_config, 'parser.features'),
        logging_config = glom(_config, 'logging')
    )
    
config = load_config()