#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_bot.py — 内容核对机器人：比对 Blogger 原文与迁移后的静态站。

用法:
  python verify_bot.py                # local   : 缓存的原文 feeds vs public/ 生成站
  python verify_bot.py --mode live    # live    : 重新抓取 blog.imxiaohe.com vs public/，
                                      #           并显示原文自缓存以来新增/修改/删除的内容
  python verify_bot.py --mode remote  # remote  : 缓存的原文 vs 已部署的 blog-imxiaohe.pages.dev

输出: 控制台摘要 + verify_report.md / verify_report.json
退出码: 0 = 全部通过, 1 = 存在问题（适合 cron 定时任务判断）
"""
import hashlib, html as H, json, os, re, sys, urllib.parse, urllib.request
from datetime import datetime, timezone
from difflib import SequenceMatcher

import scrape_blog as S

BASE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(BASE, "public")
IMG_DIR = os.path.join(PUBLIC, "assets", "img")
LIVE_URL = "https://blog-imxiaohe.pages.dev"
ORIGIN = "https://blog.imxiaohe.com"
CACHE_P = os.path.join(BASE, "_feeds_posts.json")
CACHE_G = os.path.join(BASE, "_feeds_pages.json")
LIVE_P = os.path.join(BASE, "_live_posts.json")
LIVE_G = os.path.join(BASE, "_live_pages.json")
SIM_FAIL = 0.95   # 正文文本相似度低于此值判为失败
SIM_WARN = 0.99   # 低于此值给警告

def load_feeds(pp, gp):
    posts = [S.entry_data(e) for e in json.load(open(pp, encoding="utf-8"))["feed"].get("entry", [])]
    pages = [S.entry_data(e) for e in json.load(open(gp, encoding="utf-8"))["feed"].get("entry", [])]
    return posts, pages

def total_in(pp):
    f = json.load(open(pp, encoding="utf-8"))["feed"]
    try:
        return int(f["openSearch$totalResults"]["$t"])
    except Exception:
        return None

def text_of(frag):
    t = re.sub(r"<[^>]+>", " ", frag)
    t = H.unescape(t)
    return re.sub(r"\s+", " ", t).strip()

def extract_generated(page_html):
    """从生成页提取 (title, date, content_html)。"""
    t = re.search(r'<h1 class="post-title">(.*?)</h1>', page_html, re.S)
    title = H.unescape(t.group(1)).strip() if t else ""
    d = re.search(r'<div class="meta"><time>(.*?)</time>', page_html, re.S)
    date = d.group(1).strip() if d else ""
    c0 = page_html.find('<div class="content">')
    c1 = page_html.find("</article>")
    content = page_html[c0 + len('<div class="content">'):c1] if c0 >= 0 and c1 > c0 else ""
    return title, date, content

def orig_img_urls(content):
    return S.IMG_RE.findall(content)

def expected_stem(canon_url):
    return hashlib.sha1(canon_url.encode()).hexdigest()[:12]

def find_img_file(stem):
    if not os.path.isdir(IMG_DIR):
        return None
    for fn in os.listdir(IMG_DIR):
        if fn.startswith(stem + "."):
            return fn
    return None

def fetch_page(url):
    req = urllib.request.Request(url, headers=S.UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode("utf-8", "replace"), r.status

class Verifier:
    def __init__(self, mode):
        self.mode = mode
        self.issues = []       # (level, item, msg)
        self.stats = {}

    def check(self, ok, item, msg):
        if not ok:
            self.issues.append(("FAIL", item, msg))
        return ok

    def warn(self, item, msg):
        self.issues.append(("WARN", item, msg))

    # ---------- 通用检查 ----------
    def check_article(self, kind, p, local_html=None, remote_html=None, expect_date=True):
        """核对单篇文章：标题、日期、图片、正文相似度。local_html/remote_html 至少给一个。
        expect_date=False 用于页面（生成站刻意不渲染日期）。"""
        item = f"{kind}/{p['slug']}"
        for html in (local_html, remote_html):
            if html is None:
                continue
            title, date, content = extract_generated(html)
            self.check(title.strip() == p["title"].strip(), item,
                       f"标题不一致: 原文[{p['title'][:40]}] vs 生成[{title[:40]}]")
            want_date = p["published"][:10] if expect_date else ""
            self.check(date == want_date, item, f"日期不一致: 原文[{p['published'][:10]}] vs 生成[{date}]")
            if content:
                sim = SequenceMatcher(None, text_of(p["content"]), text_of(content)).ratio()
                if sim < SIM_FAIL:
                    self.check(False, item, f"正文相似度 {sim:.4f} < {SIM_FAIL}")
                elif sim < SIM_WARN:
                    self.warn(item, f"正文相似度 {sim:.4f}（轻微差异）")
            # 图片：原文每个图 URL -> 本地文件必须存在
            local_refs = re.findall(r'/assets/img/[^"&]+', content)
            local_refs = [r for r in local_refs if re.fullmatch(r'/assets/img/[A-Za-z0-9_.-]+', r)]
            local_refs = list(dict.fromkeys(local_refs))
            for u in orig_img_urls(p["content"]):
                can = S.canonical_img(u)
                stem = expected_stem(can)
                fn = find_img_file(stem)
                if fn is None:
                    self.check(False, item, f"图片缺失: {can[:90]}")
                elif f"/assets/img/{fn}" not in local_refs:
                    self.warn(item, f"图片未在页面引用: {fn}（{can[:70]}…）")
            # 生成页引用的本地图片文件必须存在
            for ref in local_refs:
                self.check(os.path.isfile(os.path.join(PUBLIC, ref.lstrip("/"))),
                           item, f"生成页引用了不存在的图片: {ref}")
            # 外链残留
            self.check("blogger.googleusercontent.com" not in content and ORIGIN not in content,
                       item, "生成正文仍含原文外链")

    def check_tag_pages(self, posts):
        tagmap = {}
        for p in posts:
            for t in p["labels"]:
                tagmap.setdefault(t, 0)
                tagmap[t] += 1
        for t in tagmap:
            d = os.path.join(PUBLIC, "tags", t)
            self.check(os.path.isfile(os.path.join(d, "index.html")),
                       f"tags/{t}", "标签页缺失")

    def check_index_and_feeds(self, posts, pages):
        # 首页分页覆盖全部文章
        n_cards = 0
        for f in [os.path.join(PUBLIC, "index.html")] + \
                 [os.path.join(PUBLIC, "page", str(i), "index.html")
                  for i in range(2, 100) if os.path.isdir(os.path.join(PUBLIC, "page", str(i)))]:
            if os.path.isfile(f):
                n_cards += open(f, encoding="utf-8").read().count('class="post-card')
        self.check(n_cards == len(posts), "index", f"首页卡片 {n_cards} != 文章数 {len(posts)}")
        # sitemap 覆盖全部文章/页面/标签
        if os.path.isfile(os.path.join(PUBLIC, "sitemap.xml")):
            sm = open(os.path.join(PUBLIC, "sitemap.xml"), encoding="utf-8").read()
            missing = [p["slug"] for p in posts if f"/posts/{p['slug']}/" not in sm]
            missing += [p["slug"] for p in pages if f"/pages/{p['slug']}/" not in sm]
            self.check(not missing, "sitemap.xml", f"缺少 {len(missing)} 条: {missing[:5]}")
        # RSS 前 20 篇
        if os.path.isfile(os.path.join(PUBLIC, "rss.xml")):
            rss = open(os.path.join(PUBLIC, "rss.xml"), encoding="utf-8").read()
            want = min(20, len(posts))
            self.check(rss.count("<item>") == want, "rss.xml",
                       f"RSS 条目 {rss.count('<item>')} != 期望 {want}")

    # ---------- 各模式 ----------
    def run_local(self, posts, pages):
        self.stats["posts"] = len(posts)
        self.stats["pages"] = len(pages)
        for p in posts:
            f = os.path.join(PUBLIC, "posts", p["slug"], "index.html")
            if not self.check(os.path.isfile(f), f"posts/{p['slug']}", "文章页缺失"):
                continue
            self.check_article("posts", p, local_html=open(f, encoding="utf-8").read())
        for p in pages:
            f = os.path.join(PUBLIC, "pages", p["slug"], "index.html")
            if not self.check(os.path.isfile(f), f"pages/{p['slug']}", "页面缺失"):
                continue
            self.check_article("pages", p, local_html=open(f, encoding="utf-8").read(), expect_date=False)
        # 生成站里多余的目录（排除属于文章路径的父目录，如 2026/、2026/04/）
        if os.path.isdir(os.path.join(PUBLIC, "posts")):
            slugs = {p["slug"] for p in posts}
            parts = {tuple(s.split("/")[:i]) for s in slugs for i in range(1, len(s.split("/")))}
            for d in os.listdir(os.path.join(PUBLIC, "posts")):
                if (d,) in parts:
                    continue
                if d not in slugs:
                    self.warn("posts/" + d, "生成站有多余目录（原文中不存在）")
        self.check_tag_pages(posts)
        self.check_index_and_feeds(posts, pages)
        # 图片总量
        self.stats["images"] = len([f for f in os.listdir(IMG_DIR) if os.path.isfile(os.path.join(IMG_DIR, f))]) \
            if os.path.isdir(IMG_DIR) else 0
        # 未被任何页面引用的孤儿图片
        used = set()
        for root, _dirs, files in os.walk(PUBLIC):
            for fn in files:
                if fn.endswith(".html"):
                    used |= set(re.findall(r'/assets/img/[^"&]+', open(os.path.join(root, fn), encoding="utf-8").read()))
        if os.path.isdir(IMG_DIR):
            for f in os.listdir(IMG_DIR):
                if f"/assets/img/{f}" not in used and os.path.isfile(os.path.join(IMG_DIR, f)):
                    self.warn("assets/img/" + f, "孤儿图片：没有页面引用")

    def run_live(self, posts, pages):
        print("正在重新抓取原文 feeds ...")
        fresh_posts, fresh_pages = load_feeds(LIVE_P, LIVE_G)
        print(f"原文现有 {len(fresh_posts)} 篇文章 / {len(fresh_pages)} 个页面")
        by_slug = {p["slug"]: p for p in fresh_posts}
        # 原文自缓存以来的变化
        old = {p["slug"]: p for p in posts}
        for slug, p in by_slug.items():
            if slug not in old:
                self.warn("原文", f"原文新增文章: {p['title'][:50]}")
            else:
                if old[slug]["title"] != p["title"]:
                    self.warn("原文", f"原标题变更: {p['title'][:50]}")
                if SequenceMatcher(None, text_of(old[slug]["content"]), text_of(p["content"])).ratio() < SIM_FAIL:
                    self.warn("原文", f"原文正文已修改: {p['title'][:50]}")
        for slug in old:
            if slug not in by_slug:
                self.warn("原文", f"原文已删除文章: {old[slug]['title'][:50]}")
        self.run_local(fresh_posts, fresh_pages)

    def run_remote(self, posts, pages):
        self.stats["posts"] = len(posts)
        self.stats["pages"] = len(pages)
        ok = 0
        for p in posts:
            url = f"{LIVE_URL}/posts/{p['slug']}/"
            try:
                html, status = fetch_page(url)
            except Exception as ex:
                self.check(False, f"posts/{p['slug']}", f"部署站不可达: {ex}")
                continue
            if status != 200:
                self.check(False, f"posts/{p['slug']}", f"HTTP {status}")
                continue
            ok += 1
            self.check_article("posts", p, remote_html=html)
        for p in pages:
            url = f"{LIVE_URL}/pages/{p['slug']}/"
            try:
                html, status = fetch_page(url)
            except Exception as ex:
                self.check(False, f"pages/{p['slug']}", f"部署站不可达: {ex}")
                continue
            if status != 200:
                self.check(False, f"pages/{p['slug']}", f"HTTP {status}")
                continue
            self.check_article("pages", p, remote_html=html, expect_date=False)
        self.stats["reachable"] = ok

    # ---------- 报告 ----------
    def report(self):
        fails = [i for i in self.issues if i[0] == "FAIL"]
        warns = [i for i in self.issues if i[0] == "WARN"]
        now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
        verdict = "全部通过" if not fails else f"{len(fails)} 个问题"
        head = (f"# 内容核对报告（{self.mode}）\n\n"
                f"- 时间: {now}\n- 核对对象: {ORIGIN} → {LIVE_URL}\n"
                f"- 结论: {'✅ ' + verdict if not fails else '❌ ' + verdict}\n")
        body = ["", "## 统计", ""]
        for k, v in self.stats.items():
            body.append(f"- {k}: {v}")
        if warns:
            body += ["", "## 警告", ""] + [f"- ⚠️ [{it}] {msg}" for _, it, msg in warns]
        if fails:
            body += ["", "## 问题", ""] + [f"- ❌ [{it}] {msg}" for _, it, msg in fails]
        md = head + "\n".join(body)
        open(os.path.join(BASE, "verify_report.md"), "w", encoding="utf-8").write(md)
        json.dump({"mode": self.mode, "time": now, "verdict": verdict,
                   "stats": self.stats, "issues": self.issues},
                  open(os.path.join(BASE, "verify_report.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        return md, fails, warns

def main():
    mode = "local"
    if "--mode" in sys.argv:
        mode = sys.argv[sys.argv.index("--mode") + 1]
    assert mode in ("local", "live", "remote"), f"未知模式 {mode}"
    posts, pages = load_feeds(CACHE_P, CACHE_G)
    if mode == "live":
        fp, fg = S.fetch(f"{ORIGIN}/feeds/posts/default?alt=json&max-results=500"), \
                 S.fetch(f"{ORIGIN}/feeds/pages/default?alt=json&max-results=500")
        json.dump(fp, open(LIVE_P, "w", encoding="utf-8"), ensure_ascii=False)
        json.dump(fg, open(LIVE_G, "w", encoding="utf-8"), ensure_ascii=False)
        tot = total_in(CACHE_P)
        if tot is not None and tot != len(posts):
            print(f"⚠️ 缓存 feeds 声明 {tot} 篇，实际 {len(posts)} 篇（可能抓取不完整）")
    v = Verifier(mode)
    getattr(v, f"run_{mode}")(posts, pages)
    md, fails, warns = v.report()
    print(md)
    print(f"\nEXIT: {'OK' if not fails else f'{len(fails)} FAIL / {len(warns)} WARN'} -> verify_report.md")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()