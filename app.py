"""Mailchimp Connector extension declaration."""
from imperal_sdk import ChatExtension, Extension

ext = Extension(
    "mailchimp-connector", version="0.1.0", display_name="Mailchimp", icon="icon.svg",
    capabilities=["mailchimp:read", "mailchimp:write"],
    description="Connect Mailchimp Marketing API to manage audiences, contacts, tags, campaigns, and reports.",
)
chat = ChatExtension(ext)
