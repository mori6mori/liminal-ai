# -*- coding: utf-8 -*-
"""generate_video.py (v2)

End‑to‑end *local‑first* avatar pipeline with **automatic gradient fallback**.

Steps
─────
1. 🎨  Portrait creation with **OpenAI DALL·E 3** (9 : 16, Wes‑Anderson).
2. 📤  Upload portrait + ElevenLabs audio (*MP3*) to **transfer.sh** for temp CDN URLs.
3. 📹  **PikaLabs /generate** animates the portrait → talking‑head clip (duration = audio_length).
4. 🎙   `ffmpeg` converts MP3 → WAV; WAV is uploaded.
5. 👄  **PikaLabs /web/lipSync** fuses lips with the WAV.
6. 🌀  **Fallback** – if steps 3‑5 fail, generate a hypnotic gradient loop matching duration.
7. ⬇  Download final MP4 to the requested path.

No private server needed; all uploads done via transfer.sh (14‑day retention).

──────────────────────────────────────────────────────────────────────────────
Usage
─────
    python generate_video.py intro.mp3 \
        --prompt "head‑and‑shoulders news anchor, pastel Wes‑Anderson palette, symmetrical" \
        --out intro_final.mp4

Requirements
────────────
    pip install openai requests tqdm python-dotenv
    # ensure ffmpeg + ffprobe binaries in PATH

Environment variables
─────────────────────
    OPENAI_API_KEY   – for image generation
    PIKA_API_KEY     – session token / bearer for Pika Labs
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict

import openai
import requests
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Constants & helpers
# ---------------------------------------------------------------------------

SESSION = requests.Session()
TRANSFER_URL = "https://transfer.sh"  # simple, no‑auth file CDN
PIKA_BASE = "https://api.pikapikapika.io"
HEADERS_PIKA = {"Authorization": f"Bearer {os.getenv('PIKA_API_KEY', '')}"}

# ⚙️  sanity‑check API keys early
if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("OPENAI_API_KEY not set")
if not os.getenv("PIKA_API_KEY"):
    raise EnvironmentError("PIKA_API_KEY not set")

# ---------------------------------------------------------------------------
# 0.  Utility: file upload & job polling
# ---------------------------------------------------------------------------

def upload_file(path: Path) -> str:
    """Upload *path* to transfer.sh and return a shareable URL."""
    with path.open("rb") as f:
        r = SESSION.put(f"{TRANSFER_URL}/{path.name}", data=f, timeout=120)
    r.raise_for_status()
    return r.text.strip()


def poll_job(job_id: str, what: str, timeout: int = 300) -> Dict:
    start = time.time()
    with tqdm(total=timeout, desc=what, unit="s", leave=False) as bar:
        while True:
            job = SESSION.get(f"{PIKA_BASE}/web/jobs/{job_id}", headers=HEADERS_PIKA).json()
            status = job.get("status")
            if status == "success":
                return job
            if status == "failed":
                raise RuntimeError(f"{what} failed → {job}")
            elapsed = time.time() - start
            if elapsed > timeout:
                raise TimeoutError(f"{what} timed‑out after {timeout}s")
            bar.update(3)
            time.sleep(3)

# ---------------------------------------------------------------------------
# 1.  Create portrait image with DALL·E 3
# ---------------------------------------------------------------------------

def create_portrait(prompt: str, out_path: Path) -> Path:
    client = openai.OpenAI()
    resp = client.images.generate(
        prompt=prompt,
        model="dall-e-3",
        n=1,
        size="1024x1792"  # ~9:16
    )
    img_url = resp.data[0].url
    img_bytes = SESSION.get(img_url, timeout=60).content
    out_path.write_bytes(img_bytes)
    return out_path

# ---------------------------------------------------------------------------
# 2.  Audio tools (require ffmpeg & ffprobe)
# ---------------------------------------------------------------------------

def mp3_to_wav(mp3: Path) -> tuple[Path, float]:
    wav = mp3.with_suffix(".wav")
    subprocess.run(["ffmpeg", "-y", "-i", str(mp3), "-ar", "44100", "-ac", "1", str(wav)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    dur = float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
        "default=noprint_wrappers=1:nokey=1", str(wav)
    ]).strip())
    return wav, dur

# ---------------------------------------------------------------------------
# 3.  Pika generate helpers
# ---------------------------------------------------------------------------

def generate_avatar(img_url: str, duration: int, motion_prompt: str) -> str:
    payload = {
        "promptText": f"{motion_prompt}",
        "image": img_url,
        "options": {
            "aspectRatio": "9:16",
            "frameRate": 24,
            "parameters": {"motion": 1, "guidanceScale": 15},
            "duration": duration
        }
    }
    r = SESSION.post(f"{PIKA_BASE}/web/generate", json=payload, headers=HEADERS_PIKA, timeout=30)
    r.raise_for_status()
    job_id = r.json()["video"]["pikaVideoId"]
    job = poll_job(job_id, "avatar clip")
    return job["outputUrl"]


def gradient_video(duration: int) -> str:
    prompt = "vibrant liquid gradient, smooth morphing colors, hypnotic, loop, 9:16"
    payload = {
        "promptText": prompt,
        "options": {
            "aspectRatio": "9:16",
            "frameRate": 24,
            "parameters": {"motion": 1, "guidanceScale": 12},
            "duration": duration
        }
    }
    r = SESSION.post(f"{PIKA_BASE}/web/generate", json=payload, headers=HEADERS_PIKA, timeout=30)
    r.raise_for_status()
    job_id = r.json()["video"]["pikaVideoId"]
    job = poll_job(job_id, "gradient clip")
    return job["outputUrl"]


def lipsync(video_url: str, wav_url: str, duration: int) -> str:
    payload = {
        "video": video_url,
        "speech": wav_url,
        "speechStart": 0,
        "speechEnd": duration
    }
    r = SESSION.post(f"{PIKA_BASE}/web/lipSync", json=payload, headers=HEADERS_PIKA, timeout=30)
    r.raise_for_status()
    job_id = r.json()["videos"][0]["pikaVideoId"]
    job = poll_job(job_id, "lip‑sync")
    return job["outputUrl"]

# ---------------------------------------------------------------------------
# 4.  Orchestrator
# ---------------------------------------------------------------------------

def pipeline(audio_path: Path, img_prompt: str, out_path: Path):
    tmp = Path(tempfile.mkdtemp(prefix="pika_"))

    # 4.1 portrait → transfer
    print("🎨  Generating portrait…")
    portrait_path = tmp / "portrait.png"
    try:
        create_portrait(img_prompt, portrait_path)
        img_url = upload_file(portrait_path)
    except Exception as e:
        print("⚠️  Portrait generation failed:", e)
        img_url = None  # will trigger gradient fallback

    # 4.2 audio prep
    print("🎧  Preparing audio…")
    wav_path, duration = mp3_to_wav(audio_path)
    wav_url = upload_file(wav_path)
    duration_int = int(duration) or 10

    # 4.3 generate avatar OR gradient
    try:
        if img_url:
            print("🎬  Creating avatar clip…")
            avatar_url = generate_avatar(img_url, duration_int, "subtle head motion, telling a compelling story")
        else:
            raise RuntimeError("No portrait URL; skipping to gradient")
    except Exception as avatar_err:
        print("⚠️  Avatar generation failed:", avatar_err)
        print("🌈  Falling back to gradient video…")
        avatar_url = gradient_video(duration_int)
        # gradient clip is final output (no lips)
        final_bytes = SESSION.get(avatar_url, timeout=120).content
        out_path.write_bytes(final_bytes)
        print("✅  Saved gradient clip →", out_path)
        return

    # 4.4 lip‑sync
    try:
        print("👄  Lip‑syncing…")
        final_url = lipsync(avatar_url, wav_url, duration_int)
    except Exception as lip_err:
        print("⚠️  Lip‑sync failed:", lip_err)
        print("✅  Saving non‑synced avatar as fallback")
        final_url = avatar_url

    # 4.5 download final
    print("⬇️  Downloading video…")
    vid_bytes = SESSION.get(final_url, timeout=120).content
    out_path.write_bytes(vid_bytes)
    print("✅  Final MP4 →", out_path)

# ---------------------------------------------------------------------------
# 5.  CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Generate Pika avatar video with fallback gradient.")
    ap.add_argument("audio", type=Path, help="Local MP3 from ElevenLabs")
    ap.add_argument("--prompt", required=True, help="Portrait prompt")
    ap.add_argument("--out", type=Path, default=Path("final.mp4"), help="Output MP4 path")
    args = ap.parse_args()

    pipeline(args.audio, args.prompt, args.out)


if __name__ == "__main__":
    main()
