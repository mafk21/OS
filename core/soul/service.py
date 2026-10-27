"""Runtime lifecycle facade for the persistent Soul.

This is the only integration surface application/provider code should call. A
Soul failure always degrades to the legacy prompt path rather than blocking app
startup or task execution.
"""
from __future__ import annotations

import json
import threading
from dataclasses import replace
from pathlib import Path
from typing import Callable

from .affect import AffectEvent, AffectUpdate, apply_event_to_soul
from .context import SoulContext, SoulContextBuilder, SoulContextInputs
from .migrations import COMPANIONS_IMPORT_ID, import_companion_compatibility
from .models import Edition, RelationshipKind, Sensitivity, SoulState, utc_now_iso
from .relationship import (
    ForgetResult,
    RelationshipUpdate,
    apply_relationship_to_soul,
    forget_relationship_subject,
)
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

    def record_affect_event(
        self,
        event: AffectEvent | str,
        *,
        evidence_ref: str,
        occurred_at: str | None = None,
    ) -> AffectUpdate | None:
        """Persist one verified expressive event; return None when affect is disabled."""
        with self._lock:
            self.initialize()
            state = self.store.load()
            self._state = state
            if not state.privacy.affect_enabled:
                return None
            holder: dict[str, AffectUpdate] = {}
            stamp = occurred_at or utc_now_iso()

            def mutate(current: SoulState) -> SoulState:
                changed, update = apply_event_to_soul(
                    current, event, occurred_at=stamp, evidence_ref=evidence_ref
                )
                holder["update"] = update
                return changed

            self._state = self.store.transact(
                mutate,
                expected_revision=state.revision,
                reason=f"apply bounded affect event {AffectEvent(event).value}",
                source="affect",
                event="soul.affect_changed",
            )
            self.builder.clear_cache()
            return holder["update"]

    def record_relationship(
        self,
        *,
        kind: RelationshipKind | str,
        subject: str,
        value: str,
        evidence_ref: str,
        explicit: bool,
        sensitivity: Sensitivity | str = Sensitivity.NORMAL,
        observed_at: str | None = None,
    ) -> RelationshipUpdate | None:
        """Persist attributable continuity when relationship learning is enabled."""
        with self._lock:
            self.initialize()
            state = self.store.load()
            self._state = state
            if not state.privacy.relationship_learning:
                return None
            holder: dict[str, RelationshipUpdate] = {}
            stamp = observed_at or utc_now_iso()

            def mutate(current: SoulState) -> SoulState:
                changed, update = apply_relationship_to_soul(
                    current, kind=kind, subject=subject, value=value,
                    evidence_ref=evidence_ref, observed_at=stamp,
                    explicit=explicit, sensitivity=sensitivity,
                )
                holder["update"] = update
                return changed

            self._state = self.store.transact(
                mutate, expected_revision=state.revision,
                reason="record evidence-backed relationship continuity",
                source="relationship", event="soul.relationship_changed",
            )
            self.builder.clear_cache()
            return holder["update"]

    def forget_relationship(self, *, subject: str) -> ForgetResult:
        """Forget subject content; the audit record deliberately omits its value."""
        with self._lock:
            self.initialize()
            state = self.store.load()
            holder: dict[str, ForgetResult] = {}

            def mutate(current: SoulState) -> SoulState:
                result = forget_relationship_subject(current.relationship, subject)
                holder["result"] = result
                return replace(current, relationship=result.state)

            self._state = self.store.transact(
                mutate, expected_revision=state.revision,
                reason="user-requested selective relationship forgetting",
                source="relationship", event="soul.relationship_forgotten",
            )
            self.builder.clear_cache()
            return holder["result"]

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


def record_runtime_affect_event(
    event: AffectEvent | str,
    *,
    evidence_ref: str,
    occurred_at: str | None = None,
) -> AffectUpdate | None:
    """Record an app-verified event only when staged Soul runtime is enabled."""
    try:
        from memory import config_manager as cfg
        if not cfg.get_soul_enabled():
            return None
        return get_default_service().record_affect_event(
            event, evidence_ref=evidence_ref, occurred_at=occurred_at
        )
    except Exception as exc:
        print(f"[Soul] Affect event skipped: {type(exc).__name__}: {exc}")
        return None


def record_runtime_relationship(
    *,
    kind: RelationshipKind | str,
    subject: str,
    value: str,
    evidence_ref: str,
    explicit: bool,
    sensitivity: Sensitivity | str = Sensitivity.NORMAL,
    observed_at: str | None = None,
) -> RelationshipUpdate | None:
    """Record continuity only when Soul and adaptive learning are enabled."""
    try:
        from memory import config_manager as cfg
        if not cfg.get_soul_enabled() or not cfg.get_adaptive_learning_enabled():
            return None
        return get_default_service().record_relationship(
            kind=kind, subject=subject, value=value, evidence_ref=evidence_ref,
            explicit=explicit, sensitivity=sensitivity, observed_at=observed_at,
        )
    except Exception as exc:
        print(f"[Soul] Relationship event skipped: {type(exc).__name__}: {exc}")
        return None


def record_long_task_completion(task: dict) -> None:
    """LongTaskManager notifier adapter; accepts verified completed records only."""
    if not isinstance(task, dict) or task.get("status") != "completed":
        return
    task_id = str(task.get("id") or "").strip()
    evidence = str(task.get("completion_evidence") or "").strip()
    if not task_id or not evidence:
        return
    evidence_ref = f"long-task:{task_id}:completed"
    record_runtime_affect_event(AffectEvent.VERIFIED_TASK_SUCCESS, evidence_ref=evidence_ref)
    record_runtime_relationship(
        kind=RelationshipKind.MILESTONE,
        subject=f"completed-task:{task_id}",
        value="Completed a durable task together",
        evidence_ref=evidence_ref,
        explicit=False,
    )


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
