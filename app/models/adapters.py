from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urljoin
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.config import AppConfig, ProviderConfig


@dataclass
class ModelResult:
    provider: str
    content: str
    confidence: float
    metadata: dict[str, Any]


class BaseAdapter:
    provider_name = "base"

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.provider_config = config.provider(self.provider_name)

    def generate(self, normalized_request: dict) -> ModelResult:
        if self.provider_config.use_mock or not self.provider_config.api_url:
            return self._mock_generate(normalized_request)
        return self._remote_generate(normalized_request)

    def _remote_generate(self, normalized_request: dict) -> ModelResult:
        prompt = self._build_messages(normalized_request)
        api_url = self._resolve_api_url()
        payload = {
            "model": self.provider_config.model_name,
            "messages": prompt,
            "temperature": 0.3,
        }
        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.provider_config.api_key:
            headers["Authorization"] = f"Bearer {self.provider_config.api_key}"

        request = Request(
            api_url,
            data=body,
            headers=headers,
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.provider_config.timeout_seconds) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            return ModelResult(
                provider=self.provider_name,
                content=f"{self.provider_name} API 请求失败，状态码 {exc.code}。",
                confidence=0.15,
                metadata={"mode": "remote", "error": "http_error", "status_code": exc.code},
            )
        except URLError as exc:
            return ModelResult(
                provider=self.provider_name,
                content=f"{self.provider_name} API 网络连接失败：{exc.reason}",
                confidence=0.1,
                metadata={"mode": "remote", "error": "network_error"},
            )

        content = self._extract_content(response_payload)
        return ModelResult(
            provider=self.provider_name,
            content=content,
            confidence=0.87,
            metadata={
                "mode": "remote",
                "model_name": self.provider_config.model_name,
                "api_url": api_url,
            },
        )

    def _resolve_api_url(self) -> str:
        if self.provider_config.api_url:
            return self.provider_config.api_url
        if not self.provider_config.base_url:
            return ""

        base_url = self.provider_config.base_url.rstrip("/") + "/"
        return urljoin(base_url, "chat/completions")

    def _build_messages(self, normalized_request: dict) -> list[dict[str, str]]:
        query = normalized_request["query"]
        location = normalized_request["geo_context"].get("location_name") or "未知区域"
        tags = "、".join(normalized_request.get("enriched_tags", [])[:8]) or "无"
        user_profile = json.dumps(normalized_request["user_profile"], ensure_ascii=False)
        geo_context = json.dumps(normalized_request["geo_context"], ensure_ascii=False)
        context_signals = json.dumps(normalized_request["context_signals"], ensure_ascii=False)

        system_prompt = (
            "你是 GEO 智能优化助手。请结合地理位置、坐标、用户画像、天气和时间信息，"
            "输出面向产品系统的分析结论，重点关注推荐策略、地理特征、风险提示和后续可视化要点。"
        )
        user_prompt = (
            f"用户请求：{query}\n"
            f"地理位置：{location}\n"
            f"GEO上下文：{geo_context}\n"
            f"用户画像：{user_profile}\n"
            f"环境信号：{context_signals}\n"
            f"增强标签：{tags}\n"
            "请给出简洁但可执行的分析结果。"
        )
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _extract_content(self, response_payload: dict) -> str:
        choices = response_payload.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            if isinstance(message, dict) and message.get("content"):
                return str(message["content"])
        if response_payload.get("output_text"):
            return str(response_payload["output_text"])
        return "模型已返回响应，但未识别到标准文本字段。"

    def _mock_generate(self, normalized_request: dict) -> ModelResult:
        query = normalized_request["query"]
        location = normalized_request["geo_context"].get("location_name") or "未知区域"
        preferences = normalized_request["user_profile"].get("preferred_categories", [])
        category_hint = "、".join(preferences[:3]) if preferences else "本地生活"
        content = (
            f"已基于 {location} 的地理上下文分析请求“{query}”，"
            f"建议优先围绕 {category_hint} 场景生成结果，并结合附近 POI、天气、时间段做排序。"
        )
        return ModelResult(
            provider=self.provider_name,
            content=content,
            confidence=0.76,
            metadata={
                "mode": "mock",
                "model_name": self.provider_config.model_name,
                "provider_config": {
                    **asdict(self.provider_config),
                    "api_key": bool(self.provider_config.api_key),
                },
            },
        )


class DeepSeekAdapter(BaseAdapter):
    provider_name = "deepseek"


class DoubaoAdapter(BaseAdapter):
    provider_name = "doubao"


class GeminiAdapter(BaseAdapter):
    provider_name = "gemini"


class ModelGateway:
    def __init__(self, config: AppConfig) -> None:
        self.adapters = {
            "deepseek": DeepSeekAdapter(config),
            "doubao": DoubaoAdapter(config),
            "gemini": GeminiAdapter(config),
        }

    def generate(self, model_name: str, normalized_request: dict) -> ModelResult:
        adapter = self.adapters.get(str(model_name).lower())
        if adapter is None:
            supported = ", ".join(sorted(self.adapters))
            raise ValueError(f"Unsupported model '{model_name}'. Supported: {supported}.")
        return adapter.generate(normalized_request)

    def supported_models(self) -> list[str]:
        return sorted(self.adapters)

    def provider_status(self) -> list[dict[str, Any]]:
        statuses = []
        for name, adapter in sorted(self.adapters.items()):
            provider_config = adapter.provider_config
            statuses.append(
                {
                    "provider": name,
                    "model_name": provider_config.model_name,
                    "use_mock": provider_config.use_mock,
                    "base_url": provider_config.base_url,
                    "api_url": provider_config.api_url or adapter._resolve_api_url(),
                    "has_api_key": bool(provider_config.api_key),
                }
            )
        return statuses
