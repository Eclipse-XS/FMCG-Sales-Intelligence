from __future__ import annotations

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.types import ASGIApp, Receive, Scope, Send

from ..engine import Engine, EngineError


class InferenceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rows: list[dict] = Field(min_length=1, max_length=1000)
    version: str | None = None
    domain: str | None = None


class BodyLimit:
    """Enforce actual bytes, including chunked requests, before JSON parsing."""
    def __init__(self, app: ASGIApp, max_bytes: int):
        self.app, self.max_bytes = app, max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http" or scope["method"] not in {"POST", "PUT", "PATCH"}:
            return await self.app(scope, receive, send)
        messages, size = [], 0
        while True:
            message = await receive()
            size += len(message.get("body", b""))
            if size > self.max_bytes:
                response = JSONResponse(status_code=413, content={"error": {
                    "code": "REQUEST_TOO_LARGE", "message": "Request body exceeds configured limit"}})
                return await response(scope, receive, send)
            messages.append(message)
            if not message.get("more_body", False):
                break
        async def replay():
            if messages:
                return messages.pop(0)
            return await receive()
        await self.app(scope, replay, send)


def install_engine_api(app: FastAPI, engine: Engine):
    router = APIRouter(prefix="/api/v1")

    @app.exception_handler(EngineError)
    async def engine_error(request: Request, exc: EngineError):
        return JSONResponse(status_code=exc.status, content={"error": {
            "code": exc.code, "message": str(exc),
            "request_id": getattr(request.state, "request_id", None)}})

    @router.get("/models")
    def models():
        return {"items": engine.registry.metadata()}

    @router.get("/models/{name}")
    def model(name: str, version: str | None = None):
        return engine.registry.resolve(name, version).metadata()

    @router.get("/models/{name}/schema")
    def schema(name: str, version: str | None = None):
        return engine.registry.resolve(name, version).signature.metadata()

    @router.post("/models/{name}/validate")
    def validate(name: str, body: InferenceRequest):
        model, frame = engine.validate(name, body.rows, version=body.version, domain=body.domain)
        return {"valid": True, "rows": len(frame), "model": model.name, "version": model.version}

    @router.post("/models/{name}/inferences")
    def infer(name: str, body: InferenceRequest, request: Request):
        return engine.infer(name, body.rows, version=body.version, domain=body.domain,
                            request_id=getattr(request.state, "request_id", None))

    @router.get("/domains")
    def domains():
        return {"items": engine.domains.metadata()}

    @router.get("/runtime/ready")
    def ready():
        metadata = engine.registry.metadata()
        ready = bool(metadata) and all(m["ready"] for m in metadata)
        return JSONResponse(status_code=200 if ready else 503,
                            content={"ready": ready, "models": metadata})

    app.include_router(router)
