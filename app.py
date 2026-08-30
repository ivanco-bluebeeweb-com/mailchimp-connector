"""Mailchimp Connector extension declaration."""
from imperal_sdk import ChatExtension, Extension

ext = Extension(
    "mailchimp-connector", version="0.1.0", display_name="Mailchimp", icon="icon.svg",
    capabilities=["mailchimp:read", "mailchimp:write"],
    description="Connect Mailchimp Marketing API to manage audiences, contacts, tags, campaigns, and reports.",
)
chat = ChatExtension(ext)


@ext.health_check
async def health_check(ctx) -> dict:
    """Fast configuration health; no third-party call -- just confirms at
    least one account connection is stored, same shape as Buildium's/Cin7
    Core's health_check."""
    import json as _json
    raw = await ctx.secrets.get("mailchimp_connections")
    try:
        count = len(_json.loads(raw)) if raw else 0
    except Exception:
        count = 0
    return {
        "healthy": True,
        "detail": (
            f"{count} Mailchimp account(s) connected." if count
            else "Not connected yet -- run connect_mailchimp."
        ),
    }
