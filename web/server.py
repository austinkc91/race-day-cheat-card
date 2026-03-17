#!/usr/bin/env python3
"""
Race Day Cheat Card — Live Web Server

Features:
- Basic auth (username/password)
- Multi-track support (select track from UI)
- Start/stop research from the web UI (creates cron via Listen server)
- Auto-updates every 30 seconds from per-track JSON data files

Usage:
    python3 server.py [--port 7700]
"""

import json
import os
import re
import secrets
import argparse
import hashlib
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Response, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start background tasks on startup."""
    task = asyncio.create_task(background_scheduler())
    yield
    task.cancel()


app = FastAPI(title="Race Day Cheat Card", lifespan=lifespan)
security = HTTPBasic()

WEB_DIR = Path(__file__).parent
DATA_DIR = Path("/tmp/race_day_data")
SCHEDULE_FILE = DATA_DIR / "_schedules.json"
LISTEN_URL = os.environ.get("LISTEN_URL", "http://localhost:7600")

# Auth credentials — override with env vars
AUTH_USER = os.environ.get("CHEATCARD_USER", "AKC")
AUTH_PASS = os.environ.get("CHEATCARD_PASS", "TX")

# OTB live schedule API
OTB_API_URL = "https://ojlbo7v5hb.execute-api.us-west-2.amazonaws.com/current_races/v2"
OTB_CACHE_FILE = DATA_DIR / "_otb_schedule.json"
OTB_CACHE_TTL = 300  # Refresh every 5 minutes

# Pre-race update tracking — avoid double-triggering
# { "track_slug": { "race_num": <int>, "triggered_at": <timestamp> } }
PRE_RACE_TRIGGERS = {}

# Known tracks with metadata
TRACKS = {
    "fair-grounds": {"name": "Fair Grounds", "location": "New Orleans, LA", "code": "FG"},
    "oaklawn": {"name": "Oaklawn Park", "location": "Hot Springs, AR", "code": "OP"},
    "gulfstream": {"name": "Gulfstream Park", "location": "Hallandale Beach, FL", "code": "GP"},
    "santa-anita": {"name": "Santa Anita Park", "location": "Arcadia, CA", "code": "SA"},
    "aqueduct": {"name": "Aqueduct", "location": "Ozone Park, NY", "code": "AQU"},
    "churchill-downs": {"name": "Churchill Downs", "location": "Louisville, KY", "code": "CD"},
    "keeneland": {"name": "Keeneland", "location": "Lexington, KY", "code": "KEE"},
    "belmont": {"name": "Belmont Park", "location": "Elmont, NY", "code": "BEL"},
    "del-mar": {"name": "Del Mar", "location": "Del Mar, CA", "code": "DMR"},
    "saratoga": {"name": "Saratoga", "location": "Saratoga Springs, NY", "code": "SAR"},
    "pimlico": {"name": "Pimlico", "location": "Baltimore, MD", "code": "PIM"},
    "tampa-bay": {"name": "Tampa Bay Downs", "location": "Tampa, FL", "code": "TAM"},
    "turfway": {"name": "Turfway Park", "location": "Florence, KY", "code": "TP"},
    "laurel": {"name": "Laurel Park", "location": "Laurel, MD", "code": "LRL"},
    "sam-houston": {"name": "Sam Houston Race Park", "location": "Houston, TX", "code": "HOU"},
    "lone-star": {"name": "Lone Star Park", "location": "Grand Prairie, TX", "code": "LS"},
    "remington": {"name": "Remington Park", "location": "Oklahoma City, OK", "code": "RP"},
    "parx": {"name": "Parx Racing", "location": "Bensalem, PA", "code": "PRX"},
}

# Map OTB API track names → our slugs (lowercase matching)
OTB_NAME_MAP = {}
for _slug, _info in TRACKS.items():
    # Map by full name and by code
    OTB_NAME_MAP[_info["name"].lower()] = _slug
    OTB_NAME_MAP[_info["code"].lower()] = _slug
# Manual overrides for OTB naming quirks
OTB_NAME_MAP.update({
    "fair grounds": "fair-grounds",
    "oaklawn park": "oaklawn",
    "gulfstream park": "gulfstream",
    "santa anita": "santa-anita",
    "santa anita park": "santa-anita",
    "churchill downs": "churchill-downs",
    "del mar": "del-mar",
    "tampa bay downs": "tampa-bay",
    "tampa bay": "tampa-bay",
    "turfway park": "turfway",
    "laurel park": "laurel",
    "sam houston": "sam-houston",
    "sam houston race park": "sam-houston",
    "lone star park": "lone-star",
    "lone star": "lone-star",
    "remington park": "remington",
    "parx racing": "parx",
    "parx": "parx",
    "belmont park": "belmont",
    "belmont at the big a": "belmont",
    "belmont at aqueduct": "belmont",
    "pimlico race course": "pimlico",
})


def _match_otb_track(otb_name: str) -> Optional[str]:
    """Try to match an OTB track name to one of our track slugs."""
    name_lower = otb_name.lower().strip()
    # Skip non-thoroughbred racing (harness, greyhound, etc.)
    skip_keywords = ["harness", "greyhound", "(aus)", "(uk)", "(fr)", "(tur)",
                     "(ita)", "(ig)", "(nor)", "(swe)", "(arg)", "japan",
                     "eve (uk)", "australia"]
    if any(kw in name_lower for kw in skip_keywords):
        return None
    # Exact match only — no loose substring matching
    if name_lower in OTB_NAME_MAP:
        return OTB_NAME_MAP[name_lower]
    return None


async def fetch_otb_schedule() -> dict:
    """Fetch today's live racing schedule from OTB API with caching."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Check cache
    if OTB_CACHE_FILE.exists():
        try:
            with open(OTB_CACHE_FILE) as f:
                cached = json.load(f)
            cached_at = cached.get("_cached_at", 0)
            if (datetime.now().timestamp() - cached_at) < OTB_CACHE_TTL:
                return cached.get("schedule", {})
        except (json.JSONDecodeError, IOError):
            pass

    # Fetch fresh data
    schedule = {}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(OTB_API_URL)
            if resp.status_code == 200:
                data = resp.json()
                tracks_list = data.get("todaysraces", {}).get("tracks", [])
                for t in tracks_list:
                    otb_name = t.get("name", "")
                    slug = _match_otb_track(otb_name)
                    if slug:
                        schedule[slug] = {
                            "otb_name": otb_name,
                            "first_post": t.get("time", ""),
                            "current_race": t.get("currentRace", ""),
                            "mtp": t.get("mtp", ""),
                            "results_url": t.get("resultsUrl", ""),
                            "program_date": t.get("programDate", ""),
                        }
                # Cache it
                with open(OTB_CACHE_FILE, "w") as f:
                    json.dump({"_cached_at": datetime.now().timestamp(), "schedule": schedule}, f, indent=2)
    except Exception:
        pass  # Return empty on failure
    return schedule


