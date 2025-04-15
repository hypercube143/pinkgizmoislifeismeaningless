from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import datetime
import os
from zoneinfo import ZoneInfo

TIME_ZONE = "Pacific/Auckland" # "Antarctica/McMurdo"

PASSWORD = "erm"

API_DIR = "api"
os.makedirs(API_DIR, exist_ok=True)
DATA_DIR = f"{API_DIR}/data"
os.makedirs(DATA_DIR, exist_ok=True)
COUNTS_DIR = f"{DATA_DIR}/counts"
os.makedirs(COUNTS_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app)

# Main page. Documentation should be displayed here if ever
@app.route("/")
def index():
    return render_template("index.html"), 200


def time_elapsed(now_timestamp, start_timestmap, dt_expected):
    return (now_timestamp - start_timestmap) >= dt_expected


# Create counter object
@app.route("/counter/create", methods=['POST'])
def count_create():
    name = request.args.get("name")
    p = request.args.get("key")
    if p != PASSWORD:
        return {"res": "You clearly have a lot of free time. Go do something productive :p"}
    time_now = datetime.datetime.now()
    time_now_timestamp = time_now.timestamp()

    tz = ZoneInfo(TIME_ZONE)
    dt = datetime.datetime.fromtimestamp(time_now_timestamp, tz)
    
    minute_start = dt.replace(second=0, microsecond=0)
    hour_start = dt.replace(minute=0, second=0, microsecond=0)
    day_start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = day_start - datetime.timedelta(days=day_start.weekday())
    month_start = day_start.replace(day=1)
    if dt.month <= 5:
        six_months_start = dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        six_months_start = dt.replace(month=6, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Calculate the start of the year.
    year_start = dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    try:
        with open(f"{COUNTS_DIR}/{name}.json", "x") as f:
            data = {
                "name": name,
                "timestamp-last-count": time_now_timestamp,
                "timestamp-created": time_now_timestamp,
                "count": 0,
                "count-minute": 0,
                "timestamp-cm-last-reset": minute_start.timestamp(),
                "count-hour": 0,
                "timestamp-ch-last-reset": hour_start.timestamp(),
                "count-day": 0,
                "timestamp-cd-last-reset": day_start.timestamp(),
                "count-week": 0,
                "timestamp-cw-last-reset": week_start.timestamp(),
                "count-month": 0,
                "timestamp-cmo-last-reset": month_start.timestamp(),
                "count-month-6": 0,
                "timestamp-cmo6-last-reset": six_months_start.timestamp(),
                "count-year": 0,
                "timestamp-cy-last-reset": year_start.timestamp()
                }
            json.dump(data, f, indent=4)
    except FileExistsError:
        res = jsonify({"res": f"'{name}' counter already exists"})
        res.headers.add('Access-Control-Allow-Origin', '*')
        return res, 418
    res = jsonify({"res": f"'{name}' counter successfully created"})
    res.headers.add('Access-Control-Allow-Origin', '*')
    return res, 200


def update_counter(name, amount=1):
    time_now = datetime.datetime.now()
    tsn = time_now.timestamp() # timestamp now

    with open(f"{COUNTS_DIR}/{name}.json", "r") as f:
         data = json.loads(f.read())

    data["count"] += amount
    # amount 0 is used only for updating reset times and reset values
    if amount > 0:
        data["timestamp-last-count"] = tsn
    # if an hour has passed, reset hour counter then add, etc, etc
    if time_elapsed(tsn, data["timestamp-ch-last-reset"], 3600):
        data["timestamp-ch-last-reset"] = tsn
        data["count-hour"] = 0
    data["count-hour"] += amount
    # minute
    if time_elapsed(tsn, data["timestamp-cm-last-reset"], 60):
        data["timestamp-cm-last-reset"] = tsn
        data["count-minute"] = 0
    data["count-minute"] += amount
    # day
    if time_elapsed(tsn, data["timestamp-cd-last-reset"], 86400):
        data["timestamp-cd-last-reset"] = tsn
        data["count-day"] = 0
    data["count-day"] += amount
    # week
    if time_elapsed(tsn, data["timestamp-cw-last-reset"], 604800):
        data["timestamp-cw-last-reset"] = tsn
        data["count-week"] = 0
    data["count-week"] += amount
    # month
    if time_elapsed(tsn, data["timestamp-cmo-last-reset"], 2.628e+6):
        data["timestamp-cmo-last-reset"] = tsn
        data["count-month"] = 0
    data["count-month"] += amount
    # 6 months
    if time_elapsed(tsn, data["timestamp-cmo6-last-reset"], 2.628e+6 * 6):
        data["timestamp-cmo6-last-reset"] = tsn
        data["count-month-6"] = 0
    data["count-month-6"] += amount
    # year
    if time_elapsed(tsn, data["timestamp-cy-last-reset"], 3.154e+7):
        data["timestamp-cy-last-reset"] = tsn
        data["count-year"] = 0
    data["count-year"] += amount

    with open(f"{COUNTS_DIR}/{name}.json", "w") as f:
        json.dump(data, f, indent=4)


@app.route("/counter/heartbeat", methods=["POST"])
def count_heartbeat():
    name = request.args.get("name")
    try:
        update_counter(name, 1)
    except FileNotFoundError:
        res = jsonify({"res": f"'{name}' counter does not exist"})
        res.headers.add('Access-Control-Allow-Origin', '*')
        return res, 404
    res = jsonify({"res": f"heart beat for '{name}'"})
    res.headers.add('Access-Control-Allow-Origin', '*')
    return res, 200


@app.route("/counter/get", methods=["GET"])
def count_get():
    names = request.args.get("names")

    final_data = {}
    
    try:
        for name in names.split(","):
            update_counter(name, 0)
            with open(f"{COUNTS_DIR}/{name}.json", "r") as f:
                data = json.loads(f.read())
            trimmed_data = {
                "timestamp-last-count": data["timestamp-last-count"],
                "timestamp-created": data["timestamp-created"],
                "count": data["count"],
                "count-minute": data["count-minute"],
                "count-hour": data["count-hour"],
                "count-day": data["count-day"],
                "count-week": data["count-week"],
                "count-month": data["count-month"],
                "count-month-6": data["count-month-6"],
                "count-year": data["count-year"]
            }
            final_data[name] = trimmed_data

    except FileNotFoundError:
        res = jsonify({"res": f"'{name}' counter does not exist"})
        res.headers.add('Access-Control-Allow-Origin', '*')
        return res, 404
    res = jsonify(final_data)
    res.headers.add('Access-Control-Allow-Origin', '*')
    return res, 200

app.run()