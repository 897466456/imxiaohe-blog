# 晓鹤的博客 (imxiaohe-blog)

由 Blogger 博客 [blog.imxiaohe.com](https://blog.imxiaohe.com) 迁移重建的静态博客。

- **内容**：69 篇文章、3 个页面、92 张图片（文章/页面提取自 Blogger 源，图片已下载到本地 `public/assets/img/`）
- **技术**：纯静态 HTML + CSS（由 `scrape_blog.py` 生成），零构建依赖
- **部署**：Cloudflare Pages（免费托管）

## 目录结构

```
scrape_blog.py   # 迁移脚本：抓取 Blogger 源 → 生成 public/
public/          # 生成的静态站点（部署目录）
style.css        # 主题样式
```

## 重新生成

```bash
python scrape_blog.py   # 读取本地 feeds 缓存重新生成
# 删除 _feeds_posts.json / _feeds_pages.json 可强制重新抓取 Blogger 源
```

## 部署

```bash
npx wrangler pages deploy public --project-name=blog-imxiaohe
```