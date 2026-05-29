from __future__ import annotations

import argparse
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_URLS = {
    "train": "https://raw.githubusercontent.com/UniversalDependencies/UD_Ukrainian-IU/master/uk_iu-ud-train.conllu",
    "dev": "https://raw.githubusercontent.com/UniversalDependencies/UD_Ukrainian-IU/master/uk_iu-ud-dev.conllu",
    "test": "https://raw.githubusercontent.com/UniversalDependencies/UD_Ukrainian-IU/master/uk_iu-ud-test.conllu",
}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def download_file(url: str, destination: Path, overwrite: bool = False) -> None:
    if destination.exists() and not overwrite:
        print(f"Skip existing file: {destination}")
        return
    print(f"Downloading {url} -> {destination}")
    with urllib.request.urlopen(url) as response:
        destination.write_bytes(response.read())


def build_manifest(urls: dict[str, str]) -> dict[str, object]:
    return {
        "source": "UD Ukrainian-IU",
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": urls,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download UD Ukrainian-IU treebank files.")
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_dir(args.raw_dir)

    local_paths = {}
    for split, url in DEFAULT_URLS.items():
        destination = args.raw_dir / f"uk_iu-ud-{split}.conllu"
        download_file(url, destination, overwrite=args.overwrite)
        local_paths[split] = str(destination)

    manifest_path = args.raw_dir / "download_manifest.json"
    manifest_path.write_text(
        json.dumps(build_manifest(DEFAULT_URLS) | {"local_paths": local_paths}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Saved manifest: {manifest_path}")


if __name__ == "__main__":
    main()

