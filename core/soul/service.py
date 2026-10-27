"""Runtime lifecycle facade for the persistent Soul.

This is the only integration surface application/provider code should call. A
Soul failure always degrades to the legacy prompt path rather than blocking app
startup or task execution.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Callable

from .context import SoulContext, SoulContextBuilder, SoulContextInputs
from .migrations import COMPANIONS_IMPORT_ID, import_companion_compatibility
from .models import Edition, SoulState
from .store import SoulStore, SoulStoreError

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_COMPANIONS_PATH = BASE_DIR / "memory" / "companions.json"


class SoulService:
    def __init__(
        self,
        store: SoulStore | None = None,
        *,
        companions_path: Path | str = DEFAULT_COMPANIONS_PATH,
        builder: SoulContextBuilder | None = None,
        logger: Callable[[str], None] | None = None,
    ) -> None:
        self.store = store or SoulStore()
        self.companions_path = Path(companions_path)
        self.builder = builder or SoulContextBuilder()
        self.logger = logger or (lambda message: print(f"[Soul] {message}"))
        self._lock = threading.RLock()
        self._state: SoulState | None = None
        self.degraded_reason: str | None = None

    def initialize(self) -> SoulState:
        with self._lock:
            if self._state is not None:
                return self._state
            state = self.store.initialize()
            state = self._import_companions_once(state)
            self._state = state
            if self.store.last_recovery:
                self.logger(self.store.last_recovery)
            return state

    def reload(self) -> SoulState:
        with self._lock:
            self._state = self.store.load()
            self.builder.clear_cache()
            return self._state

    def build_context(self, inputs: SoulContextInputs) -> SoulContext:
        with self._lock:
            state = self.initialize()
            return self.builder.build(state, inputs)

    def _import_companions_once(self, state: SoulState) -> SoulState:
        if COMPANIONS_IMPORT_ID in state.completed_migrations or not self.companions_path.exists():
            return state
        try:
            raw = json.loads(self.companions_path.read_text(encoding="utf-8"))
            result = import_companion_compatibility(state, raw)
            if not result.applied:
                return state
            return self.store.transact(
                lambda _current: result.state,
                expected_revision=state.revision,
                reason="import existing behavior interview and adaptive rules",
                source="compatibility",
                event="soul.migrated",
            )
        except SoulStoreError as exc:
            if exc.committed:
                return self.store.load()
            self.degraded_reason = f"Companion compatibility import skipped: {type(exc).__name__}"
            self.logger(self.degraded_reason)
            return state
        except Exception as exc:
            # Companion corruption must not brick Soul or app startup. Keep the
            # validated Soul state and leave the marker absent so a repaired
            # companion file can be imported later.
            self.degraded_reason = f"Companion compatibility import skipped: {type(exc).__name__}"
            self.logger(self.degraded_reason)
            return state


_DEFAULT_LOCK = threading.RLock()
_DEFAULT_SERVICE: SoulService | None = None


def get_default_service() -> SoulService:
    global _DEFAULT_SERVICE
    with _DEFAULT_LOCK:
        if _DEFAULT_SERVICE is None:
            _DEFAULT_SERVICE = SoulService()
        return _DEFAULT_SERVICE


def reset_default_service_for_tests() -> None:
    global _DEFAULT_SERVICE
    with _DEFAULT_LOCK:
        _DEFAULT_SERVICE = None


def build_runtime_context(*, include_personalization: bool | None = None) -> str:
    """Build canonical context from live config, or return empty on rollback/failure."""
    try:
        from memory import config_manager as cfg

        if not cfg.get_soul_enabled():
            return ""
        persona = cfg.get_persona()
        edition = Edition.FEMALE if persona == "female" else Edition.MALE
        personalized = cfg.get_personalization_enabled() if include_personalization is None else bool(include_personalization)
        inputs = SoulContextInputs(
            edition=edition,
            assistant_name=cfg.get_assistant_name(),
            user_name=cfg.get_user_name(),
            voice_name=cfg.get_voice(),
            personalization_enabled=personalized,
        )
        return get_default_service().build_context(inputs).text
    except Exception as exc:
        print(f"[Soul] Context unavailable; using legacy identity: {type(exc).__name__}: {exc}")
        return ""
