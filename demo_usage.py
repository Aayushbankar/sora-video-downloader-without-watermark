#!/usr/bin/env python3
"""
Demo script showing how to use the Sora Video Downloader
"""

import subprocess
import sys
import os

def run_demo():
    """Demonstrate the usage of the Sora Video Downloader"""
    
    print("🎬 Sora Video Downloader - Demo Script")
    print("=" * 50)
    
    # Check if files exist
    files_to_check = [
        'sora_video_downloader.py',
        'sora_download_curl.sh', 
        'README.md',
        'test_api.py'
    ]
    
    print("📁 Checking created files:")
    all_exist = True
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            all_exist = False
    
    if not all_exist:
        print("\n⚠️  Some files are missing. Please ensure all files are created.")
        return
    
    print("\n🧪 Running API test...")
    try:
        result = subprocess.run([sys.executable, 'test_api.py'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ API test completed successfully")
        else:
            print("❌ API test failed")
            print(result.stdout)
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error running API test: {e}")
    
    print("\n📖 Available commands:")
    print("1. Test API connection:")
    print("   python test_api.py")
    print()
    print("2. Download video (Python):")
    print("   python sora_video_downloader.py \"https://sora.chatgpt.com/p/your-url\" -o video.mp4")
    print()
    print("3. Download video (Bash):")
    print("   ./sora_download_curl.sh \"https://sora.chatgpt.com/p/your-url\" video.mp4")
    print()
    print("4. Get video info only:")
    print("   python sora_video_downloader.py \"https://sora.chatgpt.com/p/your-url\" --info-only")
    print()
    print("5. View documentation:")
    print("   cat README.md")
    
    print("\n🔍 Example Sora URL format:")
    print("   https://sora.chatgpt.com/p/s_69399f8654808191876cb4613d165b5e")
    print("   https://sora.chatgpt.com/p/s_abc123def456ghi789")
    
    print("\n⚠️  Important Notes:")
    print("• Make sure the Sora URL is publicly accessible")
    print("• The API might have rate limits - add delays between downloads")
    print("• Use responsibly and respect content creators' rights")
    print("• This is for educational and personal use only")
    
    print("\n🎉 Setup complete! You can now download Sora videos without watermarks.")

if __name__ == "__main__":
    run_demo()