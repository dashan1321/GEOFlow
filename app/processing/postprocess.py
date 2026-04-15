from __future__ import annotations

from app.models.adapters import ModelResult


class Postprocessor:
    def run(
        self,
        original_request: dict,
        normalized_request: dict,
        model_response: ModelResult,
    ) -> dict:
        geo_context = normalized_request["geo_context"]
        user_profile = normalized_request["user_profile"]
        context_signals = normalized_request["context_signals"]

        recommendations = self._build_recommendations(
            geo_context=geo_context,
            user_profile=user_profile,
            context_signals=context_signals,
        )

        return {
            "query": normalized_request["query"],
            "model": model_response.provider,
            "analysis": model_response.content,
            "confidence": model_response.confidence,
            "recommendations": recommendations,
            "normalized_geo_context": geo_context,
            "enriched_tags": normalized_request["enriched_tags"],
            "visualization": {
                "map_center": geo_context["normalized_coordinates"],
                "layers": ["poi_heatmap", "region_boundary", "recommendation_markers"],
            },
            "metadata": {
                "adapter": model_response.metadata,
                "request_has_user_profile": bool(original_request.get("user_profile")),
                "storage": {"status": "pending"},
            },
        }

    def _build_recommendations(
        self,
        geo_context: dict,
        user_profile: dict,
        context_signals: dict,
    ) -> list[dict]:
        location_name = geo_context.get("location_name") or "当前区域"
        categories = user_profile.get("preferred_categories") or ["本地服务"]
        weather = context_signals.get("weather") or "未知天气"
        time_of_day = context_signals.get("time_of_day") or "当前时段"

        return [
            {
                "title": f"{location_name} 周边候选推荐",
                "reason": f"结合 {weather} 与 {time_of_day} 条件优先筛选。",
                "focus_category": categories[0],
            },
            {
                "title": f"{location_name} 用户画像补全建议",
                "reason": "建议补充停留时长、出行方式与消费偏好，提升推荐质量。",
                "focus_category": categories[min(1, len(categories) - 1)],
            },
        ]
