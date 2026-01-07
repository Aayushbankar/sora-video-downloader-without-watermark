#!/usr/bin/env python3
"""
Sora Video Downloader (Playwright/Camoufox Edition)
Independent downloader using anti-detect browser to bypass Cloudflare.

This eliminates dependency on third-party CDN workers by directly
extracting video URLs from Sora pages.

Author: Independent Implementation
Date: 2026-01-07
"""

import argparse
import os
import re
import sys
import time
from urllib.parse import urlparse, unquote

try:
    from camoufox.sync_api import Camoufox
    CAMOUFOX_AVAILABLE = True
except ImportError:
    CAMOUFOX_AVAILABLE = False

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

import requests


class SoraPlaywrightDownloader:
    """
    Downloads watermark-free Sora videos using an anti-detect browser.
    
    Uses Camoufox (if available) or falls back to standard Playwright
    with stealth patches for Cloudflare bypass.
    """
    
    def __init__(self, proxy: str = None, headless: bool = True, timeout: int = 60):
        """
        Initialize the downloader.
        
        Args:
            proxy: Optional proxy URL (format: http://user:pass@host:port)
            headless: Run in headless mode (use "virtual" for Camoufox virtual display)
            timeout: Page load timeout in seconds
        """
        self.proxy = proxy
        self.headless = headless
        self.timeout = timeout * 1000  # Convert to milliseconds
        self.captured_video_url = None
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
            'Accept': 'video/webm,video/ogg,video/*;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    
    def _setup_request_interception(self, page):
        """
        Set up network request interception to capture CDN video URLs.
        
        The raw video is served from cdn.openai.com without watermark.
        """
        def handle_request(route, request):
            url = request.url
            
            # Capture video URLs from OpenAI CDN
            if 'cdn.openai.com' in url and '/MP4/' in url:
                print(f"📹 Captured video URL: {url[:80]}...")
                self.captured_video_url = url
            
            # Alternative patterns
            elif 'sora' in url.lower() and '.mp4' in url.lower():
                if not self.captured_video_url:
                    print(f"📹 Captured video URL (alt): {url[:80]}...")
                    self.captured_video_url = url
            
            route.continue_()
        
        page.route("**/*", handle_request)
    
    def _extract_video_from_dom(self, page) -> str:
        """
        Fallback: Extract video URL from DOM elements.
        """
        selectors = [
            "video source",
            "video[src]",
            "source[type='video/mp4']",
            "[data-video-url]",
        ]
        
        for selector in selectors:
            try:
                element = page.locator(selector).first
                if element:
                    src = element.get_attribute("src") or element.get_attribute("data-video-url")
                    if src and ('cdn.openai.com' in src or '.mp4' in src):
                        print(f"📹 Found video URL in DOM: {src[:80]}...")
                        return src
            except:
                continue
        
        return None
    
    def _extract_title_from_page(self, page) -> str:
        """
        Extract video title from the page.
        """
        try:
            # Try meta title first
            title = page.locator('meta[property="og:title"]').get_attribute("content")
            if title:
                return title
            
            # Try page title
            title = page.title()
            if title and 'sora' not in title.lower():
                return title
            
            # Try heading
            h1 = page.locator("h1").first
            if h1:
                return h1.text_content()
                
        except:
            pass
        
        return None
    
    def _clean_filename(self, filename: str) -> str:
        """
        Clean filename for saving to disk.
        """
        if not filename:
            return "sora_video"
        
        # Remove special chars
        cleaned = re.sub(r'[^a-zA-Z0-9\-_\s]', '', filename)
        cleaned = re.sub(r'\s+', '_', cleaned)
        cleaned = cleaned[:80]  # Limit length
        
        return cleaned if cleaned else "sora_video"
    
    def _download_video(self, video_url: str, output_path: str):
        """
        Download video from URL to file.
        """
        print(f"📥 Downloading video...")
        
        try:
            response = requests.get(video_url, headers=self.headers, stream=True, timeout=120)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=32768):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"⏳ Progress: {progress:.1f}%", end='\r')
            
            file_size = os.path.getsize(output_path)
            print(f"\n✅ Downloaded: {output_path} ({file_size / (1024*1024):.2f} MB)")
            return output_path
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            raise
    
    def download_with_camoufox(self, sora_url: str, output_path: str = None) -> str:
        """
        Download video using Camoufox anti-detect browser.
        """
        print("🦊 Using Camoufox (anti-detect mode)...")
        
        headless_mode = "virtual" if self.headless else False
        
        with Camoufox(headless=headless_mode) as browser:
            page = browser.new_page()
            page.set_default_timeout(self.timeout)
            
            # Set up network interception
            self._setup_request_interception(page)
            
            print(f"🌐 Navigating to: {sora_url}")
            
            try:
                page.goto(sora_url, wait_until="networkidle")
            except Exception as e:
                print(f"⚠️ Navigation warning: {e}")
            
            # Wait for video to potentially load
            page.wait_for_timeout(3000)
            
            # Try DOM extraction as fallback
            if not self.captured_video_url:
                self.captured_video_url = self._extract_video_from_dom(page)
            
            if not self.captured_video_url:
                raise ValueError("❌ Could not find video URL on page")
            
            # Get title for filename
            title = self._extract_title_from_page(page)
            
            if not output_path:
                clean_title = self._clean_filename(title)
                output_path = f"{clean_title}_nowatermark.mp4"
            
            return self._download_video(self.captured_video_url, output_path)
    
    def download_with_playwright(self, sora_url: str, output_path: str = None) -> str:
        """
        Download video using standard Playwright with stealth patches.
        """
        print("🎭 Using Playwright...")
        
        with sync_playwright() as p:
            # Launch with stealth settings
            browser = p.firefox.launch(
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
                locale='en-US',
            )
            
            page = context.new_page()
            page.set_default_timeout(self.timeout)
            
            # Hide webdriver
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            # Set up network interception
            self._setup_request_interception(page)
            
            print(f"🌐 Navigating to: {sora_url}")
            
            try:
                page.goto(sora_url, wait_until="networkidle")
            except Exception as e:
                print(f"⚠️ Navigation warning: {e}")
            
            page.wait_for_timeout(3000)
            
            if not self.captured_video_url:
                self.captured_video_url = self._extract_video_from_dom(page)
            
            if not self.captured_video_url:
                browser.close()
                raise ValueError("❌ Could not find video URL (Cloudflare may have blocked access)")
            
            title = self._extract_title_from_page(page)
            browser.close()
            
            if not output_path:
                clean_title = self._clean_filename(title)
                output_path = f"{clean_title}_nowatermark.mp4"
            
            return self._download_video(self.captured_video_url, output_path)
    
    def download(self, sora_url: str, output_path: str = None) -> str:
        """
        Download video from Sora URL.
        
        Automatically uses Camoufox if available, falls back to Playwright.
        
        Args:
            sora_url: The Sora video share URL
            output_path: Optional output path (auto-generated if not provided)
            
        Returns:
            Path to downloaded video file
        """
        # Validate URL
        if 'sora' not in sora_url.lower():
            raise ValueError("URL must be a Sora share link")
        
        self.captured_video_url = None
        
        # Prefer Camoufox for better Cloudflare bypass
        if CAMOUFOX_AVAILABLE:
            return self.download_with_camoufox(sora_url, output_path)
        elif PLAYWRIGHT_AVAILABLE:
            print("⚠️ Camoufox not installed, using standard Playwright (may get blocked)")
            return self.download_with_playwright(sora_url, output_path)
        else:
            raise RuntimeError(
                "Neither Camoufox nor Playwright is installed!\n"
                "Install with: pip install camoufox playwright && camoufox fetch"
            )


def main():
    parser = argparse.ArgumentParser(
        description='Download watermark-free Sora videos using Playwright',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sora_playwright_downloader.py "https://sora.chatgpt.com/p/your-video-url"
  python sora_playwright_downloader.py "URL" -o my_video.mp4
  python sora_playwright_downloader.py "URL" --visible  # See browser window

Requirements:
  pip install camoufox playwright
  camoufox fetch
        """
    )
    
    parser.add_argument('url', help='Sora video share URL')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('--visible', action='store_true', help='Show browser window')
    parser.add_argument('--proxy', help='Proxy URL (http://user:pass@host:port)')
    parser.add_argument('--timeout', type=int, default=60, help='Page load timeout in seconds')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎬 Sora Video Downloader (Playwright Edition)")
    print("=" * 60)
    
    try:
        downloader = SoraPlaywrightDownloader(
            proxy=args.proxy,
            headless=not args.visible,
            timeout=args.timeout
        )
        
        output_path = downloader.download(args.url, args.output)
        
        print("\n" + "=" * 60)
        print(f"🎉 Success! Video saved to: {output_path}")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n⚠️ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
