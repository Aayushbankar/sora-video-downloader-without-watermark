# SoraSave Downloader - API Change Report

## Overview
The SoraSave downloader (both CLI and Web) stopped working correctly because the upstream API (`api.soracdn.workers.dev`) changed its response structure.

---

## 1. CLI App Changes Made (`sora_downloader.py`)

### Problem
The `extract_video_info` method was looking for `title` at the top level of the API response:
```python
title = video_data.get('title')
```

### Root Cause
The API now returns `title` inside a nested `post_info` object.

### Fix Applied
Updated the extraction logic to check `post_info` first:
```diff
-title = video_data.get('title')
+post_info = video_data.get('post_info', {})
+title = video_data.get('title') or post_info.get('title')
+
+# Map back to flat structure for compatibility
+if not video_data.get('title') and title:
+    video_data['title'] = title
```

---

## 2. API Response Structure Changes

### Old Structure (Expected)
```json
{
  "post_id": "s_xxx",
  "title": "Video Title",
  "description": "...",
  "created_at": "..."
}
```

### New Structure (Current)
```json
{
  "post_id": "s_xxx",
  "original_input": "...",
  "links": {
    "thumbnail": "https://cdn.openai.com/THUMBNAIL/...",
    "mp4": "https://cdn.openai.com/MP4/...",
    "gif": "https://cdn.openai.com/GIF/..."
  },
  "post_info": {
    "title": "Video Title",
    "prompt": null,
    "view_count": 326986,
    "like_count": 2822,
    "attachments_count": 1
  }
}
```

### Key Differences
| Field            | Old Location | New Location                         |
| ---------------- | ------------ | ------------------------------------ |
| `title`          | Top-level    | `post_info.title`                    |
| `description`    | Top-level    | Removed                              |
| `created_at`     | Top-level    | Removed                              |
| Direct CDN links | Not present  | `links.mp4`, `links.thumbnail`, etc. |

---

## 3. Web App Issue: Missing `.mp4` Extension

### Problem
Downloaded files have no extension (e.g., `ain_t_seen_ya__round_these_parts_before_SR` instead of `ain_t_seen_ya__round_these_parts_before_SR.mp4`).

### Root Cause in `app.js`
The filename generation logic does NOT append `.mp4`:
```javascript
let c = n.replace(/[^a-zA-Z0-9\-\._ ]/g, '').replace(/\s+/g, '_').substring(0, 85);
if (!c) c = 'e_' + d.post_id;
c += '_SR';  // <-- No .mp4 extension added!
```

### Fix Required
Add `.mp4` extension to the filename:
```javascript
c += '_SR.mp4';  // <-- Add .mp4 extension
```

---

## 4. Why Download Still Works (Partially)

The download proxy URL (`/download-proxy`) correctly returns the video with `Content-Type: video/mp4` headers. Browsers can usually play the file, but without the `.mp4` extension:
- File managers may not recognize the file type
- Media players may require manual file association
- Sharing/uploading the file may fail validation

---

## Summary of Actions

| Component                  | Issue                             | Status                     |
| -------------------------- | --------------------------------- | -------------------------- |
| CLI (`sora_downloader.py`) | Title extraction from `post_info` | ✅ Fixed                    |
| CLI                        | File extension                    | ✅ Already correct (`.mp4`) |
| Web (`app.js`)             | Title extraction from `post_info` | ✅ Already handled          |
| Web (`app.js`)             | Missing `.mp4` extension          | ❌ Needs fix                |
