# app/config.py
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # ===== DB =====
    # .env의 DATABASE_URL이 있으면 그걸 우선 사용; 없으면 아래 기본값 사용
    database_url: str = Field(
        "mysql+pymysql://username:password@localhost:3306/green_shipping_db",
        alias="DATABASE_URL",
    )

    # ✅ CSV 경로(.env의 PORT_DB_CSV_PATH) — 없으면 None
    port_db_csv_path: Optional[str] = Field(None, alias="PORT_DB_CSV_PATH")

    # ===== Security =====
    secret_key: str = Field("your-secret-key-here", alias="SECRET_KEY")
    algorithm: str = Field("HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # ===== Server =====
    host: str = Field("0.0.0.0", alias="HOST")
    port: int = Field(8000, alias="PORT")
    debug: bool = Field(True, alias="DEBUG")

    # ===== MySQL (선택) =====
    mysql_host: str = Field("localhost", alias="MYSQL_HOST")
    mysql_port: int = Field(3306, alias="MYSQL_PORT")
    mysql_user: str = Field("username", alias="MYSQL_USER")
    mysql_password: str = Field("password", alias="MYSQL_PASSWORD")
    mysql_database: str = Field("green_shipping_db", alias="MYSQL_DATABASE")

    # ===== Env =====
    environment: Optional[str] = Field(None, alias="ENVIRONMENT")

    # ===== AI / LLM =====
    ai_provider: str = Field("openai", alias="AI_PROVIDER")
    ai_model: str = Field("gpt-5", alias="AI_MODEL")
    openai_api_key: Optional[str] = Field(None, alias="OPENAI_API_KEY")
    embedding_model: str = Field("text-embedding-3-small", alias="EMBEDDING_MODEL")
    ai_temperature: float = Field(1.0, alias="AI_TEMPERATURE")
    ai_max_tokens: int = Field(1000, alias="AI_MAX_TOKENS")

    # ===== Internal simulation API (stubbed if not set) =====
    sim_api_base: Optional[str] = Field(None, alias="SIM_API_BASE")
    sim_api_key: Optional[str] = Field(None, alias="SIM_API_KEY")

    # ===== Internal-only protection =====
    internal_api_token: Optional[str] = Field(None, alias="INTERNAL_API_TOKEN")

    # ===== RAG persistence =====
    rag_persist_dir: str = Field("./data/chroma", alias="RAG_PERSIST_DIR")

    # ===== Pydantic Settings v2 설정 =====
    # - .env 읽기, 대소문자 무시
    # - 정의 안 된 키(.env의 기타 항목)는 무시 → extra="ignore" (에러 방지 포인트)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
