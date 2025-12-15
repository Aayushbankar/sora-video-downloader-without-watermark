#!/usr/bin/env python3
"""
Fast Sora Video Downloader - Optimized for speed
Includes multiple optimizations to reduce download time
"""

import requests
import json
import sys
import argparse
from urllib.parse import urlparse, quote
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import os

class FastSoraVideoDownloader:
    def __init__(self):
        self.api_base = "https://api.soracdn.workers.dev"
        self.api_proxy = f"{self.api_base}/api-proxy/"
        self.download_proxy = f"{self.api_base}/download-proxy"
        self.thumbnail_proxy = f"{self.api_base}/thumbnail-proxy"
        
        # Optimized headers for faster downloads
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://sorasave.app',
            'Referer': 'https://sorasave.app/',
            'Accept-Encoding': 'gzip, deflate, br',  # Enable compression
            'Connection': 'keep-alive',  # Keep connection alive
            'Cache-Control': 'no-cache'
        }
        
        self.download_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Origin': 'https://sorasave.app',
            'Referer': 'https://sorasave.app/',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
    
    def extract_video_info_fast(self, sora_url):
        """Fast video info extraction with optimized settings"""
        print(f"🔍 Extracting video info...")
        
        try:
            # Use session for connection pooling
            session = requests.Session()
            session.headers.update(self.headers)
            
            api_url = self.api_proxy + quote(sora_url, safe='')
            
            # Faster timeout settings
            response = session.get(api_url, timeout=15)
            response.raise_for_status()
            
            video_data = response.json()
            
            if not video_data.get('post_id'):
                raise ValueError("Video ID not found")
            
            print(f"✅ Got video data in {response.elapsed.total_seconds():.2f}s")
            return video_data
            
        except requests.RequestException as e:
            print(f"❌ Network error: {e}")
            raise
        except (KeyError, ValueError) as e:
            print(f"❌ Invalid response: {e}")
            raise
    
    def download_with_resume(self, download_url, output_path, chunk_size=8192*4):
        """Download with resume capability and optimized settings"""
        print(f"📥 Starting optimized download...")
        
        # Check if partial file exists
        temp_path = output_path + '.tmp'
        resume_pos = 0
        
        if os.path.exists(temp_path):
            resume_pos = os.path.getsize(temp_path)
            print(f"📄 Resuming from {resume_pos / (1024*1024):.2f} MB")
        
        # Setup headers for resume
        download_headers = self.download_headers.copy()
        if resume_pos > 0:
            download_headers['Range'] = f'bytes={resume_pos}-'
        
        session = requests.Session()
        session.headers.update(download_headers)
        
        try:
            response = session.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0)) + resume_pos
            
            # Open file in appropriate mode
            mode = 'ab' if resume_pos > 0 else 'wb'
            with open(temp_path, mode) as f:
                if resume_pos > 0:
                    f.seek(resume_pos)
                
                downloaded = resume_pos
                start_time = time.time()
                
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Calculate speed and ETA
                        elapsed = time.time() - start_time
                        if elapsed > 0:
                            speed = downloaded / elapsed / (1024*1024)  # MB/s
                            if total_size > 0:
                                progress = (downloaded / total_size) * 100
                                eta = (total_size - downloaded) / (speed * 1024*1024) if speed > 0 else 0
                                print(f"⏳ {progress:.1f}% | {speed:.1f} MB/s | ETA: {eta:.0f}s", end='\r')
            
            # Rename temp file to final file
            os.rename(temp_path, output_path)
            
            total_time = time.time() - start_time
            file_size = os.path.getsize(output_path) / (1024*1024)
            avg_speed = file_size / total_time if total_time > 0 else 0
            
            print(f"\n✅ Downloaded {file_size:.2f} MB in {total_time:.1f}s ({avg_speed:.1f} MB/s)")
            return True
            
        except Exception as e:
            print(f"\n❌ Download failed: {e}")
            # Keep temp file for resume
            return False
    
    def download_video_fast(self, sora_url, output_path=None, use_resume=True):
        """Fast video download with optimizations"""
        try:
            # Step 1: Get video info (optimized)
            start_total = time.time()
            video_info = self.extract_video_info_fast(sora_url)
            
            # Step 2: Generate download URL
            post_id = video_info.get('post_id')
            title = video_info.get('title', 'untitled_video')
            clean_filename = self._clean_filename(title)
            
            if not output_path:
                output_path = f"{clean_filename}.mp4"
            
            download_url = f"{self.download_proxy}?id={quote(post_id)}&filename={quote(clean_filename)}"
            print(f"🔗 Download URL: {download_url}")
            
            # Step 3: Download with optimizations
            if use_resume:
                success = self.download_with_resume(download_url, output_path)
            else:
                success = self._simple_download(download_url, output_path)
            
            if success:
                total_time = time.time() - start_total
                print(f"🎉 Total time: {total_time:.1f}s")
                return output_path
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def _simple_download(self, download_url, output_path):
        """Simple download without resume capability"""
        session = requests.Session()
        session.headers.update(self.download_headers)
        
        response = session.get(download_url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        start_time = time.time()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192*4):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        elapsed = time.time() - start_time
                        speed = downloaded / elapsed / (1024*1024) if elapsed > 0 else 0
                        print(f"⏳ {progress:.1f}% | {speed:.1f} MB/s", end='\r')
        
        return True
    
    def _clean_filename(self, filename):
        """Clean filename"""
        if not filename:
            return "untitled_video"
        
        import re
        cleaned = re.sub(r'[^a-zA-Z0-9]', '_', filename)
        cleaned = cleaned[:100]
        return cleaned if cleaned else "untitled_video"
    
    def test_speed(self):
        """Test download speed"""
        print("🚀 Testing download speed...")
        
        # Test with a small file first
        test_url = "https://httpbin.org/bytes/100000"  # 100KB test file
        
        start_time = time.time()
        try:
            response = requests.get(test_url, headers=self.download_headers, timeout=10)
            response.raise_for_status()
            
            download_time = time.time() - start_time
            file_size = len(response.content) / (1024*1024)  # MB
            speed = file_size / download_time if download_time > 0 else 0
            
            print(f"✅ Speed test: {speed:.1f} MB/s (downloaded {file_size:.2f} MB in {download_time:.1f}s)")
            return speed
            
        except Exception as e:
            print(f"❌ Speed test failed: {e}")
            return 0

