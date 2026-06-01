import os
import requests
import json
import pandas as pd
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()
requests.packages.urllib3.disable_warnings()
domain = "api.us-west.exabeam.cloud"

DEFAULT_FILTER = (
    'web_domain: "api.betanysports.eu"\n'
    'AND url: "api/betsoft"\n'
    'AND product: "Imperva Incapsula"'
)


def bearToken():
    url = "https://" + domain + "/auth/v1/token"

    payload = {
        "grant_type": "client_credentials",
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET")
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers, verify=False)
    response.raise_for_status()
    data = response.json()
    return data['access_token']


def getDurationURL(startime="2026-05-29T00:00:00Z",
                   endtime="2026-05-30T23:55:00Z",
                   filter_str=DEFAULT_FILTER):
    url = "https://" + domain + "/search/v2/events"

    payload = {
        "limit": 922337200,
        "distinct": True,
        "fields": ["time", "end_time", "url"],
        "startTime": startime,
        "endTime": endtime,
        "filter": filter_str
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Bearer " + str(bearToken())
    }

    response = requests.post(url, json=payload, headers=headers, verify=False)
    response.raise_for_status()
    data = response.json()
    rows = data.get('rows', [])
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["time", "end_time", "url", "duration"])
    # Exabeam returns time / end_time as epoch milliseconds; duration in ms.
    df['duration'] = df['end_time'] - df['time']
    return df


if __name__ == "__main__":
    hour = 5
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=hour)
    start_formatted = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_formatted = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    df = getDurationURL(start_formatted, end_formatted)
    df.to_csv('time-betsoft.csv', index=False, encoding='utf-8')
