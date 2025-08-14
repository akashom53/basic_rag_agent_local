from app.core.config import settings

print(f"Database URL: {settings.database_url}")
print(f"Embed Model: {settings.embed_model}")
print(f"LLM Model: {settings.llm_model}")
print(f"Top K: {settings.retrieval_top_k}")