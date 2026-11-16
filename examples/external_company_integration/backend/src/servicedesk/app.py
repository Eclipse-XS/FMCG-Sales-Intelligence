from __future__ import annotations

import logging
import math
import os
import sqlite3
from contextlib import asynccontextmanager
from dataclasses import dataclass
from uuid import uuid4

import httpx
from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse

from .features import REFERENCE_TIME, extract_features, get_ticket, parse_time

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class Settings:
    database: str = "/state/tickets.sqlite"
    engine_url: str = "http://engine:8000"
    model_name: str = "servicedesk-sla"
    model_version: str = "2"
    reference_time: str = REFERENCE_TIME
    connect_timeout: float = 2.0
    request_timeout: float = 10.0

    @classmethod
    def from_env(cls):
        return cls(database=os.getenv("TICKET_DATABASE", cls.database),
                   engine_url=os.getenv("ML_ENGINE_URL", cls.engine_url),
                   model_version=os.getenv("SLA_MODEL_VERSION", cls.model_version),
                   reference_time=os.getenv("REFERENCE_TIME", cls.reference_time),
                   connect_timeout=float(os.getenv("ENGINE_CONNECT_TIMEOUT", cls.connect_timeout)),
                   request_timeout=float(os.getenv("ENGINE_REQUEST_TIMEOUT", cls.request_timeout)))


class BusinessError(Exception):
    def __init__(self, status, code, message):
        super().__init__(message)
        self.status, self.code = status, code


def create_app(settings: Settings | None = None):
    settings = settings or Settings.from_env()
    parse_time(settings.reference_time)
    if any(not math.isfinite(value) or value <= 0 for value in (settings.connect_timeout, settings.request_timeout)):
        raise ValueError("Timeouts must be positive")

    @asynccontextmanager
    async def lifespan(app):
        with httpx.Client(base_url=settings.engine_url.rstrip("/"), trust_env=False,
                          timeout=httpx.Timeout(settings.request_timeout, connect=settings.connect_timeout)) as client:
            app.state.engine = client
            yield

    app = FastAPI(title="Independent ServiceDesk", lifespan=lifespan)

    @app.middleware("http")
    async def request_identity(request: Request, call_next):
        request.state.request_id = str(uuid4())
        try:
            response = await call_next(request)
        except Exception:
            LOGGER.exception("Unexpected backend error request_id=%s", request.state.request_id)
            response = JSONResponse(status_code=500, content={"error": {"code": "INTERNAL_ERROR",
                "message": "Ticket request failed", "request_id": request.state.request_id}})
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    @app.exception_handler(BusinessError)
    async def business_error(request, exc):
        return JSONResponse(status_code=exc.status, content={"error": {"code": exc.code,
            "message": str(exc), "request_id": request.state.request_id}})

    def ticket_record(ticket_id):
        try:
            record = get_ticket(settings.database, ticket_id)
        except sqlite3.Error as exc:
            LOGGER.exception("Ticket database unavailable")
            raise BusinessError(503, "DATABASE_UNAVAILABLE", "Ticket database unavailable") from exc
        if record is None:
            raise BusinessError(404, "TICKET_NOT_FOUND", "Unknown ticket")
        return record

    @app.get("/health")
    def health():
        return {"status": "alive", "service": "independent-servicedesk"}

    @app.get("/tickets/{ticket_id}")
    def ticket(ticket_id: int):
        return ticket_record(ticket_id)

    @app.get("/tickets/{ticket_id}/risk")
    def risk(ticket_id: int, request: Request,
             version: str = Query(settings.model_version, pattern=r"^[1-9][0-9]*$")):
        record = ticket_record(ticket_id)
        try:
            features = extract_features(record, settings.reference_time)
        except (ValueError, TypeError, KeyError) as exc:
            raise BusinessError(422, "INVALID_TICKET_SNAPSHOT", "Ticket features are incompatible with the reference time") from exc
        try:
            result = request.app.state.engine.post(f"/api/v1/models/{settings.model_name}/inferences",
                headers={"X-Request-ID": request.state.request_id},
                json={"rows": [features], "domain": "servicedesk", "version": version})
        except httpx.ConnectTimeout as exc:
            raise BusinessError(503, "ENGINE_UNAVAILABLE", "Risk service unavailable") from exc
        except httpx.TimeoutException as exc:
            raise BusinessError(504, "ENGINE_TIMEOUT", "Risk service timed out") from exc
        except httpx.RequestError as exc:
            raise BusinessError(503, "ENGINE_UNAVAILABLE", "Risk service unavailable") from exc
        if result.status_code == 422:
            raise BusinessError(422, "INVALID_FEATURES", "Ticket features were rejected by the risk model")
        if result.status_code == 404:
            raise BusinessError(503, "MODEL_VERSION_UNAVAILABLE", "Requested risk model version is not deployed")
        if result.status_code == 503:
            raise BusinessError(503, "MODEL_UNAVAILABLE", "Risk model unavailable")
        if result.status_code != 200:
            raise BusinessError(502, "ENGINE_ERROR", "Risk service failed")
        try:
            payload = result.json()
            metadata = payload["metadata"]
            probability = float(payload["probabilities"][0][payload["classes"].index(1)])
            if (not math.isfinite(probability) or not 0 <= probability <= 1
                    or metadata["version"] != version or metadata["model"] != settings.model_name
                    or metadata["request_id"] != request.state.request_id
                    or metadata["provenance"]["uri"] != f"models:/{settings.model_name}/{version}"):
                raise ValueError("Inconsistent model response")
            return {"ticket_id": ticket_id, "sla_breach_probability": probability,
                    "model": metadata["model"], "model_version": metadata["version"],
                    "model_uri": metadata["provenance"]["uri"], "model_run_id": metadata["provenance"]["run_id"],
                    "request_id": metadata["request_id"], "reference_time": settings.reference_time,
                    "data_kind": "synthetic demonstration"}
        except (ValueError, TypeError, KeyError, IndexError, AttributeError) as exc:
            LOGGER.warning("Invalid engine response request_id=%s", request.state.request_id)
            raise BusinessError(502, "INVALID_ENGINE_RESPONSE", "Risk service returned an invalid response") from exc

    return app
