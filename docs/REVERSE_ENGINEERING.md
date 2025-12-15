# SoraSave Reverse Engineering Report

## 🔍 Analysis Summary

Successfully reverse engineered the SoraSave video downloader service (sorasave.app) to understand how it extracts non-watermarked videos from Sora.

## 🏗️ Architecture Discovered

### Frontend
- **Technology**: React-based single-page application
- **Styling**: Tailwind CSS
- **Main JS**: `/assets/index-DMmagjR7.js` (623KB)

### Backend API
- **Base URL**: `https://api.soracdn.workers.dev`
- **Technology**: Cloudflare Workers
- **CORS**: Enabled for `sorasave.app` origin

## 🔗 API Endpoints Discovered

### 1. Video Information Extraction
```
GET /api-proxy/{encoded_sora_url}
```
- **Purpose**: Extracts video metadata from Sora URL
- **Variable in JS**: `Sx`
- **Response**: JSON with `post_id`, `title`, `description`

### 2. Video Download
```
GET /download-proxy?id={post_id}&filename={filename}
```
- **Purpose**: Provides direct download link
- **Variable in JS**: `Ex`
- **Response**: MP4 video file (no watermarks)

### 3. Thumbnail Download
```
GET /thumbnail-proxy?id={post_id}
```
- **Purpose**: Gets video thumbnail
- **Variable in JS**: `Ax`
- **Response**: Image file

## 🔄 Workflow Analysis

1. **URL Processing**: Client encodes Sora URL using `encodeURIComponent()`
2. **API Request**: Sends to `/api-proxy/` endpoint
3. **Metadata Extraction**: API returns video information including `post_id`
4. **Download URL Generation**: Client constructs download URL with `post_id` and cleaned filename
5. **Direct Download**: API serves video file without watermarks

## 🛠️ Tools Created

### 1. Python Script (`sora_video_downloader.py`)
- Full-featured downloader with progress bars
- Multiple options: info-only, thumbnail download, custom output
- Error handling and validation
- 200+ lines of clean, documented code

### 2. Bash Script (`sora_download_curl.sh`)
- Lightweight alternative using curl/wget
- JSON parsing with jq
- URL encoding and filename cleaning
- Progress indicators

### 3. Testing Tools
- `test_api.py`: API connectivity and response validation
- `demo_usage.py`: Demonstration and usage examples

### 4. Documentation
- `README.md`: Comprehensive usage guide
- `REVERSE_ENGINEERING_REPORT.md`: This technical report

## 🔒 Security & Privacy Claims

Based on the original site's claims:
- No data storage on servers
- No video content viewing
- Secure proxy functionality
- Privacy-focused approach

## ⚠️ Legal Considerations

- Tool for educational and personal use
- Respect content creators' rights
- Comply with Sora's terms of service
- Not affiliated with OpenAI (as stated by original site)

## 🎯 Key Findings

1. **No Magic**: The service uses a simple proxy API to bypass watermarks
2. **Cloudflare Workers**: Serverless architecture for scalability
3. **Clean API Design**: Simple, RESTful endpoints
4. **Rate Limiting**: Likely present but not documented
5. **Public URLs Required**: Only works with publicly accessible Sora videos

## 📊 Technical Details

### API Response Format
```json
{
  "post_id": "s_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "title": "video_title",
  "description": "video_description",
  "created_at": "2025-12-15T10:30:00Z"
}
```

### Filename Cleaning Algorithm
- Replace non-alphanumeric characters with `_`
- Limit to 100 characters
- Default to "untitled_video" if empty

### Headers Required
```
User-Agent: Mozilla/5.0 (compatible browser)
Accept: application/json
Origin: https://sorasave.app
Referer: https://sorasave.app/
```

## 🚀 Usage Examples

### Basic Download
```bash
python sora_video_downloader.py "https://sora.chatgpt.com/p/video_id"
```

### With Custom Output
```bash
python sora_video_downloader.py "https://sora.chatgpt.com/p/video_id" -o custom.mp4
```

### Get Info Only
```bash
python sora_video_downloader.py "https://sora.chatgpt.com/p/video_id" --info-only
```

## 🔍 Reverse Engineering Process

1. **Website Analysis**: Loaded sorasave.app, examined structure
2. **JavaScript Inspection**: Found main bundle at `/assets/index-DMmagjR7.js`
3. **API Discovery**: Located three API endpoints in JS variables
4. **Pattern Analysis**: Identified URL encoding and request patterns
5. **Testing**: Verified API endpoints and response formats
6. **Implementation**: Created working tools based on discovered patterns

## 📈 Success Metrics

- ✅ API endpoints successfully identified
- ✅ Response format understood
- ✅ Working Python implementation
- ✅ Working Bash implementation
- ✅ Comprehensive documentation
- ✅ Error handling implemented
- ✅ Test tools created

## 🎉 Conclusion

The reverse engineering was successful. The SoraSave service uses a simple but effective proxy-based approach to extract non-watermarked videos from Sora. The discovered API endpoints and workflow have been implemented in multiple tools for different use cases.

**Key Takeaway**: The "magic" is simply a proxy service that handles the watermark removal server-side, allowing clients to download clean videos directly.
## 🔬 Direct Download Analysis

### Findings
The service relies on a proxy (`api.soracdn.workers.dev`) to fetch videos. Direct access to `sora.chatgpt.com` or `videos.openai.com` is protected by:
1.  **Cloudflare**: Prevents automated scraping (blocks headless browsers).
2.  **Azure Blob Storage Auth**: The underlying storage uses SAS tokens or strict container policies, returning `400 Bad Request` for direct access without a valid signature.

### Recommendation
Use the provided `src/sora_downloader.py` (which uses the `api.soracdn.workers.dev` proxy) as it is the only reliable method found.
