from __future__ import annotations


class Preprocessor:
    SUPPORTED_COORDINATE_SYSTEMS = {"WGS84", "GCJ-02", "BD-09", "UTM"}

    def run(self, payload: dict) -> dict:
        cleaned = {
            "query": str(payload.get("query", "")).strip(),
            "geo_context": self._normalize_geo_context(payload.get("geo_context", {})),
            "user_profile": self._normalize_user_profile(payload.get("user_profile", {})),
            "context_signals": self._normalize_context_signals(payload.get("context_signals", {})),
        }
        cleaned["enriched_tags"] = self._build_enriched_tags(cleaned)
        return cleaned

    def _normalize_geo_context(self, geo_context: dict) -> dict:
        if not isinstance(geo_context, dict):
            geo_context = {}

        coordinates = geo_context.get("coordinates", {})
        lat = self._safe_float(coordinates.get("lat"))
        lng = self._safe_float(coordinates.get("lng"))
        coordinate_system = str(geo_context.get("coordinate_system", "WGS84")).upper()
        if coordinate_system not in self.SUPPORTED_COORDINATE_SYSTEMS:
            coordinate_system = "WGS84"

        return {
            "location_name": str(geo_context.get("location_name", "")).strip(),
            "coordinates": {
                "lat": lat,
                "lng": lng,
            },
            "coordinate_system": coordinate_system,
            "normalized_coordinates": self._convert_coordinates(lat, lng, coordinate_system),
        }

    def _normalize_user_profile(self, user_profile: dict) -> dict:
        if not isinstance(user_profile, dict):
            user_profile = {}

        categories = user_profile.get("preferred_categories", [])
        if not isinstance(categories, list):
            categories = []

        return {
            "preferred_categories": [str(item).strip() for item in categories if str(item).strip()],
            "history_summary": str(user_profile.get("history_summary", "")).strip(),
        }

    def _normalize_context_signals(self, context_signals: dict) -> dict:
        if not isinstance(context_signals, dict):
            context_signals = {}

        return {
            "weather": str(context_signals.get("weather", "")).strip(),
            "time_of_day": str(context_signals.get("time_of_day", "")).strip(),
            "event": str(context_signals.get("event", "")).strip(),
        }

    def _build_enriched_tags(self, cleaned: dict) -> list[str]:
        tags = []
        geo_context = cleaned["geo_context"]
        context_signals = cleaned["context_signals"]
        user_profile = cleaned["user_profile"]

        if geo_context.get("location_name"):
            tags.append(f"region:{geo_context['location_name']}")
        if context_signals.get("weather"):
            tags.append(f"weather:{context_signals['weather']}")
        if context_signals.get("time_of_day"):
            tags.append(f"time:{context_signals['time_of_day']}")
        for category in user_profile.get("preferred_categories", [])[:5]:
            tags.append(f"pref:{category}")
        return tags

    def _convert_coordinates(self, lat: float | None, lng: float | None, coordinate_system: str) -> dict:
        if lat is None or lng is None:
            return {"lat": None, "lng": None, "coordinate_system": coordinate_system}

        # Placeholder conversion hook for future GIS integration.
        return {
            "lat": round(lat, 6),
            "lng": round(lng, 6),
            "coordinate_system": coordinate_system,
        }

    @staticmethod
    def _safe_float(value) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
