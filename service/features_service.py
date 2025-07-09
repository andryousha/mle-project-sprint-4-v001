"""Service for outputing online recommendations (track similarity)."""
import logging
import os
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("uvicorn.error")
logging.basicConfig(level=logging.INFO)


class SimilarTracks:
    """Class for displaying online recommendations."""

    def __init__(self) -> None:
        """Initializes a class instance."""
        self._similar_tracks = None

    def load(self, path: str, **kwargs):
        """Загрузить онлайн рекомендации"""
        logger.info("Loading similarity data")
        self._similar_tracks = pd.read_parquet(path, **kwargs)
        self._similar_tracks = self._similar_tracks.set_index("track_id_1")
        logger.info("Loaded similarity data")

    def get(self, track_id: int, k: int = 10):
        """Вернуть первые к онлайн рекомендаций"""
        try:
            i2i = self._similar_tracks.loc[track_id].head(k)
            i2i = i2i[["track_id_2", "score"]].to_dict(orient="list")
        except KeyError:
            logger.error("No recommendations found")
            i2i = {"track_id_2": [], "score": []}

        return i2i


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Загрузить данные при старте"""
    sim_items_store = SimilarTracks()
    sim_items_store.load(path=os.getenv("ONLINE_RECS_PATH"))
    logger.info("Ready for online recommendations")

    yield {"sim_items_store": sim_items_store}


app = FastAPI(title="features", lifespan=lifespan)


@app.get("/healthy")
async def healthy():
    """Проверить здоровье сервиса"""
    return {"status": "healthy"}


@app.post("/similar_tracks")
async def similar_tracks(request: Request, track_id: int, k: int):
    """Сгенерировать онлайн рекомендации."""
    sim_items_store = request.state.sim_items_store
    i2i = sim_items_store.get(track_id, k)
    return i2i