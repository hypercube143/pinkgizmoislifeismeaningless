from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import datetime
import os
from zoneinfo import ZoneInfo
import weird_ai as evil_ai
import random
from evil_util import *

app = Flask(__name__)
CORS(app)

# Main page. Documentation should be displayed here if ever
@app.route("/")
def index():
    return render_template("index.html"), 200


@app.route("/counter/create", methods=['POST'])
def count_create():
    name = request.args.get("name")
    p = request.args.get("key")

    if p != get_config_value("admin-password"):
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
        content = f.read()

    try:
        data = json.loads(content)
    except json.decoder.JSONDecodeError:
        # sometimes an extra } is added to the end of this file... whyyy
        fixed_content = content[:-1]
        data = json.loads(fixed_content)

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


@app.route("/oracle/y-o-n", methods=["POST", "GET"])
def oracle_y_o_n():
    time_now = datetime.datetime.now()
    tsn = time_now.timestamp() # timestamp now
    query = request.args.get("query")

    print(query)

    with open(f"{ORACLE_DIR}/y-o-n.json", "r") as f:
        data = json.loads(f.read())

    # remove all cached questions that have expired
    expire_time = 86400 # 86400 # 1 day (to prevent cached questions from flooding the server)
    to_remove = []
    for q in data:
        if time_elapsed(tsn, q["ts"], expire_time):
            to_remove.append(q)
    for r in to_remove:
        data.remove(r)

    # add question-mark to query & remove trailing whitespace if not already to help the silly ai
    query = query.strip()
    if not query.endswith("?"):
        query += "?"
    
    # do ai thing here
    gemini_key = get_config_value("gemini-api-key")
    o_b = "{"
    c_b = "}"
    full_prompt = f"""
    you are to determine whether a question is a yes or no question, and whether it exists in the list below (by semantic meaning)

    your response must be in a json format like so:
    {o_b}"cached": true, "valid": true{c_b}
    this is an example of a query which is:
    cached: in the list 
    valid: is a valid yes or no question

    if cached, return an extra parameter "index" which is equal to the index of the cached query from the list that best matches the current query

    extra notes:
    - you must retain logical consistency: if the user asks if the sky is red and a cached query asks if the sky was blue and the result was yes, then the sky cannot be red
      if you encounter a question that asks of the opposite of a cached question, your response must be the opposite of its yes-or-no value
      thus, any 'reverse' question / related negative question should count as being cached
    - your final output MUST only contain json

    QUERY: "{query}"

    LIST: {[{"query": x["q"], "yes-or-no": x["yn"]}for x in data]}
    """
    res = evil_ai.prompt(full_prompt, "gemini-2.0-flash", gemini_key)
    # if res.startswith("```json"):
    res = res.replace("```json", "")
    # if res.endswith("```"):
    res = res.replace("```", "") # this will cause errors if user query contains ``` etc :c
    print(res)

    res_json = json.loads(res)

    # valid question, not cached
    if res_json["valid"] and not res_json["cached"]:
        fate = random.choice(["yes", "no"])
        data.append({"q": query, "ts": tsn, "yn": fate})
        with open(f"{ORACLE_DIR}/y-o-n.json", "w") as f:
            json.dump(data, f, indent=4)
        return jsonify({"fate": fate}), 200
    
    # valid question, cached
    elif res_json["valid"] and res_json["cached"]:
        # update ts
        data[res_json["index"]]["ts"] = tsn
        with open(f"{ORACLE_DIR}/y-o-n.json", "w") as f:
            json.dump(data, f, indent=4)
        fate = data[res_json["index"]]["yn"]
        return jsonify({"fate": fate}), 200

    # invalid question
    elif not res_json["valid"]:
        return jsonify({"res": "not a yes or no question"}), 400


@app.route("/status/update", methods=["POST", "GET"])
def status_update():
    headers = request.headers
    data = json.loads(request.data)

    print(headers)
    print(data)

    if headers["key"] != get_config_value("admin-password"):
        return jsonify({"res": "you cannot do that :p"}), 403
    
    time_now = datetime.datetime.now()
    tsn = time_now.timestamp() # timestamp now
    
    with open(f"{STATUS_DIR}/current-status.json", "w") as f:
        new_data = {
            "status-id": data["status-id"],
            "status-message": data["status-message"],
            "timestamp": tsn
        }
        json.dump(new_data, f, indent=4)

    return jsonify({"res": "successfully updated status :p"})


@app.route("/status/get", methods=["GET"])
def status_get():

    with open(f"{STATUS_DIR}/current-status.json", "r", encoding="utf-8") as f:
        data = json.loads(f.read())
    
    return data, 200


app.run()