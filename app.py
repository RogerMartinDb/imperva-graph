#!/usr/bin/env python3
"""Web app: fetch Imperva/Exabeam URL durations for a date range and graph them.

Replaces the manual flow (export from Exabeam -> add.py -> open index.html).
The page lets you pick start/end dates and an Exabeam filter, then the server
queries Exabeam, computes per-request duration, and returns the data as JSON
for the chart to render.
"""

from flask import Flask, jsonify, request, send_from_directory

import get

app = Flask(__name__, static_folder=None)

HERE = __import__("os").path.dirname(__file__)


@app.route("/")
def index():
    return send_from_directory(HERE, "index.html")


@app.route("/api/default-filter")
def default_filter():
    return jsonify({"filter": get.DEFAULT_FILTER})


@app.route("/api/data")
def data():
    start = request.args.get("start", "").strip()
    end = request.args.get("end", "").strip()
    filter_str = request.args.get("filter", "").strip() or get.DEFAULT_FILTER

    if not start or not end:
        return jsonify({"error": "start and end are required"}), 400

    try:
        df = get.getDurationURL(start, end, filter_str)
    except Exception as exc:  # surface API / auth errors to the page
        return jsonify({"error": str(exc)}), 502

    records = [
        {"time": int(t), "duration": float(d)}
        for t, d in zip(df["time"], df["duration"])
        if t == t and d == d  # drop NaN
    ]
    return jsonify({"records": records, "count": len(records)})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
