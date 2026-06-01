# Imperva / Exabeam Duration Graph

A small web app that queries [Exabeam](https://www.exabeam.com/) for Imperva
Incapsula web request events over a chosen time range, computes each request's
duration, and graphs it in the browser.

It replaces the old manual flow (export a CSV from Exabeam → run `add.py` to add
a `duration` column → open a static `index.html`). Now everything happens from
one page: pick the dates, optionally tweak the filter, click **Fetch**.

## How it works

```
browser (index.html) ──GET /api/data?start&end&filter──▶ app.py (Flask)
                                                              │
                                                              ▼
                                                    get.py → Exabeam API
```

- **`get.py`** — talks to Exabeam: obtains an OAuth bearer token from your
  client credentials, runs a `search/v2/events` query for the given time range
  and filter, and returns a DataFrame with `time`, `end_time`, `url`, and a
  computed `duration` (in milliseconds). Can also be run on its own to dump a
  CSV (see below).
- **`app.py`** — Flask server exposing the page and a small JSON API.
- **`index.html`** — the UI and Chart.js rendering. No build step; it pulls
  Chart.js from a CDN.

## Setup

1. Create a `.env` file in the project root with your Exabeam API credentials:

   ```
   CLIENT_ID=your-client-id
   CLIENT_SECRET=your-client-secret
   ```

2. Install dependencies (a virtualenv is recommended):

   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```

## Running

```bash
.venv/bin/python app.py
```

Then open <http://127.0.0.1:5000> and:

1. Set the **Start** and **End** dates (default: the last 5 hours). These are
   interpreted as **UTC** to match the Exabeam query window.
2. Adjust the **Exabeam filter** if needed (pre-filled with the default from
   `get.py`). It's a multiline field — the query syntax is Exabeam's.
3. Click **Fetch**.

### Chart controls

- **Metric**
  - **Count (duration > threshold)** — number of requests per time bucket whose
    duration exceeds the **Threshold (ms)** value.
  - **Percentile of duration** — the chosen **Percentile (0–100)** of request
    durations within each time bucket (e.g. p95 latency).
- **Time bucket** — how finely time is grouped (1 min … 1 hour).

Changing any chart control re-renders instantly from the already-fetched data;
only changing the date range or filter requires another **Fetch**.

## HTTP API

- `GET /` — the web page.
- `GET /api/default-filter` — returns the default Exabeam filter string.
- `GET /api/data?start=<ISO>&end=<ISO>&filter=<str>` — queries Exabeam and
  returns `{ "records": [{ "time": <epoch_ms>, "duration": <ms> }, ...],
  "count": <n> }`. `start`/`end` are required and use the Exabeam timestamp
  format `YYYY-MM-DDTHH:MM:SSZ`; `filter` is optional and defaults to the
  built-in filter. Exabeam/auth errors are returned as `{ "error": ... }` with
  a 502 status.

## Command-line CSV export (optional)

`get.py` can be run directly to dump the last 5 hours of results to
`time-betsoft.csv`:

```bash
.venv/bin/python get.py
```

Edit the `hour` value or call `getDurationURL(start, end, filter)` for a custom
range.

## Files

| File               | Purpose                                          |
| ------------------ | ------------------------------------------------ |
| `app.py`           | Flask server (page + JSON API)                   |
| `get.py`           | Exabeam client / duration computation            |
| `index.html`       | Web UI and Chart.js rendering                    |
| `requirements.txt` | Python dependencies                              |
| `.env`             | Exabeam credentials (not committed)              |

## Notes

- TLS verification to the Exabeam API is disabled (`verify=False`); the
  corresponding urllib3 warnings are suppressed.
- The server binds to `127.0.0.1:5000` in debug mode — it's meant for local use,
  not public exposure.
