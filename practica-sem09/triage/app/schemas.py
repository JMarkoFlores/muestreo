from typing import Any
from pydantic import BaseModel, Field
class AlertData(BaseModel):
    alert_id:int|None=None; source:str='unknown'; title:str=Field(min_length=1); description:str=''; source_ip:str|None=None; destination_ip:str|None=None; severity:str='low'; raw_payload:dict[str,Any]={}
class TriageResponse(BaseModel):
    severity:str; verdict:str; summary:str; recommendations:list[str]; confidence:float=Field(ge=0,le=1); provider:str; model:str|None=None; enrichment:dict[str,Any]={}; error_message:str|None=None
