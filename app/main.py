from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import chat, tickets, ingestion

app = FastAPI(title="AI Support Bot", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(tickets.router, prefix="/api/v1", tags=["tickets"])
app.include_router(ingestion.router, prefix="/api/v1", tags=["ingestion"])

@app.get("/")
async def root():
    return {"message": "AI Support Bot API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Support Bot"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)