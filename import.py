#!/usr/bin/env python3
"""
U531 watchlog — YouTube Watch History → Checkvist journal importer.

Usage:
    python import.py watch-history.json --month 2026-04

Requires env vars: CHECKVIST_USERNAME, CHECKVIST_REMOTE_KEY
"""
import argparse
import json
import os
import re
import sys
from datetime import date, datetime
from urllib.parse import parse_qs, urlparse

import httpx

BASE_URL = "https://checkvist.com"
_token = ""


# ---------------------------------------------------------------------------
# Auth / HTTP
# ---------------------------------------------------------------------------

def _refresh_token():
    r = httpx.post(
        f"{BASE_URL}/auth/login.json",
        data={
            "username": os.environ["CHECKVIST_USERNAME"],
            "remote_key": os.environ["CHECKVIST_REMOTE_KEY"],
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def api(method, path, params=None, data=None):
    global _token
    if not _token:
        _token = _refresh_token()
    p = dict(params or {})
    p["token"] = _token
    r = httpx.request(method, f"{BASE_URL}{path}", params=p, data=data, timeout=30)
    if r.status_code == 401:
        _token = _refresh_token()
        p["token"] = _token
        r = httpx.request(method, f"{BASE_URL}{path}", params=p, data=data, timeout=30)
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------------------
# Takeout parsing
# ---------------------------------------------------------------------------

def extract_video_id(url):
    if not url:
        return None
    qs = parse_qs(urlparse(url).query)
    ids = qs.get("v", [])
    return ids[0] if ids else None


def load_takeout(path, year, month):
    with open(path, encoding="utf-8") as f:
        entries = json.load(f)

    videos = []
    for e in entries:
        url = e.get("titleUrl", "")
        video_id = extract_video_id(url)
        if not video_id:
            continue
        try:
            dt = datetime.fromisoformat(e.get("time", "").replace("Z", "+00:00"))
        except ValueError:
            continue
        d = dt.date()
        if d.year != year or d.month != month:
            continue

        title = e.get("title", "").removeprefix("Watched ")
        channel = (e.get("subtitles") or [{}])[0].get("name", "")
        label = f"{title} — {channel}" if channel else title
        content = f"[{label}](https://www.youtube.com/watch?v={video_id})"

        videos.append({"date": d, "video_id": video_id, "content": content})

    return videos


# ---------------------------------------------------------------------------
# Checkvist helpers
# ---------------------------------------------------------------------------

def find_journal_list(all_lists, year, month):
    yy = str(year)[2:]
    mm = f"{month:02d}"
    month_name = date(year, month, 1).strftime("%B")
    exact = f"0_ZLOG_{yy}{mm}_{month_name}_{year}"
    prefix = f"0_ZLOG_{yy}{mm}_"
    for lst in all_lists:
        if lst["name"] == exact:
            return lst
    for lst in all_lists:
        if lst["name"].startswith(prefix):
            return lst
    return None


def day_node_content(d):
    return f"{d.strftime('%B')} {d.day} ({d.strftime('%A')})"


def build_state(all_tasks):
    children_of = {}
    for t in all_tasks:
        children_of.setdefault(t["parent_id"], []).append(t)
    return children_of


def find_child(children_of, parent_id, content):
    for t in children_of.get(parent_id, []):
        if t["content"] == content:
            return t["id"]
    return None


def ensure_task(list_id, children_of, content, parent_id=None):
    pid = parent_id if parent_id is not None else 0
    found = find_child(children_of, pid, content)
    if found:
        return found
    data = {"task[content]": content}
    if parent_id is not None:
        data["task[parent_id]"] = str(parent_id)
    t = api("POST", f"/checklists/{list_id}/tasks.json", data=data)
    children_of.setdefault(pid, []).append(t)
    return t["id"]


def existing_video_ids(all_tasks):
    pattern = re.compile(r"youtube\.com/watch\?v=([\w-]+)")
    ids = set()
    for t in all_tasks:
        m = pattern.search(t.get("content", ""))
        if m:
            ids.add(m.group(1))
    return ids


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Import YouTube watch history into Checkvist journal")
    parser.add_argument("file", help="Path to watch-history.json from Google Takeout")
    parser.add_argument("--month", required=True, help="YYYY-MM")
    args = parser.parse_args()

    try:
        year, month = [int(x) for x in args.month.split("-")]
    except ValueError:
        sys.exit("--month must be YYYY-MM")

    videos = load_takeout(args.file, year, month)
    if not videos:
        print(f"No watch history entries found for {args.month}.")
        return

    by_date = {}
    for v in videos:
        by_date.setdefault(v["date"], []).append(v)

    all_lists = api("GET", "/checklists.json")
    journal = find_journal_list(all_lists, year, month)
    if not journal:
        sys.exit(f"No journal list found for {args.month}. Expected name like 0_ZLOG_{str(year)[2:]}{month:02d}_...")

    list_id = journal["id"]
    all_tasks = api("GET", f"/checklists/{list_id}/tasks.json")
    children_of = build_state(all_tasks)
    seen_ids = existing_video_ids(all_tasks)

    added = 0
    for d in sorted(by_date):
        day_id = ensure_task(list_id, children_of, day_node_content(d))
        videos_id = ensure_task(list_id, children_of, "Videos", parent_id=day_id)

        for v in by_date[d]:
            if v["video_id"] in seen_ids:
                continue
            api("POST", f"/checklists/{list_id}/tasks.json", data={
                "task[content]": v["content"],
                "task[parent_id]": str(videos_id),
            })
            seen_ids.add(v["video_id"])
            children_of.setdefault(videos_id, []).append({"content": v["content"]})
            added += 1

    print(f"Done — {added} video(s) added to {journal['name']}.")


if __name__ == "__main__":
    main()
