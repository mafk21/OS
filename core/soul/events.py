"""Typed local audit events for durable Soul mutations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .models import ValidationError, _integer, _mapping, _strict, _text, _timestamp


@dataclass(frozen=True, slots=True)
class SoulAuditEvent:
    event: str
    timestamp: str
    revision: int
    reason: str
    source: str
    mutation_id: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "event", _text(self.event, "audit event", maximum=80))
        object.__setattr__(self, "timestamp", _timestamp(self.timestamp, "audit timestamp"))
        object.__setattr__(self, "revision", _integer(self.revision, "audit revision"))
        object.__setattr__(self, "reason", _text(self.reason, "audit reason", maximum=240))
        object.__setattr__(self, "source", _text(self.source, "audit source", maximum=80))
        object.__setattr__(self, "mutation_id", _text(self.mutation_id, "audit mutation ID", maximum=80))

    def to_dict(self) -> dict[str, Any]:
        return {
            "event": self.event,
            "timestamp": self.timestamp,
            "revision": self.revision,
            "reason": self.reason,
            "source": self.source,
            "mutation_id": self.mutation_id,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any] | Any) -> "SoulAuditEvent":
        data = _mapping(raw, "audit record")
        fields = {"event", "timestamp", "revision", "reason", "source", "mutation_id"}
        _strict(data, fields, "audit record")
        missing = fields - set(data)
        if missing:
            raise ValidationError(f"audit record is missing fields: {', '.join(sorted(missing))}")
        return cls(**data)
