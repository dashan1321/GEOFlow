from __future__ import annotations

import os
from dataclasses import dataclass, field


def _load_dotenv(dotenv_path: str = ".env") -> None:
    if not os.path.exists(dotenv_path):
        return

    with open(dotenv_path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("'").strip('"'))


_load_dotenv()


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class ProviderConfig:
    base_url: str
    api_url: str
    api_key: str
    model_name: str
    use_mock: bool
    timeout_seconds: int = 30


@dataclass(frozen=True)
class AppConfig:
    host: str = field(default_factory=lambda: os.getenv("GEO_APP_HOST", "127.0.0.1"))
    port: int = field(default_factory=lambda: int(os.getenv("GEO_APP_PORT", "5000")))
    default_model: str = field(default_factory=lambda: os.getenv("GEO_DEFAULT_MODEL", "deepseek"))
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///geo_optimizer.db"))
    sql_echo: bool = field(default_factory=lambda: _env_flag("GEO_SQL_ECHO", False))
    secret_key: str = field(default_factory=lambda: os.getenv("GEO_SECRET_KEY", "dev-secret-key"))
    admin_username: str = field(default_factory=lambda: os.getenv("GEO_ADMIN_USERNAME", "admin"))
    admin_password: str = field(default_factory=lambda: os.getenv("GEO_ADMIN_PASSWORD", "admin123"))

    doubao_base_url: str = field(default_factory=lambda: os.getenv("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"))
    doubao_api_url: str = field(default_factory=lambda: os.getenv("DOUBAO_API_URL", ""))
    doubao_api_key: str = field(default_factory=lambda: os.getenv("DOUBAO_API_KEY", ""))
    doubao_model_name: str = field(default_factory=lambda: os.getenv("DOUBAO_MODEL_NAME", "doubao-seed-1-6"))
    doubao_use_mock: bool = field(default_factory=lambda: _env_flag("DOUBAO_USE_MOCK", True))

    deepseek_base_url: str = field(default_factory=lambda: os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"))
    deepseek_api_url: str = field(default_factory=lambda: os.getenv("DEEPSEEK_API_URL", ""))
    deepseek_api_key: str = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY", ""))
    deepseek_model_name: str = field(default_factory=lambda: os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-chat"))
    deepseek_use_mock: bool = field(default_factory=lambda: _env_flag("DEEPSEEK_USE_MOCK", True))

    gemini_base_url: str = field(default_factory=lambda: os.getenv("GEMINI_BASE_URL", ""))
    gemini_api_url: str = field(default_factory=lambda: os.getenv("GEMINI_API_URL", ""))
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    gemini_model_name: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-pro"))
    gemini_use_mock: bool = field(default_factory=lambda: _env_flag("GEMINI_USE_MOCK", True))

    def provider(self, provider_name: str) -> ProviderConfig:
        normalized = provider_name.lower()
        if normalized == "doubao":
            return ProviderConfig(
                base_url=self.doubao_base_url,
                api_url=self.doubao_api_url,
                api_key=self.doubao_api_key,
                model_name=self.doubao_model_name,
                use_mock=self.doubao_use_mock,
            )
        if normalized == "deepseek":
            return ProviderConfig(
                base_url=self.deepseek_base_url,
                api_url=self.deepseek_api_url,
                api_key=self.deepseek_api_key,
                model_name=self.deepseek_model_name,
                use_mock=self.deepseek_use_mock,
            )
        if normalized == "gemini":
            return ProviderConfig(
                base_url=self.gemini_base_url,
                api_url=self.gemini_api_url,
                api_key=self.gemini_api_key,
                model_name=self.gemini_model_name,
                use_mock=self.gemini_use_mock,
            )
        raise ValueError(f"Unsupported provider '{provider_name}'.")
