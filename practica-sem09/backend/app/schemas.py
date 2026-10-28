from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field, ConfigDict

class LoginRequest(BaseModel): username: str=Field(min_length=2,max_length=80); password: str=Field(min_length=8,max_length=200)
class UserOut(BaseModel): model_config=ConfigDict(from_attributes=True); id:int; username:str; email:str; full_name:str; roles:list[str]
class TokenOut(BaseModel): access_token:str; token_type:str='bearer'; user:UserOut
class AlertIn(BaseModel):
    external_id:str|None=None; source:str='unknown'; title:str=Field(min_length=1,max_length=255); description:str=''; source_ip:str|None=None; destination_ip:str|None=None; severity:str='low'; raw_payload:dict[str,Any]={}
class AlertOut(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int; external_id:str|None; source:str; title:str; description:str; source_ip:str|None; destination_ip:str|None; severity:str; status:str; received_at:datetime; completed_at:datetime|None; error_message:str|None; triage:Any=None; enrichment:Any=None
class TriageIn(BaseModel): alert_id:int; source:str; title:str; description:str=''; source_ip:str|None=None; destination_ip:str|None=None; severity:str='low'; raw_payload:dict[str,Any]={}
class TriageOut(BaseModel): severity:str; verdict:str; summary:str; recommendations:list[str]; confidence:float; provider:str; model:str|None=None; enrichment:dict[str,Any]={}; error_message:str|None=None
class IncidentIn(BaseModel): alert_id:int; title:str=Field(min_length=1,max_length=255); assignee_id:int|None=None; notes:str=''; reviewed_verdict:str|None=None
class IncidentPatch(BaseModel): status:str|None=None; assignee_id:int|None=None; notes:str|None=None; reviewed_verdict:str|None=None
class IncidentOut(BaseModel): model_config=ConfigDict(from_attributes=True); id:int; alert_id:int; title:str; status:str; assignee_id:int|None; notes:str; reviewed_verdict:str|None; created_at:datetime; updated_at:datetime
