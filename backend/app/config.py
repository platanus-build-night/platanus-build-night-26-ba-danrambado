import os

from pydantic_settings import BaseSettings

_env_files = [f for f in (".env", "../.env") if os.path.isfile(f)]


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    database_url: str = "sqlite:///./data/serendip.db"
    chroma_persist_dir: str = "./data/chroma"
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = {"env_file": _env_files, "env_file_encoding": "utf-8"}


settings = Settings()
