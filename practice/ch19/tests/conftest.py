"""共用 fixture：每個測試都用獨立的暫存資料檔，不碰真實帳本。"""

import pytest


@pytest.fixture
def data_file(tmp_path):
    return tmp_path / "ledger.json"
