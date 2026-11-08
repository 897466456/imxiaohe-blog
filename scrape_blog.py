#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migrate blog.imxiaohe.com (Blogger) -> clean static site in public/."""
import hashlib, html, json, os, re, sys, urllib.parse, urllib.request
from datetime import datetime, timezone

BLOG = "https://blog.imxiaohe.com"
SITE_URL = "https://blog-imxiaohe.pages.dev"  # updated after Cloudflare deploy
SITE_TITLE = "晓鹤的博客"
SITE_SUBTITLE = "技术 · 分享 · 生活"
PUBLIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
IMG_DIR = os.path.join(PUBLIC, "assets", "img")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)

def get_feeds():
    pf, gf = "_feeds_posts.json", "_feeds_pages.json"
    if os.path.exists(pf) and os.path.exists(gf):
        with open(pf, encoding="utf-8") as f: posts = json.load(f)
        with open(gf, encoding="utf-8") as f: pages = json.load(f)
        print("using cached feeds")
        return posts, pages
    posts = fetch(f"{BLOG}/feeds/posts/default?alt=json&max-results=500")
    pages = fetch(f"{BLOG}/feeds/pages/default?alt=json&max-results=500")
    with open(pf, "w", encoding="utf-8") as f: json.dump(posts, f, ensure_ascii=False)
    with open(gf, "w", encoding="utf-8") as f: json.dump(pages, f, ensure_ascii=False)
    print("feeds refreshed")
    return posts, pages

def entry_data(e):
    title = e["title"]["$t"]
    url = next((l["href"] for l in e["link"] if l.get("rel") == "alternate"), "")
    slug = urllib.parse.urlparse(url).path.rstrip("/").lstrip("/")
    if slug.endswith(".html"): slug = slug[:-5]
    published = e["published"]["$t"]
    labels = [c["term"] for c in e.get("category", [])]
    content = e["content"]["$t"] if "content" in e else e.get("summary", {}).get("$t", "")
    return dict(title=title, slug=slug, published=published,
                labels=labels, content=content, url=url)

# ---------- image handling ----------
IMG_RE = re.compile(r'https://blogger\.googleusercontent\.com/[^"\'\s)]+')
SIZE_RE = re.compile(r'/(?:w\d+(?:-h\d+)?(?:-p-k-no-nu)?|s\d+(?:-c)?|h\d+|w\d+-h\d+)(?=/)')

def canonical_img(url):
    u = url.split("?")[0]
    if SIZE_RE.search(u):
        u = SIZE_RE.sub("/s0", u)
    return u

img_map = {}  # canonical url -> local path

def localize(url):
    can = canonical_img(url)
    if can not in img_map:
        fn = None
        try:
            base = os.path.basename(urllib.parse.urlparse(can).path)
            base = urllib.parse.unquote(base)
            ext = os.path.splitext(base)[1].lower()
            if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".svg", ".bmp"):
                ext = ""
            h = hashlib.sha1(can.encode()).hexdigest()[:12]
            fn = f"{h}{ext or '.img'}"
            dest = os.path.join(IMG_DIR, fn)
            if not os.path.exists(dest):
                req = urllib.request.Request(can, headers=UA)
                with urllib.request.urlopen(req, timeout=120) as r:
                    data = r.read()
                if not ext:
                    ctype = r.headers.get("Content-Type", "")
                    m = re.search(r'image/(\w+)', ctype)
                    if m:
                        fn = f"{h}.{m.group(1).replace('jpeg','jpg')}"
                        dest = os.path.join(IMG_DIR, fn)
                with open(dest, "wb") as f: f.write(data)
                print(f"  img: {fn} ({len(data)//1024} KB)")
            img_map[can] = f"/assets/img/{fn}"
        except Exception as ex:
            print(f"  img FAIL {can[:80]}... : {ex}")
            img_map[can] = url  # keep original remote url as fallback
    return img_map[can]

def process_content(c):
    # drop srcset entirely (we serve a single optimized image per asset)
    c = re.sub(r'\ssrcset="[^"]*"', "", c)
    c = re.sub(r'\sdata-src="[^"]*"', "", c)
    c = re.sub(r'\ssizes="[^"]*"', "", c)
    def rep(m):
        u = m.group(0)
        return f'assets/img/{localize(u)}'
    # rewrite src= and poster= references
    def rep_src(m):
        return m.group(1) + '="' + localize(m.group(2)) + '"'
    c = re.sub(r'(src|poster)="(https://blogger\.googleusercontent\.com/[^"]+)"', rep_src, c)
    # any remaining bare references (href/css) -> local path
    c = IMG_RE.sub(lambda m: localize(m.group(0)), c)
    return c

