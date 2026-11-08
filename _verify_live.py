import re, urllib.request

BASE = "https://blog-imxiaohe.pages.dev"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0"}

def get(path):
    r = urllib.request.urlopen(urllib.request.Request(BASE + path, headers=UA), timeout=30)
    return r.status, r.read()

posts_to_check = ["/posts/2025/11/cloudflare/", "/posts/2026/11/123_0411195847/", "/posts/2025/10/hy2/", "/pages/"]
all_ok = True
for path in posts_to_check:
    s, data = get(path)
    html = data.decode("utf-8", "ignore")
    srcs = re.findall(r'src="(/assets/img/[^"]+)"', html)
    broken = []
    for src in srcs:
        try:
            s2, _ = get(src)
            if s2 != 200:
                broken.append((src, s2))
        except Exception as e:
            broken.append((src, str(e)))
    status = "OK" if not broken else f"BROKEN {broken}"
    print(f"{path}: page={s} imgs={len(srcs)} -> {status}")
    if broken:
        all_ok = False

print("ALL_OK" if all_ok else "HAS_ERRORS")