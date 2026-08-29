"""Read-only account health report for Mailchimp Connector."""
from __future__ import annotations
from imperal_sdk import ActionResult
import mailchimp_client as mc
from app import chat
from handlers_connection import resolve_or_error
from schemas import AuditMailchimpParams, MailchimpReport

@chat.function(
    "audit_mailchimp_account",
    "Build a read-only Mailchimp snapshot: account name, audiences, members, and campaigns.",
    action_type="read", chain_callable=True, data_model=MailchimpReport,
)
async def audit_mailchimp_account(ctx, params: AuditMailchimpParams) -> ActionResult:
    """Read account and collection totals without altering Mailchimp data."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err:
        return err
    try:
        account = await mc.request(conn["api_key"], "GET", "/", action="read account")
        audiences = await mc.request(conn["api_key"], "GET", "/lists", params={"count": 100}, action="list audiences")
        campaigns = await mc.request(conn["api_key"], "GET", "/campaigns", params={"count": 1}, action="count campaigns")
    except mc.ClientFail as exc:
        return ActionResult.error(exc.payload["message"], code=exc.payload["code"])
    return ActionResult.ok(MailchimpReport(
        account_name=account.get("account_name", ""),
        total_audiences=audiences.get("total_items", len(audiences.get("lists", []))),
        total_members=sum(item.get("stats", {}).get("member_count", 0) for item in audiences.get("lists", [])),
        total_campaigns=campaigns.get("total_items", len(campaigns.get("campaigns", []))),
    ))