# ---------- templating ----------
def esc(s): return html.escape(s, quote=True)

def fmt_date(iso):
    try:
        d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return d.strftime("%Y-%m-%d")
    except Exception:
        return iso[:10]

CSS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.css"), encoding="utf-8").read()

PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="/assets/css/style.css">
<link rel="alternate" type="application/rss+xml" title="{site}" href="/rss.xml">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/">{site}</a>
    <nav><a href="/">首页</a>{nav_pages}<a href="/rss.xml">RSS</a></nav>
  </div>
</header>
<main class="wrap">
{body}
</main>
<footer class="site-footer">
  <div class="wrap"><p>{site} · 由 Blogger 迁移 · <a href="https://github.com/897466456/imxiaohe-blog">GitHub</a></p></div>
</footer>
<script>
(function() {{
  var els = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window)) {{
    els.forEach(function(e) {{ e.classList.add('visible'); }});
    return;
  }}
  var io = new IntersectionObserver(function(entries) {{
    entries.forEach(function(en) {{
      if (en.isIntersecting) {{
        en.target.classList.add('visible');
        io.unobserve(en.target);
      }}
    }});
  }}, {{ threshold: 0.1 }});
  els.forEach(function(e, i) {{
    e.style.transitionDelay = (i % 6) * 60 + 'ms';
    io.observe(e);
  }});
}})();
</script>
</body>
</html>"""

def render(title, body, desc="", nav_pages=""):
    return PAGE.format(title=title, desc=esc(desc), site=SITE_TITLE, nav_pages=nav_pages, body=body, gh="GitHub")

def post_card(p, featured=False):
    labels = "".join(f'<a class="tag" href="/tags/{esc(urllib.parse.quote(t))}/">{esc(t)}</a>' for t in p["labels"])
    cls = "post-card reveal" + (" featured" if featured else "")
    img = ""
    m = re.search(r'<img[^>]+src="(/assets/img/[^"]+)"', p["content"])
    if m:
        img = f'<img class="card-img" src="{esc(m.group(1))}" loading="lazy" alt="">'
    return f"""<article class="{cls}">
  {img}
  <h2><a href="/posts/{p['slug']}/">{esc(p['title'])}</a></h2>
  <div class="meta"><time>{fmt_date(p['published'])}</time>{labels}</div>
  <p class="excerpt">{esc(html.unescape(re.sub(r'<[^>]+>', ' ', p['content']))[:160])}</p>
</article>"""

def main():
    posts_feed, pages_feed = get_feeds()
    # copy stylesheet into public/assets/css/
    css_dir = os.path.join(PUBLIC, "assets", "css")
    os.makedirs(css_dir, exist_ok=True)
    open(os.path.join(css_dir, "style.css"), "w", encoding="utf-8").write(CSS)
    posts = [entry_data(e) for e in posts_feed["feed"].get("entry", [])]
    pages = [entry_data(e) for e in pages_feed["feed"].get("entry", [])]
    posts.sort(key=lambda p: p["published"], reverse=True)
    os.makedirs(IMG_DIR, exist_ok=True)

    print(f"processing {len(posts)} posts, {len(pages)} pages...")
    for i, p in enumerate(posts, 1):
        p["content"] = process_content(p["content"])
        print(f"[{i}/{len(posts)}] {p['title'][:40]}")
    for p in pages:
        p["content"] = process_content(p["content"])

    nav_pages = "".join(f'<a href="/pages/{esc(p["slug"])}/">{esc(p["title"])}</a>' for p in pages[:4])

    # ---------- index (paginated 15) ----------
    per = 15
    n = len(posts)
    nidx = (n + per - 1) // per
    for idx in range(nidx):
        chunk = posts[idx*per:(idx+1)*per]
        cards = "".join(post_card(p) for p in chunk)
        if idx == 0:
            cards = "".join(post_card(p, featured=(i == 0)) for i, p in enumerate(chunk))
            body = f'<h1 class="page-title">最新文章</h1>\n<div class="post-list">{cards}</div>\n' + pager(idx, nidx)
            open(os.path.join(PUBLIC, "index.html"), "w", encoding="utf-8").write(render(f"{SITE_TITLE} · {SITE_SUBTITLE}", body, desc=SITE_SUBTITLE, nav_pages=nav_pages))
        else:
            d = os.path.join(PUBLIC, "page", str(idx+1)); os.makedirs(d, exist_ok=True)
            cards = "".join(post_card(p) for p in chunk)
            body = f'<h1 class="page-title">最新文章</h1>\n<div class="post-list">{cards}</div>\n' + pager(idx, nidx)
            open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(render(f"第 {idx+1} 页 · {SITE_TITLE}", body, nav_pages=nav_pages))

    # ---------- posts ----------
    for p in posts:
        d = os.path.join(PUBLIC, "posts", p["slug"]); os.makedirs(d, exist_ok=True)
        labels = "".join(f'<a class="tag" href="/tags/{esc(urllib.parse.quote(t))}/">{esc(t)}</a>' for t in p["labels"])
        body = f"""<article class="post">
  <h1 class="post-title">{esc(p['title'])}</h1>
  <div class="meta"><time>{fmt_date(p['published'])}</time>{labels}</div>
  <div class="content">{p['content']}</div>
