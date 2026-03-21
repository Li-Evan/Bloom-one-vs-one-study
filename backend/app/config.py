import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))


class Settings:
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
    DASHSCOPE_BASE_URL: str = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    DASHSCOPE_MODEL: str = os.getenv("DASHSCOPE_MODEL", "qwen-plus")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./bloom.db")

    CORS_ORIGINS: list[str] = [
        o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",") if o.strip()
    ]

    TESTING: bool = os.getenv("TESTING", "").lower() in ("1", "true", "yes")


settings = Settings()
