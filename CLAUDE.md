# U531 — watchlog

YouTube Watch History → Checkvist journal importer.

## What It Does

Reads a Google Takeout `watch-history.json`, filters to a target month, and inserts
each video as a child of a `Videos` node under the corresponding day node in the
Checkvist journal. Idempotent: dedup key is the YouTube video ID — safe to re-run.

## Structure Produced in Checkvist

```
April 26 (Sunday)
  └── Videos
        └── [Title — Channel](https://www.youtube.com/watch?v=VIDEO_ID)
        └── [Another Title — Channel](https://www.youtube.com/watch?v=VIDEO_ID2)
```

Day nodes and the Videos child are created if they don't exist.

## Usage

```
# Set credentials once in your shell:
export CHECKVIST_USERNAME=...
export CHECKVIST_REMOTE_KEY=...

python import.py watch-history.json --month 2026-04
```

On Windows (PowerShell):
```powershell
$env:CHECKVIST_USERNAME="..."; $env:CHECKVIST_REMOTE_KEY="..."
python import.py watch-history.json --month 2026-04
```

## Getting the Takeout File

1. Go to https://takeout.google.com
2. Deselect all → select only "YouTube and YouTube Music"
3. Under options, select "History" only, format JSON
4. Download and extract — file is at `Takeout/YouTube and YouTube Music/history/watch-history.json`

## Journal List Lookup

Lists follow naming pattern `0_ZLOG_YYMM_Month_YYYY` (e.g. `0_ZLOG_2604_April_2026`).
The script finds the correct one automatically by matching year + month.

## Credentials

- `CHECKVIST_USERNAME` — your Checkvist login email
- `CHECKVIST_REMOTE_KEY` — found at https://checkvist.com/auth/profile (Remote access key)
