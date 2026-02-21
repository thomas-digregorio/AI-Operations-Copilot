from __future__ import annotations

import requests

from app.core.constants import ULBRICH_PUBLIC_DIR

URLS = [
    "https://www.ulbrich.com/",
    "https://www.ulbrich.com/alloys/",
    "https://www.ulbrich.com/industries/",
    "https://www.ulbrich.com/about/",
]


def main() -> None:
    ULBRICH_PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    existing_files = list(ULBRICH_PUBLIC_DIR.glob("*"))
    if existing_files:
        print(f"Found {len(existing_files)} existing files in {ULBRICH_PUBLIC_DIR}; leaving as-is.")
        return

    fetched = 0
    for i, url in enumerate(URLS, start=1):
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            out = ULBRICH_PUBLIC_DIR / f"ulbrich_page_{i}.html"
            out.write_text(response.text, encoding="utf-8", errors="ignore")
            fetched += 1
        except Exception as exc:
            print(f"Failed to fetch {url}: {exc}")

    readme = ULBRICH_PUBLIC_DIR / "README.txt"
    readme.write_text(
        "Local Ulbrich public corpus directory. Add additional HTML/PDF/TXT/MD files as needed.\n",
        encoding="utf-8",
    )
    print(f"Fetched {fetched} Ulbrich pages into {ULBRICH_PUBLIC_DIR}")


if __name__ == "__main__":
    main()
