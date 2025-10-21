from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.api.v1 import sbom as sbom_router
from app.models.db import Base, engine


def create_app() -> FastAPI:
    app = FastAPI(
        title="MyESI SBOM Service", version="1.0.0", openapi_url="/openapi.json"
    )

    # Include main router
    app.include_router(sbom_router.router)

    # Prometheus metrics
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

    # 👉 thêm event startup tạo bảng nếu chưa có
    @app.on_event("startup")
    async def on_startup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("SBOM database tables created (if not exist)")

    return app


app = create_app()


@app.get("/health")
async def health():
    return {"status": "ok"}
