from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    full_name: str
    role: str

class DetectionRequest(BaseModel):
    value: str = Field(min_length=3, max_length=10000)
    channel: str = Field(default="web", pattern="^(web|email|sms|qr)$")

class DetectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    input_value: str
    channel: str
    risk_score: float
    verdict: str
    reasons: list[str]
    created_at: datetime

class IncidentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=240)
    severity: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    detection_id: int | None = None

class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    severity: str
    status: str
    detection_id: int | None
    assignee: str | None
    created_at: datetime

class StatsOut(BaseModel):
    detections: int
    high_risk: int
    open_incidents: int
    average_risk: float
