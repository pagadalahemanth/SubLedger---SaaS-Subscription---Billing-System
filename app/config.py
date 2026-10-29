"""Small environment-based configuration for SubLedger."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./subledger.db")
    app_name: str = "SubLedger API"
    app_version: str = "1.0.0"


settings = Settings()
