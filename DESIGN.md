# DESIGN.md - 晓鹤的博客 (Minimalist Academic Edition)

## 1. Visual Theme & Atmosphere
- **设计哲学**: "Quiet paper, sharp thought." 像一份被精心排版的学术期刊/电子杂志。
- **氛围关键词**: 温暖纸色、衬线排印、大留白、发丝线、克制。
- **一句话定调**: 一份安静、庄重、以阅读为中心的电子学刊。

## 2. Color Palette & Roles
| 角色 | 变量 | HEX | RGB 辅助值 | 用途 |
| :--- | :--- | :--- | :--- | :--- |
| **Background** | `--bg` | `#faf9f5` | `250, 249, 245` | 纸色底 |
| **Surface** | `--surface` | `#f4f2ec` | `244, 242, 236` | 代码块、引用底色 |
| **Border** | `--border` | `#e6e3da` | `230, 227, 218` | 发丝分隔线 |
| **Ink** | `--ink` | `#1c1917` | `28, 25, 23` | 标题主色（墨色） |
| **Text** | `--text` | `#292524` | `41, 37, 36` | 正文 |
| **Muted** | `--muted` | `#79716b` | `121, 113, 107` | 日期、摘要、辅助 |
| **Accent** | `--accent` | `#8c1f28` | `140, 31, 40` | 链接/强调（学术酒红） |

仅浅色主题（纸质感是核心；不做暗色变体）。

## 3. Typography Rules
- **正文/标题**: `'Source Serif 4', 'Noto Serif SC', 'Songti SC', Simsun, serif` — 中英文统一衬线。
- **代码**: `'JetBrains Mono', monospace`（仅代码，Meta 不用等宽）。
- **字号层级**: H1 30px/600 · H2(卡) 21px/600 · Body 17px/1.95 · Meta 13.5px 斜体 · 摘要 15px/1.85。
- 中文行高 ≥ 1.9，字距 0.02em；Meta 用斜体 + 0.03em 字距代替等宽感。

## 4. Component Stylings
- **导航**: 纸色实底 + 底部发丝线；无玻璃拟态、无阴影。品牌名衬线加粗。
- **列表条目**: **无卡片盒** — 上下发丝线分隔的纯排版条目：衬线标题（hover 变酒红 + 下划线 offset 4px）、斜体日期、纯文本标签（无药丸背景）。
- **正文链接**: 酒红 + 下划线（offset 3px），hover 变墨色。
- **代码块**: `var(--surface)` 底 + 发丝边框，radius 6px；行内 code 同底色。
- **引用**: 左侧 2px 墨色线，无底色，斜体。
- **图片**: radius 2px，无边框（学术图版感）。

## 5. Layout Principles
- **单列阅读流**: 容器 720px（比 Bento 版更窄，纯阅读宽度）。
- **首页**: 垂直列表（非网格），条目间大留白（上下 28px）。
- **间距**: 8px 梯度；标题区上下留白 ≥ 48px。

## 6. Depth & Elevation
- **零阴影体系**。层级只靠：纸色 vs surface 底色 + 发丝线 + 留白。

## 7. Animation & Interaction (档位: L1→L2 克制)
- **入场**: 滚动 reveal 仅 opacity + 8px 微移，0.5s ease-out（保留 IntersectionObserver，去掉夸张位移）。
- **Hover**: 标题变色 + 下划线展开；无 translateY、无光晕。
- **`prefers-reduced-motion`**: reveal 全部直出。
- **依赖**: 无第三方库。

## 8. Do's and Don'ts
**Do**: 全部颜色走 CSS 变量；标题一律衬线；分隔只用发丝线；中文字体必须衬线族在前。
**Don't**: 禁止阴影和玻璃拟态；禁止药丸标签/大圆角(>6px)；禁止纯黑 #000 正文；禁止等宽字体用于日期/Meta；禁止 translateY>12px 的动效；禁止在浅色底上用饱和度 >60% 的大色块。

## 9. Responsive Behavior
- **>768px**: 单列 720px 居中。
- **≤768px**: 字号降一档（H1 26px / Body 16px），留白减半，触摸目标 ≥ 44px。
