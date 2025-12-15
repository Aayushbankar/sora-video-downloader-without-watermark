import sys
import os
import time
import statistics
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.sora_downloader import SoraVideoDownloader

def clean_url(line):
    # Remove whitespace, trailing commas, trailing dots
    return line.strip().rstrip(',').rstrip('.')

def main():
    urls_file = 'test_urls.txt'
    output_dir = 'download_vids'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(urls_file, 'r') as f:
        urls = [clean_url(line) for line in f if line.strip()]
        
    print(f"Found {len(urls)} videos to download.")
    
    downloader = SoraVideoDownloader()
    times = []
    
    print("-" * 60)
    print(f"{'Video ID':<35} | {'Status':<10} | {'Time (s)':<10}")
    print("-" * 60)
    
    for i, url in enumerate(urls, 1):
        if not url.startswith('http'):
            continue
            
        start_time = time.time()
        try:
            # First extract info to get title for filename
            print(f"[{i}/{len(urls)}] Processing...", end='\r')
            video_info = downloader.extract_video_info(url)
            
            # Construct filename in download_vids folder
            title = video_info.get('title', f"video_{i}")
            post_id = video_info.get('post_id')
            if not title: 
                 title = f"sora_{post_id}"
                 
            clean_title = downloader._clean_filename(title)
            output_path = os.path.join(output_dir, f"{clean_title}.mp4")
            
            # Download
            downloader.download_video(url, output_path)
            
            duration = time.time() - start_time
            times.append(duration)
            
            # Print brief result row
            vid_id_short = post_id if post_id else "unknown"
            print(f"{vid_id_short:<35} | {'DONE':<10} | {duration:.2f}s     ")
            
        except Exception as e:
            print(f"\nFailed {url}: {e}")
    
    if times:
        avg_time = statistics.mean(times)
        total_time = sum(times)
        
        print("\n" + "=" * 60)
        print("DOWNLOAD PERFORMANCE REPORT")
        print("=" * 60)
        print(f"Total Videos: {len(times)}")
        print(f"Total Time:   {total_time:.2f} seconds")
        print(f"Average Time: {avg_time:.2f} seconds per video")
        print(f"Min Time:     {min(times):.2f} seconds")
        print(f"Max Time:     {max(times):.2f} seconds")
        print("=" * 60)
        
        # Save report to file
        with open('download_report.txt', 'w') as f:
            f.write(f"DOWNLOAD PERFORMANCE REPORT\n")
            f.write(f"Total Videos: {len(times)}\n")
            f.write(f"Total Time:   {total_time:.2f} seconds\n")
            f.write(f"Average Time: {avg_time:.2f} seconds per video\n")

if __name__ == "__main__":
    main()
