from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    #APP CONFIG
    app_name: str = "CloudOps AI"
    environment: str = "development"
    app_description: str = "AI-powered knowledge assistant for Cloud Operations."
    app_version: str = "0.1.0"
    debug: bool = False
    #GROQ API
    groq_api_key: str
    groq_model: str = "openai/gpt-oss-20b"

    #QDRANT API
    qdrant_host: str
    qdrant_port: int
    qdrant_collection: str
    

settings = Settings()