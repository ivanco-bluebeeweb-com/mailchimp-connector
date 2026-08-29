"""Mailchimp connection settings panel."""
from __future__ import annotations
from imperal_sdk import ui
from app import ext
import handlers_connection as h

@ext.panel("mailchimp_settings", slot="center")
async def mailchimp_settings(ctx, **kwargs) -> object:
    """List safe connection metadata and provide an explicit disconnect action."""
    connections = await h._load(ctx)
    children: list[ui.UINode] = [ui.Text("Mailchimp — App settings", variant="heading"), ui.Divider()]
    if not connections:
        children.append(ui.Text("No Mailchimp accounts connected yet.", variant="caption"))
    for item in connections:
        children.extend([ui.Text(item.get("label") or "Mailchimp account", variant="body"), ui.Text(item.get("account_name", ""), variant="caption"), ui.Button("Disconnect", variant="danger", size="sm", on_click=ui.Call("disconnect_mailchimp", {"connection_id": item.get("id", "")})), ui.Divider()])
    return ui.Stack(direction="v", gap=2, children=children)
