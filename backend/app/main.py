from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import v1
from app.database import create_db_and_tables
from app.seed import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    seed_data()
    yield


app = FastAPI(
    title="Saudi NPO Multi-Agent AI Platform",
    description="Multi-Agent AI platform for Saudi non-profit organizations",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Saudi NPO Multi-Agent AI Platform"}
