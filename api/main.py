from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from hate_speech.config import settings
from db.base import Base
from db.session import engine
from .routes import retrain


from .routes import prediction, feedback, dashboard_api


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
    )

    # CORS for future Streamlit UI
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # tighten this in prod
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create DB tables
    Base.metadata.create_all(bind=engine)

    app.include_router(
        prediction.router, prefix=settings.API_PREFIX
    )
    app.include_router(
        feedback.router, prefix=settings.API_PREFIX
    )

    app.include_router(dashboard_api.router)

    app.include_router(retrain.router)


    return app


app = create_app()
