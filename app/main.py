from fastapi import FastAPI

from .routes import router

app = FastAPI(
    title="GeoSense API",
    version="1.0.0",
    description="Intelligent geospatial file processing and measurement API",
)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "GeoSense API"}
