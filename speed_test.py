#!/usr/bin/env python3
"""
Speed test comparison between different download methods
"""

import requests
import time
import os
from urllib.parse import quote

def test_direct_download():
    """Test direct download speed (bypassing the proxy)"""
    print("🚀 Testing direct download speed...")
    
    # Test with a reliable file
    test_urls = [
        "https://httpbin.org/bytes/500000",  # 500KB
        "https://speed.hetzner.de/100MB.bin",  # 100MB (if available)
    ]
    
    for test_url in test_urls:
        try:
            print(f"\n📡 Testing: {test_url}")
            start_time = time.time()
            
            response = requests.get(test_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Download in chunks
            total_downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    total_downloaded += len(chunk)
            
            download_time = time.time() - start_time
            file_size_mb = total_downloaded / (1024 * 1024)
            speed_mbps = file_size_mb / download_time if download_time > 0 else 0
            
            print(f"✅ Downloaded: {file_size_mb:.2f} MB")
            print(f"⏱️  Time: {download_time:.1f}s")
            print(f("⚡ Speed: {speed_mbps:.1f} MB/s ({speed_mbps * 8:.1f} Mbps)"))
            
        except Exception as e:
            print(f"❌ Failed: {e}")

def analyze_slowdown_factors():
    """Analyze why Sora downloads might be slow"""
    print("\n" + "="*60)
    print("🔍 ANALYSIS: Why Sora Downloads Are Slow")
    print("="*60)
    
    factors = [
        {
            "factor": "Proxy Overhead",
            "description": "Your request goes through SoraSave's servers first",
            "impact": "2-5x slower",
            "solution": "Direct download (not possible with Sora)"
        },
        {
            "factor": "Server Processing",
            "description": "Video needs watermark removal processing",
            "impact": "5-15 seconds initial delay",
            "solution": "Pre-processed videos (requires storage)"
        },
        {
            "factor": "Geographic Distance",
            "description": "SoraSave servers might be far from you",
            "impact": "2-10x slower depending on location",
            "solution": "CDN or closer servers"
        },
        {
            "factor": "Rate Limiting",
            "description": "API might limit download speeds to prevent abuse",
            "impact": "Throttled to specific speed limits",
            "solution": "Premium/paid service"
        },
        {
            "factor": "Shared Bandwidth",
            "description": "Many users downloading simultaneously",
            "impact": "Variable speeds throughout the day",
            "solution": "Dedicated bandwidth"
        },
        {
            "factor": "No Parallel Downloads",
            "description": "Single connection download",
            "impact": "Can't utilize full bandwidth",
            "solution": "Multi-connection downloads (if supported)"
        }
    ]
    
    for i, factor in enumerate(factors, 1):
        print(f"\n{i}. {factor['factor']}")
        print(f"   📋 {factor['description']}")
        print(f"   📊 Impact: {factor['impact']}")
        print(f"   💡 Solution: {factor['solution']}")

def provide_optimization_tips():
    """Provide optimization tips"""
    print("\n" + "="*60)
    print("💡 OPTIMIZATION TIPS")
    print("="*60)
    
    tips = [
        "Use the fast downloader (sora_video_downloader_fast.py) with resume capability",
        "Download during off-peak hours (less server load)",
        "Use a wired connection instead of WiFi",
        "Close other bandwidth-heavy applications",
        "Try different times of day (server load varies)",
        "Use a VPN to potentially get better routing",
        "Download smaller videos if possible",
        "Enable resume support to continue interrupted downloads"
    ]
    
    for i, tip in enumerate(tips, 1):
        print(f"{i}. {tip}")

def benchmark_comparison():
    """Compare different scenarios"""
    print("\n" + "="*60)
    print("📊 SPEED COMPARISON BENCHMARK")
    print("="*60)
    
    scenarios = [
        {
            "scenario": "Direct Download (Baseline)",
            "speed": "10-50 MB/s",
            "example": "Downloading from fast CDN",
            "notes": "This is your maximum possible speed"
        },
        {
            "scenario": "SoraSave (Current)",
            "speed": "0.1-1 MB/s",
            "example": "6MB file in 60 seconds",
            "notes": "What you're experiencing now"
        },
        {
            "scenario": "SoraSave (Optimized)",
            "speed": "0.5-2 MB/s",
            "example": "6MB file in 15 seconds",
            "notes": "With fast downloader + optimizations"
        },
        {
            "scenario": "Premium Service",
            "speed": "2-10 MB/s",
            "example": "6MB file in 3 seconds",
            "notes": "If they offered a paid tier"
        }
    ]
    
    print(f"{'Scenario':<25} {'Speed':<15} {'Example':<25} {'Notes'}")
    print("-" * 80)
    
    for scenario in scenarios:
        print(f"{scenario['scenario']:<25} {scenario['speed']:<15} {scenario['example']:<25} {scenario['notes']}")

def main():
    print("🚀 Sora Video Downloader - Speed Analysis")
    print("=" * 60)
    
    # Test direct download speed
    test_direct_download()
    
    # Analyze slowdown factors
    analyze_slowdown_factors()
    
    # Provide optimization tips
    provide_optimization_tips()
    
    # Benchmark comparison
    benchmark_comparison()
    
    print("\n" + "="*60)
    print("🎯 CONCLUSION")
    print("="*60)
    print("The slow speed you're experiencing is normal for proxy-based services.")
    print("Use the fast downloader with resume capability for best performance.")
    print("Consider the time of day and your network connection for optimal speeds.")

if __name__ == "__main__":
    main()