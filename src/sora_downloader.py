import re
import json
import sys
import os
from curl_cffi import requests

class CleanSoraDownloader:
    def __init__(self, cookie=None, allow_proxy=True):
        self.session = requests.Session()
        self.allow_proxy = allow_proxy
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://sora.chatgpt.com/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
        if cookie:
            # Add session token cookie
            # Check if full string or just token
            if "session-token" not in cookie and "=" not in cookie:
                cookie_val = f"__Secure-next-auth.session-token={cookie}"
            else:
                cookie_val = cookie
            self.headers["Cookie"] = cookie_val

    def get_video_info(self, url):
        """
        Extract video metadata and download URL from the Sora page.
        """
        print(f"Fetching {url}...")
        try:
            response = self.session.get(
                url,
                impersonate="chrome120",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"Failed to fetch page: {e}")

        html_content = response.text
        
        # Extract Post ID for proxy fallback
        post_id_match = re.search(r'/p/([^/?#]+)', url)
        post_id = post_id_match.group(1) if post_id_match else None
        
        clean_url = None
        is_clean = False
        title = "sora_video"

        # 1. Try to find the "no_watermark" URL in the download_urls JSON blob
        # Pattern: no_watermark\\?":\\?"(https?://[^"]+)"
        clean_match = re.search(r'no_watermark\\?":\\?"(https?://[^"]+)', html_content)
        if clean_match:
            raw_clean = clean_match.group(1).rstrip('\\')
            try:
                clean_url = json.loads(f'"{raw_clean}"')
                if clean_url and clean_url != "null":
                    is_clean = True
            except:
                pass

        # 2. Fallback to Proxy if allowed and no clean URL found
        if not is_clean and self.allow_proxy and post_id:
            print("⚠️  Clean URL not found in metadata. Attempting sorasave.app proxy...")
            # We use the proxy stream directly.
            clean_url = f"https://api.soracdn.workers.dev/download-proxy?id={post_id}&filename=video.mp4"
            # We assume the proxy returns a clean video (it usually does).
            is_clean = True 
            print("✅  Using proxy URL for non-watermarked video.")

        # 3. Final Fallback: "downloadable_url" (Watermarked)
        download_url = clean_url
        if not download_url:
            print("⚠️  Non-watermarked URL not found. Falling back to default asset (may have watermark).")
            # Pattern: downloadable_url\\?":\\?"(https?://[^"]+)
            download_match = re.search(r'downloadable_url\\?":\\?"(https?://[^"]+)', html_content)
            
            if not download_match:
                with open("debug_fail.html", "w") as f:
                    f.write(html_content)
                raise ValueError("Could not find downloadable_url in page content. See debug_fail.html")

            raw_url = download_match.group(1).rstrip('\\')
            try:
                download_url = json.loads(f'"{raw_url}"')
            except:
                download_url = raw_url

        # Extract title
        text_match = re.search(r'"text":"([^"]+)"', html_content)
        if text_match:
             try:
                 title = json.loads(f'"{text_match.group(1)}"')
                 title = re.sub(r'[^a-zA-Z0-9_\-]', '_', title)[:100]
             except:
                 pass
                 
        return {
            "download_url": download_url,
            "title": title,
            "is_clean": is_clean
        }

    def download_video(self, url, output_dir="."):
        """
        Download the video to the output directory.
        """
        info = self.get_video_info(url)
        download_url = info["download_url"]
        title = info["title"]
        is_clean = info["is_clean"]
        
        filename = f"{title}.mp4"
        output_path = os.path.join(output_dir, filename)
        
        print(f"Downloading to {output_path}...")
        print(f"Source: {download_url}")
        print(f"Type: {'Clean (No Watermark)' if is_clean else 'Watermarked (Standard)'}")
        
        try:
            # Stream download
            response = self.session.get(
                download_url,
                impersonate="chrome120",
                headers=self.headers, # Use same headers (cookies) for download? Usually SAS is enough but no harm.
                stream=True,
                timeout=60
            )
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rProgress: {percent:.1f}%", end="")
                            
            print(f"\n✅ Download complete: {output_path}")
            return output_path
            
        except Exception as e:
            if os.path.exists(output_path):
                os.remove(output_path)
            raise Exception(f"Download failed: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean Room Sora Downloader")
    parser.add_argument("url", help="Sora Video URL")
    parser.add_argument("--cookie", help="Session token cookie for clean download", default=None)
    parser.add_argument("-o", "--output", help="Output directory", default=".")
    
    parser.add_argument("--no-proxy", action="store_true", help="Disable fallback to sorasave proxy")
    
    args = parser.parse_args()
        
    downloader = CleanSoraDownloader(cookie=args.cookie, allow_proxy=not args.no_proxy)
    try:
        downloader.download_video(args.url, output_dir=args.output)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
