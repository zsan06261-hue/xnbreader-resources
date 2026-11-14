#!/usr/bin/env python3
"""Mirror a fixed manifest from XNB's official HTTPS host into draft GitHub Releases.

Never downloads to the local developer's vault or re-hashes untrusted metadata.
Upload is permitted only after every source matches the pinned SHA-256 and size.
"""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import urllib.request

REPO = "zsan06261-hue/xnbreader-resources"
SOURCE_PREFIX = "https://download.xnbreader.tech/resources/v1/"
TAGS = ("resources-exams-v1", "resources-listening-v1",
        "resources-dictionary-v1", "resources-speech-macos-v1")
ROOT = Path(__file__).resolve().parent.parent
FILES = json.loads((ROOT / "assets.json").read_text(encoding="utf-8"))["files"]

if os.environ.get("GITHUB_REPOSITORY") != REPO:
    raise SystemExit("Unexpected repository; refusing publish")
if len(FILES) != 519 or sum(int(item["bytes"]) for item in FILES) != 1481561203:
    raise SystemExit("Unexpected mirror manifest count or size")

def release_assets(tag):
    raw = subprocess.check_output(
        ["gh", "release", "view", tag, "-R", REPO, "--json", "assets"],
        text=True)
    return {a["name"]: a for a in json.loads(raw)["assets"]}

def matches(asset, record):
    return (asset["size"] == record["bytes"]
            and asset.get("digest") == "sha256:" + record["sha256"])

def fetch_one(item, folder):
    if not item["sourceUrl"].startswith(SOURCE_PREFIX):
        raise ValueError("Untrusted resource URL")
    if "/" in item["name"] or "\\" in item["name"] or item["name"].startswith("."):
        raise ValueError("Invalid release filename")
    dest = folder / item["name"]
    sha = hashlib.sha256()
    amount = 0
    req = urllib.request.Request(item["sourceUrl"], headers={"User-Agent": "XNBReaderResourceMirror/1.0"})
    with urllib.request.urlopen(req, timeout=180) as response, dest.open("xb") as output:
        if response.status != 200:
            raise RuntimeError(f"Unexpected source HTTP: {response.status} {item['name']}")
        while block := response.read(1024 * 1024):
            amount += len(block)
            if amount > item["bytes"]:
                raise RuntimeError("Source exceeds expected length: " + item["name"])
            output.write(block)
            sha.update(block)
    if amount != item["bytes"] or sha.hexdigest() != item["sha256"]:
        dest.unlink(missing_ok=True)
        raise RuntimeError("Source size/hash mismatch: " + item["name"])
    return str(dest)

seen = set()
for record in FILES:
    key = record["tag"], record["name"]
    if record["tag"] not in TAGS or key in seen:
        raise RuntimeError("Invalid/duplicate asset identity")
    seen.add(key)

for tag in TAGS:
    wanted = [item for item in FILES if item["tag"] == tag]
    exists = release_assets(tag)
    unexpected = set(exists) - {item["name"] for item in wanted}
    if unexpected:
        raise RuntimeError(f"Unexpected existing release assets for {tag}: {unexpected}")
    for item in wanted:
        if item["name"] in exists and not matches(exists[item["name"]], item):
            raise RuntimeError("Existing release asset mismatch; will not clobber: " + item["name"])
    missing = [item for item in wanted if item["name"] not in exists]
    print(f"{tag}: {len(wanted)-len(missing)}/{len(wanted)} already verified", flush=True)
    for start in range(0, len(missing), 12):
        batch = missing[start:start + 12]
        with tempfile.TemporaryDirectory(prefix="xnb-gh-verify-") as directory:
            folder = Path(directory)
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
                uploaded_paths = list(pool.map(lambda item: fetch_one(item, folder), batch))
            subprocess.run(["gh", "release", "upload", tag, *uploaded_paths, "-R", REPO], check=True)
        current = release_assets(tag)
        for item in batch:
            asset = current.get(item["name"])
            if not asset or not matches(asset, item):
                raise RuntimeError("Remote GitHub asset verification failed: " + item["name"])
        print(f"{tag}: {min(start+len(batch),len(missing))}/{len(missing)} newly uploaded", flush=True)
    current = release_assets(tag)
    if len(current) != len(wanted) or any(
            item["name"] not in current or not matches(current[item["name"]],item)
            for item in wanted):
        raise RuntimeError("Final release inventory mismatch: " + tag)
    print(f"VERIFIED {tag}: {len(wanted)} assets", flush=True)
print("ALL 519 ASSETS VERIFIED IN DRAFT RELEASES", flush=True)
