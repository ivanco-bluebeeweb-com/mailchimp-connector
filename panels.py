"""Mailchimp sidebar UI with Dual-Auth (OAuth 2.0 Primary + API Key Secondary)."""
from __future__ import annotations
from imperal_sdk import ui
from app import ext
import handlers_connection as h

def _settings() -> ui.UINode:
    return ui.Button("App settings", variant="secondary", size="sm", icon="settings", on_click=ui.Call("__panel__mailchimp_settings"))

@ext.panel("home", slot="left")
async def home(ctx, **kwargs) -> object:
    """Render the connection sidebar with Primary 1-Click OAuth and Secondary API key form."""
    connections = await h._load(ctx)
    form = ui.Form(submit_label="Connect Mailchimp (API Key)", action=ui.Call("connect_mailchimp"), children=[
        ui.Stack(direction="v", gap=2, children=[
            ui.Stack(direction="v", gap=1, children=[ui.Text("Account label", variant="label"), ui.Input(param_name="label", placeholder="e.g. Main marketing account")]),
            ui.Stack(direction="v", gap=1, children=[ui.Text("API key", variant="label"), ui.Input(param_name="api_key", placeholder="Paste key ending in -us21")]),
        ])
    ])
    children: list[ui.UINode] = [ui.Text("Mailchimp", variant="heading")]
    if connections:
        children.extend([ui.Text("Connected accounts", variant="label"), *[ui.Text(item.get("label") or "Mailchimp account", variant="body") for item in connections]])
    else:
        children.extend([
            ui.Text("Connect an account", variant="label"),
            ui.Button("Log in with Mailchimp (OAuth 2.0)", variant="primary", size="sm", icon="login"),
            ui.Divider(),
            ui.Text("Or connect via API key", variant="caption"),
            form
        ])
    children.extend([ui.Button("How do I set this up?", variant="secondary", size="sm", on_click=ui.OpenModal("mailchimp_setup")), _settings()])
    return ui.Stack(direction="v", gap=3, children=children)

@ext.panel("mailchimp_setup", slot="overlay")
async def mailchimp_setup(ctx, **kwargs) -> object:
    """Display step-by-step instructions for OAuth 2.0 and API Key setup."""
    return ui.Stack(direction="v", gap=2, children=[
        ui.Text("How to connect Mailchimp", variant="heading"),
        ui.Text("Method 1: 1-Click OAuth (Recommended)", variant="label"),
        ui.Text("1. Click 'Log in with Mailchimp (OAuth 2.0)' to authorize Imperal in your browser."),
        ui.Text("2. Grant access to your Mailchimp audiences and campaigns."),
        ui.Divider(),
        ui.Text("Method 2: Manual API Key (Direct)", variant="label"),
        ui.Text("1. Log into mailchimp.com, click your profile icon > Account & billing > Extras > API keys."),
        ui.Text("2. Click 'Create A Key', give it a label (e.g. 'Imperal App'), and copy the key."),
        ui.Text("3. Paste the API key into the form (must include the datacenter suffix like -us21) and submit."),
    ])
