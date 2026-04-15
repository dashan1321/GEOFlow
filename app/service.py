from __future__ import annotations

from app.config import AppConfig
from app.jobs import JobManager
from app.models.adapters import ModelGateway
from app.persistence.repository import AnalysisRepository
from app.processing.postprocess import Postprocessor
from app.processing.preprocess import Preprocessor


class GeoOptimizationService:
    def __init__(self, config: AppConfig) -> None:
        self.preprocessor = Preprocessor()
        self.gateway = ModelGateway(config)
        self.postprocessor = Postprocessor()
        self.repository = AnalysisRepository(config.database_url, echo=config.sql_echo)
        self.jobs = JobManager(self.repository)
        self.config = config

    def initialize(self) -> None:
        self.repository.initialize()
        self.repository.seed_admin_user(
            username=self.config.admin_username,
            password=self.config.admin_password,
            role="admin",
        )

    def analyze(self, payload: dict, actor: str = "") -> dict:
        query = payload.get("query")
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Field 'query' is required.")

        requested_model = payload.get("model") or self.config.default_model
        normalized = self.preprocessor.run(payload)
        model_response = self.gateway.generate(requested_model, normalized)
        result = self.postprocessor.run(
            original_request=payload,
            normalized_request=normalized,
            model_response=model_response,
        )
        result["record_id"] = self.repository.save_analysis(normalized, result, created_by=actor)
        result["metadata"]["storage"] = {"status": "saved", "record_id": result["record_id"]}
        return result

    def list_recent_analyses(self, limit: int = 20) -> list[dict]:
        return self.repository.list_recent_analyses(limit=limit)

    def supported_models(self) -> list[str]:
        return self.gateway.supported_models()

    def provider_status(self) -> list[dict]:
        return self.gateway.provider_status()

    def get_analysis(self, record_id: int) -> dict | None:
        return self.repository.get_analysis(record_id)

    def submit_async_analysis(self, payload: dict, actor: str = "") -> str:
        return self.jobs.submit(lambda body: self.analyze(body, actor=actor), payload, created_by=actor)

    def get_job(self, job_id: str) -> dict | None:
        return self.jobs.get(job_id)

    def list_jobs(self, limit: int = 50) -> list[dict]:
        return self.jobs.list_jobs(limit=limit)

    def authenticate_user(self, username: str, password: str) -> dict | None:
        return self.repository.authenticate_user(username, password)

    def list_users(self, limit: int = 50) -> list[dict]:
        return self.repository.list_users(limit=limit)

    def create_user(self, username: str, password: str, role: str = "analyst") -> dict:
        return self.repository.create_user(username, password, role=role)

    def update_user(self, user_id: int, *, password: str | None = None, role: str | None = None, status: str | None = None) -> dict | None:
        return self.repository.update_user(user_id, password=password, role=role, status=status)

    def add_audit_log(self, actor: str, action: str, target_type: str = "", target_id: str = "", detail: dict | None = None) -> int:
        return self.repository.add_audit_log(actor, action, target_type, target_id, detail)

    def list_audit_logs(self, limit: int = 100, actor: str = "", action: str = "") -> list[dict]:
        return self.repository.list_audit_logs(limit=limit, actor=actor, action=action)

    def retry_job(self, job_id: str, actor: str = "") -> dict | None:
        return self.jobs.retry(job_id, lambda body: self.analyze(body, actor=actor))
