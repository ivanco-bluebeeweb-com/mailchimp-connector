"""Mailchimp audiences, members, tags, and campaign handlers."""
from __future__ import annotations
import hashlib
from imperal_sdk import ActionResult
import mailchimp_client as mc
from app import chat
from handlers_connection import resolve_or_error
from schemas import (
    ListAudiencesParams, Audience, AudienceList, CreateAudienceParams, AudienceResult,
    ListMembersParams, Member, MemberList, UpsertMemberParams, MemberResult,
    ListTagsParams, Tag, TagList, CreateTagParams, TagResult,
    ListCampaignsParams, Campaign, CampaignList, CreateCampaignParams, CampaignResult,
    SendCampaignParams, SendResult,
)

def _error(exc: mc.ClientFail) -> ActionResult:
    return ActionResult.error(exc.payload["message"], code=exc.payload["code"])

@chat.function("list_audiences", "List audiences in the connected Mailchimp account.", action_type="read", chain_callable=True, data_model=AudienceList)
async def list_audiences(ctx, params: ListAudiencesParams) -> ActionResult:
    """Return a bounded page of Mailchimp audiences."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err: return err
    try: data = await mc.request(conn["api_key"], "GET", "/lists", params={"count": params.count}, action="list audiences")
    except mc.ClientFail as exc: return _error(exc)
    return ActionResult.ok(AudienceList(audiences=[Audience(id=x.get("id", ""), name=x.get("name", ""), member_count=x.get("stats", {}).get("member_count", 0)) for x in data.get("lists", [])]))

@chat.function("create_audience", "Create a new Mailchimp audience with required sender and contact details.", action_type="write", chain_callable=True, effects=["create:audience"], event="mailchimp-connector.create_audience", data_model=AudienceResult)
async def create_audience(ctx, params: CreateAudienceParams) -> ActionResult:
    """Create a Mailchimp audience."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err: return err
    body = {"name": params.name, "contact": {"company": params.company, "address1": params.address1, "city": params.city, "country": params.country, "zip": params.zip}, "permission_reminder": params.permission_reminder, "campaign_defaults": {"from_name": params.from_name, "from_email": params.from_email, "subject": "", "language": "en"}, "email_type_option": True}
    try: data = await mc.request(conn["api_key"], "POST", "/lists", json_body=body, action="create audience")
    except mc.ClientFail as exc: return _error(exc)
    return ActionResult.ok(AudienceResult(id=data.get("id", ""), name=data.get("name", "")))

@chat.function("list_members", "List members in one Mailchimp audience.", action_type="read", chain_callable=True, data_model=MemberList)
async def list_members(ctx, params: ListMembersParams) -> ActionResult:
    """Return a bounded page of audience members."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err: return err
    try: data = await mc.request(conn["api_key"], "GET", f"/lists/{params.audience_id}/members", params={"count": params.count}, action="list audience members")
    except mc.ClientFail as exc: return _error(exc)
    return ActionResult.ok(MemberList(members=[Member(id=x.get("id", ""), email=x.get("email_address", ""), status=x.get("status", ""), merge_fields=x.get("merge_fields", {})) for x in data.get("members", [])]))

@chat.function("upsert_member", "Create or update a Mailchimp audience member by email, with explicit opt-in status for new contacts.", action_type="write", chain_callable=True, effects=["create:contact", "update:contact"], event="mailchimp-connector.upsert_member", data_model=MemberResult)
async def upsert_member(ctx, params: UpsertMemberParams) -> ActionResult:
    """Upsert one member using Mailchimp's deterministic subscriber hash."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err: return err
    member_hash = hashlib.md5(params.email.strip().lower().encode()).hexdigest()
    body = {"email_address": params.email, "status_if_new": params.status_if_new, "merge_fields": params.merge_fields}
    try: data = await mc.request(conn["api_key"], "PUT", f"/lists/{params.audience_id}/members/{member_hash}", json_body=body, action="upsert audience member")
    except mc.ClientFail as exc: return _error(exc)
    return ActionResult.ok(MemberResult(id=data.get("id", ""), email=data.get("email_address", ""), status=data.get("status", "")))

