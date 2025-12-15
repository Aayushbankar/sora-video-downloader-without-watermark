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

    try:
        # Test API accessibility
        response = requests.get(api_base, headers=headers, timeout=10)
        print(f"✅ API Base Status: {response.status_code}")

        # Test with a sample (invalid) URL to see API response format
        sample_url = "https://sora.chatgpt.com/p/test123"
        encoded_url = quote(sample_url, safe='')
        api_url = f"{api_base}/api-proxy/{encoded_url}"

        print(f"📡 Testing API endpoint: {api_url}")
        response = requests.get(api_url, headers=headers, timeout=10)

        print(f"Response Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ API Response Format: {json.dumps(data, indent=2)[:200]}...")
            except:
                print(f"📄 Response: {response.text[:200]}...")
        elif response.status_code == 404:
            print("✅ API is working (404 for invalid URL as expected)")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")

        return True

    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    test_api()
