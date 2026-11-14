"""Small, retrying downloader with checksum verification and provenance output."""

import hashlib
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from config import RAW_DIR


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def expected_size(url):
    """Content-Length reported by the server, or None when it does not say."""
    request = urllib.request.Request(
        url, method="HEAD", headers={"User-Agent": "Orbital-Insight-pipeline/1.0"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        length = response.headers.get("Content-Length")
    return int(length) if length else None


def download(url, dest, sha256=None, retries=5, timeout=120):
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists() and dest.stat().st_size > 0:
        if sha256 is None or sha256_of(dest) == sha256:
            return dest

    expected = expected_size(url)
    partial = dest.with_suffix(dest.suffix + ".part")
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            # Resume from a partial file when the server honours Range.
            offset = partial.stat().st_size if partial.exists() else 0
            headers = {"User-Agent": "Orbital-Insight-pipeline/1.0"}
            if offset:
                headers["Range"] = f"bytes={offset}-"

            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                append = offset > 0 and response.status == 206
                with open(partial, "ab" if append else "wb") as out:
                    while True:
                        block = response.read(1 << 20)
                        if not block:
                            break
                        out.write(block)

            if expected is not None and partial.stat().st_size != expected:
                raise RuntimeError(
                    f"short read: {partial.stat().st_size} of {expected} bytes"
                )

            partial.replace(dest)
            break
        except Exception as error:  # noqa: BLE001 - network errors are expected here
            last_error = error
            if attempt < retries:
                time.sleep(2 ** attempt)
    else:
        raise RuntimeError(f"download failed after {retries} attempts: {url} :: {last_error}")

    if sha256 is not None and sha256_of(dest) != sha256:
        raise RuntimeError(f"checksum mismatch for {dest}")

    return dest


def write_manifest(entries, path=None):
    path = Path(path) if path else RAW_DIR / "manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "files": entries,
    }
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return path


def file_entry(spec, path):
    return {
        "name": spec["name"],
        "role": spec.get("role") or spec.get("kind"),
        "source": spec["url"],
        "license": spec["license"],
        "citation": spec["citation"],
        "bytes": Path(path).stat().st_size,
        "sha256": sha256_of(path),
    }
