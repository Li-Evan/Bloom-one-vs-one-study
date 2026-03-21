import os
import sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

_INSECURE_JWT_DEFAULTS = {"change-me", "change-this-to-a-random-secret-key", ""}


class Settings:
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
    DASHSCOPE_BASE_URL: str = os.getenv("DASHSCOPE_BASE_URL", "https://coding.dashscope.aliyuncs.com/v1")
    DASHSCOPE_MODEL: str = os.getenv("DASHSCOPE_MODEL", "glm-5")

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

    DEFAULT_CREDITS: int = int(os.getenv("DEFAULT_CREDITS", "100"))
    CREDITS_PER_REQUEST: int = int(os.getenv("CREDITS_PER_REQUEST", "1"))

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./bloom.db")

    CORS_ORIGINS: list[str] = [
        o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",") if o.strip()
    ]

    TESTING: bool = os.getenv("TESTING", "").lower() in ("1", "true", "yes")

    def validate(self):
        if not self.TESTING and self.JWT_SECRET_KEY in _INSECURE_JWT_DEFAULTS:
            print(
                "FATAL: JWT_SECRET_KEY is not set or uses an insecure default. "
                "Set a strong secret in .env before starting the server.",
                file=sys.stderr,
            )
            sys.exit(1)


settings = Settings()
settings.validate()
