"""Mailchimp connection lifecycle."""
from __future__ import annotations
import json, uuid
from imperal_sdk import ActionResult
import mailchimp_client as mc
from app import chat
from schemas import ConnectMailchimpParams, ConnectionResult, DisconnectParams, DeleteResult, Connection, ConnectionList, NoParams
_SECRET = "mailchimp_connections"
async def _load(ctx) -> list[dict]:
    raw = await ctx.secrets.get(_SECRET)
    try: data = json.loads(raw) if raw else []
    except (TypeError, ValueError): data = []
    return data if isinstance(data, list) else []
async def _save(ctx, data: list[dict]) -> None: await ctx.secrets.set(_SECRET, json.dumps(data))
async def resolve(ctx, connection_id: str = "") -> dict | None:
    data = await _load(ctx)
    return next((x for x in data if x.get("id") == connection_id), None) if connection_id else (data[0] if data else None)
async def resolve_or_error(ctx, connection_id: str = ""):
    connection = await resolve(ctx, connection_id)
    if not connection: return None, ActionResult.error("No Mailchimp account found. Connect one with connect_mailchimp first.", code=mc.MC_NOT_CONNECTED)
    return connection, None
@chat.function("connect_mailchimp", "Connect a Mailchimp account using an API key and verify it against the account endpoint.", action_type="write", chain_callable=True, effects=["create:connection"], event="mailchimp-connector.connect_mailchimp", data_model=ConnectionResult)
async def connect_mailchimp(ctx, params: ConnectMailchimpParams) -> ActionResult:
    """Verify an API key before securely storing it."""
    try: account = await mc.request(params.api_key, "GET", "/", action="verify API key")
    except mc.ClientFail as exc: return ActionResult.error(exc.payload["message"], code=exc.payload["code"])
    connection_id = str(uuid.uuid4()); items = await _load(ctx)
    items.append({"id": connection_id, "label": params.label or account.get("account_name", "Mailchimp account"), "account_name": account.get("account_name", ""), "api_key": params.api_key})
    await _save(ctx, items)
    return ActionResult.success(ConnectionResult(connection_id=connection_id, label=items[-1]["label"]), summary="Mailchimp connected.")
@chat.function("list_connections", "List connected Mailchimp accounts without exposing API keys.", action_type="read", chain_callable=True, data_model=ConnectionList)
async def list_connections(ctx, params: NoParams) -> ActionResult:
    """Return safe connection metadata."""
    return ActionResult.success(ConnectionList(connections=[Connection(id=x.get("id", ""), label=x.get("label", ""), account_name=x.get("account_name", "")) for x in await _load(ctx)]), summary="Connections listed.")
@chat.function("disconnect_mailchimp", "Disconnect a Mailchimp account and delete only its locally saved API key.", action_type="write", chain_callable=True, effects=["delete:connection"], event="mailchimp-connector.disconnect_mailchimp", data_model=DeleteResult)
async def disconnect_mailchimp(ctx, params: DisconnectParams) -> ActionResult:
    """Remove saved access for one Mailchimp account."""
    items = await _load(ctx); kept = [x for x in items if x.get("id") != params.connection_id]
    if len(kept) == len(items): return ActionResult.error("Mailchimp connection was not found.", code=mc.MC_NOT_FOUND)
    await _save(ctx, kept); return ActionResult.success(DeleteResult(deleted=True, id=params.connection_id), summary="Mailchimp disconnected.")
