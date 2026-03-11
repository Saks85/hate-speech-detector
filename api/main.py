from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from hate_speech.config import settings
from db.base import Base
from db.session import engine
from .routes import retrain
from .deps import inference_service


from .routes import prediction, feedback, dashboard_api


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        docs_url="/docs" if settings.ENABLE_API_DOCS else None,
        redoc_url="/redoc" if settings.ENABLE_API_DOCS else None,
        openapi_url="/openapi.json" if settings.ENABLE_API_DOCS else None,
    )

    # Restrict CORS to configured frontend domains.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
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

    @app.get("/healthz", tags=["health"])
    def healthz() -> dict:
        return {
            "status": "ok",
            "version": settings.VERSION,
            "model_dir": settings.MODEL_DIR,
            "inference": inference_service.readiness(),
        }


    return app


app = create_app()
