# DESIGN.md - 晓鹤的博客 (Minimalist Editorial Edition / 方案 B · 纯净学术)

> 修订记录：v2 由方案 A（赛博极客暗色）切换至方案 B（纯净学术）。Bento Grid、玻璃拟态、滚动 reveal 全部移除。

## 1. Visual Theme & Atmosphere
- **设计哲学**: "纸与墨"。像一份排印精良的学术期刊/电子杂志：内容是唯一主角，界面退到纸的层面。
- **氛围关键词**: 纸感、衬线、大留白、细线、克制、权威。
- **一句话定调**: 一份安静、可信、以阅读为中心的中文技术随笔集。

## 2. Color Palette & Roles
| 角色 | 变量 | 数值 | RGB 辅助值 | 用途 |
| :--- | :--- | :--- | :--- | :--- |
| **Paper** | `--bg` | `#faf9f6` | `250, 249, 246` | 全局底色（暖纸白） |
| **Surface** | `--surface` | `#ffffff` | `255, 255, 255` | 代码块/引用底 |
| **Ink** | `--ink` | `#1c1c1a` | `28, 28, 26` | 正文与标题（软墨色，非纯黑） |
| **Muted** | `--muted` | `#73716c` | `115, 113, 108` | 日期、元信息、页脚 |
| **Border** | `--border` | `#e6e4de` | `230, 228, 222` | 发丝级分隔线 |
| **Accent** | `--accent` | `#a63d2f` | `166, 61, 47` | 朱砂色，仅用于标签/hover/小元素 |
| **Link** | `--link` | `#1c1c1a` | `28, 28, 26` | 链接即墨色，靠下划线区分 |

## 3. Typography Rules
- **标题/正文**: `'Noto Serif SC', 'Source Han Serif SC', 'STSong', Georgia, 'Times New Roman', serif`
- **元信息/代码**: `ui-monospace, 'SF Mono', Consolas, monospace`（小号、灰色）
- **层级**: H1 32px/900 · H2 文章题 22px/700 · 正文 17px/400/1.9 · Meta 13px mono
- **中文规则**: 行高 1.9、字距 0.01em、正文 ≥ 17px（长阅读优先）
- **禁止**: 无衬线体作正文、纯黑 #000、字重滥用水。

## 4. Component Stylings
- **导航**: 无背景色、无阴影，仅 1px 发丝底线；当前页无高亮，hover 仅变墨色。
- **文章条目**: 无卡片边框、无底色 —— 纯文字列表，条目间 1px 发丝线分隔。
- **标签**: 无背景无边框，`#标签` 形式 + 朱砂色小字。
- **引用块**: 左侧 2px 墨色短线 + 斜体，无底色。
- **代码块**: `--surface` 白底 + 发丝边框，圆角 4px（克制）。
- **链接**: 墨色 + `text-underline`（细下划线，hover 变朱砂色）。

## 5. Layout Principles
- **单栏阅读列**: max-width 680px，居中。
- **首页 = 目录**: 题录式列表（标题 + 日期 + 摘要），非卡片网格。
- **留白**: 条目上下 padding 28px；页面顶部留白 64px。
- **间距梯度**: 4 / 8 / 16 / 28 / 48 / 64。

## 6. Depth & Elevation
- **原则: 零阴影**。层次全靠发丝线与留白表达。
- 唯一例外：代码块 1px 边框 + 极浅底色差。

## 7. Animation & Interaction（档位: L1 精致静态）
- **入场**: 页面加载时整列内容 `fadeIn`（0.5s, 一次），无 JS、无观察器。
- **Hover**: 链接下划线色过渡至朱砂（200ms）；标题 hover 颜色不变（克制）。
- **过渡**: 全局 `transition: color .2s, border-color .2s`。
- **无**: 滚动 reveal、视差、卡片位移、发光、玻璃拟态。

## 8. Do's and Don'ts
- **Do**: 留白是设计的一部分；分隔用 1px 线；强调用朱砂但每次只出现一两处；日期一律等宽字体。
- **Don't**:
  1. 禁止卡片/阴影/渐变（回到方案 A 的元素）。
  2. 禁止纯黑 #000 正文。
  3. 禁止首页题图缩略图（保持文字目录的纯粹）。
  4. 禁止任何滚动驱动动画。
  5. 禁止彩色大色块。
  6. 禁止导航 glassmorphism。
  7. 禁止 > 8px 圆角。
  8. 禁止无衬线正文。

## 9. Responsive Behavior
- **Desktop**: 680px 单栏。
- **Mobile ≤ 680px**: padding 20px；H1 26px；正文 16.5px；触摸目标 ≥ 44px（行距已保证）。
