"""测试主界面与托盘独立「更新海克斯数据」功能。"""
import time
from unittest.mock import MagicMock
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from lolhex.ui.mainwindow import DataSyncWorker, MainWindow, _maybe_sync_from_local_repo


def _ensure_app():
    return QApplication.instance() or QApplication([])


def test_data_sync_worker_success():
    _ensure_app()
    store = MagicMock()
    store.sync_data.return_value = True
    store.sync_error = None
    dataset = MagicMock()
    dataset.patch = "16.21"
    dataset.snapshot_at = "2026-11-04T01:54:03"
    dataset.matches = 42169050
    store.dataset = dataset

    worker = DataSyncWorker(store)
    results = []
    worker.done.connect(lambda msg, ch: results.append((msg, ch)))
    worker.run()

    assert len(results) == 1
    msg, changed = results[0]
    assert changed is True
    assert "海克斯统计数据已成功更新" in msg
    assert "16.21" in msg
    assert "4217" in msg


def test_data_sync_worker_uptodate():
    _ensure_app()
    store = MagicMock()
    store.sync_data.return_value = False
    store.sync_error = None
    dataset = MagicMock()
    dataset.patch = "16.21"
    dataset.snapshot_at = "2026-11-04T01:54:03"
    dataset.matches = 42169050
    store.dataset = dataset

    worker = DataSyncWorker(store)
    results = []
    worker.done.connect(lambda msg, ch: results.append((msg, ch)))
    worker.run()

    assert len(results) == 1
    msg, changed = results[0]
    assert changed is False
    assert "当前海克斯统计数据已是最新" in msg


def test_data_sync_worker_failure():
    _ensure_app()
    store = MagicMock()
    store.sync_data.side_effect = RuntimeError("网络超时")
    worker = DataSyncWorker(store)
    errors = []
    worker.failed.connect(lambda err: errors.append(err))
    worker.run()

    assert len(errors) == 1
    assert "网络超时" in errors[0]


def test_mainwindow_has_sync_buttons():
    _ensure_app()
    engine = MagicMock()
    engine.settings.overlay_corner = "top-right"
    engine.settings.badge_position = "above"
    engine.settings.speed = "standard"
    engine.settings.check_data_updates = True
    engine.settings.send_usage = True
    engine.settings.game_lang = "zh_CN"
    engine.settings.riot_id = ""
    engine.settings.my_rank = {}
    engine.settings.data_band = ""
    engine.settings.show_winrate = True
    engine.settings.overlay_hotkey = ""
    engine.store.status.return_value = {"dataset": True, "dataset_patch": "16.21", "dataset_matches": 42000000}
    engine.store.heroes = {}
    engine.state = {"phase": "idle", "champ_select": None, "vision": {}, "hero_candidates": []}

    overlay = MagicMock()
    overlay.hotkey = None
    mw = MainWindow(engine, overlay)

    assert hasattr(mw, "btn_sync_data")
    assert mw.btn_sync_data.text() == "🔄 更新数据"
    assert hasattr(mw, "btn_data_sync_settings")
    assert mw.btn_data_sync_settings.text() == "立即同步数据"


def test_data_sync_worker_reads_real_dataset_manifest_matches():
    _ensure_app()
    from types import SimpleNamespace

    store = MagicMock()
    store.downloaded = None
    store.sync_data.return_value = False
    store.sync_error = None
    store.dataset = SimpleNamespace(
        patch="16.23",
        snapshot_at="2026-11-20T08:00:00+08:00",
        manifest={"matches": 4991976},
    )

    worker = DataSyncWorker(store)
    results = []
    worker.done.connect(lambda msg, ch: results.append((msg, ch)))
    worker.run()

    assert len(results) == 1
    msg, changed = results[0]
    assert changed is False
    assert "共 499 万局" in msg
    assert "16.23" in msg


def test_maybe_sync_from_local_repo_verifies_and_skips_unlisted_files(tmp_path):
    import hashlib
    import json
    from lolhex.data.public import PublicStore

    bundled = tmp_path / "bundled"
    bundled.mkdir()
    local_repo = tmp_path / "aramhex-data"
    data_dir = local_repo / "patches" / "16.23" / "normal"
    data_dir.mkdir(parents=True)

    def make_dataset(root_dir, snapshot_at: str, seq: int, matches: int):
        payloads = {
            "heroes.json": json.dumps({"17": {"games": 1000, "wins": 500, "win_rate": 0.5}}).encode("utf-8"),
            "hero_augments.json": json.dumps({"17": {"1029": {"games": 500, "wins": 260, "win_rate": 0.52}}}).encode("utf-8"),
            "meta.json": json.dumps({"patch": "16.23"}).encode("utf-8"),
        }
        files_meta = {}
        for name, body in payloads.items():
            (root_dir / name).write_bytes(body)
            files_meta[name] = {"sha256": hashlib.sha256(body).hexdigest(), "size": len(body)}
        return {
            "schema_version": 1,
            "patch": "16.23",
            "path": "patches/16.23/normal",
            "snapshot_at": snapshot_at,
            "seq": seq,
            "matches": matches,
            "bands": False,
            "files": files_meta,
        }

    old_manifest = make_dataset(bundled, "2026-11-17T18:00:00+08:00", 19, 3000000)
    (bundled / "latest.json").write_text(json.dumps(old_manifest), encoding="utf-8")

    new_manifest = make_dataset(data_dir, "2026-11-20T08:00:00+08:00", 20, 4991976)
    (data_dir / "ignored.csv").write_text("csv,should,not,be,copied\n", encoding="utf-8")
    (local_repo / "latest.json").write_text(json.dumps(new_manifest), encoding="utf-8")

    store = PublicStore(tmp_path / "app_data", bundled=bundled, check_updates=False)
    assert store.dataset.seq == 19

    assert _maybe_sync_from_local_repo(store, candidates=[local_repo]) is True
    assert store.dataset.seq == 20
    assert (store.downloaded / "latest.json").is_file()
    assert not (store.downloaded / "ignored.csv").exists()
    assert _maybe_sync_from_local_repo(store, candidates=[local_repo]) is False
