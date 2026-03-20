import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))


class Settings:
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
    DASHSCOPE_BASE_URL: str = os.getenv("DASHSCOPE_BASE_URL", "https://coding.dashscope.aliyuncs.com/v1")
    DASHSCOPE_MODEL: str = os.getenv("DASHSCOPE_MODEL", "glm-5")

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

    DEFAULT_CREDITS: int = int(os.getenv("DEFAULT_CREDITS", "100"))
    CREDITS_PER_REQUEST: int = int(os.getenv("CREDITS_PER_REQUEST", "1"))

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./bloom.db")


settings = Settings()
