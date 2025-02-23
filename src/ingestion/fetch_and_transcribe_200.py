#!/usr/bin/env python3
"""
fetch_and_transcribe_300.py

Fetches up to 300 recent TastyLiveShow videos (via pagination),
then attempts to download official transcripts using youtube_transcript_api.

- Skips videos already processed
- Skips "LIVE" videos
- Saves video metadata for tracking

WARNING: This script contains a hard-coded YouTube API key. 
         If your repo is public, your key could be compromised.

Requirements:
  - requests
  - youtube_transcript_api
"""

import os
import json
import requests
from youtube_transcript_api import (
    YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, CouldNotRetrieveTranscript
)

# ──────────────────────────────────────────────────────────────────────────
#  CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")  # Use env variable for security

CHANNEL_ID = "UCLJiSMXJ9K-1AOTqIqdXJgQ"

# File & Directory Paths
TRANSCRIPT_DIR = "data/transcripts"
PROCESSED_VIDEOS_PATH = "data/processed_videos.json"

# ──────────────────────────────────────────────────────────────────────────
#  HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────

def load_processed_videos():
    """Load already processed videos from JSON file."""
    if not os.path.exists(PROCESSED_VIDEOS_PATH):
        return {}
    with open(PROCESSED_VIDEOS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_processed_video(video_id, title):
    """Save processed video ID to JSON file to avoid reprocessing."""
    processed_videos = load_processed_videos()
    processed_videos[video_id] = title
    with open(PROCESSED_VIDEOS_PATH, "w", encoding="utf-8") as f:
        json.dump(processed_videos, f, indent=2)

def fetch_videos_paginated(api_key, channel_id, total_to_fetch=300):
    """
    Fetch up to `total_to_fetch` videos from a given YouTube channel.
    Uses pagination with `nextPageToken` to keep calling until we get enough items.

    Returns a list of video metadata dicts: [{
        "video_id": str,
        "title": str,
        "description": str,
        "publishedAt": str,
    }, ...]
    """
    base_url = "https://www.googleapis.com/youtube/v3/search"
    page_token = None
    collected_videos = []
    batch_size = 50  # Max results per YouTube API call
    processed_videos = load_processed_videos()

    while len(collected_videos) < total_to_fetch:
        params = {
            "key": api_key,
            "channelId": channel_id,
            "part": "snippet",
            "order": "date",
            "type": "video",
            "maxResults": batch_size,
        }
        if page_token:
            params["pageToken"] = page_token

        resp = requests.get(base_url, params=params)
        resp.raise_for_status()
        data = resp.json()

        items = data.get("items", [])
        for item in items:
            if len(collected_videos) >= total_to_fetch:
                break

            video_id = item["id"].get("videoId")
            snippet = item["snippet"]
            title = snippet.get("title", "")

            # Skip if the video contains "LIVE"
            if "live" in title.lower():
                print(f"[INFO] Skipping LIVE video: {title}")
                continue

            # Skip already processed videos
            if video_id in processed_videos:
                print(f"[INFO] Skipping already processed video: {title}")
                continue

            collected_videos.append({
                "video_id": video_id,
                "title": title,
                "description": snippet.get("description", ""),
                "publishedAt": snippet.get("publishedAt", ""),
            })

        page_token = data.get("nextPageToken")

        # If no more pages, stop
        if not page_token:
            break

    print(f"[INFO] Fetched {len(collected_videos)} new videos.")
    return collected_videos

def download_official_transcript(video_id):
    """
    Attempt to download the official YouTube transcript for a given video_id.
    Returns the text or None if no transcript found or auto-caption is disabled.
    """
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        return "\n".join(f"{entry['start']:.2f} - {entry['text']}" for entry in transcript_list)
    except (NoTranscriptFound, TranscriptsDisabled, CouldNotRetrieveTranscript) as e:
        print(f"[WARN] Transcript not available for video ID {video_id}: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error for video ID {video_id}: {e}")
        return None

def safe_filename(title):
    """
    Convert a video title to a safe filename by removing or replacing
    invalid characters, and limiting length to ~50 chars.
    """
    safe = "".join([c if c.isalnum() or c in " -_()" else "_" for c in title])
    return safe[:50].strip("_")

# ──────────────────────────────────────────────────────────────────────────
#  MAIN SCRIPT
# ──────────────────────────────────────────────────────────────────────────

def main():
    if not YOUTUBE_API_KEY:
        raise ValueError("No YOUTUBE_API_KEY found. Set it as an environment variable.")

    os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

    # Fetch new videos (only those not processed yet)
    video_list = fetch_videos_paginated(YOUTUBE_API_KEY, CHANNEL_ID, total_to_fetch=300)

    for idx, vid in enumerate(video_list, start=1):
        video_id = vid["video_id"]
        title = vid["title"]

        print(f"\n[{idx}/{len(video_list)}] Processing Video ID: {video_id}, Title: {title}")

        if not video_id:
            print("[WARN] No video_id found. Skipping.")
            continue

        transcript_text = download_official_transcript(video_id)
        if transcript_text:
            out_name = f"{video_id}_{safe_filename(title)}.txt"
            out_path = os.path.join(TRANSCRIPT_DIR, out_name)

            with open(out_path, "w", encoding="utf-8") as f:
                f.write(transcript_text)
            print(f"[INFO] Saved transcript to {out_path}")

            # Mark video as processed
            save_processed_video(video_id, title)
        else:
            print(f"[INFO] Skipping transcript save for {video_id}")

    print(f"\n[INFO] Finished processing {len(video_list)} new videos.")


if __name__ == "__main__":
    main()