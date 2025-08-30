import yaml
import os
from dotenv import load_dotenv
from typing import Any, Dict

load_dotenv()

CONFIG_PATH = os.getenv("CONFIG_PATH", "config.yaml")


class Config:
    def __init__(self, path: str = CONFIG_PATH):
        with open(path, "r") as f:
            self.data = yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)


config = Config()
