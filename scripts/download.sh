#!/bin/bash

# Sora Video Downloader - Curl Version
# Reverse engineered from sorasave.app
# Usage: ./sora_download_curl.sh <sora_url> [output_filename]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# API endpoints
API_BASE="https://api.soracdn.workers.dev"
API_PROXY="${API_BASE}/api-proxy/"
DOWNLOAD_PROXY="${API_BASE}/download-proxy"

# Headers
HEADERS=(
    "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    "Accept: application/json"
    "Accept-Language: en-US,en;q=0.9"
    "Origin: https://sorasave.app"
    "Referer: https://sorasave.app/"
)

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to URL encode
urlencode() {
    local string="${1}"
    local strlen=${#string}
    local encoded=""
    local pos c o

    for (( pos=0 ; pos<strlen ; pos++ )); do
        c=${string:$pos:1}
        case "$c" in
            [-_.~a-zA-Z0-9]) o="${c}" ;;
            *) printf -v o '%%%02x' "'$c" ;;
        esac
        encoded+="${o}"
    done
    echo "${encoded}"
}

# Function to clean filename
clean_filename() {
    local filename="$1"
    if [ -z "$filename" ]; then
        echo "untitled_video"
        return
    fi
    
    # Replace special characters with underscore
    filename=$(echo "$filename" | sed 's/[^a-zA-Z0-9]/_/g')
    # Limit to 100 characters
    filename=$(echo "$filename" | cut -c1-100)
    
    if [ -z "$filename" ]; then
        echo "untitled_video"
    else
        echo "$filename"
    fi
}

# Check if URL argument is provided
if [ $# -eq 0 ]; then
    print_status $RED "❌ Error: Please provide a Sora video URL"
    echo "Usage: $0 <sora_url> [output_filename]"
    echo "Example: $0 \"https://sora.chatgpt.com/p/s_69399f8654808191876cb4613d165b5e\""
    exit 1
fi

SORA_URL="$1"
OUTPUT_FILE="$2"

# Validate URL format
if [[ ! "$SORA_URL" =~ ^https://sora\.chatgpt\.com/p/ ]]; then
    print_status $RED "❌ Error: Invalid Sora URL format"
    echo "URL must start with 'https://sora.chatgpt.com/p/'"
    exit 1
fi

print_status $BLUE "🔍 Processing Sora URL: $SORA_URL"

# Step 1: Get video information from API
print_status $YELLOW "📡 Fetching video information..."

ENCODED_URL=$(urlencode "$SORA_URL")
API_URL="${API_PROXY}${ENCODED_URL}"

# Make API request
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "${HEADERS[@]}" "$API_URL")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
    print_status $RED "❌ API request failed with status: $HTTP_CODE"
    echo "Response: $BODY"
    exit 1
fi

# Extract video information
POST_ID=$(echo "$BODY" | jq -r '.post_id // empty')
TITLE=$(echo "$BODY" | jq -r '.title // "untitled_video"')
DESCRIPTION=$(echo "$BODY" | jq -r '.description // "No description"')

if [ -z "$POST_ID" ]; then
    print_status $RED "❌ Failed to extract video ID from API response"
    echo "Response: $BODY"
    exit 1
fi

print_status $GREEN "✅ Video information extracted successfully"
print_status $BLUE "   Title: $TITLE"
print_status $BLUE "   Post ID: $POST_ID"
print_status $BLUE "   Description: $DESCRIPTION"

# Step 2: Generate download URL
print_status $YELLOW "🔗 Generating download URL..."

CLEAN_TITLE=$(clean_filename "$TITLE")
ENCODED_ID=$(urlencode "$POST_ID")
ENCODED_TITLE=$(urlencode "$CLEAN_TITLE")

DOWNLOAD_URL="${DOWNLOAD_PROXY}?id=${ENCODED_ID}&filename=${ENCODED_TITLE}"

print_status $GREEN "✅ Download URL generated: $DOWNLOAD_URL"

# Step 3: Download the video
if [ -z "$OUTPUT_FILE" ]; then
    OUTPUT_FILE="${CLEAN_TITLE}.mp4"
fi

print_status $YELLOW "📥 Downloading video to: $OUTPUT_FILE"

# Download with progress
if command -v curl >/dev/null 2>&1; then
    # Use curl with progress bar
    curl -L -# -o "$OUTPUT_FILE" "${HEADERS[@]}" "$DOWNLOAD_URL"
elif command -v wget >/dev/null 2>&1; then
    # Use wget as fallback
    wget --show-progress -O "$OUTPUT_FILE" "$DOWNLOAD_URL"
else
    print_status $RED "❌ Error: Neither curl nor wget is available"
    exit 1
fi

# Check if download was successful
if [ -f "$OUTPUT_FILE" ] && [ -s "$OUTPUT_FILE" ]; then
    FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
    print_status $GREEN "✅ Video downloaded successfully!"
    print_status $BLUE "   File: $OUTPUT_FILE"
    print_status $BLUE "   Size: $FILE_SIZE"
else
    print_status $RED "❌ Download failed or file is empty"
    exit 1
fi

# Optional: Download thumbnail
if [ "$DOWNLOAD_THUMBNAIL" = "true" ]; then
    print_status $YELLOW "🖼️  Downloading thumbnail..."
    
    THUMBNAIL_URL="${THUMBNAIL_PROXY}?id=${ENCODED_ID}"
    THUMBNAIL_FILE="${OUTPUT_FILE%.mp4}_thumbnail.jpg"
    
    curl -s -o "$THUMBNAIL_FILE" "${HEADERS[@]}" "$THUMBNAIL_URL"
    
    if [ -f "$THUMBNAIL_FILE" ] && [ -s "$THUMBNAIL_FILE" ]; then
        print_status $GREEN "✅ Thumbnail saved: $THUMBNAIL_FILE"
    else
        print_status $YELLOW "⚠️  Thumbnail download failed"
    fi
fi

print_status $GREEN "🎉 All done!"