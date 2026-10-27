"""Deterministic work-count/correctness checks; no cloud calls or UI changes."""
import asyncio
import json
import os
from pathlib import Path
from unittest.mock import Mock

import pytest

from memory import config_manager as cfg
from core import skill_loader as skills


@pytest.fixture
def config(tmp_path, monkeypatch):
    path=tmp_path/"api_keys.json"
    monkeypatch.setattr(cfg,"CONFIG_FILE",path)
    monkeypatch.setattr(cfg,"CONFIG_DIR",tmp_path)
    monkeypatch.setattr(cfg,"_CONFIG_READ_CACHE",None)
    return path


def test_repeated_getters_parse_disk_once_and_return_isolated_values(config,monkeypatch):
    config.write_text(json.dumps({"persona":"male","plugins_enabled":{"x":True}}))
    monkeypatch.setattr(cfg.time,"monotonic",lambda:10.)
    original=Path.read_text
    reads=[]
    def read(path,*a,**kw):
        if path==config:reads.append(path)
        return original(path,*a,**kw)
    monkeypatch.setattr(Path,"read_text",read)
    for _ in range(100):assert cfg.load_api_keys()["persona"]=="male"
    assert len(reads)==1
    data=cfg.load_api_keys();data["plugins_enabled"]["x"]=False
    assert cfg.load_api_keys()["plugins_enabled"]["x"] is True


def test_edits_replacements_and_deletion_take_effect_without_ttl(config):
    config.write_text('{"provider":"gemini"}')
    assert cfg.get_provider()=="gemini"
    cfg.save_provider("openai")
    assert cfg.get_provider()=="openai"
    replacement=config.with_suffix(".new")
    replacement.write_text('{"provider":"local"}')
    os.replace(replacement,config)
    assert cfg.get_provider()=="local"
    config.unlink()
    assert cfg.load_api_keys()=={}
    config.write_text('{"provider":"auto"}')
    assert cfg.get_provider()=="auto"


def test_corrupt_config_never_serves_old_credentials(config):
    config.write_text('{"gemini_api_key":"fixture"}')
    assert cfg.get_gemini_key()=="fixture"
    config.write_text('{broken')
    assert cfg.load_api_keys()=={}
    assert cfg._CONFIG_READ_CACHE is None


def test_vault_results_are_not_cached(config,monkeypatch):
    from core import security_vault
    config.write_text('{"gemini_api_key":"enc:v1:fixture"}')
    decrypt=Mock(side_effect=[{"gemini_api_key":"first"},{"gemini_api_key":"rotated"}])
    monkeypatch.setattr(security_vault,"decrypt_dict_secrets",decrypt)
    assert cfg.get_gemini_key()=="first"
    assert cfg.get_gemini_key()=="rotated"
    assert decrypt.call_count==2
    assert cfg._CONFIG_READ_CACHE[1]["gemini_api_key"]=="enc:v1:fixture"


def test_switching_config_paths_cannot_reuse_other_profile(config,tmp_path,monkeypatch):
    config.write_text('{"provider":"openai"}')
    assert cfg.get_provider()=="openai"
    other=tmp_path/"other.json";other.write_text('{"provider":"gemini"}')
    monkeypatch.setattr(cfg,"CONFIG_FILE",other)
    assert cfg.get_provider()=="gemini"


def test_skill_reads_only_cap_plus_one_character(tmp_path,monkeypatch):
    path=tmp_path/"large.md";path.write_text("x"*200000)
    sizes=[]
    real_open=Path.open
    class Reader:
        def __enter__(self):return self
        def __exit__(self,*a):self.source.close()
        def read(self,n):sizes.append(n);return self.source.read(n)
    def opened(p,*a,**kw):
        reader=Reader();reader.source=real_open(p,*a,**kw);return reader
    monkeypatch.setattr(Path,"open",opened)
    result=skills._read_capped(path,"fixture")
    assert sizes==[skills._MAX_BODY+1]
    assert result.startswith("x"*skills._MAX_BODY) and "truncated" in result


def test_resource_index_stops_after_40_and_skips_dependency_trees(tmp_path,monkeypatch):
    for n in range(80):(tmp_path/f"{n:03}.md").write_text("reference")
    for folder in ("node_modules",".venv",".git"):
        (tmp_path/folder).mkdir();(tmp_path/folder/"private.json").write_text("not indexed")
    real_scandir=skills.os.scandir
    visited=[]
    def scan(path):visited.append(Path(path));return real_scandir(path)
    monkeypatch.setattr(skills.os,"scandir",scan)
    assert skills._resource_listing(tmp_path)==[f"{n:03}.md" for n in range(40)]
    assert visited==[tmp_path]


