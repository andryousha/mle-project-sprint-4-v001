"""Service for outputing offline recommendations (personal and top-popular)."""
import logging
import os
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("uvicorn.error")
logging.basicConfig(level=logging.INFO)


class Recommender:
    """Класс для генерации оффлайн рекомендаций"""

    def __init__(self):
        self._recs = {
            "personal": None,
            "default": None,
        }
        self._stats = {
            "request_personal_count": 0,
            "request_default_count": 0,
        }

    def load(self, rec_type, path, **kwargs):
        """Загрузить оффлайн рекомендации"""
        logger.info(f"Loading recommendations: {rec_type}")
        self._recs[rec_type] = pd.read_parquet(path, **kwargs)
        if rec_type == "personal":
            self._recs[rec_type] = self._recs[rec_type].set_index("user_id")
        logger.info("Recommendations loaded")

    def get(self, user_id: int, k: int = 10):
        """Сгененрировать к оффлайн рекомендаций по юзеру."""
        if user_id in self._recs["personal"].index:
            recs = self._recs["personal"].loc[user_id]
            recs = recs["track_id"].tolist()[:k]
            self._stats["request_personal_count"] += 1
            logger.info(f"user {user_id} - using personal history")
        else:
            recs = self._recs["default"]
            recs = recs["track_id"].tolist()[:k]
            self._stats["request_default_count"] += 1
            logger.info(f"user {user_id} - using default")

        return recs


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Загрузить данные при старте сервиса"""
    rec_store = Recommender()
    rec_store.load(rec_type="personal", path=os.getenv("PERSONAL_RECS_PATH"))
    rec_store.load(rec_type="default", path=os.getenv("DEFAULT_RECS_PATH"))

    yield {"rec_store": rec_store}


app = FastAPI(title="recommendations_offline", lifespan=lifespan)


@app.post("/get_recs")
async def recommendations(request: Request, user_id: int, k: int):
    """Ручка для получения оффлайн рекомендаций"""
    rec_store = request.state.rec_store

    i2i = rec_store.get(user_id, k)

    return i2i


@app.get("/healthy")
async def healthy():
    """Посмотреть здоровье сервиса"""
    return {"status": "healthy"}


@app.get("/get_stats")
async def get_stats(request: Request):
    """Получить статистику сервиса"""
    rec_store = request.state.rec_store

    return rec_store._stats