#!/usr/bin/env python3
"""
Script to verify SoraSave API changes.
It attempts to fetch a video and checks for:
1. Old structure (Top-level title) -> Expected to be MISSING
2. New structure (post_info.title) -> Expected to be PRESENT
"""

import requests
import json
from urllib.parse import quote

def verify_api():
    # Valid URL from test_urls.txt
    target_url = "https://sora.chatgpt.com/p/s_693b10946d588191b354320369fbf4e3"
    api_base = "https://api.soracdn.workers.dev"
    
    print(f"🔍 Verifying API for URL: {target_url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Origin': 'https://sorasave.app',
        'Referer': 'https://sorasave.app/'
    }
    
    api_url = f"{api_base}/api-proxy/{quote(target_url, safe='')}"
    print(f"📡 Requesting: {api_url}")
    
    try:
        response = requests.get(api_url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"❌ API Request failed: {response.status_code}")
            return False
            
        data = response.json()
        print("\n📊 Response Analysis:")
        
        # Check 1: Old Structure (Top-level title)
        top_level_title = data.get('title')
        if top_level_title:
            print(f"❓ [Unexpected] Found top-level title: '{top_level_title}'")
            print("   (The API might have backward compatibility or revert?)")
        else:
            print("✅ [Expected] Top-level 'title' is MISSING (Old structure gone)")
            
        # Check 2: New Structure (post_info.title)
        post_info = data.get('post_info', {})
        nested_title = post_info.get('title')
        
        if nested_title:
            print(f"✅ [Expected] Found nested title in 'post_info': '{nested_title}'")
        else:
            print("❌ [Critical] Could not find title in 'post_info' either!")
            
        # Check 3: Links
        links = data.get('links', {})
        if links.get('mp4'):
             print(f"✅ [Expected] Found direct 'mp4' link in 'links' object")
        else:
             print("❌ [Critical] 'links.mp4' missing!")

        print("\n📝 Raw Structure Snippet:")
        print(json.dumps(data, indent=2)[:300] + "\n...")
        
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    verify_api()
