"""Pydantic models for Mailchimp Connector."""
from pydantic import BaseModel, Field
class NoParams(BaseModel): pass
class Scoped(BaseModel): connection_id: str = Field("", description="Saved Mailchimp account id; omit if only one account is connected.")
class ConnectMailchimpParams(BaseModel):
    label: str = Field("", description="Friendly label, e.g. Main marketing account.")
    api_key: str = Field(description="Mailchimp API key including its data-center suffix, e.g. ...-us21.")
class ConnectionResult(BaseModel): connection_id: str = ""; label: str = ""
class DisconnectParams(BaseModel): connection_id: str
class Connection(BaseModel): id: str = ""; label: str = ""; account_name: str = ""
class ConnectionList(BaseModel): connections: list[Connection] = Field(default_factory=list)
class DeleteResult(BaseModel): deleted: bool = False; id: str = ""
class ListAudiencesParams(Scoped): count: int = Field(20, ge=1, le=100)
class Audience(BaseModel): id: str = ""; name: str = ""; member_count: int = 0
class AudienceList(BaseModel): audiences: list[Audience] = Field(default_factory=list)
class CreateAudienceParams(Scoped):
    name: str
    from_name: str
    from_email: str
    permission_reminder: str = Field(description="Why recipients are receiving mail, e.g. You signed up on our website.")
    company: str
    address1: str
    city: str
    country: str
    zip: str
class AudienceResult(BaseModel): id: str = ""; name: str = ""
class ListMembersParams(Scoped): audience_id: str; count: int = Field(20, ge=1, le=100)
class Member(BaseModel): id: str = ""; email: str = ""; status: str = ""; merge_fields: dict = Field(default_factory=dict)
class MemberList(BaseModel): members: list[Member] = Field(default_factory=list)
class UpsertMemberParams(Scoped):
    audience_id: str
    email: str
    status_if_new: str = Field("subscribed", description="New member status: subscribed, pending, unsubscribed, or transactional.")
    merge_fields: dict = Field(default_factory=dict, description="Audience merge fields, e.g. {'FNAME':'Ada'}.")
class MemberResult(BaseModel): id: str = ""; email: str = ""; status: str = ""
class ListTagsParams(Scoped): audience_id: str; count: int = Field(20, ge=1, le=100)
class Tag(BaseModel): id: int = 0; name: str = ""
class TagList(BaseModel): tags: list[Tag] = Field(default_factory=list)
class CreateTagParams(Scoped): audience_id: str; name: str
class TagResult(BaseModel): id: int = 0; name: str = ""
class ListCampaignsParams(Scoped): count: int = Field(20, ge=1, le=100)
class Campaign(BaseModel): id: str = ""; title: str = ""; status: str = ""; emails_sent: int = 0
class CampaignList(BaseModel): campaigns: list[Campaign] = Field(default_factory=list)
class CreateCampaignParams(Scoped): audience_id: str; subject_line: str; from_name: str; reply_to: str; title: str
class CampaignResult(BaseModel): id: str = ""; title: str = ""; status: str = ""
class SendCampaignParams(Scoped): campaign_id: str
class SendResult(BaseModel): id: str = ""; status: str = ""
class AuditMailchimpParams(Scoped): pass
class MailchimpReport(BaseModel): account_name: str = ""; total_audiences: int = 0; total_members: int = 0; total_campaigns: int = 0
