# U531 watchlog

Exports your YouTube watch history from Google Takeout into monthly markdown files, grouped by day — ready to paste into Checkvist or any outliner.

## What it does

Reads `watch-history.json` from a Google Takeout export, filters to a target month, and writes a markdown file with entries in the format:

```
Videos (April 3)

- [Title — Channel](https://www.youtube.com/watch?v=VIDEO_ID)
- [Another Title — Channel](https://www.youtube.com/watch?v=VIDEO_ID)

Videos (April 4)
...
```

The day header format (`Videos (Month D)`) is intentional — it matches the node structure used in a Checkvist journal where each day has a `Videos` child.

## Requirements

- Python 3.9+
- `httpx` (`pip install httpx`)

## Usage

```bash
python import.py watch-history.json --month 2026-04
```

This writes `april_2026.md` to the current directory.

## Getting your Takeout export

1. Go to [takeout.google.com](https://takeout.google.com)
2. Deselect all → select only **YouTube and YouTube Music**
3. Under options, choose **History** only, format **JSON**
4. Download and extract
5. File is at: `Takeout/YouTube and YouTube Music/history/watch-history.json`

## Idempotency

Each YouTube video has a unique ID (`v=...` in the URL). The script uses this as a dedup key — re-running the same month is safe.

## Notes

- Timestamps in the Takeout file are UTC. Day assignment uses UTC date, which is close enough for a watch log.
- Entries where the video has been deleted (no `titleUrl`) are silently skipped.
- The Takeout file typically spans years of history — only the target month is processed.

## Planned

- Auto-tagging via Claude API (tag by topic before insertion)
- Direct Checkvist push (currently generates markdown for manual review/curation)
