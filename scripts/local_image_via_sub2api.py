#!/usr/bin/env python3
"""
Generate an image asset from your local machine through a sub2api/OpenAI-compatible
Responses endpoint.

This intentionally uses streaming Responses + image_generation to avoid the
non-streaming image path that can hit context-canceled failures.

Required:
  create a .env file:
    OPENAI_API_KEY=your_api_key
    OPENAI_BASE_URL=https://toolhug.com
    OPENAI_MODEL=gpt-image-2

Example:
  python local_image_via_sub2api.py "a tiny robot making tea, watercolor" --out tea.png
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def find_images(value: Any) -> list[str]:
    """Find base64 image payloads in common Responses/Image streaming shapes."""
    found: list[str] = []

    if isinstance(value, dict):
        value_type = value.get("type")

        if value_type == "image_generation_call" and isinstance(value.get("result"), str):
            found.append(value["result"])

        for key in (
            "partial_image_b64",
            "b64_json",
            "image_b64",
            "image_base64",
            "result",
        ):
            candidate = value.get(key)
            if isinstance(candidate, str) and looks_like_base64_image(candidate):
                found.append(candidate)

        for child in value.values():
            found.extend(find_images(child))

    elif isinstance(value, list):
        for child in value:
            found.extend(find_images(child))

    return found


def looks_like_base64_image(text: str) -> bool:
    if text.startswith("data:image/"):
        return True
    if len(text) < 200:
        return False
    return all(ch.isalnum() or ch in "+/=\n\r" for ch in text[:300])


def decode_image(image_b64: str) -> bytes:
    if image_b64.startswith("data:image/"):
        image_b64 = image_b64.split(",", 1)[1]
    return base64.b64decode(image_b64)


def load_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    tool: dict[str, Any] = {"type": "image_generation"}
    if args.partial_images is not None:
        tool["partial_images"] = args.partial_images
    if args.size:
        tool["size"] = args.size
    if args.quality:
        tool["quality"] = args.quality

    return {
        "model": args.model,
        "input": args.prompt,
        "stream": True,
        "tools": [tool],
    }


def save_image(image_b64: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(decode_image(image_b64))


def request_stream(args: argparse.Namespace) -> int:
    dotenv = load_dotenv(Path(args.env_file))
    api_key = (
        args.api_key
        or dotenv.get("OPENAI_API_KEY")
        or dotenv.get("SUB2API_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or os.environ.get("SUB2API_API_KEY")
    )
    if not api_key:
        print("Missing API key. Set OPENAI_API_KEY in .env or pass --api-key.", file=sys.stderr)
        return 2

    base_url = (
        args.base_url
        or dotenv.get("OPENAI_BASE_URL")
        or dotenv.get("SUB2API_BASE_URL")
        or os.environ.get("OPENAI_BASE_URL")
        or os.environ.get("SUB2API_BASE_URL")
        or "https://toolhug.com"
    ).rstrip("/")
    args.model = (
        args.model
        or dotenv.get("OPENAI_MODEL")
        or dotenv.get("SUB2API_MODEL")
        or os.environ.get("OPENAI_MODEL")
        or os.environ.get("SUB2API_MODEL")
        or "gpt-image-2"
    )
    url = f"{base_url}/responses"
    payload = build_payload(args)

    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        },
        method="POST",
    )

    print(f"POST {url}")
    print(f"model={args.model} stream=true out={args.out}")

    latest_image: str | None = None
    image_count = 0
    buffer: list[str] = []

    try:
        with urlopen(request, timeout=args.timeout) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8", "replace").rstrip("\n")

                if not line:
                    if buffer:
                        image_count, latest_image = handle_sse_data(buffer, args, image_count, latest_image)
                        buffer = []
                    continue

                if line.startswith("data:"):
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    buffer.append(data)

        if latest_image:
            save_image(latest_image, Path(args.out))
            print(f"saved final image: {args.out}")
            return 0

        print("No image payload found in the response stream.", file=sys.stderr)
        return 1

    except HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        print(f"HTTP {exc.code}: {body}", file=sys.stderr)
        return 1
    except URLError as exc:
        print(f"Network error: {exc}", file=sys.stderr)
        return 1
    except TimeoutError:
        print(f"Timed out after {args.timeout} seconds.", file=sys.stderr)
        return 1


def handle_sse_data(
    buffer: list[str],
    args: argparse.Namespace,
    image_count: int,
    latest_image: str | None,
) -> tuple[int, str | None]:
    data = "\n".join(buffer)
    try:
        event = json.loads(data)
    except json.JSONDecodeError:
        return image_count, latest_image

    event_type = event.get("type", "")
    if event_type:
        print(f"event: {event_type}")

    images = find_images(event)
    for image_b64 in images:
        latest_image = image_b64
        image_count += 1
        if args.save_partials:
            partial_path = Path(args.out)
            stem = partial_path.stem
            suffix = partial_path.suffix or ".png"
            save_image(image_b64, partial_path.with_name(f"{stem}.partial-{image_count}{suffix}"))
            print(f"saved partial image #{image_count}")

    return image_count, latest_image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate image assets through sub2api Responses streaming.")
    parser.add_argument("prompt", help="Image prompt")
    parser.add_argument("--env-file", default=".env", help="Env file path, default: .env")
    parser.add_argument("--base-url", default=None, help="Default: OPENAI_BASE_URL from .env/env")
    parser.add_argument("--api-key", default=None, help="Default: OPENAI_API_KEY from .env/env")
    parser.add_argument("--model", default=None, help="Default: OPENAI_MODEL from .env/env, fallback: gpt-image-2")
    parser.add_argument("--out", default=f"image-{int(time.time())}.png", help="Output image path")
    parser.add_argument("--partial-images", type=int, default=1, choices=[0, 1, 2, 3])
    parser.add_argument("--save-partials", action="store_true", help="Save each partial image event too")
    parser.add_argument("--quality", choices=["low", "medium", "high", "auto"], default="auto", help="Image quality, default: auto")
    parser.add_argument("--size", default=None, help="Optional size, e.g. 1024x1024")
    parser.add_argument("--timeout", type=int, default=360, help="Socket timeout seconds")
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(request_stream(parse_args()))
