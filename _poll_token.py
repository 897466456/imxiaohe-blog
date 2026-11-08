import json, time, urllib.request, urllib.parse, sys

DEVICE_CODE = "fa155a01a4fd25ed4c6c5ea104d54aee5d841cf1"
CLIENT_ID = "178c6fc778ccc68e1d6a"
OUT = "C:/Users/heg01/imxiaohe-blog/_gh_token.txt"

deadline = time.time() + 860
while time.time() < deadline:
    body = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "device_code": DEVICE_CODE,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
    }).encode()
    req = urllib.request.Request("https://github.com/login/oauth/access_token", data=body,
                                 headers={"Accept": "application/json", "User-Agent": "x"})
    try:
        d = json.load(urllib.request.urlopen(req, timeout=20))
        if "access_token" in d:
            with open(OUT, "w") as f:
                f.write(d["access_token"])
            print("TOKEN_OK")
            sys.exit(0)
        if "error" in d and d["error"] == "authorization_pending":
            pass
        else:
            print("ERR", json.dumps(d)[:200])
    except Exception as e:
        print("NETERR", e)
    time.sleep(5)
print("TIMEOUT")
sys.exit(1)