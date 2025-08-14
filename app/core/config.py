from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    embed_model: str = "BAAI/bge-small-en-v1.5"
    llm_model: str = "ollama:qwen2.5:7b-instruct"
    retrieval_top_k: int = 5
    gpu_layers: int = 20  # Number of GPU layers to use for Ollama
    
    class Config:
        env_file = ".env"

settings = Settings()