from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import desc, text
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import Base, create_session_factory
from app.persistence.models import AnalysisRecord, AuditLogRecord, JobRecord, UserRecord


class AnalysisRepository:
    def __init__(self, database_url: str, echo: bool = False) -> None:
        self.engine, self.session_factory = create_session_factory(database_url, echo=echo)

    def initialize(self) -> None:
        if self.engine.dialect.name == "postgresql":
            with self.engine.begin() as connection:
                connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        Base.metadata.create_all(self.engine)
        self._ensure_analysis_columns()
        if self.engine.dialect.name == "postgresql":
            with self.engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE analysis_records "
                        "ADD COLUMN IF NOT EXISTS geom geometry(Point, 4326)"
                    )
                )

    def _ensure_analysis_columns(self) -> None:
        inspector_sql = text("PRAGMA table_info(analysis_records)")
        with self.engine.begin() as connection:
            if self.engine.dialect.name == "sqlite":
                rows = connection.execute(inspector_sql).fetchall()
                existing = {row[1] for row in rows}
                if "created_by" not in existing:
                    connection.execute(
                        text("ALTER TABLE analysis_records ADD COLUMN created_by VARCHAR(64) NOT NULL DEFAULT ''")
                    )
            elif self.engine.dialect.name == "postgresql":
                connection.execute(
                    text(
                        "ALTER TABLE analysis_records "
                        "ADD COLUMN IF NOT EXISTS created_by VARCHAR(64) NOT NULL DEFAULT ''"
                    )
                )

    def seed_admin_user(self, username: str, password: str, role: str = "admin") -> None:
        with self.session_factory() as session:
            existing = session.query(UserRecord).filter(UserRecord.username == username).first()
            if existing is None:
                session.add(
                    UserRecord(
                        username=username,
                        password_hash=generate_password_hash(password),
                        role=role,
                        status="active",
                    )
                )
                session.commit()

    def authenticate_user(self, username: str, password: str) -> dict | None:
        with self.session_factory() as session:
            user = session.query(UserRecord).filter(UserRecord.username == username).first()
            if user is None or user.status != "active":
                return None
            if not check_password_hash(user.password_hash, password):
                return None
            return {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "status": user.status,
            }

    def list_users(self, limit: int = 50) -> list[dict]:
        with self.session_factory() as session:
            users = session.query(UserRecord).order_by(UserRecord.created_at.desc()).limit(limit).all()
        return [
            {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "status": user.status,
                "created_at": user.created_at.isoformat() + "Z",
            }
            for user in users
        ]

    def create_user(self, username: str, password: str, role: str = "analyst") -> dict:
        with self.session_factory() as session:
            existing = session.query(UserRecord).filter(UserRecord.username == username).first()
            if existing is not None:
                raise ValueError("Username already exists.")
            user = UserRecord(
                username=username,
                password_hash=generate_password_hash(password),
                role=role,
                status="active",
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "status": user.status,
                "created_at": user.created_at.isoformat() + "Z",
            }

    def update_user(
        self,
        user_id: int,
        *,
        password: str | None = None,
        role: str | None = None,
        status: str | None = None,
    ) -> dict | None:
        with self.session_factory() as session:
            user = session.get(UserRecord, user_id)
            if user is None:
                return None
            if password:
                user.password_hash = generate_password_hash(password)
            if role:
                user.role = role
            if status:
                user.status = status
            session.commit()
            return {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "status": user.status,
                "created_at": user.created_at.isoformat() + "Z",
            }

    def save_analysis(self, normalized_request: dict, response_payload: dict, created_by: str = "") -> int:
        geo_context = normalized_request.get("geo_context", {})
        coordinates = geo_context.get("normalized_coordinates", {})
        lat = coordinates.get("lat")
        lng = coordinates.get("lng")
        geom_wkt = None
        if lat is not None and lng is not None:
            geom_wkt = f"POINT({lng} {lat})"

        record = AnalysisRecord(
            query=normalized_request.get("query", ""),
            model=response_payload.get("model", ""),
            location_name=geo_context.get("location_name", ""),
            latitude=lat,
            longitude=lng,
            coordinate_system=coordinates.get("coordinate_system") or "WGS84",
            geom_wkt=geom_wkt,
            normalized_request_json=json.dumps(normalized_request, ensure_ascii=False),
            response_json=json.dumps(response_payload, ensure_ascii=False),
            created_by=created_by,
        )

        with self.session_factory() as session:
            session.add(record)
            session.commit()
            session.refresh(record)
            if self.engine.dialect.name == "postgresql" and geom_wkt is not None:
                session.execute(
                    text(
                        "UPDATE analysis_records "
                        "SET geom = ST_GeomFromText(:geom_wkt, 4326) "
                        "WHERE id = :record_id"
                    ),
                    {"geom_wkt": geom_wkt, "record_id": record.id},
                )
                session.commit()
            return int(record.id)

    def list_recent_analyses(self, limit: int = 20) -> list[dict]:
        with self.session_factory() as session:
            records = (
                session.query(AnalysisRecord)
                .order_by(desc(AnalysisRecord.created_at))
                .limit(limit)
                .all()
            )
        return [
            {
                "id": record.id,
                "query": record.query,
                "model": record.model,
                "location_name": record.location_name,
                "latitude": record.latitude,
                "longitude": record.longitude,
                "coordinate_system": record.coordinate_system,
                "created_by": record.created_by,
                "created_at": record.created_at.isoformat() + "Z",
            }
            for record in records
        ]

    def get_analysis(self, record_id: int) -> dict | None:
        with self.session_factory() as session:
            record = session.get(AnalysisRecord, record_id)
            if record is None:
                return None
        normalized_request = json.loads(record.normalized_request_json)
        response_payload = json.loads(record.response_json)
        return {
            "id": record.id,
            "query": record.query,
            "model": record.model,
            "location_name": record.location_name,
            "latitude": record.latitude,
            "longitude": record.longitude,
            "coordinate_system": record.coordinate_system,
            "geom_wkt": record.geom_wkt,
            "created_by": record.created_by,
            "created_at": record.created_at.isoformat() + "Z",
            "normalized_request": normalized_request,
            "response": response_payload,
        }

    def create_job(self, job_id: str, payload: dict, created_by: str = "", max_retries: int = 2) -> dict:
        record = JobRecord(
            id=job_id,
            status="queued",
            payload_json=json.dumps(payload, ensure_ascii=False),
            result_json=None,
            error_json=None,
            retries=0,
            max_retries=max_retries,
            created_by=created_by,
            updated_at=datetime.utcnow(),
        )
        with self.session_factory() as session:
            session.add(record)
            session.commit()
        return self.get_job(job_id)

    def update_job(self, job_id: str, **changes) -> dict | None:
        with self.session_factory() as session:
            record = session.get(JobRecord, job_id)
            if record is None:
                return None
            if "status" in changes:
                record.status = changes["status"]
            if "result" in changes:
                record.result_json = json.dumps(changes["result"], ensure_ascii=False)
            if "error" in changes:
                record.error_json = json.dumps(changes["error"], ensure_ascii=False)
            if "retries" in changes:
                record.retries = changes["retries"]
            record.updated_at = datetime.utcnow()
            session.commit()
        return self.get_job(job_id)

    def get_job(self, job_id: str) -> dict | None:
        with self.session_factory() as session:
            record = session.get(JobRecord, job_id)
            if record is None:
                return None
            return {
                "id": record.id,
                "status": record.status,
                "payload": json.loads(record.payload_json),
                "result": json.loads(record.result_json) if record.result_json else None,
                "error": json.loads(record.error_json) if record.error_json else None,
                "retries": record.retries,
                "max_retries": record.max_retries,
                "created_by": record.created_by,
                "created_at": record.created_at.isoformat() + "Z",
                "updated_at": record.updated_at.isoformat() + "Z",
            }

    def list_jobs(self, limit: int = 50) -> list[dict]:
        with self.session_factory() as session:
            records = session.query(JobRecord).order_by(desc(JobRecord.created_at)).limit(limit).all()
        return [
            {
                "id": record.id,
                "status": record.status,
                "retries": record.retries,
                "max_retries": record.max_retries,
                "created_by": record.created_by,
                "created_at": record.created_at.isoformat() + "Z",
                "updated_at": record.updated_at.isoformat() + "Z",
            }
            for record in records
        ]

    def retry_job(self, job_id: str) -> dict | None:
        with self.session_factory() as session:
            record = session.get(JobRecord, job_id)
            if record is None:
                return None
            record.status = "queued"
            record.error_json = None
            record.updated_at = datetime.utcnow()
            session.commit()
        return self.get_job(job_id)

    def add_audit_log(
        self,
        actor: str,
        action: str,
        target_type: str = "",
        target_id: str = "",
        detail: dict | None = None,
    ) -> int:
        record = AuditLogRecord(
            actor=actor or "system",
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail_json=json.dumps(detail or {}, ensure_ascii=False),
        )
        with self.session_factory() as session:
            session.add(record)
            session.commit()
            session.refresh(record)
            return int(record.id)

    def list_audit_logs(self, limit: int = 100, actor: str = "", action: str = "") -> list[dict]:
        with self.session_factory() as session:
            query = session.query(AuditLogRecord)
            if actor:
                query = query.filter(AuditLogRecord.actor == actor)
            if action:
                query = query.filter(AuditLogRecord.action == action)
            records = query.order_by(desc(AuditLogRecord.created_at)).limit(limit).all()
        return [
            {
                "id": record.id,
                "actor": record.actor,
                "action": record.action,
                "target_type": record.target_type,
                "target_id": record.target_id,
                "detail": json.loads(record.detail_json),
                "created_at": record.created_at.isoformat() + "Z",
            }
            for record in records
        ]
