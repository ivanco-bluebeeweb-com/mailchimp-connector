"""HTTP client for Mailchimp Marketing API 3.0."""
from __future__ import annotations
from typing import Any
import httpx

MC_NOT_CONNECTED = "MAILCHIMP_NOT_CONNECTED"
MC_UNAUTHORIZED = "MAILCHIMP_UNAUTHORIZED"
MC_FORBIDDEN = "MAILCHIMP_FORBIDDEN"
MC_NOT_FOUND = "MAILCHIMP_NOT_FOUND"
MC_RATE_LIMITED = "MAILCHIMP_RATE_LIMITED"
MC_BACKEND_ERROR = "MAILCHIMP_BACKEND_ERROR"
MC_VALIDATION_FAILED = "MAILCHIMP_VALIDATION_FAILED"
MC_RESPONSE_UNEXPECTED = "MAILCHIMP_RESPONSE_UNEXPECTED"
_MESSAGES = {
    MC_NOT_CONNECTED: "No Mailchimp account is connected. Connect one first.",
    MC_UNAUTHORIZED: "Mailchimp rejected the API key as invalid or revoked.",
    MC_FORBIDDEN: "Mailchimp denied access to this resource.",
    MC_NOT_FOUND: "That Mailchimp record was not found.",
    MC_RATE_LIMITED: "Mailchimp rate-limited this request. Try again shortly.",
    MC_BACKEND_ERROR: "Mailchimp returned an error.",
    MC_VALIDATION_FAILED: "Mailchimp rejected the request as invalid.",
    MC_RESPONSE_UNEXPECTED: "Mailchimp returned an unexpected response.",
}
def fail(code: str, detail: str = "") -> dict:
    text = _MESSAGES.get(code, "Mailchimp request failed.")
    return {"code": code, "message": f"{text} ({detail})" if detail else text}
class ClientFail(Exception):
    def __init__(self, payload: dict):
        super().__init__(payload["message"]); self.payload = payload

def data_center(api_key: str) -> str:
    try: return api_key.rsplit("-", 1)[1]
    except IndexError: raise ClientFail(fail(MC_VALIDATION_FAILED, "API key must include its data-center suffix, e.g. -us21."))
def _code(status: int) -> str:
    if status == 401: return MC_UNAUTHORIZED
    if status == 403: return MC_FORBIDDEN
    if status == 404: return MC_NOT_FOUND
    if status == 429: return MC_RATE_LIMITED
    if status >= 500: return MC_BACKEND_ERROR
    return MC_VALIDATION_FAILED
async def request(api_key: str, method: str, path: str, *, params: dict | None = None, json_body: Any = None, action: str = "") -> dict:
    url = f"https://{data_center(api_key)}.api.mailchimp.com/3.0{path}"
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.request(method, url, params=params, json=json_body, auth=("anystring", api_key), headers={"Accept": "application/json"})
    if response.status_code >= 400:
        raise ClientFail(fail(_code(response.status_code), f"{action or method}: HTTP {response.status_code}: {response.text[:240]}"))
    if response.status_code == 204 or not response.content: return {}
    try: return response.json()
    except ValueError: raise ClientFail(fail(MC_RESPONSE_UNEXPECTED, response.text[:240]))
