# API Changes & Fixes Report - 2026-02-11

## Overview

This document details the changes discovered in the SoraSave API on **February 11, 2026**, the impact on our services, and the fixes implemented in the `local_designing` codebase.

## 1. API Changes Discovered

The upstream Sora API (`api.soracdn.workers.dev`) underwent significant structural changes.

### A. Response Structure: Title Relocation
*   **Old Structure:** The video `title` was a top-level field in the JSON response.
*   **New Structure:** The video `title` is now nested inside a `post_info` object. The top-level `title` field is **missing**.

**Old JSON (Simplified):**
```json
{
  "post_id": "s_123...",
  "title": "My Video Title",  <-- NO LONGER HERE
  "description": "..."
}
```

**New JSON (Simplified):**
```json
{
  "post_id": "s_123...",
  "post_info": {
    "title": "My Video Title", <-- MOVED HERE
    "view_count": 1234
  },
  "links": { ... }
}
```

### B. Response Structure: Direct Links
*   **New Feature:** The API now provides a `links` object containing direct URLs for `mp4`, `thumbnail`, and `gif`. This simplifies access compared to constructing the download URL manually, though the manual construction method still works.

## 2. Impact on Services

### A. CLI Downloader (`sora_downloader.py`)
*   **Issue:** The tool was failing to extract the video title, defaulting to "untitled_video" or raising errors depending on strictness.
*   **Status:** **FIXED**.
*   **Fix Details:** Updated logic to check `video_data.get('post_info', {}).get('title')` if the top-level title is missing.

### B. Web Application
*   **Issue 1 (Title):** The frontend (`app.js`) was failing to find the title, likely resulting in "undefined" filenames.
*   **Issue 2 (Extension):** The downloaded files were missing the `.mp4` extension (e.g., `video_SR` instead of `video_SR.mp4`), causing playback issues for users.
*   **Status:** **VERIFIED FIXED**.
*   **Fix Details:**
    *   **Snippet in `app.js`:**
        ```javascript
        const pi = d.post_info || {}; // Handle new structure
        let n = pi.title || ...;
        // ...
        c += '_SR.mp4'; // Explicitly add extension
        ```
    *   **Verification:** inspected `assets/js/app.js` and confirmed the fixes are present in the deployed code.

## 3. Verification Steps Performed

1.  **Reproduction:** Created `verify_api_changes.py` to hit the live API with a known valid URL.
    *   Confirmed top-level `title` is missing.
    *   Confirmed `post_info.title` is present.
    *   Confirmed `links.mp4` is present.

2.  **Test Suite Update:** Updated `tests/test_api.py`.
    *   Switched to a valid, live Sora URL for integration testing.
    *   Added assertions for `post_info` and `links` presence.
    *   Tests **PASSED**.

3.  **Code Review:**
    *   `src/sora_downloader.py`: Verified logic handles both old and new structures (backward compatibility).
    *   `assets/js/app.js`: Verified frontend code handles new structure and file extensions.

## 4. Conclusion

The API changes have been successfully identified and addressed. Both the Python CLI tools and the Web Application frontend code are updated to support the new API structure as of Feb 11, 2026.

**Files Created/Updated:**
*   `tests/test_api.py` (Updated assertions)
*   `verify_api_changes.py` (New verification utility)
*   `docs/API_CHANGES_2026_02_11.md` (This report)
