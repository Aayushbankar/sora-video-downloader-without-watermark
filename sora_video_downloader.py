#!/usr/bin/env python3
"""
Sora Video Downloader - Extract non-watermarked videos from Sora
Reverse engineered from sorasave.app

Author: Reverse Engineered
Date: 2025-12-15
"""

import requests
import json
import sys
import argparse
from urllib.parse import urlparse, quote
import time

class SoraVideoDownloader:
    def __init__(self):
        self.api_base = "https://api.soracdn.workers.dev"
        self.api_proxy = f"{self.api_base}/api-proxy/"
        self.download_proxy = f"{self.api_base}/download-proxy"
        self.thumbnail_proxy = f"{self.api_base}/thumbnail-proxy"
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://sorasave.app',
            'Referer': 'https://sorasave.app/'
        }
    
    def extract_video_info(self, sora_url):
        """
        Extract video information from Sora URL
        
        Args:
            sora_url (str): The Sora video URL
            
        Returns:
            dict: Video information including post_id and other metadata
        """
        print(f"🔍 Extracting video info from: {sora_url}")
        
        try:
            # Make API call to get video data
            api_url = self.api_proxy + quote(sora_url, safe='')
            print(f"📡 Calling API: {api_url}")
            
            response = requests.get(api_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            video_data = response.json()
            print(f"✅ Got video data: {json.dumps(video_data, indent=2)[:200]}...")
            
            if not video_data.get('post_id'):
                raise ValueError("Video ID not found in response")
            
            return video_data
            
        except requests.RequestException as e:
            print(f"❌ Network error: {e}")
            raise
        except (KeyError, ValueError) as e:
            print(f"❌ Invalid response format: {e}")
            raise
    
    def generate_download_url(self, video_info):
        """
        Generate the direct download URL for the video
        
        Args:
            video_info (dict): Video information from extract_video_info
            
        Returns:
            str: Direct download URL
        """
        post_id = video_info.get('post_id')
        title = video_info.get('title', 'untitled_video')
        
        # Clean filename (similar to ky function in the original code)
        clean_filename = self._clean_filename(title)
        
        download_url = f"{self.download_proxy}?id={quote(post_id)}&filename={quote(clean_filename)}"
        print(f"🔗 Generated download URL: {download_url}")
        
        return download_url
    
    def _clean_filename(self, filename):
        """
        Clean filename by removing special characters (similar to ky function)
        
        Args:
            filename (str): Original filename
            
        Returns:
            str: Cleaned filename
        """
        if not filename:
            return "untitled_video"
        
        # Replace non-alphanumeric characters with underscore
        cleaned = re.sub(r'[^a-zA-Z0-9]', '_', filename)
        # Limit to 100 characters
        cleaned = cleaned[:100]
        
        return cleaned if cleaned else "untitled_video"
    
    # def download_video(self, sora_url, output_path=None):
    #     """
    #     Download the video from Sora URL
        
    #     Args:
    #         sora_url (str): The Sora video URL
    #         output_path (str): Optional output path for the video file
            
    #     Returns:
    #         str: Path to the downloaded video file
    #     """
    #     try:
    #         # Step 1: Extract video info
    #         video_info = self.extract_video_info(sora_url)
            
    #         # Step 2: Generate download URL
    #         download_url = self.generate_download_url(video_info)
            
    #         # Step 3: Download the video
    #         print(f"📥 Downloading video...")
            
    #         response = requests.get(download_url, headers=self.headers, stream=True, timeout=60)
    #         response.raise_for_status()
            
    #         # Determine output filename
    #         if not output_path:
    #             title = video_info.get('title', 'sora_video')
    #             clean_title = self._clean_filename(title)
    #             output_path = f"{clean_title}.mp4"
            
    #         # Save the video
    #         total_size = int(response.headers.get('content-length', 0))
    #         downloaded = 0
            
    #         with open(output_path, 'wb') as f:
    #             for chunk in response.iter_content(chunk_size=8192):
    #                 if chunk:
    #                     f.write(chunk)
    #                     downloaded += len(chunk)
                        
    #                     if total_size > 0:
    #                         progress = (downloaded / total_size) * 100
    #                         print(f"⏳ Progress: {progress:.1f}%", end='\r')
            
    #         print(f"\n✅ Video downloaded successfully: {output_path}")
    #         print(f"📊 File size: {downloaded / (1024*1024):.2f} MB")
            
    #         return output_path
            
    #     except Exception as e:
    #         print(f"❌ Download failed: {e}")
    #         raise
    
    def download_video(self, sora_url, output_path=None):
        """
        Download the video from Sora URL

        Args:
            sora_url (str): The Sora video URL
            output_path (str): Optional output path for the video file

        Returns:
            str: Path to the downloaded video file
        """
        try:
            # Step 1: Extract video info
            video_info = self.extract_video_info(sora_url)

            # Step 2: Generate download URL
            download_url = self.generate_download_url(video_info)

            # Step 3: Download the video
            print(f"📥 Downloading video...")

            response = requests.get(download_url, headers=self.headers, stream=True, timeout=60)
            response.raise_for_status()

            # Determine output filename
            if not output_path:
                title = video_info.get('title', 'sora_video')
                clean_title = self._clean_filename(title)
                output_path = f"{clean_title}.mp4"

            # Save the video
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"⏳ Progress: {progress:.1f}%", end='\r')

            print(f"\n✅ Video downloaded successfully: {output_path}")
            print(f"📊 File size: {downloaded / (1024*1024):.2f} MB")

            return output_path

        except Exception as e:
            print(f"❌ Download failed: {e}")
            raise
    def get_thumbnail_url(self, video_info):
        """
        Get the thumbnail URL for the video
        
        Args:
            video_info (dict): Video information
            
        Returns:
            str: Thumbnail URL
        """
        post_id = video_info.get('post_id')
        if not post_id:
            return None
        
        thumbnail_url = f"{self.thumbnail_proxy}?id={quote(post_id)}"
        print(f"🖼️  Thumbnail URL: {thumbnail_url}")
        return thumbnail_url
    
    def test_connection(self):
        """
        Test if the API is accessible
        
        Returns:
            bool: True if API is accessible
        """
        try:
            response = requests.get(self.api_base, headers=self.headers, timeout=10)
            return response.status_code == 200
        except:
            return False


