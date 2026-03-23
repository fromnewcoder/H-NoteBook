from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    chroma_persist_path: str = "./chroma_data"
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 8
    minimax_api_key: str
    minimax_api_base_url: str
    minimax_model: str = "MiniMax-Text-2.7"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    export_storage_path: str = "./exports"
    rag_chunk_size: int = 512
    rag_chunk_overlap: int = 64
    rag_top_k: int = 5
    rag_history_turns: int = 10
    max_upload_size_mb: int = 10

    class Config:
        env_file = ".env"


settings = Settings()
