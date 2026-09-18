from __future__ import annotations

import logging
import time
import uuid
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

from .. import __version__
from ..analytics import AnalyticsReadService, BusinessIntelligenceService
from ..capabilities import evaluate_capabilities
from ..contracts import load_registry
from ..domain_packs import DomainPackRegistry
from ..serving import ForecastService, FrozenModelRegistry, StockoutService
from .schemas import BatchRequest, ContractRowsRequest
from .settings import Settings


LOGGER = logging.getLogger("fsi.api")
REQUESTS = Counter("fsi_http_requests_total", "HTTP requests", ["method", "route", "status"])
LATENCY = Histogram("fsi_http_request_duration_seconds", "HTTP request latency", ["route"])
INFERENCE = Counter("fsi_inference_rows_total", "Inference rows", ["model", "status"])
READY = Gauge("fsi_model_ready", "Frozen model readiness", ["model"])


def create_app(settings: Settings | None = None, artifact_root: str | Path | None = None) -> FastAPI:
    settings = settings or Settings()
    registry = FrozenModelRegistry(artifact_root or settings.artifact_root)
    contracts, packs, analytics, bi = (
        load_registry(),
        DomainPackRegistry(),
        AnalyticsReadService(),
        BusinessIntelligenceService(),
    )
    forecast, stockout = ForecastService(registry), StockoutService(registry)
    for name, record in registry.records.items():
        READY.labels(model=name).set(1 if record.ready else 0)

    application = FastAPI(
        title="FMCG Sales Intelligence API",
        version=__version__,
        description="Company-agnostic local API for canonical contracts, frozen predictions, and reviewed analytics.",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[x.strip() for x in settings.cors_origins.split(",")],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-Request-ID"],
    )

    @application.middleware("http")
    async def telemetry(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            LOGGER.exception("request_failed", extra={"request_id": request_id, "route": request.url.path})
            response = JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "Request failed",
                        "details": None,
                        "request_id": request_id,
                    }
                },
            )
        elapsed = time.perf_counter() - started
        response.headers["X-Request-ID"] = request_id
        route = request.url.path
        REQUESTS.labels(request.method, route, str(response.status_code)).inc()
        LATENCY.labels(route).observe(elapsed)
        LOGGER.info(
            "request_complete",
            extra={
                "request_id": request_id,
                "route": route,
                "status": response.status_code,
                "latency_seconds": elapsed,
            },
        )
        return response

    @application.exception_handler(ValueError)
    async def value_error(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "INVALID_INPUT",
                    "message": str(exc),
                    "details": None,
                    "request_id": getattr(request.state, "request_id", "unknown"),
                }
            },
        )

    @application.get("/health", summary="Process liveness")
    def health():
        return {"status": "alive", "service": "fmcg-sales-intelligence"}

    @application.get("/ready", summary="Frozen-model readiness")
    def ready():
        payload = {
            "status": "ready" if registry.ready else "not_ready",
            "models": registry.metadata(),
            "mlflow_required": settings.mlflow_required_for_readiness,
        }
        return JSONResponse(status_code=200 if registry.ready else 503, content=payload)

    @application.get("/version", summary="Application version")
    def version():
        return {"version": __version__, "api": "v1", "active_domain_pack": settings.active_domain_pack}

    @application.get("/metrics", include_in_schema=False)
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @application.get("/api/v1/models", summary="List safe frozen-model metadata")
    def models():
        return {"items": registry.metadata()}

    @application.get("/api/v1/models/{model_name}", summary="Get frozen-model metadata")
    def model(model_name: str):
        try:
            return registry.get(model_name).public_metadata()
        except KeyError:
            raise HTTPException(404, "Unknown model")

    @application.get("/api/v1/contracts", summary="List canonical contracts")
    def contract_list():
        return {"registry_version": contracts.payload["registry_version"], "items": contracts.list()}

    @application.get("/api/v1/contracts/{contract_id}", summary="Describe a canonical contract")
    def contract(contract_id: str):
        try:
            return contracts.get(contract_id)
        except KeyError:
            raise HTTPException(404, "Unknown contract")

    @application.get("/api/v1/domain-packs", summary="List safe company/domain profiles")
    def domain_packs():
        return {"items": packs.list(), "active": settings.active_domain_pack}

    @application.get("/api/v1/domain-packs/{profile_id}", summary="Describe a safe company/domain profile")
    def domain_pack(profile_id: str):
        try:
            return packs.get(profile_id)
        except KeyError:
            raise HTTPException(404, "Unknown domain pack")

    @application.get("/api/v1/capabilities", summary="Evaluate active profile capabilities")
    def capabilities(profile_id: str | None = None):
        try:
            profile = packs.get(profile_id or settings.active_domain_pack)
        except KeyError:
            raise HTTPException(404, "Unknown domain pack")
        return {"profile_id": profile["profile_id"], "items": evaluate_capabilities(profile["contracts"])}

    @application.post("/api/v1/data/validate", summary="Validate small normalized rows against a contract")
    def validate_data(body: ContractRowsRequest):
        try:
            return contracts.validate(body.contract_id, pd.DataFrame(body.rows)).as_dict()
        except KeyError:
            raise HTTPException(404, "Unknown contract")

    @application.post("/api/v1/predict/forecast", summary="Predict aggregate realized units in (t,t+7d]")
    def predict_forecast(body: BatchRequest):
        values = forecast.predict(body.rows)
        INFERENCE.labels("forecasting", "success").inc(len(values))
        return {"items": values}

    @application.post("/api/v1/predict/stockout", summary="Score stockout occurrence within (t,t+7d]")
    def predict_stockout(body: BatchRequest):
        values = stockout.predict(body.rows)
        INFERENCE.labels("stockout_classification", "success").inc(len(values))
        return {"items": values}

    @application.get("/api/v1/analytics/{name}", summary="Read frozen offline analytical outputs")
    def read_analytics(name: str, offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500)):
        try:
            return analytics.read(name, offset, limit)
        except KeyError:
            raise HTTPException(404, "Unknown analytical output")

    @application.get("/api/v1/bi/summary", summary="Read supported sales KPI summary")
    def bi_summary():
        return bi.summary()

    @application.get("/api/v1/bi/timeseries", summary="Read aggregate sales time series")
    def bi_timeseries(limit: int = Query(120, ge=1, le=366)):
        return {"items": bi.timeseries(limit)}

    @application.get(
        "/api/v1/bi/breakdown/{dimension}", summary="Read a supported dimensional sales breakdown"
    )
    def bi_breakdown(dimension: str, limit: int = Query(20, ge=1, le=100)):
        return {"dimension": dimension, "items": bi.breakdown(dimension, limit)}

    return application


app = create_app()
