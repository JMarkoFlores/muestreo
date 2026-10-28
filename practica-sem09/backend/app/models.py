from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Boolean, Integer, ForeignKey, JSON, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

def now_utc(): return datetime.now(timezone.utc)

user_roles = __import__('sqlalchemy').Table('user_roles', Base.metadata,
    __import__('sqlalchemy').Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    __import__('sqlalchemy').Column('role_id', ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True))
role_permissions = __import__('sqlalchemy').Table('role_permissions', Base.metadata,
    __import__('sqlalchemy').Column('role_id', ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    __import__('sqlalchemy').Column('permission_id', ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True))

class User(Base):
    __tablename__='users'
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    username: Mapped[str]=mapped_column(String(80), unique=True, index=True)
    email: Mapped[str]=mapped_column(String(160), unique=True)
    full_name: Mapped[str]=mapped_column(String(160))
    password_hash: Mapped[str]=mapped_column(String(255))
    is_active: Mapped[bool]=mapped_column(Boolean, default=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now_utc)
    roles: Mapped[list['Role']]=relationship(secondary=user_roles, back_populates='users')

class Role(Base):
    __tablename__='roles'
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    name: Mapped[str]=mapped_column(String(40), unique=True)
    users: Mapped[list[User]]=relationship(secondary=user_roles, back_populates='roles')
    permissions: Mapped[list['Permission']]=relationship(secondary=role_permissions, back_populates='roles')

class Permission(Base):
    __tablename__='permissions'
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    code: Mapped[str]=mapped_column(String(80), unique=True)
    roles: Mapped[list[Role]]=relationship(secondary=role_permissions, back_populates='permissions')

class Alert(Base):
    __tablename__='alerts'
    __table_args__=(UniqueConstraint('dedup_key', name='uq_alert_dedup'), Index('ix_alert_received', 'received_at'), Index('ix_alert_severity', 'severity'))
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    external_id: Mapped[str|None]=mapped_column(String(160), index=True)
    source: Mapped[str]=mapped_column(String(40), default='unknown')
    title: Mapped[str]=mapped_column(String(255))
    description: Mapped[str]=mapped_column(Text, default='')
    source_ip: Mapped[str|None]=mapped_column(String(64), index=True)
    destination_ip: Mapped[str|None]=mapped_column(String(64))
    severity: Mapped[str]=mapped_column(String(20), default='low', index=True)
    status: Mapped[str]=mapped_column(String(30), default='pending', index=True)
    raw_payload: Mapped[dict]=mapped_column(JSON, default=dict)
    dedup_key: Mapped[str]=mapped_column(String(128), unique=True)
    received_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now_utc)
    completed_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
    error_message: Mapped[str|None]=mapped_column(Text)
    enrichment: Mapped['EnrichmentData|None']=relationship(back_populates='alert', uselist=False, cascade='all, delete-orphan')
    triage: Mapped['TriageResult|None']=relationship(back_populates='alert', uselist=False, cascade='all, delete-orphan')
    incidents: Mapped[list['Incident']]=relationship(back_populates='alert')

class EnrichmentData(Base):
    __tablename__='enrichment_data'
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    alert_id: Mapped[int]=mapped_column(ForeignKey('alerts.id', ondelete='CASCADE'), unique=True)
    provider: Mapped[str]=mapped_column(String(40), default='simulado')
    data: Mapped[dict]=mapped_column(JSON, default=dict)
    is_simulated: Mapped[bool]=mapped_column(Boolean, default=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now_utc)
    alert: Mapped[Alert]=relationship(back_populates='enrichment')

class TriageResult(Base):
    __tablename__='triage_results'
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    alert_id: Mapped[int]=mapped_column(ForeignKey('alerts.id', ondelete='CASCADE'), unique=True)
    severity: Mapped[str]=mapped_column(String(20))
    verdict: Mapped[str]=mapped_column(String(40))
    summary: Mapped[str]=mapped_column(Text)
    recommendations: Mapped[list]=mapped_column(JSON, default=list)
    confidence: Mapped[float]=mapped_column(default=0.0)
    provider: Mapped[str]=mapped_column(String(40), default='heuristic-demo')
    model: Mapped[str|None]=mapped_column(String(80))
    error_message: Mapped[str|None]=mapped_column(Text)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now_utc)
    alert: Mapped[Alert]=relationship(back_populates='triage')

class Incident(Base):
    __tablename__='incidents'
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    alert_id: Mapped[int]=mapped_column(ForeignKey('alerts.id', ondelete='RESTRICT'))
    title: Mapped[str]=mapped_column(String(255))
    status: Mapped[str]=mapped_column(String(30), default='open', index=True)
    assignee_id: Mapped[int|None]=mapped_column(ForeignKey('users.id', ondelete='SET NULL'))
    notes: Mapped[str]=mapped_column(Text, default='')
    reviewed_verdict: Mapped[str|None]=mapped_column(String(40))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    alert: Mapped[Alert]=relationship(back_populates='incidents')
    assignee: Mapped[User|None]=relationship()

class AuditLog(Base):
    __tablename__='audit_log'
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    actor: Mapped[str]=mapped_column(String(160), index=True)
    occurred_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now_utc, index=True)
    module: Mapped[str]=mapped_column(String(80))
    action: Mapped[str]=mapped_column(String(120))
    result: Mapped[str]=mapped_column(String(30))
    resource_type: Mapped[str|None]=mapped_column(String(80))
    resource_id: Mapped[str|None]=mapped_column(String(120))
    correlation_id: Mapped[str|None]=mapped_column(String(80), index=True)
    details: Mapped[dict]=mapped_column(JSON, default=dict)
