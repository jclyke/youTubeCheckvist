# U531 watchlog

YouTube Watch History → Checkvist journal importer.

## What It Does

A single-page HTML app that reads your Google Takeout `watch-history.json`, lets you select which months to process, and generates Checkvist-ready markdown — one copyable block per day.

Paste each day's block into your Checkvist monthly journal list and choose **"Split into many"** — Checkvist will create the right hierarchy automatically:

```
April 26 (Sunday)
  Videos
    Why Healthy 70-Year-Olds SUDDENLY DECLINE — Doctors of Ojai
    LLMs are a Dead End — Kiraa
```

## Usage

1. Open `index.html` in your browser (no install, no server)
2. Drop or browse to your `watch-history.json`
3. Select the months you want (grouped by year, with day/video counts)
4. Click **Generate output**
5. For each day card, click **Copy** and paste into the matching Checkvist list → Split into many

Previously-copied months are dimmed with a ✓ so you can focus on new ones. Use **Clear done history** to reset.

## Getting the Takeout File

1. Go to [takeout.google.com](https://takeout.google.com)
2. Deselect all → select only **YouTube and YouTube Music**
3. Under options, choose **History** only, format **JSON**
4. Download and extract
5. File is at: `Takeout/YouTube and YouTube Music/history/watch-history.json`

## Output Format

Each day block uses Checkvist's indented hierarchy (one space per level):

```
April 26 (Sunday)
 Videos
  [Title — Channel](https://www.youtube.com/watch?v=VIDEO_ID)
  [Another Title — Channel](https://www.youtube.com/watch?v=VIDEO_ID2)
```

Paste with **Split into many** to get the day as a parent node, Videos as a child, and each video link as a grandchild.

## Notes

- Timestamps in the Takeout file are UTC; day assignment uses UTC date
- Entries where the video has been deleted (no URL) are silently skipped
- The file can be large (30MB+) — handled entirely in-browser, no upload
- Done-month tracking persists in `localStorage` for that browser
