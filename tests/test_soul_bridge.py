"""Phase 11 Soul Studio backend API and bridge tests."""
from dataclasses import replace

from fastapi.testclient import TestClient

from core.apex_bridge import ApexHudBridge
from core.soul import LearnedTrait, SoulService, SoulState, SoulStore, TraitOrigin, TraitStatus
from core.soul.api import SoulStudioAPI

NOW = "2026-10-27T12:00:00+03:00"

class UI:
    def __init__(self):
        self._win = type("W", (), {"_ready": True})()
        self._integrations_ready = True; self._persona_selected = True; self.muted = False


def setup(tmp_path):
    store = SoulStore(tmp_path / "memory" / "soul.json", clock=lambda: NOW)
    service = SoulService(store, companions_path=tmp_path / "none.json")
    service.initialize()
    return store, service, SoulStudioAPI(service)


def test_snapshot_export_and_affect_explanation_are_redacted_from_credentials(tmp_path):
    store, service, api = setup(tmp_path)
    snap = api.snapshot()
    assert snap["revision"] == 0
    assert "not biological emotion" in snap["affect"]["framing"]
    assert snap["context_preview"].startswith("[CONSTITUTION]")
    exported = api.export()
    text = str(exported).lower()
    assert exported["format"] == "jarvis-soul"
    assert "api_key" not in text and "token" not in text and "password" not in text


def test_snapshot_exposes_read_only_authoritative_commitment_projection(tmp_path, monkeypatch):
    _, _, api = setup(tmp_path)
    projected = ("long-task:7; status=active; title=Finish report; authoritative_source=long_task",)
    monkeypatch.setattr("core.soul.api.project_runtime_commitments", lambda: projected)
    assert api.snapshot()["commitments"] == list(projected)


def test_identity_update_is_bounded_and_stale_revision_conflicts(tmp_path):
    from core.soul import RevisionConflict, ValidationError
    _, _, api = setup(tmp_path)
    changed = api.update_identity({"directness": .9}, 0)
    assert changed.identity.directness.value == .9 and changed.revision == 1
    try:
        api.update_identity({"directness": .8}, 0)
        assert False
    except RevisionConflict:
        pass
    try:
        api.update_identity({"unknown": .5}, 1)
        assert False
    except ValidationError:
        pass


def test_trait_decision_reset_and_undo(tmp_path):
    store, service, api = setup(tmp_path)
    trait = LearnedTrait(id="t1", name="tone", value="direct", status=TraitStatus.CANDIDATE,
        confidence=.7, evidence_count=2, evidence_refs=("a", "b"), origin=TraitOrigin.REFLECTION,
        rationale="observed", first_observed_at=NOW, last_observed_at=NOW,
        revision_created=0, revision_modified=0)
    seeded = store.transact(lambda s: replace(s, learned_traits=(trait,)), expected_revision=0, reason="seed", source="test")
    accepted = api.decide_trait("t1", "accept", seeded.revision)
    assert accepted.learned_traits[0].status is TraitStatus.ACTIVE
    reset = api.reset("learned_traits", accepted.revision)
    assert reset.learned_traits == ()
    undone = api.undo(reset.revision)
    assert undone.learned_traits[0].status is TraitStatus.ACTIVE


def test_bridge_routes_return_409_for_stale_revision_and_validate_payloads(tmp_path, monkeypatch):
    _, _, api = setup(tmp_path)
    bridge = ApexHudBridge(UI(), host="127.0.0.1", port=8765)
    monkeypatch.setattr(bridge, "_get_soul_api", lambda: api)
    with TestClient(bridge._build_app()) as client:
        get = client.get("/api/hud/soul")
        assert get.status_code == 200 and get.json()["soul"]["revision"] == 0
        good = client.post("/api/hud/soul", json={"operation": "identity", "expected_revision": 0, "values": {"warmth": .7}})
        assert good.status_code == 200 and good.json()["revision"] == 1
        stale = client.post("/api/hud/soul", json={"operation": "identity", "expected_revision": 0, "values": {"warmth": .8}})
        assert stale.status_code == 409 and stale.json()["code"] == "revision_conflict"
        bad = client.post("/api/hud/soul", json={"operation": "identity", "expected_revision": 1, "values": {"hacker": 1}})
        assert bad.status_code == 400
        export = client.get("/api/hud/soul/export")
        assert export.status_code == 200 and export.json()["export"]["format"] == "jarvis-soul"


def test_selective_forgetting_uses_revision_and_removes_content(tmp_path):
    store, service, api = setup(tmp_path)
    service.record_relationship(kind="preference", subject="nickname", value="PrivateName",
        evidence_ref="turn:1", explicit=True, observed_at=NOW)
    revision = store.load().revision
    state, claims, contradictions = api.forget_relationship("nickname", revision)
    assert claims == 1 and contradictions == 0
    assert "PrivateName" not in str(state.to_dict())
    assert "PrivateName" not in store.audit_path.read_text(encoding="utf-8")
