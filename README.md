# Sora Video Downloader - Reverse Engineered

This is a reverse-engineered solution to download non-watermarked videos from Sora, based on the analysis of `sorasave.app`.

## 🔍 How It Works

The solution uses the same API endpoints discovered in the sorasave.app JavaScript code:

1. **API Base**: `https://api.soracdn.workers.dev`
2. **Video Info Endpoint**: `/api-proxy/` - Extracts video metadata from Sora URL
3. **Download Endpoint**: `/download-proxy` - Provides direct download links
4. **Thumbnail Endpoint**: `/thumbnail-proxy` - Gets video thumbnails

## 📦 Files Included

- **`sora_video_downloader.py`** - Full-featured Python script with progress bars and multiple options
- **`sora_download_curl.sh`** - Lightweight bash script using curl/wget
- **`README.md`** - This documentation

## 🚀 Quick Start

### Python Script (Recommended)

```bash
# Basic usage
python sora_video_downloader.py "https://sora.chatgpt.com/p/your-video-url"

# Specify output filename
python sora_video_downloader.py "https://sora.chatgpt.com/p/your-video-url" -o my_video.mp4

# Get video info only
python sora_video_downloader.py "https://sora.chatgpt.com/p/your-video-url" --info-only

# Download with thumbnail
python sora_video_downloader.py "https://sora.chatgpt.com/p/your-video-url" --thumbnail
```

### Bash Script

```bash
# Basic usage
./sora_download_curl.sh "https://sora.chatgpt.com/p/your-video-url"

# Specify output filename
./sora_download_curl.sh "https://sora.chatgpt.com/p/your-video-url" "my_video.mp4"
```

## 🛠️ Installation

### Python Script Requirements

```bash
# Install required packages (if any)
pip install requests
```

### Bash Script Requirements

```bash
# Required tools (usually pre-installed)
- curl or wget
- jq (for JSON parsing)
- bash

# Install jq if not available
sudo apt-get install jq  # Debian/Ubuntu
brew install jq          # macOS
```

## 📋 Usage Examples

### Python Script Options

```bash
# Test API connection
python sora_video_downloader.py --test

# Full download with all options
python sora_video_downloader.py "https://sora.chatgpt.com/p/s_69399f8654808191876cb4613d165b5e" -o emotional_scene.mp4 --thumbnail

# Batch processing (using shell loop)
for url in "url1" "url2" "url3"; do
    python sora_video_downloader.py "$url" -o "video_$(date +%s).mp4"
done
```

### Manual API Usage

If you want to use the API directly:

```bash
# Step 1: Get video info
VIDEO_URL="https://sora.chatgpt.com/p/your-video-url"
ENCODED_URL=$(echo "$VIDEO_URL" | jq -sRr @uri)
curl "https://api.soracdn.workers.dev/api-proxy/$ENCODED_URL"

# Step 2: Download video (using post_id from step 1)
POST_ID="your_post_id"
curl "https://api.soracdn.workers.dev/download-proxy?id=$POST_ID&filename=video.mp4" -o video.mp4
```

## 🏗️ API Reference

### Get Video Information

```
GET https://api.soracdn.workers.dev/api-proxy/{encoded_sora_url}
```

**Response:**
```json
{
  "post_id": "s_69399f8654808191876cb4613d165b5e",
  "title": "emotional sad moment",
  "description": "ring doorbell camera with no watermark...",
  "created_at": "2025-12-15T10:30:00Z"
}
```

### Download Video

```
GET https://api.soracdn.workers.dev/download-proxy?id={post_id}&filename={filename}
```

**Parameters:**
- `id`: The post_id from the video info
- `filename`: Desired filename (will be cleaned automatically)

### Get Thumbnail

```
GET https://api.soracdn.workers.dev/thumbnail-proxy?id={post_id}
```

## ⚠️ Important Notes

1. **URL Format**: Only works with Sora URLs in the format: `https://sora.chatgpt.com/p/{video_id}`

2. **Rate Limiting**: The API may have rate limits. Add delays between multiple downloads:
   ```bash
   sleep 2  # Wait 2 seconds between downloads
   ```

3. **File Naming**: Filenames are automatically cleaned (special characters replaced with underscores, limited to 100 chars)

4. **Privacy**: The API acts as a proxy and doesn't store your data according to the original site's claims

## 🐛 Troubleshooting

### Common Issues

1. **"Video ID not found" error**
   - Ensure the Sora URL is publicly accessible
   - Check that the URL format is correct

2. **"API request failed"**
   - Check internet connection
   - The API might be temporarily unavailable
   - Try again after a few minutes

3. **"Invalid response format"**
   - The Sora URL might be invalid or private
   - Verify the URL works in a browser first

### Debug Mode

For the Python script, you can add debug prints or use:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔒 Legal and Ethical Considerations

- This tool is for educational and personal use only
- Respect content creators' rights
- Don't use for copyright infringement
- Be aware of Sora's terms of service
- The original site (sorasave.app) claims no affiliation with OpenAI

## 📝 Technical Details

### Reverse Engineering Process

1. **Analyzed** sorasave.app JavaScript files
2. **Discovered** API endpoints in `/assets/index-DMmagjR7.js`
3. **Identified** three main endpoints:
   - `Sx` = `"https://api.soracdn.workers.dev/api-proxy/"`
   - `Ex` = `"https://api.soracdn.workers.dev/download-proxy"`
   - `Ax` = `"https://api.soracdn.workers.dev/thumbnail-proxy"`

### API Flow

1. Client encodes Sora URL and sends to `/api-proxy/`
2. API returns video metadata including `post_id`
3. Client constructs download URL with `post_id` and filename
4. Direct download link provided without watermarks

## 🤝 Contributing

Feel free to submit improvements, bug fixes, or additional features!

## 📄 License

This is a reverse-engineered tool for educational purposes. Use responsibly and in accordance with applicable laws and terms of service.

---

**⚠️ Disclaimer**: This tool is provided as-is for educational purposes. The author is not responsible for any misuse or legal issues arising from its use.