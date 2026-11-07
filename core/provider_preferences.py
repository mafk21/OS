"""User-visible non-secret routing preferences."""
from __future__ import annotations

VALID_COST = {"balanced", "lowest"}
VALID_LATENCY = {"balanced", "fastest"}


def get() -> dict[str, str]:
    from memory import config_manager as cfg
    data = cfg.load_api_keys()
    cost = str(data.get("provider_cost_priority") or "balanced")
    latency = str(data.get("provider_latency_priority") or "balanced")
    return {"cost_priority": cost if cost in VALID_COST else "balanced",
            "latency_priority": latency if latency in VALID_LATENCY else "balanced",
            "provider": cfg.get_provider()}


def save(cost_priority: str, latency_priority: str) -> dict[str, str]:
    from memory import config_manager as cfg
    cost = str(cost_priority or "balanced").lower()
    latency = str(latency_priority or "balanced").lower()
    if cost not in VALID_COST or latency not in VALID_LATENCY:
        raise ValueError("invalid provider routing preference")
    cfg._save_flag("provider_cost_priority", cost)
    cfg._save_flag("provider_latency_priority", latency)
    return get()
