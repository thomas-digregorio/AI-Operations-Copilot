from pathlib import Path

from bs4 import BeautifulSoup
from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".txt", ".md", ".html", ".htm", ".pdf"}


def _read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def _read_html(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(" ", strip=True)


def load_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _read_pdf(path)
    if suffix in {".html", ".htm"}:
        return _read_html(path)
    return path.read_text(encoding="utf-8", errors="ignore")


def collect_documents(directory: Path) -> list[dict]:
    docs: list[dict] = []
    if not directory.exists():
        return docs
    for path in sorted(directory.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        content = load_text(path).strip()
        if not content:
            continue
        docs.append({"source": str(path), "text": content})
    return docs
