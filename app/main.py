from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1 import chat_session_api, message_api
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.db import Base, engine

setup_logging()

Base.metadata.create_all(bind=engine)

fast_api_app = FastAPI(title=settings.app_name)

fast_api_app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key
)

# Register Routes
fast_api_app.include_router(chat_session_api.router, prefix="/api/v1/chat-sessions", tags=["Chat Sessions"])
fast_api_app.include_router(message_api.router, prefix="/api/v1/messages", tags=["Messages"])