def verify_auth(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify basic auth credentials."""
    correct_user = secrets.compare_digest(credentials.username.encode(), AUTH_USER.encode())
    correct_pass = secrets.compare_digest(credentials.password.encode(), AUTH_PASS.encode())
    if not (correct_user and correct_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def get_data_path(track_slug: str) -> Path:
    """Get data file path for a track."""
    return DATA_DIR / f"{track_slug}.json"


def get_track_data(track_slug: str) -> Optional[dict]:
    """Load track data from JSON file."""
    path = get_data_path(track_slug)
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def load_schedules() -> dict:
    """Load scheduled start times from file."""
    if not SCHEDULE_FILE.exists():
        return {}
    try:
        with open(SCHEDULE_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_schedules(schedules: dict):
    """Save scheduled start times to file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(schedules, f, indent=2)


def is_track_finished(track_slug: str) -> bool:
    """Check if all races at a track are COMPLETED with no PENDING bets."""
    data = get_track_data(track_slug)
    if not data:
        return False
    races = data.get("races", [])
    if not races:
        return False
    # All races must be COMPLETED
    for race in races:
        if race.get("status", "PENDING") != "COMPLETED":
            return False
    # All P&L entries must have results (no PENDING)
    pnl = data.get("pnl", [])
    if pnl:
        for entry in pnl:
            result = (entry.get("result") or "PENDING").upper()
            if "PENDING" in result:
                return False
    return True


async def background_scheduler():
    """Background task: check scheduled starts and auto-stop finished tracks every 60s."""
    while True:
        await asyncio.sleep(60)
        try:
            # --- Scheduled starts ---
            schedules = load_schedules()
            now = datetime.now()
            changed = False
            for slug, info in list(schedules.items()):
                start_str = info.get("start_time")
                if not start_str or info.get("started"):
                    continue
                try:
                    start_dt = datetime.fromisoformat(start_str)
                except ValueError:
                    continue
                if now >= start_dt:
                    # Time to start this track
                    if slug in TRACKS:
                        async with httpx.AsyncClient(timeout=10.0) as client:
                            await client.post(
                                f"http://localhost:{app.state.port if hasattr(app.state, 'port') else 7700}/api/start/{slug}",
                                auth=(AUTH_USER, AUTH_PASS),
                            )
                        schedules[slug]["started"] = True
                        changed = True
            if changed:
                save_schedules(schedules)

            # --- Pre-race auto-refresh: trigger research when MTP <= 15 ---
            try:
                otb_schedule = await fetch_otb_schedule()
                async with httpx.AsyncClient(timeout=5.0) as client:
                    crons_resp = await client.get(f"{LISTEN_URL}/crons")
                    crons_for_trigger = crons_resp.json().get("crons", []) if crons_resp.status_code == 200 else []

                for slug, otb in otb_schedule.items():
                    if slug not in TRACKS:
                        continue
                    try:
                        mtp = int(otb.get("mtp", 99))
                        current_race = int(otb.get("current_race", 0))
                    except (ValueError, TypeError):
                        continue

                    # Trigger when MTP is between 1-15 minutes (15 min before each race)
                    if 1 <= mtp <= 15:
                        prev = PRE_RACE_TRIGGERS.get(slug, {})
                        already_triggered = (
                            prev.get("race_num") == current_race
                            and (datetime.now().timestamp() - prev.get("triggered_at", 0)) < 600
                        )
                        if not already_triggered:
                            # Find the cron for this track and trigger it
                            cron_name = f"Cheat Card: {TRACKS[slug]['name']}"
                            for c in crons_for_trigger:
                                if c.get("name") == cron_name and c.get("enabled", False):
                                    async with httpx.AsyncClient(timeout=10.0) as client:
                                        await client.post(f"{LISTEN_URL}/cron/{c['id']}/trigger")
                                    PRE_RACE_TRIGGERS[slug] = {
                                        "race_num": current_race,
                                        "triggered_at": datetime.now().timestamp(),
                                    }
                                    break
            except Exception:
                pass

            # --- Auto-stop finished tracks ---
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{LISTEN_URL}/crons")
                if resp.status_code == 200:
                    crons = resp.json().get("crons", [])
                    for c in crons:
                        name = c.get("name", "")
                        if not name.startswith("Cheat Card:") or not c.get("enabled", False):
                            continue
                        # Find the matching track slug
                        matched_slug = None
                        for ts in TRACKS:
                            if TRACKS[ts]["name"].lower().replace(" ", "-") in name.lower().replace(" ", "-") or ts in name.lower().replace(" ", "-"):
                                matched_slug = ts
                                break
                        if matched_slug and is_track_finished(matched_slug):
                            # All races done, disable the cron
                            await client.put(
                                f"{LISTEN_URL}/cron/{c['id']}",
                                json={"enabled": False},
                            )
        except Exception:
            pass  # Don't crash the background task


def build_cron_prompt(track_slug: str, track_info: dict) -> str:
    """Build the cron prompt for race day research."""
    track_name = track_info["name"]
    track_code = track_info["code"]
    location = track_info["location"]
    data_path = str(get_data_path(track_slug))

    return f"""You are the Race Day Cheat Card AI for {track_name} ({track_code}) in {location}.

Your job: Research today's races at {track_name} and update the live cheat card data file.

STEP 1: Check the current data file at {data_path}
- If it exists, read it to see what version we're on and what's already been researched
- If it doesn't exist, start fresh

STEP 2: Research today's card at {track_name}
- web_search: '{track_name} entries today {track_code}'
- web_search: '{track_name} picks today expert'
- web_search: '{track_name} weather {location} today'
- web_search: 'equibase {track_code} entries today'
- web_search: '{track_name} results today' (for completed races)
- Check all 6 expert sources: SFTB, Racing Dudes, FanDuel Research, Ultimate Capper, Today's Racing Digest, AllChalk
- Look for scratches, track conditions, odds changes

STEP 3: Apply the betting strategy
- WIN bets only at 5/1+ odds
- Consensus tier system: GREEN (4+ sources), YELLOW (3), ORANGE (2), RED (1)
- Race type targeting: CLM = GOLDMINE, MCL = longshot value, MOC = SKIP, STK = SKIP
- $1 Exacta Box every race with our pick + value horse
- $0.50 Trifecta Box on best race of the day
- Value Score >= 2.0 for value plays
- Halve bets on sloppy/muddy tracks
- No place bets

STEP 4: Write the data file
- Follow the JSON schema at ~/race-day-cheat-card/web/schema.json EXACTLY
- Write to: {data_path}
- Make sure the directory exists first: mkdir -p {str(DATA_DIR)}
- Increment the version number each update
- Update race statuses: check results for completed races
- Update P&L tracker with any new results
- IMPORTANT: Do NOT modify bets/picks for races with status "COMPLETED" — preserve their results exactly
- For PENDING races, update with the LATEST odds, scratches, and picks so the user gets the freshest data before betting closes

STEP 5: Report what changed
- Summarize what's new in this update (new races researched, results updated, scratches, etc.)
- Keep the summary SHORT for Telegram

IMPORTANT: The web app reads this JSON file every 30 seconds. Write valid JSON or the page breaks."""


@app.get("/", response_class=HTMLResponse)
async def landing_page(user: str = Depends(verify_auth)):
    """Landing page with track selection."""
    html_path = WEB_DIR / "index.html"
    return HTMLResponse(content=html_path.read_text(), status_code=200)


@app.get("/track/{track_slug}", response_class=HTMLResponse)
async def track_page(track_slug: str, user: str = Depends(verify_auth)):
    """Cheat card page for a specific track."""
    if track_slug not in TRACKS:
        raise HTTPException(status_code=404, detail="Track not found")
    card_path = WEB_DIR / "card.html"
    return HTMLResponse(content=card_path.read_text(), status_code=200)


@app.get("/api/tracks")
async def list_tracks(user: str = Depends(verify_auth)):
    """List all available tracks with their status."""
    result = []
    schedules = load_schedules()
    # Fetch live OTB schedule
    otb_schedule = await fetch_otb_schedule()
    # Check which tracks have active crons
    active_crons = {}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{LISTEN_URL}/crons")
            if resp.status_code == 200:
                crons = resp.json().get("crons", [])
                for c in crons:
                    name = c.get("name", "")
                    if name.startswith("Cheat Card:"):
                        slug = name.replace("Cheat Card: ", "").lower().replace(" ", "-").replace("'", "")
                        # Try to match slug
                        for ts in TRACKS:
                            if TRACKS[ts]["name"].lower().replace(" ", "-") in slug or ts in slug:
                                active_crons[ts] = {
                                    "cron_id": c["id"],
                                    "enabled": c.get("enabled", False),
                                }
                                break
    except Exception:
        pass

    for slug, info in TRACKS.items():
        data = get_track_data(slug)
        has_data = data is not None
        last_update = None
        version = None
        if has_data:
            path = get_data_path(slug)
            last_update = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            version = data.get("version", "")

        cron_info = active_crons.get(slug, {})
        sched = schedules.get(slug, {})
        all_done = is_track_finished(slug) if has_data else False
        otb = otb_schedule.get(slug, {})

        result.append({
            "slug": slug,
            "name": info["name"],
            "location": info["location"],
            "code": info["code"],
            "has_data": has_data,
            "last_update": last_update,
            "version": version,
            "cron_active": bool(cron_info.get("cron_id")),
            "cron_enabled": cron_info.get("enabled", False),
            "cron_id": cron_info.get("cron_id"),
            "scheduled_start": sched.get("start_time") if not sched.get("started") else None,
            "all_races_complete": all_done,
            "racing_today": bool(otb) and otb.get("mtp", "0") != "0",
            "raced_today": bool(otb) and otb.get("mtp", "0") == "0",
            "first_post": otb.get("first_post", ""),
            "current_race": otb.get("current_race", ""),
            "mtp": otb.get("mtp", ""),
            "results_url": otb.get("results_url", ""),
        })

    return JSONResponse(content=result)


@app.get("/api/data/{track_slug}")
async def get_data(track_slug: str, user: str = Depends(verify_auth)):
    """Get race data for a specific track, enriched with live OTB data."""
    if track_slug not in TRACKS:
        return JSONResponse(content={"error": "Track not found"}, status_code=404)

    data = get_track_data(track_slug)
    if data is None:
        return JSONResponse(
            content={"error": f"No data yet for {TRACKS[track_slug]['name']}. Start research first!"},
            status_code=404,
        )

    data["_server_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S CT")

    # Add last-refreshed timestamp (when the data file was last written by a scan)
    data_path = get_data_path(track_slug)
    if data_path.exists():
        mtime = data_path.stat().st_mtime
        data["_last_refreshed"] = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %I:%M:%S %p CT")

    # Merge live OTB data so frontend can show MTP countdown and lock races
    otb_schedule = await fetch_otb_schedule()
    otb = otb_schedule.get(track_slug, {})
    if otb:
        current_race = 0
        try:
            current_race = int(otb.get("current_race", 0))
        except (ValueError, TypeError):
            pass
        mtp = 0
        try:
            mtp = int(otb.get("mtp", 0))
        except (ValueError, TypeError):
            pass

        data["_live"] = {
            "current_race": current_race,
            "mtp": mtp,
            "first_post": otb.get("first_post", ""),
        }

        # Mark race lock status based on live data
        for race in data.get("races", []):
            race_num = 0
            try:
                race_num = int(race.get("number", 0))
            except (ValueError, TypeError):
                pass
            if race_num < current_race:
                race["_locked"] = True
            elif race_num == current_race and mtp == 0:
                race["_locked"] = True
            else:
                race["_locked"] = False

    return JSONResponse(content=data)


@app.post("/api/start/{track_slug}")
async def start_research(track_slug: str, user: str = Depends(verify_auth)):
    """Start race day research for a track. Runs first scan immediately, then auto-scans 15 min before each race."""
    if track_slug not in TRACKS:
        return JSONResponse(content={"error": "Track not found"}, status_code=404)

    track_info = TRACKS[track_slug]
    cron_name = f"Cheat Card: {track_info['name']}"

    # Ensure data dir exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Check if cron already exists
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{LISTEN_URL}/crons")
            if resp.status_code == 200:
                crons = resp.json().get("crons", [])
                for c in crons:
                    if c.get("name") == cron_name:
                        # Enable it if disabled
                        if not c.get("enabled", True):
                            await client.put(
                                f"{LISTEN_URL}/cron/{c['id']}",
                                json={"enabled": True},
                            )
                        # Trigger it now
                        await client.post(f"{LISTEN_URL}/cron/{c['id']}/trigger")
                        return JSONResponse(content={
                            "status": "started",
                            "message": f"Restarted research for {track_info['name']} — auto-updates 15 min before each race",
                            "cron_id": c["id"],
                        })

            # Create new cron — baseline once daily at 6am, real updates come from
            # the MTP-based pre-race trigger (15 min before each race post time)
            prompt = build_cron_prompt(track_slug, track_info)
            resp = await client.post(
                f"{LISTEN_URL}/cron",
                json={
                    "name": cron_name,
                    "schedule": "0 6 * * *",
                    "prompt": prompt,
                    "timezone": "US/Central",
                },
            )

            if resp.status_code == 200:
                cron_data = resp.json()
                cron_id = cron_data.get("id") or cron_data.get("cron", {}).get("id")

                # Trigger it immediately for the first scan
                if cron_id:
                    await client.post(f"{LISTEN_URL}/cron/{cron_id}/trigger")

                return JSONResponse(content={
                    "status": "started",
                    "message": f"Started research for {track_info['name']} — auto-updates 15 min before each race",
                    "cron_id": cron_id,
                })
            else:
                return JSONResponse(
                    content={"error": f"Failed to create cron: {resp.text}"},
                    status_code=500,
                )
    except Exception as e:
        return JSONResponse(
            content={"error": f"Could not reach Listen server: {str(e)}"},
            status_code=500,
        )


@app.post("/api/refresh/{track_slug}")
async def refresh_research(track_slug: str, user: str = Depends(verify_auth)):
    """Manually trigger a fresh research scan for a track."""
    if track_slug not in TRACKS:
        return JSONResponse(content={"error": "Track not found"}, status_code=404)

    track_info = TRACKS[track_slug]
    cron_name = f"Cheat Card: {track_info['name']}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try to trigger via existing cron first
            resp = await client.get(f"{LISTEN_URL}/crons")
            if resp.status_code == 200:
                crons = resp.json().get("crons", [])
                for c in crons:
                    if c.get("name") == cron_name:
                        if c.get("enabled", False):
                            await client.post(f"{LISTEN_URL}/cron/{c['id']}/trigger")
                            return JSONResponse(content={
                                "status": "refreshing",
                                "message": f"Manual refresh triggered for {track_info['name']}",
                                "cron_id": c["id"],
                            })

            # No active cron — submit a one-off job directly
            prompt = build_cron_prompt(track_slug, track_info)
            resp = await client.post(
                f"{LISTEN_URL}/job",
                json={"prompt": prompt},
            )
            if resp.status_code == 200:
                job_data = resp.json()
                return JSONResponse(content={
                    "status": "refreshing",
                    "message": f"One-off refresh started for {track_info['name']}",
                    "job_id": job_data.get("id"),
                })
            else:
                return JSONResponse(
                    content={"error": f"Failed to start refresh job: {resp.text}"},
                    status_code=500,
                )
    except Exception as e:
        return JSONResponse(
            content={"error": f"Could not reach Listen server: {str(e)}"},
            status_code=500,
        )


@app.post("/api/stop/{track_slug}")
async def stop_research(track_slug: str, user: str = Depends(verify_auth)):
    """Stop race day research for a track (disables the cron AND kills running jobs)."""
    if track_slug not in TRACKS:
        return JSONResponse(content={"error": "Track not found"}, status_code=404)

    track_info = TRACKS[track_slug]
    cron_name = f"Cheat Card: {track_info['name']}"
    killed_jobs = []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. Disable the cron to prevent future triggers
            cron_id = None
            resp = await client.get(f"{LISTEN_URL}/crons")
            if resp.status_code == 200:
                crons = resp.json().get("crons", [])
                for c in crons:
                    if c.get("name") == cron_name:
                        await client.put(
                            f"{LISTEN_URL}/cron/{c['id']}",
                            json={"enabled": False},
                        )
                        cron_id = c["id"]
                        break

            # 2. Kill any currently running jobs for this track
            jobs_resp = await client.get(f"{LISTEN_URL}/jobs")
            if jobs_resp.status_code == 200:
                import yaml as _yaml
                jobs_data = _yaml.safe_load(jobs_resp.text)
                for job in (jobs_data or {}).get("jobs", []):
                    if job.get("status") == "running":
                        prompt = job.get("prompt", "")
                        if track_info["name"].lower() in prompt.lower() or track_slug in prompt.lower():
                            try:
                                await client.delete(f"{LISTEN_URL}/job/{job['id']}")
                                killed_jobs.append(job["id"])
                            except Exception:
                                pass

            if cron_id or killed_jobs:
                msg = f"Stopped research for {track_info['name']}"
                if killed_jobs:
                    msg += f" and cancelled {len(killed_jobs)} running scan(s)"
                return JSONResponse(content={
                    "status": "stopped",
                    "message": msg,
                    "cron_id": cron_id,
                    "killed_jobs": killed_jobs,
                })

            return JSONResponse(content={
                "status": "not_found",
                "message": f"No active cron found for {track_info['name']}",
            })
    except Exception as e:
        return JSONResponse(
            content={"error": f"Could not reach Listen server: {str(e)}"},
            status_code=500,
        )


@app.post("/api/schedule/{track_slug}")
async def schedule_start(track_slug: str, request: Request, user: str = Depends(verify_auth)):
    """Schedule a track to start research at a specific date/time."""
    if track_slug not in TRACKS:
        return JSONResponse(content={"error": "Track not found"}, status_code=404)

    body = await request.json()
    start_time = body.get("start_time")  # ISO format: "2026-03-17T12:00"
    if not start_time:
        return JSONResponse(content={"error": "start_time required"}, status_code=400)

    try:
        dt = datetime.fromisoformat(start_time)
    except ValueError:
        return JSONResponse(content={"error": "Invalid date/time format"}, status_code=400)

    schedules = load_schedules()
    schedules[track_slug] = {
        "start_time": start_time,
        "started": False,
        "track_name": TRACKS[track_slug]["name"],
        "scheduled_at": datetime.now().isoformat(),
    }
    save_schedules(schedules)

    return JSONResponse(content={
        "status": "scheduled",
        "message": f"{TRACKS[track_slug]['name']} scheduled to start at {dt.strftime('%b %d, %Y %I:%M %p')}",
        "start_time": start_time,
    })


@app.delete("/api/schedule/{track_slug}")
async def cancel_schedule(track_slug: str, user: str = Depends(verify_auth)):
    """Cancel a scheduled start for a track."""
    schedules = load_schedules()
    if track_slug in schedules:
        del schedules[track_slug]
        save_schedules(schedules)
    return JSONResponse(content={"status": "cancelled"})


@app.get("/api/schedules")
async def list_schedules(user: str = Depends(verify_auth)):
    """List all scheduled track starts."""
    return JSONResponse(content=load_schedules())


@app.get("/api/live-schedule")
async def live_schedule(user: str = Depends(verify_auth)):
    """Get today's live racing schedule from OTB."""
    # Force refresh by clearing cache
    if OTB_CACHE_FILE.exists():
        OTB_CACHE_FILE.unlink()
    schedule = await fetch_otb_schedule()
    return JSONResponse(content={
        "racing_today": len(schedule),
        "tracks": schedule,
    })


@app.get("/api/health")
async def health():
    """Health check (no auth required)."""
    return {"status": "ok", "tracks": len(TRACKS)}


def main():
    parser = argparse.ArgumentParser(description="Race Day Cheat Card Web Server")
    parser.add_argument("--port", type=int, default=7700, help="Port (default: 7700)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host")
    args = parser.parse_args()

    print(f"Race Day Cheat Card — http://{args.host}:{args.port}")
    print(f"Auth: {AUTH_USER} / {'*' * len(AUTH_PASS)}")
    print(f"Tracks: {len(TRACKS)}")
    print(f"Data dir: {DATA_DIR}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
