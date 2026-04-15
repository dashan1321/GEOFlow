from __future__ import annotations

from flask import Flask, Response, jsonify, redirect, render_template, request, session, url_for

from app.auth import admin_required, current_user, is_authenticated, login_required
from app.config import AppConfig
from app.exporters import export_analysis_excel, export_analysis_json, export_analysis_pdf
from app.service import GeoOptimizationService


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["APP_SETTINGS"] = AppConfig()
    app.secret_key = app.config["APP_SETTINGS"].secret_key
    app.config["SERVICE"] = GeoOptimizationService(app.config["APP_SETTINGS"])
    app.config["SERVICE"].initialize()

    def base_template_context() -> dict:
        return {
            "default_model": app.config["APP_SETTINGS"].default_model,
            "supported_models": app.config["SERVICE"].supported_models(),
            "authenticated": is_authenticated(),
            "current_user": current_user(),
        }

    @app.before_request
    def protect_routes():
        allowed_endpoints = {"login_page", "login_submit", "health", "static"}
        if request.endpoint in allowed_endpoints:
            return None
        if not is_authenticated():
            if request.path.startswith("/api/"):
                return jsonify({"error": "Authentication required."}), 401
            return redirect(url_for("login_page", next=request.path))
        return None

    @app.get("/login")
    def login_page():
        if is_authenticated():
            return redirect(url_for("index"))
        return render_template("login.html", page="login", error=None, **base_template_context())

    @app.post("/login")
    def login_submit():
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = app.config["SERVICE"].authenticate_user(username, password)
        if user is not None:
            session["authenticated"] = True
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            app.config["SERVICE"].add_audit_log(
                actor=user["username"],
                action="auth.login",
                target_type="user",
                target_id=str(user["id"]),
            )
            next_url = request.args.get("next") or url_for("index")
            return redirect(next_url)
        return render_template(
            "login.html",
            page="login",
            error="用户名或密码不正确。",
            **base_template_context(),
        ), 401

    @app.post("/logout")
    def logout():
        if is_authenticated():
            app.config["SERVICE"].add_audit_log(
                actor=session.get("username", "unknown"),
                action="auth.logout",
                target_type="user",
                target_id=str(session.get("user_id", "")),
            )
        session.clear()
        return redirect(url_for("login_page"))

    @app.get("/")
    @login_required
    def index():
        return render_template("dashboard.html", page="dashboard", **base_template_context())

    @app.get("/history")
    @login_required
    def history_page():
        return render_template("history.html", page="history", **base_template_context())

    @app.get("/settings")
    @login_required
    def settings_page():
        return render_template("settings.html", page="settings", **base_template_context())

    @app.get("/jobs")
    @admin_required
    def jobs_page():
        return render_template("jobs.html", page="jobs", **base_template_context())

    @app.get("/jobs/<job_id>")
    @admin_required
    def job_detail_page(job_id: str):
        job = app.config["SERVICE"].get_job(job_id)
        if job is None:
            return render_template("404.html", page="jobs", **base_template_context()), 404
        return render_template("job_detail.html", page="jobs", job=job, **base_template_context())

    @app.get("/admin/users")
    @admin_required
    def users_page():
        return render_template("users.html", page="users", **base_template_context())

    @app.get("/admin/audit")
    @admin_required
    def audit_page():
        return render_template("audit.html", page="audit", **base_template_context())

    @app.get("/history/<int:record_id>")
    @login_required
    def history_detail_page(record_id: int):
        record = app.config["SERVICE"].get_analysis(record_id)
        if record is None:
            return render_template("404.html", page="history", **base_template_context()), 404
        return render_template(
            "analysis_detail.html",
            page="history",
            record=record,
            **base_template_context(),
        )

    @app.get("/health")
    def health() -> tuple[dict[str, str], int]:
        return {"status": "ok"}, 200

    @app.get("/api/v1/geo/models")
    @login_required
    def geo_models():
        return jsonify(
            {
                "default_model": app.config["APP_SETTINGS"].default_model,
                "models": app.config["SERVICE"].supported_models(),
            }
        )

    @app.get("/api/v1/geo/providers")
    @login_required
    def geo_providers():
        return jsonify({"items": app.config["SERVICE"].provider_status()})

    @app.get("/api/v1/geo/analyses")
    @login_required
    def recent_analyses():
        limit = request.args.get("limit", default=20, type=int)
        limit = max(1, min(limit, 100))
        return jsonify({"items": app.config["SERVICE"].list_recent_analyses(limit=limit)})

    @app.get("/api/v1/admin/users")
    @admin_required
    def admin_users():
        return jsonify({"items": app.config["SERVICE"].list_users()})

    @app.post("/api/v1/admin/users")
    @admin_required
    def admin_create_user():
        payload = request.get_json(silent=True) or {}
        username = str(payload.get("username", "")).strip()
        password = str(payload.get("password", "")).strip()
        role = str(payload.get("role", "analyst")).strip() or "analyst"
        if not username or not password:
            return jsonify({"error": "Username and password are required."}), 400
        try:
            user = app.config["SERVICE"].create_user(username, password, role=role)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        app.config["SERVICE"].add_audit_log(
            actor=session.get("username", "unknown"),
            action="admin.user.create",
            target_type="user",
            target_id=str(user["id"]),
            detail={"username": user["username"], "role": user["role"]},
        )
        return jsonify(user), 201

    @app.patch("/api/v1/admin/users/<int:user_id>")
    @admin_required
    def admin_update_user(user_id: int):
        payload = request.get_json(silent=True) or {}
        user = app.config["SERVICE"].update_user(
            user_id,
            password=str(payload.get("password", "")).strip() or None,
            role=str(payload.get("role", "")).strip() or None,
            status=str(payload.get("status", "")).strip() or None,
        )
        if user is None:
            return jsonify({"error": "User not found."}), 404
        app.config["SERVICE"].add_audit_log(
            actor=session.get("username", "unknown"),
            action="admin.user.update",
            target_type="user",
            target_id=str(user_id),
            detail={k: v for k, v in payload.items() if k in {"role", "status"} and v},
        )
        return jsonify(user)

    @app.get("/api/v1/admin/jobs")
    @admin_required
    def admin_jobs():
        limit = request.args.get("limit", default=50, type=int)
        return jsonify({"items": app.config["SERVICE"].list_jobs(limit=limit)})

    @app.get("/api/v1/admin/jobs/<job_id>")
    @admin_required
    def admin_job_detail(job_id: str):
        job = app.config["SERVICE"].get_job(job_id)
        if job is None:
            return jsonify({"error": "Job not found."}), 404
        return jsonify(job)

    @app.post("/api/v1/admin/jobs/<job_id>/retry")
    @admin_required
    def admin_retry_job(job_id: str):
        job = app.config["SERVICE"].retry_job(job_id, actor=session.get("username", ""))
        if job is None:
            return jsonify({"error": "Job not found."}), 404
        app.config["SERVICE"].add_audit_log(
            actor=session.get("username", "unknown"),
            action="admin.job.retry",
            target_type="job",
            target_id=job_id,
        )
        return jsonify(job), 202

    @app.get("/api/v1/admin/audit")
    @admin_required
    def admin_audit():
        limit = request.args.get("limit", default=100, type=int)
        actor = request.args.get("actor", default="", type=str)
        action = request.args.get("action", default="", type=str)
        return jsonify({"items": app.config["SERVICE"].list_audit_logs(limit=limit, actor=actor, action=action)})

    @app.get("/api/v1/geo/analyses/<int:record_id>")
    @login_required
    def analysis_detail(record_id: int):
        record = app.config["SERVICE"].get_analysis(record_id)
        if record is None:
            return jsonify({"error": "Record not found."}), 404
        return jsonify(record)

    @app.get("/api/v1/geo/analyses/<int:record_id>/export")
    @login_required
    def export_analysis(record_id: int):
        record = app.config["SERVICE"].get_analysis(record_id)
        if record is None:
            return jsonify({"error": "Record not found."}), 404
        app.config["SERVICE"].add_audit_log(
            actor=session.get("username", "unknown"),
            action="analysis.export",
            target_type="analysis",
            target_id=str(record_id),
            detail={"format": request.args.get("format", "json")},
        )

        format_name = request.args.get("format", "json").lower()
        if format_name == "json":
            payload = export_analysis_json(record)
            mimetype = "application/json"
            filename = f"geo-analysis-{record_id}.json"
        elif format_name == "xlsx":
            payload = export_analysis_excel(record)
            mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"geo-analysis-{record_id}.xlsx"
        elif format_name == "pdf":
            payload = export_analysis_pdf(record)
            mimetype = "application/pdf"
            filename = f"geo-analysis-{record_id}.pdf"
        else:
            return jsonify({"error": "Unsupported export format."}), 400

        return Response(
            payload,
            mimetype=mimetype,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    @app.post("/api/v1/geo/analyze")
    @login_required
    def analyze_geo():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Invalid JSON payload."}), 400

        try:
            result = app.config["SERVICE"].analyze(payload, actor=session.get("username", ""))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        app.config["SERVICE"].add_audit_log(
            actor=session.get("username", "unknown"),
            action="analysis.sync",
            target_type="analysis",
            target_id=str(result["record_id"]),
            detail={"model": result["model"]},
        )

        return jsonify(result), 200

    @app.post("/api/v1/geo/analyze/async")
    @login_required
    def analyze_geo_async():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Invalid JSON payload."}), 400
        try:
            job_id = app.config["SERVICE"].submit_async_analysis(payload, actor=session.get("username", ""))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        app.config["SERVICE"].add_audit_log(
            actor=session.get("username", "unknown"),
            action="analysis.async.submit",
            target_type="job",
            target_id=job_id,
            detail={"query": payload.get("query", "")},
        )
        return jsonify({"job_id": job_id, "status": "queued"}), 202

    @app.get("/api/v1/geo/jobs/<job_id>")
    @login_required
    def job_status(job_id: str):
        job = app.config["SERVICE"].get_job(job_id)
        if job is None:
            return jsonify({"error": "Job not found."}), 404
        return jsonify(job)

    return app
