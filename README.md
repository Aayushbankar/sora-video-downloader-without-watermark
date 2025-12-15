# Sora Video Downloader

A collection of tools to download watermark-free videos from Sora (OpenAI), reverse-engineered from `sorasave.app`.

## 📂 Project Structure

- `src/sora_downloader.py`: **Main Tool**. Fast, concurrent downloader with resume support.
- `scripts/download.sh`: Lightweight Bash/Curl alternative.
- `examples/minimal_download.py`: A minimal, dependency-free Python example.
- `docs/`: Technical documentation and reverse engineering reports.
- `tests/`: API connectivity tests.

## 🚀 Usage

### 1. Python Downloader (Recommended)
Fastest method. Supports resumption and parallel downloads.

```bash
# Install dependencies
pip install -r requirements.txt

# Run
python src/sora_downloader.py "https://sora.chatgpt.com/p/your_video_id"
```

### 2. Bash Script
No dependencies other than `curl` and `jq`.

```bash
./scripts/download.sh "https://sora.chatgpt.com/p/your_video_id"
```

### 3. Minimal Example
Pure Python (std lib only).

```bash
python examples/minimal_download.py "https://sora.chatgpt.com/p/your_video_id"
```

## ⚠️ Disclaimer
This tool uses a third-party proxy (`api.soracdn.workers.dev`) discovered via reverse engineering. It is for educational purposes only.