def main():
    parser = argparse.ArgumentParser(description='Fast Sora Video Downloader')
    parser.add_argument('url', help='Sora video URL')
    parser.add_argument('-o', '--output', help='Output path')
    parser.add_argument('--no-resume', action='store_true', help='Disable resume capability')
    parser.add_argument('--speed-test', action='store_true', help='Run speed test only')
    parser.add_argument('--benchmark', action='store_true', help='Benchmark download speed')
    
    args = parser.parse_args()
    
    downloader = FastSoraVideoDownloader()
    
    if args.speed_test:
        downloader.test_speed()
        return
    
    if not args.url.startswith('https://sora.chatgpt.com/p/'):
        print("❌ Error: Invalid Sora URL format")
        sys.exit(1)
    
    try:
        if args.benchmark:
            print("📊 Benchmarking download speed...")
            start_time = time.time()
            result = downloader.download_video_fast(args.url, args.output, use_resume=not args.no_resume)
            total_time = time.time() - start_time
            
            if result and os.path.exists(result):
                file_size = os.path.getsize(result) / (1024*1024)
                avg_speed = file_size / total_time if total_time > 0 else 0
                print(f"\n📈 Benchmark Results:")
                print(f"   File size: {file_size:.2f} MB")
                print(f"   Total time: {total_time:.1f}s")
                print(f"   Average speed: {avg_speed:.1f} MB/s")
            else:
                print("❌ Benchmark failed")
        else:
            result = downloader.download_video_fast(args.url, args.output, use_resume=not args.no_resume)
            
            if result:
                print(f"🎉 Video saved to: {result}")
            else:
                print("❌ Download failed")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n⚠️  Download interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()