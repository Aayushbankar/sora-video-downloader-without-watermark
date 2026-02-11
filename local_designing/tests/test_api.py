#!/usr/bin/env python3
"""
Test script for Sora Video Downloader API
"""

import requests
import json
from urllib.parse import quote

def test_api():
    """Test the API endpoints"""
    api_base = "https://api.soracdn.workers.dev"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Origin': 'https://sorasave.app',
        'Referer': 'https://sorasave.app/'
    }

    print("🧪 Testing SoraSave API...")

    # Test API accessibility
    try:
        response = requests.get(api_base, headers=headers, timeout=10)
        assert response.status_code == 200, f"API Base Status: {response.status_code}"
        print(f"✅ API Base Status: {response.status_code}")
    except Exception as e:
        print(f"❌ API Base accessible failed: {e}")
        assert False, f"API Base accessible failed: {e}"

    # Test with a VALID URL to see API response format and check for structure changes
    # Using a known valid URL from test_urls.txt
    valid_url = "https://sora.chatgpt.com/p/s_693b10946d588191b354320369fbf4e3"
    encoded_url = quote(valid_url, safe='')
    api_url = f"{api_base}/api-proxy/{encoded_url}"

    print(f"📡 Testing API endpoint: {api_url}")
    
    try:
        response = requests.get(api_url, headers=headers, timeout=20)
        assert response.status_code == 200, f"API Request failed with status {response.status_code}"
        
        data = response.json()
        print(f"✅ API Response received")
        
        # Verify New API Structure
        # 1. Check for 'post_info'
        if 'post_info' in data:
            print("✅ Found 'post_info' object (New API Structure)")
            post_info = data['post_info']
            assert 'title' in post_info, "Title missing from post_info"
            print(f"   Title: {post_info['title']}")
        else:
            print("⚠️ 'post_info' not found, checking top-level...")
            # Fallback check (Old API or simplified)
            assert 'title' in data, "Title missing from response (checked both top-level and post_info)"
        
        # 2. Check for 'links' (New API Structure)
        if 'links' in data:
            print("✅ Found 'links' object (New API Structure)")
            links = data['links']
            assert 'mp4' in links or 'video' in links, "Video link missing from links object"
        
        # 3. Check for 'post_id'
        assert 'post_id' in data, "post_id missing from response"
        print(f"✅ Valid post_id: {data['post_id']}")

    except Exception as e:
        print(f"❌ API test failed: {e}")
        assert False, f"API test failed: {e}"

if __name__ == "__main__":
    test_api()
