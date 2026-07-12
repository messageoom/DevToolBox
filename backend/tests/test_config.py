"""配置管理:get_max_upload_bytes 上限统一 + load_config/save_config 缓存。"""
import pathlib
import shutil
import tempfile
import utils.config_manager as cm


def _isolate_config(monkeypatch, tmp_path):
    """把 config 路径指向临时目录,避免读写真实的 devtoolbox_config.json。"""
    monkeypatch.setattr(cm, 'get_config_path',
                        lambda: pathlib.Path(str(tmp_path)) / 'test_config.json')
    cm._config_cache = None
    cm._config_mtime = None


def test_get_max_upload_bytes_default(monkeypatch, tmp_path):
    _isolate_config(monkeypatch, tmp_path)
    assert cm.get_max_upload_bytes() == 50 * 1024 * 1024


def test_get_max_upload_bytes_clamped(monkeypatch, tmp_path):
    _isolate_config(monkeypatch, tmp_path)
    cfg = cm.load_config()
    cfg['storage']['max_file_size_mb'] = 100
    assert cm.get_max_upload_bytes(cfg) == 100 * 1024 * 1024
    cfg['storage']['max_file_size_mb'] = 99999  # 超上限钳到 500
    assert cm.get_max_upload_bytes(cfg) == 500 * 1024 * 1024
    cfg['storage']['max_file_size_mb'] = 0  # 下限钳到 1
    assert cm.get_max_upload_bytes(cfg) == 1 * 1024 * 1024


def test_save_config_refreshes_cache(monkeypatch, tmp_path):
    _isolate_config(monkeypatch, tmp_path)
    cfg = cm.load_config()
    cfg['storage']['max_file_size_mb'] = 77
    assert cm.save_config(cfg)
    cfg2 = cm.load_config()
    assert cfg2['storage']['max_file_size_mb'] == 77


def test_cache_returns_deepcopy_isolation(monkeypatch, tmp_path):
    """返回的缓存副本被修改,不应污染内部缓存。"""
    _isolate_config(monkeypatch, tmp_path)
    cfg = cm.load_config()
    cfg['storage']['max_file_size_mb'] = 77
    cm.save_config(cfg)
    cfg2 = cm.load_config()  # 命中缓存
    cfg2['storage']['max_file_size_mb'] = 999  # 篡改副本
    cfg3 = cm.load_config()
    assert cfg3['storage']['max_file_size_mb'] == 77  # 缓存未被污染
