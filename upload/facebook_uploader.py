"""
Facebook Reels Direct Uploader via Meta Graph API v21.0
3-step Resumable Video Reels Publishing with Automatic Page Token Resolution
and Automatic Pinned Engagement Comment
"""
import os
import sys
import json
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

LOCAL_TOKENS_PATHS = [
    Path(r"C:\Users\kreg9\logic_pages_tokens.json"),
    Path(r"C:\Users\kreg9\facebook_pages_tokens.json")
]

def load_page_tokens() -> Dict[str, Any]:
    """Loads page tokens from environment secret or local tokens store."""
    tokens = {}
    env_json = os.getenv("FACEBOOK_PAGES_JSON") or os.getenv("PAGE_TOKENS_JSON")
    if env_json:
        try:
            tokens = json.loads(env_json)
        except Exception as e:
            print(f"[uploader] Notice parsing FACEBOOK_PAGES_JSON: {e}")

    for p in LOCAL_TOKENS_PATHS:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        tokens.update(data)
            except Exception as e:
                print(f"[uploader] Notice reading {p.name}: {e}")

    return tokens

def get_token_for_page(page_id: str, tokens: Dict[str, Any]) -> Optional[str]:
    """Resolves token for specific page ID."""
    entry = tokens.get(str(page_id)) or tokens.get(page_id)
    if isinstance(entry, dict):
        return entry.get("access_token")
    elif isinstance(entry, str):
        return entry
    
    return (
        os.getenv("FACEBOOK_ACCESS_TOKEN") or
        os.getenv("META_ACCESS_TOKEN") or
        os.getenv("META_LONG_LIVED_ACCESS_TOKEN")
    )

def upload_reel_to_facebook(
    video_path: str,
    title: str,
    description: str,
    page_id: str,
    access_token: Optional[str] = None,
    pinned_comment: Optional[str] = None
) -> Dict[str, Any]:
    """
    Publishes 1080x1920 video to Facebook Reels and optionally posts a pinned engagement comment.
    """
    print("\n" + "=" * 60)
    print("[FACEBOOK] REEL PUBLISHING PIPELINE")
    print(f"Target Page ID: {page_id}")
    print(f"Video File: {video_path}")
    print("=" * 60)

    if not access_token:
        tokens = load_page_tokens()
        access_token = get_token_for_page(page_id, tokens)

    if not access_token:
        err = f"No access token found for Page ID {page_id}"
        print(f"[facebook] [ERROR] {err}")
        return {"status": "failed", "error": err}

    vid_path = Path(video_path)
    if not vid_path.exists():
        err = f"Video file not found: {video_path}"
        print(f"[facebook] [ERROR] {err}")
        return {"status": "failed", "error": err}

    file_size = vid_path.stat().st_size
    api_version = "v21.0"

    # Step 0: Verify / resolve page access token
    try:
        pt_url = f"https://graph.facebook.com/{api_version}/{page_id}?fields=access_token,name"
        res = requests.get(pt_url, params={"access_token": access_token}, timeout=15)
        if res.status_code == 200:
            data = res.json()
            resolved = data.get("access_token")
            pname = data.get("name", "Page")
            if resolved:
                print(f"[facebook] Verified Page Token for '{pname}'")
                access_token = resolved
    except Exception as e:
        print(f"[facebook] Notice verifying page token: {e}")

    base_url = f"https://graph.facebook.com/{api_version}/{page_id}/video_reels"

    try:
        # Step 1: Initialize Upload Session
        print("[facebook] Step 1/3: Starting Reel upload session...")
        start_payload = {
            "access_token": access_token,
            "upload_phase": "start",
            "file_size": file_size
        }
        res_start = requests.post(base_url, data=start_payload, timeout=30)
        if res_start.status_code != 200:
            err = f"Start phase error ({res_start.status_code}): {res_start.text}"
            print(f"[facebook] [ERROR] {err}")
            return {"status": "failed", "error": err}

        start_json = res_start.json()
        video_id = start_json.get("video_id")
        upload_url = start_json.get("upload_url")
        print(f"[facebook] Session initialized. Video ID: {video_id}")

        # Step 2: Binary Video Chunk Transfer
        print("[facebook] Step 2/3: Transferring video binary payload...")
        headers = {
            "Authorization": f"OAuth {access_token}",
            "offset": "0",
            "file_size": str(file_size)
        }
        with open(vid_path, "rb") as f:
            video_bytes = f.read()

        res_transfer = requests.post(
            upload_url,
            headers=headers,
            data=video_bytes,
            timeout=120
        )
        if res_transfer.status_code not in (200, 201):
            err = f"Transfer failed ({res_transfer.status_code}): {res_transfer.text}"
            print(f"[facebook] [ERROR] {err}")
            return {"status": "failed", "error": err}

        print("[facebook] Video binary uploaded successfully.")

        # Step 3: Finish & Publish
        print("[facebook] Step 3/3: Finalizing publication...")
        finish_payload = {
            "access_token": access_token,
            "upload_phase": "finish",
            "video_id": video_id,
            "video_state": "PUBLISHED",
            "description": description,
            "title": title
        }
        res_finish = requests.post(base_url, data=finish_payload, timeout=30)
        if res_finish.status_code != 200:
            err = f"Finish phase failed ({res_finish.status_code}): {res_finish.text}"
            print(f"[facebook] [ERROR] {err}")
            return {"status": "failed", "error": err}

        finish_json = res_finish.json()
        print(f"[facebook] [SUCCESS] Reel Published! Success: {finish_json.get('success', True)}")

        # Step 4: Optional Pinned Engagement Comment
        if pinned_comment:
            print("[facebook] Waiting 15s for reel indexing before posting pinned comment...")
            time.sleep(15)
            try:
                comment_url = f"https://graph.facebook.com/{api_version}/{video_id}/comments"
                c_res = requests.post(comment_url, data={
                    "access_token": access_token,
                    "message": pinned_comment
                }, timeout=15)
                if c_res.status_code == 200:
                    print(f"[facebook] [PIN] Pinned engagement comment posted successfully!")
            except Exception as e:
                print(f"[facebook] Notice posting pinned comment: {e}")

        return {
            "status": "success",
            "video_id": video_id,
            "page_id": page_id,
            "published_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    except Exception as e:
        err = f"Unexpected upload exception: {e}"
        print(f"[facebook] [ERROR] {err}")
        return {"status": "failed", "error": err}
