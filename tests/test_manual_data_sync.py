"""测试主界面与托盘独立「更新海克斯数据」功能。"""
import time
from unittest.mock import MagicMock
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from lolhex.ui.mainwindow import DataSyncWorker, MainWindow


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
    engine.store.status.return_value = {"dataset": True, "dataset_patch": "16.21", "dataset_matches": 42000000}
    engine.store.heroes = {}
    engine.state = {"phase": "idle", "champ_select": None, "vision": {}, "hero_candidates": []}

    overlay = MagicMock()
    mw = MainWindow(engine, overlay)

    assert hasattr(mw, "btn_sync_data")
    assert mw.btn_sync_data.text() == "🔄 更新数据"
    assert hasattr(mw, "btn_data_sync_settings")
    assert mw.btn_data_sync_settings.text() == "立即同步数据"