def test_resource_order_matches_lexical_path_order(tmp_path):
    (tmp_path/"a").mkdir();(tmp_path/"a/z.md").write_text("a")
    (tmp_path/"b.md").write_text("b")
    (tmp_path/"a.md").write_text("a")
    expected=[str(p.relative_to(tmp_path)) for p in sorted(tmp_path.rglob("*")) if p.is_file()]
    assert skills._resource_listing(tmp_path)==expected


@pytest.mark.asyncio
async def test_stalled_hud_cannot_block_healthy_window(monkeypatch):
    from core.apex_bridge import ApexHudBridge
    bridge=ApexHudBridge.__new__(ApexHudBridge)
    delivered=asyncio.Event()
    class Healthy:
        async def send_text(self,text):delivered.set()
    class Stalled:
        closed=False
        async def send_text(self,text):await asyncio.Future()
        async def close(self,code):self.closed=code==1013
    good,bad=Healthy(),Stalled()
    bridge._clients={good,bad}
    wait_for=asyncio.wait_for
    async def short(awaitable,timeout):return await wait_for(awaitable,min(timeout,.05))
    monkeypatch.setattr(asyncio,"wait_for",short)
    work=asyncio.create_task(bridge._async_broadcast({"type":"state"}))
    await wait_for(delivered.wait(),timeout=.5)
    assert not work.done()
    await work
    assert bridge._clients=={good}
    assert bad.closed


@pytest.mark.asyncio
async def test_overlapping_hud_updates_remain_ordered_per_window():
    from core.apex_bridge import ApexHudBridge
    bridge=ApexHudBridge.__new__(ApexHudBridge)
    class Client:
        def __init__(self):self.active=False;self.received=[]
        async def send_text(self,text):
            assert not self.active,"Concurrent writes to one websocket"
            self.active=True
            await asyncio.sleep(0)
            self.received.append(json.loads(text)["n"])
            self.active=False
    client=Client();bridge._clients={client}
    await asyncio.gather(*(bridge._async_broadcast({"n":n}) for n in range(20)))
    assert client.received==list(range(20))


def test_loop_close_race_does_not_allocate_coroutine():
    from core.apex_bridge import ApexHudBridge
    bridge=ApexHudBridge.__new__(ApexHudBridge)
    loop=Mock();loop.is_closed.return_value=False
    loop.call_soon_threadsafe.side_effect=RuntimeError("closed")
    bridge._loop=loop
    bridge._async_broadcast=Mock()
    bridge._broadcast_threadsafe({"type":"state"})
    bridge._async_broadcast.assert_not_called()


def test_parallel_config_readers_get_independent_snapshots(config):
    from concurrent.futures import ThreadPoolExecutor
    config.write_text('{"plugins_enabled":{"x":true}}')
    def read(_):
        data=cfg.load_api_keys()
        assert data["plugins_enabled"]["x"] is True
        data["plugins_enabled"]["x"]=False
    with ThreadPoolExecutor(max_workers=8) as pool:list(pool.map(read,range(80)))
    assert cfg.load_api_keys()["plugins_enabled"]["x"] is True


def test_decryption_failure_returns_a_copy_without_poisoning_cache(config,monkeypatch):
    from core import security_vault
    config.write_text('{"nested":{"x":true}}')
    monkeypatch.setattr(security_vault,"decrypt_dict_secrets",Mock(side_effect=RuntimeError("temporary vault failure")))
    data=cfg.load_api_keys();data["nested"]["x"]=False
    assert cfg.load_api_keys()["nested"]["x"] is True


def test_environment_key_changes_are_not_frozen_by_config_cache(config,monkeypatch):
    config.write_text('{}')
    monkeypatch.setenv("GEMINI_API_KEY","first-fixture")
    assert cfg.get_gemini_key()=="first-fixture"
    monkeypatch.setenv("GEMINI_API_KEY","changed-fixture")
    assert cfg.get_gemini_key()=="changed-fixture"


def test_managed_writes_invalidate_even_with_identical_file_stamps(config,monkeypatch):
    config.write_text('{"provider":"gemini"}')
    monkeypatch.setattr(cfg,"_config_stamp",lambda _: ("fixed-stamp",))
    assert cfg.get_provider()=="gemini"
    cfg.save_provider("openai")
    assert cfg.get_provider()=="openai"


def test_external_same_stamp_edit_refreshes_within_maximum_cache_age(config,monkeypatch):
    config.write_text('{"provider":"gemini"}')
    clock=[10.]
    monkeypatch.setattr(cfg,"_config_stamp",lambda _: ("fixed-stamp",))
    monkeypatch.setattr(cfg.time,"monotonic",lambda:clock[0])
    assert cfg.get_provider()=="gemini"
    config.write_text('{"provider":"openai"}')
    clock[0]+=.26
    assert cfg.get_provider()=="openai"
