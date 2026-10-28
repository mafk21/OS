"""Validated backend operations for Soul Studio."""
from __future__ import annotations

from dataclasses import replace
from typing import Any

from .affect import explain_affect
from .context import SoulContextInputs
from .models import (
    AffectState, Edition, IdentityProfile, InitiativePolicy, RelationshipState,
    SoulState, TraitRange, TraitStatus, ValidationError,
)
from .service import SoulService, project_runtime_commitments
from .store import RevisionConflict


class SoulStudioAPI:
    def __init__(self, service: SoulService):
        self.service = service

    def snapshot(self) -> dict[str, Any]:
        state = self.service.reload()
        try:
            from memory import config_manager as cfg
            inputs = SoulContextInputs(
                edition=Edition.FEMALE if cfg.get_persona() == "female" else Edition.MALE,
                assistant_name=cfg.get_assistant_name(), user_name=cfg.get_user_name(),
                voice_name=cfg.get_voice(), personalization_enabled=cfg.get_personalization_enabled(),
            )
        except Exception:
            inputs = SoulContextInputs()
        context = self.service.builder.build(state, inputs)
        return {
            "schema_version": state.schema_version, "revision": state.revision,
            "runtime_enabled": bool(cfg.get_soul_enabled()) if 'cfg' in locals() else False,
            "constitution_version": state.constitution_version,
            "identity": state.to_dict()["identity"],
            "affect": explain_affect(state.affect),
            "relationship": state.to_dict()["relationship"],
            # Read-only projection; authoritative task and memory stores remain unchanged.
            "commitments": list(project_runtime_commitments()),
            "learned_traits": state.to_dict()["learned_traits"],
            "initiative_policy": state.to_dict()["initiative_policy"],
            "reflection_state": state.to_dict()["reflection_state"],
            "privacy": state.to_dict()["privacy"],
            "context_preview": context.text,
            "context_fingerprint": context.fingerprint,
            "history": [event.to_dict() for event in self.service.store.read_events(limit=100)],
            "recovery": self.service.store.last_recovery,
            "degraded": self.service.degraded_reason,
        }

    def export(self) -> dict[str, Any]:
        return {"format": "jarvis-soul", "state": self.service.reload().to_dict()}

    def update_identity(self, data: dict[str, Any], expected_revision: int) -> SoulState:
        allowed = {"warmth", "humor", "formality", "directness", "challenge", "initiative"}
        if set(data) - allowed:
            raise ValidationError("identity update contains unknown fields")
        def mutate(state):
            changes = {}
            for name, value in data.items():
                old = getattr(state.identity, name)
                changes[name] = TraitRange(value, old.minimum, old.maximum)
            return replace(state, identity=replace(state.identity, **changes))
        return self._transact(mutate, expected_revision, "update identity traits")

    def update_initiative(self, data: dict[str, Any], expected_revision: int) -> SoulState:
        editable = {"enabled", "timezone", "quiet_start", "quiet_end", "daily_budget", "coaching_mode", "snooze_until"}
        if set(data) - editable:
            raise ValidationError("initiative update contains unknown fields")
        return self._transact(
            lambda state: replace(state, initiative_policy=replace(state.initiative_policy, **data)),
            expected_revision, "update initiative policy",
        )

    def update_privacy(self, data: dict[str, Any], expected_revision: int) -> SoulState:
        editable = {"relationship_learning", "affect_enabled", "reflection_enabled", "initiative_enabled"}
        if set(data) - editable or any(not isinstance(value, bool) for value in data.values()):
            raise ValidationError("privacy update contains invalid fields or values")
        def mutate(state):
            privacy = replace(state.privacy, **data)
            reflection = replace(state.reflection_state, enabled=data.get("reflection_enabled", state.reflection_state.enabled))
            initiative = replace(state.initiative_policy, enabled=data.get("initiative_enabled", state.initiative_policy.enabled))
            return replace(state, privacy=privacy, reflection_state=reflection, initiative_policy=initiative)
        return self._transact(mutate, expected_revision, "update Soul privacy controls")

    def decide_trait(self, trait_id: str, decision: str, expected_revision: int) -> SoulState:
        status = {"accept": TraitStatus.ACTIVE, "reject": TraitStatus.REJECTED}.get(decision)
        if status is None:
            raise ValidationError("trait decision must be accept or reject")
        def mutate(state):
            found = False; rows = []
            for trait in state.learned_traits:
                if trait.id == trait_id:
                    rows.append(replace(trait, status=status, revision_modified=state.revision + 1)); found = True
                else: rows.append(trait)
            if not found: raise ValidationError("unknown learned trait ID")
            return replace(state, learned_traits=tuple(rows))
        return self._transact(mutate, expected_revision, f"{decision} learned trait")

    def forget_relationship(self, subject: str, expected_revision: int) -> tuple[SoulState, int, int]:
        from .relationship import forget_relationship_subject
        holder = {}
        def mutate(state):
            result = forget_relationship_subject(state.relationship, subject)
            holder["result"] = result
            return replace(state, relationship=result.state)
        state = self._transact(mutate, expected_revision, "selective relationship forgetting")
        result = holder["result"]
        return state, result.removed_claims, result.removed_contradictions

    def reset(self, scope: str, expected_revision: int) -> SoulState:
        if scope not in {"affect", "relationship", "learned_traits", "all"}:
            raise ValidationError("unsupported reset scope")
        def mutate(state):
            if scope == "affect": return replace(state, affect=AffectState(updated_at=state.updated_at, daily_date=state.updated_at[:10]))
            if scope == "relationship": return replace(state, relationship=RelationshipState())
            if scope == "learned_traits": return replace(state, learned_traits=())
            defaults = SoulState.new(state.updated_at)
            return replace(defaults, created_at=state.created_at, revision=state.revision,
                           completed_migrations=state.completed_migrations)
        return self._transact(mutate, expected_revision, f"reset {scope}")

    def undo(self, expected_revision: int) -> SoulState:
        backup = self.service.store.load_backup()
        if backup is None:
            raise ValidationError("no validated Soul backup is available")
        return self._transact(
            lambda current: replace(backup, created_at=current.created_at,
                                    schema_version=current.schema_version,
                                    constitution_version=current.constitution_version),
            expected_revision, "undo previous Soul mutation",
        )

    def _transact(self, mutate, expected_revision: int, reason: str) -> SoulState:
        if isinstance(expected_revision, bool) or not isinstance(expected_revision, int):
            raise ValidationError("expected_revision must be an integer")
        state = self.service.store.transact(
            mutate, expected_revision=expected_revision, reason=reason,
            source="soul_studio", event="soul.studio_changed",
        )
        self.service.reload()
        return state