@chat.function("list_tags", "List tags configured for a Mailchimp audience.", action_type="read", chain_callable=True, data_model=TagList)
async def list_tags(ctx, params: ListTagsParams) -> ActionResult:
    """Return a bounded page of audience tags."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err: return err
    try: data = await mc.request(conn["api_key"], "GET", f"/lists/{params.audience_id}/segments", params={"count": params.count, "type": "static"}, action="list tags")
    except mc.ClientFail as exc: return _error(exc)
    return ActionResult.ok(TagList(tags=[Tag(id=x.get("id", 0), name=x.get("name", "")) for x in data.get("segments", [])]))

@chat.function("create_tag", "Create a new static Mailchimp audience tag.", action_type="write", chain_callable=True, effects=["create:tag"], event="mailchimp-connector.create_tag", data_model=TagResult)
async def create_tag(ctx, params: CreateTagParams) -> ActionResult:
    """Create a static segment, which Mailchimp uses as an audience tag."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err: return err
    try: data = await mc.request(conn["api_key"], "POST", f"/lists/{params.audience_id}/segments", json_body={"name": params.name, "static_segment": []}, action="create tag")
    except mc.ClientFail as exc: return _error(exc)
    return ActionResult.ok(TagResult(id=data.get("id", 0), name=data.get("name", "")))

@chat.function("list_campaigns", "List campaigns in the connected Mailchimp account.", action_type="read", chain_callable=True, data_model=CampaignList)
async def list_campaigns(ctx, params: ListCampaignsParams) -> ActionResult:
    """Return a bounded page of campaigns."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err: return err
    try: data = await mc.request(conn["api_key"], "GET", "/campaigns", params={"count": params.count}, action="list campaigns")
    except mc.ClientFail as exc: return _error(exc)
    return ActionResult.ok(CampaignList(campaigns=[Campaign(id=x.get("id", ""), title=x.get("settings", {}).get("title", ""), status=x.get("status", ""), emails_sent=x.get("emails_sent", 0)) for x in data.get("campaigns", [])]))

@chat.function("create_campaign", "Create a regular email campaign draft for one Mailchimp audience. It is not sent until send_campaign.", action_type="write", chain_callable=True, effects=["create:campaign"], event="mailchimp-connector.create_campaign", data_model=CampaignResult)
async def create_campaign(ctx, params: CreateCampaignParams) -> ActionResult:
    """Create a Mailchimp campaign draft without sending it."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err: return err
    body = {"type": "regular", "recipients": {"list_id": params.audience_id}, "settings": {"subject_line": params.subject_line, "from_name": params.from_name, "reply_to": params.reply_to, "title": params.title}}
    try: data = await mc.request(conn["api_key"], "POST", "/campaigns", json_body=body, action="create campaign")
    except mc.ClientFail as exc: return _error(exc)
    return ActionResult.ok(CampaignResult(id=data.get("id", ""), title=data.get("settings", {}).get("title", ""), status=data.get("status", "")))

@chat.function("send_campaign", "Send a Mailchimp campaign that is ready to send. This emails the campaign audience.", action_type="write", chain_callable=True, effects=["send:email"], event="mailchimp-connector.send_campaign", data_model=SendResult)
async def send_campaign(ctx, params: SendCampaignParams) -> ActionResult:
    """Trigger sending only after Mailchimp accepts the campaign as ready."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err: return err
    try: await mc.request(conn["api_key"], "POST", f"/campaigns/{params.campaign_id}/actions/send", action="send campaign")
    except mc.ClientFail as exc: return _error(exc)
    return ActionResult.ok(SendResult(id=params.campaign_id, status="send_requested"))
