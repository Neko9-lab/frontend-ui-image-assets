# Frontend UI Image Assets

生成可直接用于前端项目的位图视觉素材，例如 hero 背景、产品图、空状态插画、卡片封面、头像、纹理和游戏场景图。这个仓库既可以作为 Codex skill 安装使用，也可以直接运行内置 Python 脚本生成图片。

Generate frontend-ready raster image assets for websites, web apps, dashboards, games, and prototypes, including hero backgrounds, product imagery, empty-state illustrations, card covers, avatars, textures, and scene art. This repository can be installed as a Codex skill or used directly through the bundled Python script.

## 中文说明

### 功能

- 面向前端 UI 场景生成图片资产，而不是泛泛地生成艺术图。
- 通过 sub2api 或 OpenAI-compatible streaming Responses endpoint 调用图片模型。
- 默认使用流式 Responses 接口，避免非流式图片接口可能出现的上下文取消问题。
- 生成结果会保存为本地图片文件，方便直接放入 `public/`、`assets/` 等前端静态目录。
- 脚本只依赖 Python 标准库，不需要额外安装第三方 Python 包。

### 安装为 Codex Skill

将仓库克隆到 Codex skills 目录：

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/Neko9-lab/frontend-ui-image-assets.git ~/.codex/skills/frontend-ui-image-assets
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
git clone https://github.com/Neko9-lab/frontend-ui-image-assets.git "$env:USERPROFILE\.codex\skills\frontend-ui-image-assets"
```

安装后重启或刷新 Codex，让 skill 被重新发现。之后可以在对话中这样调用：

```text
使用 $frontend-ui-image-assets 给这个 Vite 页面生成一张 hero 背景图，并接入到页面里。
```

### 直接使用脚本

克隆仓库：

```bash
git clone https://github.com/Neko9-lab/frontend-ui-image-assets.git
cd frontend-ui-image-assets
```

准备 Python 3.10 或更高版本。脚本没有第三方依赖，可以直接运行。

创建 `.env` 文件：

```dotenv
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://toolhug.com
OPENAI_MODEL=gpt-image-2
```

也支持 sub2api 风格变量：

```dotenv
SUB2API_API_KEY=your_api_key
SUB2API_BASE_URL=https://toolhug.com
SUB2API_MODEL=gpt-image-2
```

生成一张图片：

```bash
python scripts/local_image_via_sub2api.py "clean SaaS dashboard hero background, soft daylight, plenty of empty space for text, no words, no logos" --out public/assets/generated/hero.png
```

指定尺寸和质量：

```bash
python scripts/local_image_via_sub2api.py "modern product card cover for a finance app, crisp object photography, neutral background, no text" --out public/assets/generated/card-cover.png --size 1536x864 --quality auto
```

保存流式生成过程中的 partial images，方便评估方向：

```bash
python scripts/local_image_via_sub2api.py "friendly empty-state illustration for file upload, light UI style, no readable text" --out public/assets/generated/empty-state.png --partial-images 3 --save-partials
```

### 前端项目放置路径建议

- Vite / React: `public/assets/generated/`
- Next.js: `public/generated/`
- 静态 HTML: `assets/generated/`
- 已有项目：优先遵循项目已有静态资源目录约定

在前端代码中引用示例：

```tsx
export function Hero() {
  return (
    <section
      className="hero"
      style={{ backgroundImage: "url('/assets/generated/hero.png')" }}
    >
      <h1>Build faster with beautiful assets</h1>
    </section>
  );
}
```

### 命令参数

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `prompt` | 图片提示词，必填 | 无 |
| `--env-file` | `.env` 文件路径 | `.env` |
| `--base-url` | Responses endpoint 的 base URL，不需要包含 `/responses` | 读取环境变量或 `https://toolhug.com` |
| `--api-key` | API key | 读取环境变量 |
| `--model` | 图片模型 | 读取环境变量或 `gpt-image-2` |
| `--out` | 输出图片路径 | `image-{timestamp}.png` |
| `--partial-images` | 请求的 partial image 数量，可选 `0`、`1`、`2`、`3` | `1` |
| `--save-partials` | 是否保存每个 partial image | 关闭 |
| `--quality` | 图片质量，可选 `low`、`medium`、`high`、`auto` | `auto` |
| `--size` | 图片尺寸，例如 `1024x1024`、`1536x864` | 不指定 |
| `--timeout` | 请求超时时间，单位秒 | `360` |

### 提示词建议

写提示词时，把它当成前端生产素材 brief，而不是普通画图请求。建议包含：

