"""CLI 整合測試：以 main(argv) 驗證輸出與結束碼。"""

from ledger.cli import main


def run(capsys, data_file, *args):
    code = main(["--file", str(data_file), *args])
    out, err = capsys.readouterr()
    return code, out, err


# --- US1 ---
def test_add_success(capsys, data_file):
    code, out, _ = run(capsys, data_file, "add", "120", "餐飲", "--note", "午餐", "--date", "2026-10-01")
    assert code == 0
    assert "已新增 #1：2026-10-01  餐飲  120.00  午餐" in out


def test_add_invalid_amount_keeps_data(capsys, data_file):
    run(capsys, data_file, "add", "10", "餐飲")
    before = data_file.read_text(encoding="utf-8")
    for bad in ("abc", "0", "-5"):
        code, out, err = run(capsys, data_file, "add", bad, "餐飲")
        assert code == 1
        assert err.startswith("錯誤：")
        assert out == ""
    assert data_file.read_text(encoding="utf-8") == before


# --- US2 ---
def test_list_empty(capsys, data_file):
    code, out, _ = run(capsys, data_file, "list")
    assert code == 0
    assert out.strip() == "目前沒有紀錄"


def test_list_with_month(capsys, data_file):
    run(capsys, data_file, "add", "500", "房租", "--date", "2026-09-30")
    run(capsys, data_file, "add", "300", "交通", "--date", "2026-10-05")
    run(capsys, data_file, "add", "120", "餐飲", "--note", "午餐", "--date", "2026-10-01")
    code, out, _ = run(capsys, data_file, "list", "--month", "2026-10")
    assert code == 0
    assert out.splitlines() == ["#3  2026-10-01  餐飲  120.00  午餐", "#2  2026-10-05  交通  300.00"]


# --- US3 ---
def test_total(capsys, data_file):
    run(capsys, data_file, "add", "120", "餐飲", "--date", "2026-10-01")
    run(capsys, data_file, "add", "80", "餐飲", "--date", "2026-10-03")
    run(capsys, data_file, "add", "300", "交通", "--date", "2026-10-05")
    run(capsys, data_file, "add", "500", "房租", "--date", "2026-09-30")
    code, out, _ = run(capsys, data_file, "total", "2026-10")
    assert code == 0
    assert out.splitlines() == ["2026-10 合計：500.00", "  交通  300.00", "  餐飲  200.00"]


def test_total_bad_month(capsys, data_file):
    code, _, err = run(capsys, data_file, "total", "2026-13")
    assert code == 1
    assert "YYYY-MM" in err


def test_corrupted_file_reports_error(capsys, data_file):
    data_file.write_text("{oops", encoding="utf-8")
    code, _, err = run(capsys, data_file, "list")
    assert code == 1
    assert "錯誤：" in err
    assert data_file.read_text(encoding="utf-8") == "{oops"
