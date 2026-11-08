import base64, json, os, urllib.request, zipfile

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
TMP = "C:/Users/heg01/AppData/Local/Temp/web-design-skill"
os.makedirs(TMP, exist_ok=True)

def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()

# 1) SKILL.md via API (base64)
d = json.loads(get("https://api.github.com/repos/xiaopu-ai/web-design/contents/SKILL.md"))
open(os.path.join(TMP, "SKILL.md"), "w", encoding="utf-8").write(base64.b64decode(d["content"]).decode("utf-8"))
print("SKILL.md:", len(base64.b64decode(d["content"])), "bytes")

# 2) full repo zipball
zb = get("https://codeload.github.com/xiaopu-ai/web-design/zip/refs/heads/main")
zpath = os.path.join(TMP, "repo.zip")
open(zpath, "wb").write(zb)
with zipfile.ZipFile(zpath) as z:
    z.extractall(TMP)
print("zip extracted:", len(zb), "bytes")
print(os.listdir(TMP))