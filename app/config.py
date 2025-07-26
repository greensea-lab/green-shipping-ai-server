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
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings() 