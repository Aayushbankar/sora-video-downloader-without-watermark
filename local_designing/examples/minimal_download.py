import urllib.parse
import urllib.request
import json
import os
import sys

# ---------- Configuration ----------
BASE_API = "https://api.soracdn.workers.dev"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Python urllib)",
    "Accept": "application/json",
    "Origin": "https://sorasave.app",
    "Referer": "https://sorasave.app/",
}

def get_post_id(sora_url: str) -> str:
    """Fetch metadata and extract the post_id.
    The Sora URL must be URL-encoded before being sent to the API.
    """
    encoded = urllib.parse.quote_plus(sora_url)
    meta_url = f"{BASE_API}/api-proxy/{encoded}"
    req = urllib.request.Request(meta_url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
    return data["post_id"]

def clean_filename(title: str) -> str:
    """Create a safe filename (max 100 chars, alphanumerics + underscore)."""
    safe = "".join(c if c.isalnum() else "_" for c in title)
    return (safe[:100] or "untitled_video") + ".mp4"

def download_video(post_id: str, filename: str, out_path: str = None):
    """Download the MP4 directly from the download‑proxy endpoint.
    If `out_path` is None, the file is saved as `filename` in the current directory.
    """
    dl_url = f"{BASE_API}/download-proxy?id={post_id}&filename={urllib.parse.quote_plus(filename)}"
    req = urllib.request.Request(dl_url, headers=HEADERS)
    # Stream the response to avoid loading the whole file into memory
    with urllib.request.urlopen(req) as resp:
        total = int(resp.headers.get("Content-Length", 0))
        out_file = out_path or filename
        with open(out_file, "wb") as f:
            downloaded = 0
            while True:
                chunk = resp.read(8192)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    percent = downloaded * 100 // total
                    sys.stderr.write(f"\rDownloading: {percent}% ({downloaded}/{total} bytes)")
    sys.stderr.write("\nDownload complete.\n")

def main(sora_url: str, custom_name: str = None):
    post_id = get_post_id(sora_url)
    # Optional: fetch title from metadata to generate a nice filename
    if not custom_name:
        # Re‑use the metadata call to get the title
        encoded = urllib.parse.quote_plus(sora_url)
        meta_url = f"{BASE_API}/api-proxy/{encoded}"
        req = urllib.request.Request(meta_url, headers=HEADERS)
        with urllib.request.urlopen(req) as resp:
            meta = json.load(resp)
        title = meta.get("title", "")
        filename = clean_filename(title)
    else:
        filename = clean_filename(custom_name)
    download_video(post_id, filename)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python direct_download.py <sora_video_url> [custom_name]")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
