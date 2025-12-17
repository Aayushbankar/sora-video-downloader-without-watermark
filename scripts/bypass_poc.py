
import sys
import json
import re
from curl_cffi import requests

def main():
    url = "https://sora.chatgpt.com/p/s_693b10946d588191b354320369fbf4e3"
    print(f"Fetching {url}...")
    
    try:
        session = requests.Session()
        response = session.get(
            url,
            impersonate="chrome120",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://sora.chatgpt.com/"
            },
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Look for __NEXT_DATA__
            match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', response.text)
            if match:
                data = json.loads(match.group(1))
                print("✅ Found __NEXT_DATA__!")
                
                # Save to file for inspection
                with open("next_data.json", "w") as f:
                    json.dump(data, f, indent=2)
                print("Saved next_data.json")
                
                # Try to find video info
                page_props = data.get('props', {}).get('pageProps', {})
                print("Keys in pageProps:", page_props.keys())
                
            else:
                print("❌ __NEXT_DATA__ not found in HTML")
                with open("debug.html", "w") as f:
                    f.write(response.text)
                print("Saved debug.html")
        else:
            print("❌ Request failed")
            print(response.text[:500])
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
