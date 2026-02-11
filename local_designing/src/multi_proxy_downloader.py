#!/usr/bin/env python3
"""
Multi-Proxy Sora Video Downloader
Implements automatic fallback between multiple proxy services for reliability.
"""

import base64
import hashlib
import time
import requests
from typing import Dict, Optional, List
from urllib.parse import quote
from dataclasses import dataclass


@dataclass
class ProxyResponse:
    """Standardized response from proxy services"""
    success: bool
    video_url: Optional[str] = None
    post_id: Optional[str] = None
    title: Optional[str] = None
    prompt: Optional[str] = None
    error: Optional[str] = None
    proxy_used: Optional[str] = None


class RateLimitManager:
    """Manages rate limiting for proxy services"""
    def __init__(self):
        self.rate_limits = {}
    
    def is_limited(self, proxy_name: str) -> bool:
        """Check if proxy is currently rate limited"""
        if proxy_name not in self.rate_limits:
            return False
        return time.time() < self.rate_limits[proxy_name]
    
    def mark_limited(self, proxy_name: str, duration: int = 3600):
        """Mark proxy as rate limited for specified duration (seconds)"""
        self.rate_limits[proxy_name] = time.time() + duration
    
    def clear_limit(self, proxy_name: str):
        """Clear rate limit for proxy"""
        if proxy_name in self.rate_limits:
            del self.rate_limits[proxy_name]


