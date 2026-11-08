# DESIGN.md - 晓鹤的博客 (Cyber Tech Edition)

## 1. Visual Theme & Atmosphere
- **设计哲学**: "Precision, Power, and Privacy". 模拟开发者终端与现代 SaaS 产品的融合感。
- **氛围关键词**: 暗色调、高对比、精密、数字化、极客感。
- **一句话定调**: 一个像 IDE 一样精准，像 Vercel 一样现代的极客技术空间。

## 2. Color Palette & Roles
所有颜色均通过 CSS 变量定义，支持 rgba 透明度。

| 角色 | 变量 | 数值 (HEX) | RGB 辅助值 | 用途 |
| :--- | :--- | :--- | :--- | :--- |
| **Background** | `--bg` | `#0a0a0a` | `10, 10, 10` | 全局底色，极深灰 |
| **Surface** | `--surface` | `#111111` | `17, 17, 17` | 卡片、导航栏底色 |
| **Border** | `--border` | `#222222` | `34, 34, 34` | 细线边框，区分模块 |
| **Accent** | `--accent` | `#3b82f6` | `59, 130, 246` | 核心强调色 (Electric Blue) |
| **Accent Soft** | `--accent-soft` | `#1e3a8a` | `30, 58, 138` | 强调色淡化/背景 |
| **Text Primary** | `--text-p` | `#eeeeee` | `238, 238, 238` | 正文、标题主色 |
| **Text Muted** | `--text-m` | `#888888` | `136, 136, 136` | 元数据、辅助文本 |
| **Success** | `--success` | `#10b981` | `16, 185, 129` | 正面状态/标签 |

## 3. Typography Rules
- **Header/UI**: `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif` (现代、清晰)
- **Meta/Code**: `"JetBrains Mono", "Fira Code", "Roboto Mono", monospace` (极客感)
- **字号层级**:
  - H1 (Page Title): `32px / 1.2 / Bold`
  - H2 (Post Title): `20px / 1.4 / SemiBold`
  - Body: `16px / 1.75 / Regular`
  - Meta: `13px / 1.5 / Regular` (Monospace)

## 4. Component Stylings
- **Navigation**: 玻璃拟态 (Glassmorphism)，`backdrop-filter: blur(12px)`，底部 1px 亮边。
- **Bento Card**: 
  - `background: var(--surface)`, `border: 1px solid var(--border)`, `border-radius: 16px`.
  - **Hover**: `border-color: var(--accent)`, `transform: translateY(-4px)`, 增加微弱的蓝色外发光。
- **Tags**: `background: var(--accent-soft)`, `color: var(--accent)`, `font-family: monospace`, `border-radius: 4px`.
- **Post Content**: 
  - 代码块：`background: #000`, `border-radius: 8px`, `padding: 1rem`, 搭配自定义滚动条。
  - 引用块：`border-left: 3px solid var(--accent)`, `background: #161616`.

## 5. Layout Principles
- **Max-Width**: `800px` (阅读舒适区)。
- **Index Layout**: 采用 **Bento Grid (不等高网格)**。核心热门文章占据 2x2 区域，普通文章 1x1。
- **Spacing**: 遵循 8px 步进梯度 (8, 16, 24, 32, 48, 64)。

## 6. Depth & Elevation
- **Level 0**: `var(--bg)`
- **Level 1 (Card)**: `box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3)`
- **Level 2 (Hover)**: `box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.1)`

## 7. Animation & Interaction (档位: L2 流畅交互)
- **Entrance**: 页面加载时，卡片采用 `staggered fade-in-up` (渐显并向上微移 20px)。
- **Reveal**: 滚动时，内容块通过 `IntersectionObserver` 触发 `opacity: 0 -> 1` + `blur(10px) -> blur(0)`.
- **Hover**: 
  - 标题在 hover 时产生 `text-shadow` 霓虹效果。
  - 链接在 hover 时底部边框由中心向两侧展开。
- **Dependencies**: 纯 CSS + 原生 JS (IntersectionObserver)，无第三方库。

## 8. Do's and Don'ts
- **Do**: 
  - 使用 CSS 变量控制所有颜色。
  - 保持深色背景的纯净度，避免过多的灰色阶。
  - 所有的交互必须有 200ms-300ms 的 transition。
  - 移动端保持单列布局，触摸目标 ≥ 44px。
- **Don't**:
  - 禁止使用纯白色 (#FFF) 作为正文色，使用 #EEE 以减轻视觉疲劳。
  - 禁止使用过大的圆角 (> 24px)，保持精致感。
  - 禁止使用复杂的 3D 旋转，仅限微小的位移和缩放。
  - 禁止在暗色模式下使用高饱和度的纯红/纯绿。

## 9. Responsive Behavior
- **Desktop (> 768px)**: 2-3 列 Bento Grid。
- **Mobile (≤ 768px)**: 
  - 强制单列布局。
  - 导航栏简化为紧凑模式。
  - 字体大小微调 (H1 -> 24px)。
