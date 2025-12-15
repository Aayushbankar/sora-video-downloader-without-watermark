# Sora Video Downloader

A collection of tools to download watermark-free videos from Sora (OpenAI), reverse-engineered from `sorasave.app`.

## 📂 Project Structure

- `src/sora_downloader.py`: **Main Tool**. Robust Python downloader with automatic filename generation.
- `scripts/`:
    - `download.sh`: Lightweight Bash/Curl alternative.
    - `benchmark_downloads.py`: Script to bulk download and measure speed.
- `examples/minimal_download.py`: A minimal, dependency-free Python example.
- `docs/`: Technical documentation and reverse engineering reports.
- `download_vids/`: (Created at runtime) Directory for downloaded videos.

## 🚀 Usage

### 1. Python Downloader (Recommended)
Fastest method. Automatically names files based on the video title.

```bash
# Install dependencies
pip install -r requirements.txt

# Run
python src/sora_downloader.py "https://sora.chatgpt.com/p/your_video_id"

# Options
python src/sora_downloader.py "..." -o my_custom_name.mp4
python src/sora_downloader.py "..." --info-only
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

## ⚡ Performance & Benchmarking

We include a benchmarking tool to measure download speeds across multiple videos.

**Latest Benchmark Results (Dec 16, 2025):**
```text
DOWNLOAD PERFORMANCE REPORT
Total Videos: 11
Total Time:   242.79 seconds
Average Time: 22.07 seconds per video
Min Time:     17.83 seconds
Max Time:     32.78 seconds
```

**Run the benchmark:**
1. Add URLs to `test_urls.txt` (one per line).
2. Run:
   ```bash
   python scripts/benchmark_downloads.py
   ```
3. Check `download_report.txt` for the summary.

## 📚 Documentation
- [Reverse Engineering Report](docs/REVERSE_ENGINEERING.md): How the exploit works.
- [Comprehensive Analysis](docs/COMPREHENSIVE_ANALYSIS.md): Detailed breakdown of failed attempts (browser automation, direct access) and why the proxy is required.

## ⚠️ Disclaimer
This tool uses a third-party proxy (`api.soracdn.workers.dev`) discovered via reverse engineering. It is for educational purposes only.