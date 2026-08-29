"""Mailchimp sidebar UI following the shared UI interface standard."""
from __future__ import annotations
from imperal_sdk import ui
from app import ext
import handlers_connection as h

def _settings() -> ui.UINode:
    return ui.Button("App settings", variant="secondary", size="sm", full_width=True,
                     icon="settings", on_click=ui.Call("__panel__mailchimp_settings"))

@ext.panel("home", slot="left")
async def home(ctx, **kwargs) -> object:
    """Render the concise connection sidebar; detailed setup stays in overlay help."""
    connections = await h._load(ctx)
    form = ui.Form(submit_label="Connect Mailchimp", action=ui.Call("connect_mailchimp"), children=[
        ui.Stack(direction="v", gap=2, children=[
            ui.Stack(direction="v", gap=1, children=[ui.Text("Account label", variant="label"), ui.Input(param_name="label", placeholder="e.g. Main marketing account")]),
            ui.Stack(direction="v", gap=1, children=[ui.Text("API key", variant="label"), ui.Input(param_name="api_key", placeholder="Paste key ending in its data-center suffix, e.g. -us21")]),
        ])
    ])
    children: list[ui.UINode] = [ui.Text("Mailchimp", variant="heading")]
    if connections:
        children.extend([ui.Text("Connected accounts", variant="label"), *[ui.Text(item.get("label") or "Mailchimp account", variant="body") for item in connections]])
    else:
        children.extend([ui.Text("Connect an account", variant="label"), form])
    children.extend([ui.Button("How do I set this up?", variant="secondary", size="sm", full_width=True, on_click=ui.OpenModal("mailchimp_setup")), _settings()])
    return ui.Stack(direction="v", gap=3, children=children)

@ext.panel("mailchimp_setup", slot="overlay")
async def mailchimp_setup(ctx, **kwargs) -> object:
    """Display provider setup help only when the user asks for it."""
    return ui.Stack(direction="v", gap=2, children=[
        ui.Text("Connect Mailchimp", variant="heading"),
        ui.Text("In Mailchimp, open Account & billing → Extras → API keys and create a key. Keep its final data-center suffix (for example, -us21) intact, then paste the complete key here. It is verified before storage.", variant="body"),
    ])
