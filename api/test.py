import requests
import json

URL = "http://127.0.0.1:5000"

def post(sub):
    return requests.post(f"{URL}{sub}")

def get(sub):
    return requests.get(f"{URL}{sub}")

def pc(req): # print content
    print(json.dumps(json.loads(req.content), indent=4))

# pc(post("/counter/create?name=bongus"))
# pc(get("/counter/get?names=bingus,bongus"))

# for i in range(5):
#     pc(post("/counter/heartbeat?name=bingus"))
# for i in range(2):
#     pc(post("/counter/heartbeat?name=bongus"))

# pc(get("/counter/get?names=bingus,bongus"))

while True:
    fun = input("")
    if fun == "h":
        pc(post("/counter/heartbeat?name=bongus"))
    if fun == "j":
        pc(post("/counter/heartbeat?name=bingus"))
    if fun == "k":
        pc(get("/counter/get?names=bingus,bongus"))
    if fun.startswith("c"):
        pc(post(f"/counter/create?name={fun.split( )[1]}&key=erm"))
    