def main():
    parser = argparse.ArgumentParser(
        description='Download non-watermarked videos from Sora',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sora_video_downloader.py "https://sora.chatgpt.com/p/your-video-url"
  python sora_video_downloader.py "https://sora.chatgpt.com/p/your-video-url" -o my_video.mp4
  python sora_video_downloader.py "https://sora.chatgpt.com/p/your-video-url" --info-only
        """
    )
    
    parser.add_argument(
        'url',
        help='Sora video URL (e.g., https://sora.chatgpt.com/p/s_69399f8654808191876cb4613d165b5e)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output path for the downloaded video file'
    )
    
    parser.add_argument(
        '--info-only',
        action='store_true',
        help='Only extract video information without downloading'
    )
    
    parser.add_argument(
        '--thumbnail',
        action='store_true',
        help='Also download the thumbnail'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test API connection'
    )
    
    args = parser.parse_args()
    
    # Initialize downloader
    downloader = SoraVideoDownloader()
    
    # Test connection if requested
    if args.test:
        print("🧪 Testing API connection...")
        if downloader.test_connection():
            print("✅ API connection successful!")
        else:
            print("❌ API connection failed!")
        return
    
    # Validate URL format
    if not args.url.startswith('https://sora.chatgpt.com/p/'):
        print("❌ Error: URL must be a valid Sora video URL starting with 'https://sora.chatgpt.com/p/'")
        sys.exit(1)
    
    try:
        # Extract video info
        video_info = downloader.extract_video_info(args.url)
        
        if args.info_only:
            print("\n📋 Video Information:")
            print(f"   Title: {video_info.get('title', 'N/A')}")
            print(f"   Post ID: {video_info.get('post_id', 'N/A')}")
            print(f"   Description: {video_info.get('description', 'N/A')}")
            print(f"   Created: {video_info.get('created_at', 'N/A')}")
            
            # Get download URL
            download_url = downloader.generate_download_url(video_info)
            print(f"\n🔗 Direct Download URL:")
            print(f"   {download_url}")
            
            # Get thumbnail URL
            thumbnail_url = downloader.get_thumbnail_url(video_info)
            if thumbnail_url:
                print(f"\n🖼️  Thumbnail URL:")
                print(f"   {thumbnail_url}")
        else:
            # Download the video
            output_path = downloader.download_video(args.url, args.output)
            
            # Download thumbnail if requested
            if args.thumbnail:
                thumbnail_url = downloader.get_thumbnail_url(video_info)
                if thumbnail_url:
                    print(f"\n📥 Downloading thumbnail...")
                    response = requests.get(thumbnail_url, headers=downloader.headers)
                    if response.status_code == 200:
                        thumbnail_path = output_path.replace('.mp4', '_thumbnail.jpg')
                        with open(thumbnail_path, 'wb') as f:
                            f.write(response.content)
                        print(f"✅ Thumbnail saved: {thumbnail_path}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Download interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import re  # Import re module for _clean_filename method
    main()