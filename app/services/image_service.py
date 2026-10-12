
import os
from pathlib import Path
from uuid import uuid4

import httpx
from dotenv import load_dotenv

load_dotenv()


class ImageServiceError(Exception):
    """Raised when image generation fails."""


def generate_image(prompt: str) -> dict:
    api_url = os.getenv("IMAGE_API_URL", "").strip()
    api_token = os.getenv("IMAGE_API_TOKEN", "").strip()
    output_dir = Path(
        os.getenv("IMAGE_OUTPUT_DIR", "media/generated")
    )

    if not api_url:
        raise ImageServiceError(
            "IMAGE_API_URL is not configured."
        )

    headers = {
        "Content-Type": "application/json",
    }

    if api_token:
        headers["Authorization"] = f"Bearer {api_token}"

    try:
        response = httpx.post(
            api_url,
            headers=headers,
            json={"prompt": prompt},
            timeout=120.0,
        )
        response.raise_for_status()

    except httpx.HTTPError as exc:
        raise ImageServiceError(
            f"Image API request failed: {exc}"
        ) from exc

    content_type = response.headers.get(
        "content-type", ""
    ).lower()

    extension_by_type = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/webp": ".webp",
    }

    extension = extension_by_type.get(content_type)

    if extension is None:
        raise ImageServiceError(
            "The image API did not return a supported "
            "PNG, JPEG, or WebP image."
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}{extension}"
    output_path = output_dir / filename

    output_path.write_bytes(response.content)

    return {
        "status": "generated",
        "filename": filename,
        "path": str(output_path),
        "content_type": content_type,
    }
