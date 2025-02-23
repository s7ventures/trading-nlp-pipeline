#!/usr/bin/env python3
"""
fetch_and_transcribe_300.py

Fetches up to 300 recent TastyLiveShow videos (via pagination),
then attempts to download official transcripts using youtube_transcript_api.

WARNING: This script contains a hard-coded YouTube API key. 
         If your repo is public, your key could be compromised.

Requirements:
  - requests
  - youtube_transcript_api
"""

import os
import requests
from youtube_transcript_api import (
    YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, CouldNotRetrieveTranscript
)

# ──────────────────────────────────────────────────────────────────────────
#  HARD-CODED YOUTUBE API KEY (WARNING: RISKY IF REPO IS PUBLIC)
#  Use environment variables if possible:
#    export YOUTUBE_API_KEY="YOUR_KEY"
# ──────────────────────────────────────────────────────────────────────────
YOUTUBE_API_KEY = "AIzaSyD17mLlU_JYW-FxRIRdGgFrVyb0TuABSHY"

# TastyLiveShow channel ID
CHANNEL_ID = "UCLJiSMXJ9K-1AOTqIqdXJgQ"

# Where transcripts will be saved
TRANSCRIPT_DIR = "data/transcripts"

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
    fetched_count = 0
    batch_size = 50  # Max results per YouTube API call

    while fetched_count < total_to_fetch:
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
            # If we've already reached the limit, break
            if len(collected_videos) >= total_to_fetch:
                break

            video_id = item["id"].get("videoId")
            snippet = item["snippet"]
            collected_videos.append({
                "video_id": video_id,
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "publishedAt": snippet.get("publishedAt", ""),
            })

        fetched_count = len(collected_videos)
        page_token = data.get("nextPageToken")

        # If we run out of pages, break
        if not page_token:
            break

    print(f"[INFO] Fetched {len(collected_videos)} videos total.")
    return collected_videos


def download_official_transcript(video_id):
    """
    Attempt to download the official YouTube transcript for a given video_id.
    Returns the text or None if no transcript found or auto-caption is disabled.
    """
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        lines = []
        for entry in transcript_list:
            start_time = entry.get('start')
            text = entry.get('text', "")
            lines.append(f"{start_time:.2f} - {text}")
        return "\n".join(lines)
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


def main():
    # Check if key is present
    if not YOUTUBE_API_KEY:
        raise ValueError("No YOUTUBE_API_KEY found.")

    # Ensure data/transcripts directory
    os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

    # Fetch up to 300 videos from TastyLiveShow
    video_list = fetch_videos_paginated(YOUTUBE_API_KEY, CHANNEL_ID, total_to_fetch=300)

    for idx, vid in enumerate(video_list, start=1):
        video_id = vid["video_id"]
        title = vid["title"]
        published_at = vid["publishedAt"]
        print(f"\n[{idx}/{len(video_list)}] Video ID: {video_id}, Title: {title}")

        if not video_id:
            print("[WARN] No video_id found. Skipping.")
            continue

        # Skip videos containing the word "LIVE" (case-insensitive)
        if "live" in title.lower():
            print("[INFO] Skipping because title contains 'LIVE'")
            continue

        # Attempt to retrieve official transcript
        transcript_text = download_official_transcript(video_id)
        if transcript_text:
            # Save transcript locally
            out_name = f"{video_id}_{safe_filename(title)}.txt"
            out_path = os.path.join(TRANSCRIPT_DIR, out_name)

            with open(out_path, "w", encoding="utf-8") as f:
                f.write(transcript_text)
            print(f"[INFO] Saved transcript to {out_path}")
        else:
            print(f"[INFO] Skipping transcript save for {video_id}")

    print(f"\n[INFO] Finished processing {len(video_list)} videos.")


if __name__ == "__main__":
    main()