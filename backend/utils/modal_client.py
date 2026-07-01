import logging
import os

import httpx

logger = logging.getLogger(__name__)


class ModalNotConfiguredError(Exception):
    """Raised when a Modal endpoint is called but its URL/credentials aren't set."""


def _proxy_auth_headers() -> dict[str, str]:
    token_id = os.environ.get("MODAL_PROXY_TOKEN_ID")
    token_secret = os.environ.get("MODAL_PROXY_TOKEN_SECRET")
    if not token_id or not token_secret:
        raise ModalNotConfiguredError(
            "MODAL_PROXY_TOKEN_ID / MODAL_PROXY_TOKEN_SECRET are not set in .env"
        )
    return {"Modal-Key": token_id, "Modal-Secret": token_secret}


async def call_vton(
    person_bytes: bytes,
    garment_bytes: bytes,
    garment_des: str,
    category: str,
) -> bytes:
    url = os.environ.get("MODAL_VTON_URL")
    if not url:
        raise ModalNotConfiguredError("MODAL_VTON_URL is not set in .env")

    async with httpx.AsyncClient(timeout=180) as client:
        response = await client.post(
            url,
            headers=_proxy_auth_headers(),
            files={
                "person": ("person.jpg", person_bytes, "image/jpeg"),
                "garment": ("garment.jpg", garment_bytes, "image/jpeg"),
            },
            data={"garment_des": garment_des, "category": category},
        )
    response.raise_for_status()
    return response.content


async def call_style_transfer(content_bytes: bytes, style_bytes: bytes) -> bytes:
    url = os.environ.get("MODAL_NST_URL")
    if not url:
        raise ModalNotConfiguredError("MODAL_NST_URL is not set in .env")

    async with httpx.AsyncClient(timeout=180) as client:
        response = await client.post(
            url,
            headers=_proxy_auth_headers(),
            files={
                "content_img": ("content.jpg", content_bytes, "image/jpeg"),
                "style_img": ("style.jpg", style_bytes, "image/jpeg"),
            },
        )
    response.raise_for_status()
    return response.content