</article>
<nav class="post-nav"><a href="/">← 返回首页</a></nav>"""
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(render(f"{esc(p['title'])} · {SITE_TITLE}", body, desc=re.sub(r"<[^>]+>", " ", p["content"])[:120], nav_pages=nav_pages))

    # ---------- pages ----------
    for p in pages:
        d = os.path.join(PUBLIC, "pages", p["slug"]); os.makedirs(d, exist_ok=True)
        body = f'<article class="post"><h1 class="post-title">{esc(p["title"])}</h1>\n<div class="content">{p["content"]}</div></article>'
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(render(f"{esc(p['title'])} · {SITE_TITLE}", body, nav_pages=nav_pages))

    # ---------- tags ----------
    tagmap = {}
    for p in posts:
        for t in p["labels"]:
            tagmap.setdefault(t, []).append(p)
    for t, ps in tagmap.items():
        d = os.path.join(PUBLIC, "tags", t); os.makedirs(d, exist_ok=True)
        cards = "".join(post_card(p) for p in ps)
        body = f'<h1 class="page-title">标签：{esc(t)}</h1>\n<div class="post-list">{cards}</div>'
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(render(f"标签 {esc(t)} · {SITE_TITLE}", body, nav_pages=nav_pages))

    # ---------- 404 / robots / sitemap / rss ----------
    open(os.path.join(PUBLIC, "404.html"), "w", encoding="utf-8").write(render("页面不存在 · " + SITE_TITLE, "<h1>404</h1><p>页面不存在或已被移动。<a href='/'>返回首页</a></p>", nav_pages=nav_pages))
    open(os.path.join(PUBLIC, "robots.txt"), "w", encoding="utf-8").write("User-agent: *\nAllow: /\n\nSitemap: /sitemap.xml\n")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in ["/"] + [f"/posts/{p['slug']}/" for p in posts] + [f"/pages/{p['slug']}/" for p in pages] + [f"/tags/{t}/" for t in tagmap]:
        sm.append(f"<url><loc>{SITE_URL}{u}</loc><lastmod>{now}</lastmod></url>")
    sm.append("</urlset>")
    open(os.path.join(PUBLIC, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sm))

    rss_items = []
    for p in posts[:20]:
        rss_items.append(f"""<item><title>{esc(p['title'])}</title><link>{SITE_URL}/posts/{esc(p['slug'])}/</link><guid>{SITE_URL}/posts/{esc(p['slug'])}/</guid><pubDate>{p['published'].replace('Z','+0000')}</pubDate><description>{esc(html.unescape(re.sub(r'<[^>]+>',' ',p['content']))[:400])}</description></item>""")
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>{esc(SITE_TITLE)}</title><link>{SITE_URL}/</link><description>{esc(SITE_SUBTITLE)}</description>
{chr(10).join(rss_items)}
</channel></rss>"""
    open(os.path.join(PUBLIC, "rss.xml"), "w", encoding="utf-8").write(rss)

    total_img = sum(1 for f in os.listdir(IMG_DIR) if os.path.isfile(os.path.join(IMG_DIR, f)))
    print(f"\nDONE: {len(posts)} posts, {len(pages)} pages, {total_img} images")

def pager(cur, total):
    if total <= 1: return ""
    links = []
    for i in range(total):
        if i == cur: links.append(f"<span class='page-cur'>{i+1}</span>")
        elif i == 0: links.append(f"<a href='/'>1</a>")
        else: links.append(f"<a href='/page/{i+1}/'>{i+1}</a>")
    return f'<nav class="pager">{("".join(links))}</nav>'

if __name__ == "__main__":
    main()