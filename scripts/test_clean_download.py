import sys
from src.sora_downloader import CleanSoraDownloader

def test_download():
    # Use the test URL from analysis
    test_url = "https://sora.chatgpt.com/p/s_693b10946d588191b354320369fbf4e3"
    
    print(f"Testing downloader with {test_url}")
    
    downloader = CleanSoraDownloader()
    
    try:
        output_path = downloader.download_video(test_url, output_dir=".")
        print(f"✅ Test successfully passed. File downloaded: {output_path}")
        return 0
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(test_download())