- 素材用途：hero 背景、卡片封面、头像、空状态插画、纹理、游戏 sprite 等。
- 构图要求：如果图片上方会叠加标题或按钮，需要预留干净空间。
- 比例意图：hero 常用宽屏，卡片常用 4:3，头像或物品常用 1:1，移动端面板可用 9:16。
- 视觉约束：产品气质、颜色温度、真实感程度、光线、背景复杂度。
- UI 安全：避免可读文字、伪 UI、水印、品牌 logo，除非你明确需要。

## English

### What It Does

- Generates image assets for real frontend UI contexts instead of generic artwork.
- Calls an image model through sub2api or any OpenAI-compatible streaming Responses endpoint.
- Uses streaming Responses by default to avoid context-canceled failures sometimes seen with non-streaming image paths.
- Saves the result as a local image file that can be referenced from frontend code.
- Uses only the Python standard library. No extra Python package installation is required.

### Install as a Codex Skill

Clone this repository into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/Neko9-lab/frontend-ui-image-assets.git ~/.codex/skills/frontend-ui-image-assets
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
git clone https://github.com/Neko9-lab/frontend-ui-image-assets.git "$env:USERPROFILE\.codex\skills\frontend-ui-image-assets"
```

Restart or refresh Codex so the skill can be discovered. Then invoke it in a prompt:

```text
Use $frontend-ui-image-assets to generate a hero background for this Vite page and wire it into the UI.
```

### Use the Script Directly

Clone the repository:

```bash
git clone https://github.com/Neko9-lab/frontend-ui-image-assets.git
cd frontend-ui-image-assets
```

Use Python 3.10 or newer. The script has no third-party dependencies.

Create a `.env` file:

```dotenv
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://toolhug.com
OPENAI_MODEL=gpt-image-2
```

sub2api-style variables are also supported:

```dotenv
SUB2API_API_KEY=your_api_key
SUB2API_BASE_URL=https://toolhug.com
SUB2API_MODEL=gpt-image-2
```

Generate an image:

```bash
python scripts/local_image_via_sub2api.py "clean SaaS dashboard hero background, soft daylight, plenty of empty space for text, no words, no logos" --out public/assets/generated/hero.png
```

Set size and quality:

```bash
python scripts/local_image_via_sub2api.py "modern product card cover for a finance app, crisp object photography, neutral background, no text" --out public/assets/generated/card-cover.png --size 1536x864 --quality auto
```

Save streamed partial images when you want to inspect visual direction:

```bash
python scripts/local_image_via_sub2api.py "friendly empty-state illustration for file upload, light UI style, no readable text" --out public/assets/generated/empty-state.png --partial-images 3 --save-partials
```

### Suggested Frontend Asset Paths

- Vite / React: `public/assets/generated/`
- Next.js: `public/generated/`
- Static HTML: `assets/generated/`
- Existing projects: follow the existing asset directory convention first

Reference the saved image from frontend code:

```tsx
export function Hero() {
  return (
    <section
      className="hero"
      style={{ backgroundImage: "url('/assets/generated/hero.png')" }}
    >
      <h1>Build faster with beautiful assets</h1>
    </section>
  );
}
```

### CLI Options

| Option | Description | Default |
| --- | --- | --- |
| `prompt` | Required image prompt | None |
| `--env-file` | Path to the `.env` file | `.env` |
| `--base-url` | Base URL for the Responses endpoint, without `/responses` | Env value or `https://toolhug.com` |
| `--api-key` | API key | Env value |
| `--model` | Image model | Env value or `gpt-image-2` |
| `--out` | Output image path | `image-{timestamp}.png` |
| `--partial-images` | Number of requested partial images: `0`, `1`, `2`, or `3` | `1` |
| `--save-partials` | Save each partial image event | Off |
| `--quality` | Image quality: `low`, `medium`, `high`, or `auto` | `auto` |
| `--size` | Optional size, such as `1024x1024` or `1536x864` | Not set |
| `--timeout` | Request timeout in seconds | `360` |

### Prompting Tips

Write prompts as production asset briefs, not broad art requests. Include:

- Asset role: hero background, card cover, avatar, empty-state illustration, texture, game sprite, and so on.
- Composition: leave safe empty space when text or buttons will be overlaid.
- Aspect ratio intent: wide for heroes, 4:3 for cards, 1:1 for avatars or items, 9:16 for mobile-first panels.
- Visual constraints: product tone, color temperature, realism level, lighting, and background density.
- UI safety: avoid readable text, fake UI chrome, watermarks, and logos unless explicitly needed.

## Repository Structure

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
└── scripts/
    └── local_image_via_sub2api.py
```

## License

No license file is included yet. Add a license before publishing or distributing this project broadly.
