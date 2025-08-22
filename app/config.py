from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "mysql+pymysql://username:password@localhost:3306/green_shipping_db"
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # MySQL
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "username"
    mysql_password: str = "password"
    mysql_database: str = "green_shipping_db"
    
    # Environment
    environment: Optional[str] = None

    # AI / LLM
    ai_provider: str = "openai"
    ai_model: str = "gpt-5"
    openai_api_key: Optional[str] = None
    embedding_model: str = "text-embedding-3-small"
    ai_temperature: float = 0.2
    ai_max_tokens: int = 1000

    # Internal simulation API (stubbed if not set)
    sim_api_base: Optional[str] = None
    sim_api_key: Optional[str] = None

    # Internal-only protection
    internal_api_token: Optional[str] = None

    # RAG persistence
    rag_persist_dir: str = "./data/chroma"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings() 
