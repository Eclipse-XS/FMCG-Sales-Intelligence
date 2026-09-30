from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
REPO = Path(os.getenv("FSI_PROJECT_ROOT", str(ROOT.parent.parent)))
sys.path[:0] = [str(ROOT), str(ROOT / "backend/src")]


def unused_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def environment():
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([str(ROOT), str(ROOT / "backend/src"), str(REPO / "src")])
    env["FSI_PROJECT_ROOT"] = str(REPO)
    return env


def wait_http(url, timeout=120):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            if httpx.get(url, timeout=1, trust_env=False).status_code == 200:
                return
        except httpx.RequestError:
            pass
        time.sleep(0.2)
    raise RuntimeError(f"Service did not become ready: {url}")


@contextmanager
def service(arguments, env, logs):
    with Path(logs).open("wb") as output:
        process = subprocess.Popen([sys.executable, *arguments], env=env, cwd=ROOT,
                                   stdout=output, stderr=subprocess.STDOUT,
                                   start_new_session=os.name != "nt")
        try:
            yield process
        finally:
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True)
            else:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


@pytest.fixture(scope="session")
def services(tmp_path_factory):
    if os.getenv("SERVICEDESK_TEST_URL"):
        yield {"backend": os.environ["SERVICEDESK_TEST_URL"], "engine": os.environ["ENGINE_TEST_URL"],
               "registry": os.environ["MLFLOW_TRACKING_URI"], "state": Path(os.environ["DEMO_STATE"]),
               "database": Path(os.environ["TICKET_DATABASE"])}
        return
    state = tmp_path_factory.mktemp("servicedesk")
    registry_port, engine_port, backend_port = unused_port(), unused_port(), unused_port()
    registry, engine, backend = (f"http://127.0.0.1:{p}" for p in (registry_port, engine_port, backend_port))
    env = environment()
    env.update(DEMO_STATE=str(state), MLFLOW_TRACKING_URI=registry, ML_ENGINE_URL=engine,
               TICKET_DATABASE=str(state / "tickets.sqlite"))
    with service(["-m", "mlflow", "server", "--host", "127.0.0.1", "--port", str(registry_port),
                  "--workers", "1", "--backend-store-uri", f"sqlite:///{(state / 'mlflow.db').as_posix()}",
                  "--artifacts-destination", str(state / "artifacts"), "--serve-artifacts"], env, state / "registry.log"):
        wait_http(registry + "/health")
        with (state / "initialization.log").open("wb") as log:
            subprocess.run([sys.executable, str(ROOT / "train.py"), "--state", str(state), "--tracking-uri", registry],
                           env=env, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=240)
        with service(["-m", "uvicorn", "engine_service:create_app", "--factory", "--host", "127.0.0.1", "--port", str(engine_port)], env, state / "engine.log"):
            wait_http(engine + "/api/v1/runtime/ready")
            with service(["-m", "uvicorn", "servicedesk.app:create_app", "--factory", "--host", "127.0.0.1", "--port", str(backend_port)], env, state / "backend.log"):
                wait_http(backend + "/health")
                yield {"backend": backend, "engine": engine, "registry": registry, "state": state, "database": state / "tickets.sqlite"}


@pytest.fixture
def variant_backend(tmp_path, services):
    @contextmanager
    def start(database=None, engine=None, request_timeout=2):
        port = unused_port()
        env = environment()
        env.update(TICKET_DATABASE=str(database or services["database"]),
                   ML_ENGINE_URL=engine or services["engine"], ENGINE_CONNECT_TIMEOUT="0.3",
                   ENGINE_REQUEST_TIMEOUT=str(request_timeout))
        with service(["-m", "uvicorn", "servicedesk.app:create_app", "--factory", "--host", "127.0.0.1", "--port", str(port)], env, tmp_path / f"backend-{port}.log"):
            url = f"http://127.0.0.1:{port}"
            wait_http(url + "/health")
            yield url
    return start
