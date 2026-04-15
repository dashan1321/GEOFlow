from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.api import create_app


def main() -> None:
    app = create_app()
    client = app.test_client()

    health = client.get("/health")
    print("health:", health.status_code)

    unauth = client.get("/api/v1/geo/models")
    print("unauth_models:", unauth.status_code)

    login = client.post("/login", data={"username": "admin", "password": "admin123"})
    print("login:", login.status_code)

    dashboard = client.get("/")
    users = client.get("/admin/users")
    jobs = client.get("/jobs")
    audit = client.get("/admin/audit")

    print("dashboard:", dashboard.status_code)
    print("users:", users.status_code)
    print("jobs:", jobs.status_code)
    print("audit:", audit.status_code)


if __name__ == "__main__":
    main()
