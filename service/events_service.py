"""
Сервис позволяет симулировать онлайн историю
"""
from fastapi import FastAPI


class EventStore:
    """Класс для добавления и просмотра онлайн истории"""

    def __init__(self, max_events_per_user: int = 10):
        self.events = {}
        self.max_events_per_user = max_events_per_user

    def put(self, user_id: int, track_id: int):
        """Добавить новое событие юзеру в онлайн историю"""
        user_events = [] if self.events.get(user_id) is None else self.events[user_id]
        self.events[user_id] = [track_id] + user_events[:self.max_events_per_user]

    def get(self, user_id: int, k: int = 5):
        """Получить онлайн историю по юзеру"""
        user_events = self.events[user_id][:k] if user_id in self.events else []

        return user_events


event_store = EventStore()

app = FastAPI(title="events")


@app.get("/healthy")
async def healthy():
    """Посмотреть здоровье сервиса"""
    return {"status": "healthy"}


@app.post("/put")
async def put(user_id: int, track_id: int):
    """Ручка для добавления события в онлайн историю по юзеру"""
    event_store.put(user_id, track_id)

    return {"result": "OK"}


@app.post("/get")
async def get(user_id: int, k: int):
    """Ручка для того, чтобы получить онлайн историю по юзеру"""
    events = event_store.get(user_id, k)

    return {"events": events}