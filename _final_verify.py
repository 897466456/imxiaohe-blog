import json, re, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0"}
BASE = "https://blog-imxiaohe.pages.dev"

def get(url, headers=None):
    h = dict(UA)
    if headers:
        h.update(headers)
    return urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=30)

# 1) live footer link
html = get(BASE + "/").read().decode("utf-8", "ignore")
m = re.search(r'github\.com/[^"<]+', html)
print("live footer github link:", m.group(0) if m else "NOT FOUND")

# 2) live post page images
html = get(BASE + "/posts/2026/11/123_0411195847/").read().decode("utf-8", "ignore")
srcs = re.findall(r'src="(/assets/img/[^"]+)"', html)
ok = all(get(BASE + s).status == 200 for s in srcs)
print(f"post images: {len(srcs)} refs, all 200: {ok}")

# 3) remote repo state (public repo, no auth needed)
repo = json.load(get("https://api.github.com/repos/897466456/imxiaohe-blog"))
print("remote default branch:", repo["default_branch"])
scr = json.load(get("https://api.github.com/repos/897466456/imxiaohe-blog/contents/scrape_blog.py"))
import base64
txt = base64.b64decode(scr["content"]).decode()
print("script has /assets/img/ fix:", 'img_map[can] = f"/assets/img/{fn}"' in txt)
head = json.load(get("https://api.github.com/repos/897466456/imxiaohe-blog/git/ref/heads/main"))
print("remote head:", head["object"]["sha"][:8])