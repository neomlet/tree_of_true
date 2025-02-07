import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache.decorator import cache  # Используем декоратор из fastapi_cache
from schemas import GitHubActivity
from redis_cache import init_redis  # Убрали get_cached_data
import json

app = FastAPI(title="GitHub Activity Backend")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация Redis при старте
@app.on_event("startup")
async def startup_event():
    await init_redis()

@app.get("/health")
async def health_check():
    return {"status": "OK"}

@app.get("/api/data/{username}", response_model=list[GitHubActivity])
@cache(expire=3600)  # Используем декоратор напрямую из fastapi_cache
async def get_github_activity(username: str):
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}" if GITHUB_TOKEN else None
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.github.com/users/{username}/events/public",
                headers=headers
            )
            response.raise_for_status()
            
            events = response.json()
            commits = {}
            for event in events:
                if event["type"] == "PushEvent":
                    date = event["created_at"][:10]
                    commits[date] = commits.get(date, 0) + 1

            return [{"date": k, "commits": v} for k, v in commits.items()]

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail="GitHub API error"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)