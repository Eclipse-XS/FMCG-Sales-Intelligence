from fastapi.testclient import TestClient
from fmcg_sales_intelligence.api.app import create_app


def main() -> int:
    client = TestClient(create_app())
    for path in ["/health", "/ready", "/api/v1/contracts", "/api/v1/capabilities", "/api/v1/bi/summary"]:
        client.get(path).raise_for_status()
    print("repository smoke: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
