"""讀取 PDF 抽出文字，輸出為同目錄同名的 .txt（UTF-8）。

用法：python pdf_to_text.py <檔案.pdf> [更多檔案.pdf ...]
"""
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
    from pypdf.errors import PdfReadError
except ImportError:
    print("錯誤：找不到 pypdf，請先執行 uv pip install pypdf", file=sys.stderr)
    sys.exit(1)


def extract_text(pdf_path: Path) -> str:
    """回傳 PDF 全部頁面的文字，頁與頁之間加分隔線。"""
    reader = PdfReader(str(pdf_path))
    if reader.is_encrypted:
        # 很多 PDF 只有「權限密碼」，空密碼就能讀
        if not reader.decrypt(""):
            raise PdfReadError("PDF 已加密，無法用空密碼開啟")
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        pages.append(f"--- Page {index} ---\n{page_text.strip()}")
    return "\n\n".join(pages) + "\n"


def convert_file(pdf_path: Path) -> bool:
    """轉換單一檔案，成功回傳 True。"""
    if not pdf_path.is_file():
        print(f"錯誤：檔案不存在：{pdf_path}", file=sys.stderr)
        return False
    if pdf_path.suffix.lower() != ".pdf":
        print(f"錯誤：不是 .pdf 檔：{pdf_path}", file=sys.stderr)
        return False
    try:
        full_text = extract_text(pdf_path)
    except (PdfReadError, ValueError, OSError) as e:
        print(f"錯誤：無法讀取 {pdf_path}：{e}", file=sys.stderr)
        return False

    txt_path = pdf_path.with_suffix(".txt")
    try:
        txt_path.write_text(full_text, encoding="utf-8")
    except OSError as e:
        print(f"錯誤：無法寫入 {txt_path}：{e}", file=sys.stderr)
        return False

    char_count = len(full_text.replace("--- Page", "").strip())
    if char_count == 0:
        print(f"警告：{pdf_path} 沒有文字層（可能是掃描檔，需要 OCR）", file=sys.stderr)
    print(f"完成：{pdf_path} -> {txt_path}")
    return True


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    results = [convert_file(Path(arg)) for arg in sys.argv[1:]]
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
