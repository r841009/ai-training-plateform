from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.logging_config import configure_logging
from app.routers import (
    base_models,
    dataset_versions,
    evaluations,
    health,
    model_versions,
    projects,
    scheduler,
    trainers,
    training_jobs,
    training_servers,
)
from app.schemas.response import error_response

configure_logging()

app = FastAPI(title="AOI AI Training Platform API")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(projects.router)
app.include_router(base_models.router)
app.include_router(trainers.router)
app.include_router(dataset_versions.router)
app.include_router(training_jobs.router)
app.include_router(model_versions.router)
app.include_router(evaluations.router)
app.include_router(training_servers.router)
app.include_router(scheduler.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    body = error_response(code=str(exc.status_code), message=str(exc.detail))
    return JSONResponse(status_code=exc.status_code, content=body.model_dump())


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    body = error_response(code="INTERNAL_ERROR", message="Internal server error")
    return JSONResponse(status_code=500, content=body.model_dump())
