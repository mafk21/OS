"""Crash-safe local persistence for the JARVIS Soul.

The store owns disk mechanics only. It has no provider, UI, prompt, memory, or
action dependencies. Every mutation is validated, revision-checked, atomically
replaced, and recorded in a local audit stream.
"""
from __future__ import annotations

import json
import os
import threading
import uuid
from dataclasses import replace
from pathlib import Path
from typing import Callable

from .events import SoulAuditEvent
from .migrations import migrate_raw
from .models import SoulState, ValidationError, utc_now_iso

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_STATE_PATH = BASE_DIR / "memory" / "soul.json"
MAX_AUDIT_BYTES = 2_000_000


class RevisionConflict(RuntimeError):
    """The caller attempted to mutate a stale Soul revision."""


class SoulStoreError(RuntimeError):
    """A durable Soul operation failed."""

    def __init__(self, message: str, *, committed: bool = False):
        super().__init__(message)
        self.committed = committed


class SoulStore:
    """Thread-safe, revisioned, crash-safe Soul state repository."""

    def __init__(
        self,
        path: Path | str = DEFAULT_STATE_PATH,
        *,
        clock: Callable[[], str] = utc_now_iso,
        fault_hook: Callable[[str], None] | None = None,
        max_audit_bytes: int = MAX_AUDIT_BYTES,
    ) -> None:
        self.path = Path(path)
        self.backup_path = self.path.with_name(f"{self.path.stem}.backup{self.path.suffix}")
        self.audit_path = self.path.with_name(f"{self.path.stem}.events.jsonl")
        self.quarantine_dir = self.path.parent / f"{self.path.stem}.quarantine"
        self._clock = clock
        self._fault_hook = fault_hook
        self._max_audit_bytes = max(1024, int(max_audit_bytes))
        self._lock = threading.RLock()
        self._listeners: list[Callable[[SoulState], None]] = []
        self.last_recovery: str | None = None

    def add_listener(self, callback: Callable[[SoulState], None]) -> None:
        if not callable(callback):
            raise TypeError("Soul listener must be callable")
        with self._lock:
            if callback not in self._listeners:
                self._listeners.append(callback)

    def load(self) -> SoulState:
        """Load current state, recover backup, or return safe unsaved defaults."""
        with self._lock:
            self.last_recovery = None
            current, current_error, current_migrations = self._read_state(self.path)
            if current is not None:
                if current_migrations:
                    self._persist_migrated_state(self.path, current, current_migrations)
                self._repair_missing_audit(current)
                return current

            if current_error is not None and self.path.exists():
                self._quarantine(self.path, current_error)

            backup, backup_error, backup_migrations = self._read_state(self.backup_path)
            if backup is not None:
                if backup_migrations:
                    self._archive_pre_migration(self.backup_path, backup_migrations)
                self._atomic_write_json(self.path, backup.to_dict(), prefix="recover")
                self._atomic_write_json(self.backup_path, backup.to_dict(), prefix="recover-backup")
                self.last_recovery = "Recovered Soul state from the last known-good backup."
                self._append_event(SoulAuditEvent(
                    event="soul.recovered", timestamp=self._clock(), revision=backup.revision,
                    reason="current state missing or invalid; restored validated backup",
                    source="store", mutation_id=f"recovery-{uuid.uuid4().hex[:12]}",
                ))
                return backup

            if backup_error is not None and self.backup_path.exists():
                self._quarantine(self.backup_path, backup_error)

            self.last_recovery = (
                "Soul state was unavailable; using safe defaults."
                if current_error is not None or backup_error is not None
                else None
            )
            return SoulState.new(self._clock())

    def initialize(self) -> SoulState:
        """Persist first-run defaults if no state exists; otherwise load state."""
        with self._lock:
            if self.path.exists() or self.backup_path.exists():
                return self.load()
            state = SoulState.new(self._clock())
            self._commit_initial(state)
            return state

    def transact(
        self,
        mutate: Callable[[SoulState], SoulState],
        *,
        expected_revision: int,
        reason: str,
        source: str,
        event: str = "soul.mutation_applied",
    ) -> SoulState:
        """Apply exactly one validated mutation under optimistic concurrency."""
        if not callable(mutate):
            raise TypeError("Soul mutation must be callable")
        reason = self._bounded_label(reason, "reason", 240)
        source = self._bounded_label(source, "source", 80)
        event = self._bounded_label(event, "event", 80)
        listeners: tuple[Callable[[SoulState], None], ...] = ()
        committed = False
        with self._lock:
            current = self.load()
            if current.revision != expected_revision:
                raise RevisionConflict(
                    f"Soul revision changed: expected {expected_revision}, current {current.revision}"
                )
            proposed = mutate(current)
            if not isinstance(proposed, SoulState):
                raise ValidationError("Soul mutation must return SoulState")
            # Re-parse serialization to enforce the entire untrusted boundary,
            # including nested records that a caller may have constructed oddly.
            SoulState.from_dict(proposed.to_dict())
            if proposed.created_at != current.created_at:
                raise ValidationError("Soul mutations cannot alter created_at")
            if proposed.schema_version != current.schema_version:
                raise ValidationError("Soul mutations cannot alter schema_version")
            if proposed.constitution_version != current.constitution_version:
                raise ValidationError("Soul mutations cannot alter constitution_version")

            stamp = self._clock()
            candidate = replace(proposed, revision=current.revision + 1, updated_at=stamp)
            candidate = SoulState.from_dict(candidate.to_dict())
            mutation_id = f"mutation-{uuid.uuid4().hex[:12]}"
            try:
                self._checkpoint("validated")
                self._write_backup_of(current)
                self._checkpoint("backup_replaced")
                self._atomic_write_json(self.path, candidate.to_dict(), prefix="state")
                committed = True
                self._checkpoint("state_replaced")
                self._append_event(SoulAuditEvent(
                    event=event, timestamp=stamp, revision=candidate.revision,
                    reason=reason, source=source, mutation_id=mutation_id,
                ))
                self._checkpoint("audit_appended")
                listeners = tuple(self._listeners)
            except Exception as exc:
                if isinstance(exc, (ValidationError, RevisionConflict, SoulStoreError)):
                    raise
                raise SoulStoreError(f"Soul transaction failed: {exc}", committed=committed) from exc

        # Never call application listeners under the store lock or before the
        # state and audit record are durable.
        for callback in listeners:
            try:
                callback(candidate)
            except Exception:
                pass
        return candidate

    def load_backup(self) -> SoulState | None:
        """Return the validated previous revision without mutating current state."""
        with self._lock:
            state, _error, _migrations = self._read_state(self.backup_path)
            return state

    def read_events(self, *, limit: int = 200) -> list[SoulAuditEvent]:
        limit = max(1, min(int(limit), 1000))
        with self._lock:
            if not self.audit_path.exists():
                return []
            events: list[SoulAuditEvent] = []
            try:
                lines = self.audit_path.read_text(encoding="utf-8").splitlines()
            except OSError:
                return []
            for line in lines[-limit:]:
                try:
                    raw = json.loads(line)
                    events.append(SoulAuditEvent.from_dict(raw))
                except (json.JSONDecodeError, ValidationError):
                    continue
            return events

    def _commit_initial(self, state: SoulState) -> None:
        SoulState.from_dict(state.to_dict())
        try:
            self._atomic_write_json(self.path, state.to_dict(), prefix="initial")
            self._atomic_write_json(self.backup_path, state.to_dict(), prefix="initial-backup")
            self._append_event(SoulAuditEvent(
                event="soul.initialized", timestamp=self._clock(), revision=state.revision,
                reason="created validated Brother-Guardian defaults", source="store",
                mutation_id=f"initial-{uuid.uuid4().hex[:12]}",
            ))
        except Exception as exc:
            if isinstance(exc, SoulStoreError):
                raise
            raise SoulStoreError(f"Unable to initialize Soul state: {exc}") from exc

    def _read_state(self, path: Path) -> tuple[SoulState | None, Exception | None, tuple[str, ...]]:
        if not path.exists():
            return None, None, ()
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            result = migrate_raw(raw)
            return result.state, None, result.applied
        except (OSError, json.JSONDecodeError, ValidationError, UnicodeError) as exc:
            return None, exc, ()

    def _persist_migrated_state(self, source: Path, state: SoulState, migrations: tuple[str, ...]) -> None:
        self._archive_pre_migration(source, migrations)
        self._atomic_write_json(source, state.to_dict(), prefix="migration")
        self._atomic_write_json(self.backup_path, state.to_dict(), prefix="migration-backup")
        self._append_event(SoulAuditEvent(
            event="soul.migrated", timestamp=self._clock(), revision=state.revision,
            reason=f"applied sequential migrations: {', '.join(migrations)}",
            source="store", mutation_id=f"migration-{uuid.uuid4().hex[:12]}",
        ))
        self.last_recovery = f"Migrated Soul state using {', '.join(migrations)}."

    def _archive_pre_migration(self, source: Path, migrations: tuple[str, ...]) -> None:
        """Preserve the exact valid source bytes before the only copy is rewritten."""
        archive_dir = self.path.parent / f"{self.path.stem}.migrations"
        archive_dir.mkdir(parents=True, exist_ok=True)
        stamp = self._clock().replace(":", "-").replace("+", "_")
        label = "_".join(migrations)
        destination = archive_dir / f"{source.name}.{stamp}.{label}.json"
        if not destination.exists():
            with source.open("rb") as incoming, destination.open("xb") as outgoing:
                while True:
                    chunk = incoming.read(1024 * 1024)
                    if not chunk:
                        break
                    outgoing.write(chunk)
                outgoing.flush()
                os.fsync(outgoing.fileno())
            self._fsync_directory(archive_dir)

    def _write_backup_of(self, state: SoulState) -> None:
        self._atomic_write_json(self.backup_path, state.to_dict(), prefix="backup")

    def _atomic_write_json(self, path: Path, payload: dict, *, prefix: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(f".{path.name}.{prefix}.{uuid.uuid4().hex}.tmp")
        try:
            self._checkpoint(f"{prefix}_before_temp")
            with temp.open("w", encoding="utf-8", newline="\n") as handle:
                json.dump(payload, handle, indent=2, ensure_ascii=False, allow_nan=False)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            self._checkpoint(f"{prefix}_temp_fsynced")
            os.replace(temp, path)
            self._fsync_directory(path.parent)
        finally:
            try:
                temp.unlink(missing_ok=True)
            except OSError:
                pass

    def _append_event(self, event: SoulAuditEvent) -> None:
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        self._rotate_audit_if_needed()
        line = json.dumps(event.to_dict(), ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n"
        with self.audit_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
        self._fsync_directory(self.audit_path.parent)

    def _rotate_audit_if_needed(self) -> None:
        try:
            if self.audit_path.stat().st_size < self._max_audit_bytes:
                return
            lines = self.audit_path.read_text(encoding="utf-8").splitlines()
            keep = lines[len(lines) // 2:]
            temp = self.audit_path.with_name(f".{self.audit_path.name}.rotate.tmp")
            with temp.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write("\n".join(keep) + ("\n" if keep else ""))
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp, self.audit_path)
            self._fsync_directory(self.audit_path.parent)
        except FileNotFoundError:
            return

    def _repair_missing_audit(self, state: SoulState) -> None:
        events = self.read_events(limit=1)
        last_revision = events[-1].revision if events else -1
        if state.revision > last_revision:
            self._append_event(SoulAuditEvent(
                event="soul.audit_recovered", timestamp=self._clock(), revision=state.revision,
                reason="state commit existed without a matching audit record after interruption",
                source="store", mutation_id=f"audit-recovery-{uuid.uuid4().hex[:12]}",
            ))

    def _quarantine(self, path: Path, error: Exception) -> None:
        try:
            self.quarantine_dir.mkdir(parents=True, exist_ok=True)
            stamp = self._clock().replace(":", "-").replace("+", "_")
            destination = self.quarantine_dir / f"{path.name}.{stamp}.{uuid.uuid4().hex[:8]}.invalid"
            os.replace(path, destination)
            note = destination.with_suffix(destination.suffix + ".reason.txt")
            note.write_text(f"{type(error).__name__}: {str(error)[:500]}\n", encoding="utf-8")
            self._fsync_directory(self.quarantine_dir)
        except OSError:
            # Read-only filesystems still get safe defaults; never consume the
            # malformed content merely because quarantine could not be written.
            pass

    @staticmethod
    def _fsync_directory(path: Path) -> None:
        flags = getattr(os, "O_DIRECTORY", 0) | os.O_RDONLY
        try:
            fd = os.open(str(path), flags)
        except OSError:
            return
        try:
            os.fsync(fd)
        except OSError:
            pass
        finally:
            os.close(fd)

    def _checkpoint(self, stage: str) -> None:
        if self._fault_hook is not None:
            self._fault_hook(stage)

    @staticmethod
    def _bounded_label(value: str, label: str, maximum: int) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(f"{label} cannot be empty")
        result = value.strip()
        if len(result) > maximum:
            raise ValidationError(f"{label} exceeds {maximum} characters")
        return result