class SoraSaveProxy:
    """
    SoraSave.app implementation using Cloudflare Workers proxy
    Endpoint: api.soracdn.workers.dev
    """
    NAME = "SoraSave (Cloudflare Workers)"
    BASE_URL = "https://api.soracdn.workers.dev"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Origin': 'https://sorasave.app',
            'Referer': 'https://sorasave.app/',
        })
    
    def fetch(self, sora_url: str) -> ProxyResponse:
        """Fetch video information and download URL"""
        try:
            # Step 1: Get post_id and metadata
            encoded_url = quote(sora_url, safe='')
            api_url = f"{self.BASE_URL}/api-proxy/{encoded_url}"
            
            response = self.session.get(api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            post_id = data.get('post_id')
            
            if not post_id:
                return ProxyResponse(
                    success=False,
                    error="No post_id in response",
                    proxy_used=self.NAME
                )
            
            # Step 2: Get download URL
            download_url = f"{self.BASE_URL}/download-proxy?id={post_id}"
            
            return ProxyResponse(
                success=True,
                video_url=download_url,
                post_id=post_id,
                title=data.get('title', 'untitled'),
                proxy_used=self.NAME
            )
            
        except requests.RequestException as e:
            return ProxyResponse(
                success=False,
                error=f"SoraSave proxy error: {str(e)}",
                proxy_used=self.NAME
            )


class SaveSoraProxy:
    """
    SaveSora.com implementation with signature generation
    Endpoint: savesora.com/api
    """
    NAME = "SaveSora (Custom Backend)"
    BASE_URL = "https://savesora.com/api"
    
    def __init__(self):
        self.session = requests.Session()
        self.user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Origin': 'https://savesora.com',
            'Referer': 'https://savesora.com/',
        })
    
    def _generate_signature(self, video_url: str) -> str:
        """
        Generate anti-bot signature (reverse engineered)
        This replicates SaveSora's client-side signature mechanism
        """
        timestamp = int(time.time() * 1000)
        
        # Simple hash of URL (MD5 first 8 chars)
        url_hash = hashlib.md5(video_url.encode()).hexdigest()[:8]
        
        # Combine elements
        raw_signature = f"{timestamp}:{self.user_agent}:{url_hash}"
        
        # Base64 encode
        b64_sig = base64.b64encode(raw_signature.encode()).decode()
        
        # Character obfuscation (reverse engineered pattern)
        # This is a simplified version - actual implementation may vary
        obfuscated = (b64_sig
            .replace('a', '\x00')
            .replace('x', 'a')
            .replace('\x00', 'x')
            .replace('==', ''))
        
        return obfuscated
    
    def fetch(self, sora_url: str) -> ProxyResponse:
        """Fetch video using SaveSora API"""
        try:
            # Generate signature
            signature = self._generate_signature(sora_url)
            
            # Make API request
            payload = {
                "video_url": sora_url,
                "signature": signature
            }
            
            # Add authorization header (Bearer null for unauthenticated)
            headers = {
                'Authorization': 'Bearer null'
            }
            
            response = self.session.post(
                f"{self.BASE_URL}/web-download",
                json=payload,
                headers=headers,
                timeout=15
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Handle different response codes
            code = data.get('code')
            
            if code == 200:
                # Success
                download_links = data.get('download_links', [])
                original_video = data.get('original_video', {})
                
                return ProxyResponse(
                    success=True,
                    video_url=download_links[0] if download_links else None,
                    title=original_video.get('prompt', 'untitled'),
                    prompt=original_video.get('prompt'),
                    proxy_used=self.NAME
                )
            
            elif code in [201, 202, 203]:
                # Quota exhausted or login required
                return ProxyResponse(
                    success=False,
                    error="SaveSora quota exhausted or login required",
                    proxy_used=self.NAME
                )
            
            else:
                return ProxyResponse(
                    success=False,
                    error=f"SaveSora returned code {code}",
                    proxy_used=self.NAME
                )
        
        except requests.RequestException as e:
            return ProxyResponse(
                success=False,
                error=f"SaveSora proxy error: {str(e)}",
                proxy_used=self.NAME
            )


class MultiProxyDownloader:
    """
    Universal Sora downloader with automatic fallback between multiple proxies
    """
    def __init__(self):
        self.proxies = [
            SoraSaveProxy(),      # Primary: Cloudflare Workers (most reliable)
            SaveSoraProxy(),      # Fallback: Custom backend (feature-rich)
        ]
        self.rate_limit_manager = RateLimitManager()
    
    def get_video_info(self, sora_url: str) -> ProxyResponse:
        """
        Attempt to fetch video info using available proxies with fallback
        
        Args:
            sora_url: Full Sora video URL (e.g., https://sora.chatgpt.com/p/s_xxxxx)
        
        Returns:
            ProxyResponse with video information or error details
        """
        errors = []
        
        for proxy in self.proxies:
            proxy_name = proxy.NAME
            
            # Check rate limiting
            if self.rate_limit_manager.is_limited(proxy_name):
                errors.append(f"{proxy_name}: Rate limited (skipped)")
                continue
            
            # Attempt fetch
            print(f"Trying {proxy_name}...")
            result = proxy.fetch(sora_url)
            
            if result.success:
                print(f"✓ Success with {proxy_name}")
                return result
            
            # Handle quota exhaustion
            if "quota" in result.error.lower() or "login required" in result.error.lower():
                print(f"✗ {proxy_name}: Quota exhausted, marking as rate limited")
                self.rate_limit_manager.mark_limited(proxy_name, duration=3600)  # 1 hour
            
            errors.append(f"{proxy_name}: {result.error}")
        
        # All proxies failed
        return ProxyResponse(
            success=False,
            error=f"All proxies failed:\n" + "\n".join(errors),
            proxy_used="None"
        )
    
    def download_video(self, sora_url: str, output_path: str) -> bool:
        """
        Download video to specified path
        
        Args:
            sora_url: Sora video URL
            output_path: Path to save MP4 file
        
        Returns:
            True if successful, False otherwise
        """
        # Get video info
        result = self.get_video_info(sora_url)
        
        if not result.success:
            print(f"Error: {result.error}")
            return False
        
        if not result.video_url:
            print("Error: No download URL in response")
            return False
        
        # Download video
        print(f"Downloading from: {result.video_url}")
        try:
            response = requests.get(result.video_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=32768):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Progress indicator
                        if total_size:
                            percent = (downloaded / total_size) * 100
                            print(f"\rProgress: {percent:.1f}%", end='', flush=True)
            
            print(f"\n✓ Downloaded successfully: {output_path}")
            return True
        
        except requests.RequestException as e:
            print(f"\n✗ Download error: {e}")
            return False


def main():
    """Example usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python multi_proxy_downloader.py <sora_url> [output.mp4]")
        print("\nExample:")
        print('  python multi_proxy_downloader.py "https://sora.chatgpt.com/p/s_xxxxx" output.mp4')
        sys.exit(1)
    
    sora_url = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "downloaded_video.mp4"
    
    print(f"Sora Video Multi-Proxy Downloader")
    print(f"URL: {sora_url}")
    print(f"Output: {output_path}\n")
    
    downloader = MultiProxyDownloader()
    success = downloader.download_video(sora_url, output_path)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
