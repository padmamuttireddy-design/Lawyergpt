from pydantic_settings import BaseSettings, SettingsConfigDict


class EngineSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str = ""
    chroma_persist_dir: str = "./chroma_db"
    chroma_collection_name: str = "lawyergpt_docs"
    top_k_results: int = 5
    min_relevance_score: float = 0.3
    batch_size: int = 100
    chunk_size: int = 2000
    chunk_overlap: int = 200
    embedding_model: str = "text-embedding-3-large"
    generation_model: str = "gpt-4o"


settings = EngineSettings()
