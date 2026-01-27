import json
import os
from typing import Any, Dict

from config import BACKEND_DIR

CONFIG_PATH = os.path.join(BACKEND_DIR, "llm_config.json")

DEFAULT_CONFIG: Dict[str, Any] = {
    "enabled": False,
    "provider": "openai",
    "model": "",
    "api_base": "http://localhost:8080/v1",
    "api_key": "",
    "temperature": 0.2,
    "max_tokens": 512,
}


def load_config() -> Dict[str, Any]:
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        merged = DEFAULT_CONFIG.copy()
        merged.update({k: v for k, v in data.items() if k in DEFAULT_CONFIG})
        return merged
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(new_data: Dict[str, Any]) -> Dict[str, Any]:
    current = load_config()
    updated = current.copy()
    for key, value in new_data.items():
        if key not in DEFAULT_CONFIG:
            continue
        if key == "api_key":
            if value:
                updated[key] = value
            continue
        updated[key] = value

    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as handle:
        json.dump(updated, handle, indent=2)
    return updated


def public_config(config: Dict[str, Any]) -> Dict[str, Any]:
    safe = config.copy()
    safe["has_api_key"] = bool(safe.get("api_key"))
    safe["api_key"] = "********" if safe.get("api_key") else ""
    return safe
