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

    # DOCUMENT PROCESSING
    chunk_size: int = 1000
    chunk_overlap: int = 200

    #QDRANT API
    qdrant_host: str
    qdrant_port: int
    qdrant_collection: str

    #GEMINI API
    gemini_api_key: str
    gemini_embedding_model: str = "gemini-embedding-001"
    gemini_embedding_dimension: int = 768

    #RAG CONFIG
    rag_retrieval_limit: int = 5
    

settings = Settings()