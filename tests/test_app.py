from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path


class GeoAppTestCase(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        db_path = Path(self.tempdir.name) / "test.db"

        import os

        os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
        os.environ["GEO_ADMIN_USERNAME"] = "admin"
        os.environ["GEO_ADMIN_PASSWORD"] = "admin123"
        os.environ["DEEPSEEK_USE_MOCK"] = "true"
        os.environ["DOUBAO_USE_MOCK"] = "true"

        from app.api import create_app

        self.app = create_app()
        self.client = self.app.test_client()

    def tearDown(self):
        self.tempdir.cleanup()

    def login(self):
        return self.client.post("/login", data={"username": "admin", "password": "admin123"})

    def test_auth_required(self):
        response = self.client.get("/api/v1/geo/models")
        self.assertEqual(response.status_code, 401)

    def test_user_management_and_async_job(self):
        self.login()

        create_user = self.client.post(
            "/api/v1/admin/users",
            json={"username": "tester", "password": "secret123", "role": "analyst"},
        )
        self.assertEqual(create_user.status_code, 201)
        user_id = create_user.get_json()["id"]

        patch_user = self.client.patch(
            f"/api/v1/admin/users/{user_id}",
            json={"role": "admin", "status": "active", "password": "new-secret123"},
        )
        self.assertEqual(patch_user.status_code, 200)
        self.assertEqual(patch_user.get_json()["role"], "admin")

        job_resp = self.client.post(
            "/api/v1/geo/analyze/async",
            json={
                "query": "测试上海徐汇区夜间活动推荐",
                "model": "deepseek",
                "geo_context": {
                    "location_name": "上海市徐汇区",
                    "coordinates": {"lat": 31.188, "lng": 121.437},
                    "coordinate_system": "WGS84",
                },
            },
        )
        self.assertEqual(job_resp.status_code, 202)
        job_id = job_resp.get_json()["job_id"]

        for _ in range(30):
            job = self.client.get(f"/api/v1/geo/jobs/{job_id}").get_json()
            if job["status"] == "completed":
                break
            time.sleep(0.2)
        self.assertEqual(job["status"], "completed")
        record_id = job["result"]["record_id"]

        export_pdf = self.client.get(f"/api/v1/geo/analyses/{record_id}/export?format=pdf")
        export_xlsx = self.client.get(f"/api/v1/geo/analyses/{record_id}/export?format=xlsx")
        self.assertEqual(export_pdf.status_code, 200)
        self.assertEqual(export_xlsx.status_code, 200)

        audit = self.client.get("/api/v1/admin/audit?actor=admin").get_json()["items"]
        self.assertTrue(len(audit) >= 1)


if __name__ == "__main__":
    unittest.main()
