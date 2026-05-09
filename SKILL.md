---
name: frontend-ui-image-assets
description: Generate frontend-ready raster image assets from text prompts through a sub2api or OpenAI-compatible streaming Responses endpoint. Use when building or editing websites, web apps, React/Vue/Next/Vite projects, games, landing pages, dashboards, or UI prototypes that need hero backgrounds, product imagery, empty-state illustrations, card covers, avatars, textures, scene art, or other bitmap assets saved into the project and referenced by frontend code.
---

# Frontend UI Image Assets

Use the bundled Python script to create bitmap assets for frontend work, then save and wire those assets into the app being built.

## Configuration

Read only these environment variables or `.env` values for service configuration:

- `OPENAI_API_KEY` or `SUB2API_API_KEY`: required API key.
- `OPENAI_BASE_URL` or `SUB2API_BASE_URL`: endpoint base URL; falls back to `https://toolhug.com`.
- `OPENAI_MODEL` or `SUB2API_MODEL`: image model; falls back to `gpt-image-2`.

Do not read environment variables for quality, size, output path, partial images, or timeout. Pass those as CLI flags only when the current frontend task requires them.

## Use For

Generate raster assets when the frontend needs visual content that CSS, SVG icons, or layout code cannot supply well:

- Hero or section background images.
- Product, venue, object, or lifestyle imagery.
- Empty-state, onboarding, or feature illustrations.
- Card covers, thumbnails, avatars, and profile scenes.
- Game sprites, scene backdrops, collectible/item art, or textures.
- Subtle bitmap textures or atmospheric media that support the UI.

Avoid this skill for ordinary UI icons, buttons, simple gradients, abstract blobs, text-heavy mockups, charts, diagrams, or anything better implemented with HTML/CSS/SVG/lucide icons.

## Frontend Workflow

1. Inspect the existing frontend project before generating anything: framework, public/static asset path, design style, dominant colors, image aspect ratios, and where the asset will be used.
2. Decide whether a generated bitmap is appropriate. If a native icon, CSS treatment, or existing asset fits better, use that instead.
3. Choose an output location that the frontend can serve directly:
   - Vite/React: `public/assets/generated/`
   - Next.js: `public/generated/`
   - Static HTML: `assets/generated/`
   - Existing project convention: follow it.
4. Create a prompt that names the asset's UI role, subject, style, composition, aspect ratio, and integration needs.
5. Run `scripts/local_image_via_sub2api.py` from this skill directory and save the image into the chosen project asset path.
6. Reference the saved asset from the frontend code and verify it renders at desktop and mobile sizes.

## Prompt Rules

Write prompts as production asset briefs, not generic art requests. Include:

- Asset role: hero background, empty-state illustration, product image, card cover, game sprite, texture, etc.
- Composition: leave safe empty space for overlays when text/buttons will sit on top.
- Aspect ratio intent: 16:9 or wide for heroes, 4:3 for cards, 1:1 for avatars/items, 9:16 for mobile-first panels.
- Visual constraints from the app: brand feel, color temperature, realism level, lighting, density, and background treatment.
- UI safety: no readable text, no fake UI chrome, no watermarks, no logos unless explicitly requested.

Prefer images that are inspectable, useful, and easy to crop responsively. Avoid dark, blurry, over-cropped, purely atmospheric, or decoration-only images when the user needs the subject to be clear.

## Commands

Basic generation:

```bash
python scripts/local_image_via_sub2api.py "frontend asset prompt" --out public/assets/generated/asset.png
```

With explicit frontend options:

```bash
python scripts/local_image_via_sub2api.py "frontend asset prompt" --out public/assets/generated/hero.png --size 1536x864 --quality auto
```

Save streamed partials only when evaluating visual direction:

```bash
python scripts/local_image_via_sub2api.py "frontend asset prompt" --out public/assets/generated/hero.png --partial-images 3 --save-partials
```

## Defaults

- Model: `gpt-image-2`.
- Quality: `auto`.
- Streaming: enabled.
- Partial images requested: `1`.
- Timeout: `360` seconds.
