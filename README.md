# Sora Video Downloader (Clean-Room Hybrid)

This is the `v4` branch, featuring a rewritten, cleaner implementation of the Sora Video Downloader. It prioritizes direct communication with OpenAI's servers and only falls back to external proxies when absolutely necessary.

## 🌟 Key Features

*   **Clean-Room First**: Attempts to download videos directly from `sora.chatgpt.com` using standard web technologies (no API tokens required for public videos).
*   **Cookie Authentication**: Supports user session cookies to access non-watermarked videos if your account has permission.
*   **Hybrid Fallback**: If direct access fails (e.g., account restriction on clean videos), it automatically falls back to the `sorasave` proxy to ensure you still get a **Non-Watermarked** video.
*   **Cloudflare Bypass**: Integrated `curl_cffi` to handle anti-bot protection seamlessly.

## 📂 Project Structure

- `src/sora_downloader.py`: The core downloader script.
- `requirements.txt`: Python dependencies.
- `download_vids/`: (Created at runtime) Directory for downloaded videos.

## 🚀 Usage

### 1. Installation

```bash
# Recommended: Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Basic Usage (Hybrid Mode)

This is the default and recommended mode. It tries the clean method first, then the proxy if needed.

```bash
python src/sora_downloader.py "https://sora.chatgpt.com/p/your_video_id"
```

### 3. Authenticated Usage (Pure Clean-Room Attempt)

If you have a Sora account that can view non-watermarked videos, provide your cookie to download directly without the proxy.

1.  **Get your Cookie**:
    - Go to `sora.chatgpt.com` in your browser.
    - Open DevTools (F12) -> Application -> Cookies.
    - Copy the value of `__Secure-next-auth.session-token`.
2.  **Run with Cookie**:

```bash
python src/sora_downloader.py "URL" --cookie "your_cookie_string_or_file"
```

### 4. Strict "No Proxy" Mode

If you strictly want to avoid any third-party proxy calls (even if it means getting a watermarked video):

```bash
python src/sora_downloader.py "URL" --no-proxy
```

## ⚠️ Disclaimer
This tool interacts with sora.chatgpt.com and potentially api.soracdn.workers.dev. Use responsibly and in accordance with terms of service.