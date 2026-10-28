from contextlib import asynccontextmanager
import csv
import io
import secrets
from datetime import datetime, timezone
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from .config import ALERT_API_KEY, CORS_ORIGINS, ETL_API_KEY
from .db import Base, SessionLocal, engine, get_db
from .detector import analyze
from .models import AuditLog, Detection, Incident, Indicator, User
from .schemas import (
    DetectionOut, DetectionRequest, IncidentCreate, IncidentOut, LoginRequest,
    StatsOut, TokenResponse, UserOut,
)
from .security import create_access_token, get_current_user, hash_password, require_roles, verify_password

ADMIN_EMAIL = "admin@sentinelbank.com"

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if not db.scalar(select(User).where(User.email == ADMIN_EMAIL)):
            db.add(User(email=ADMIN_EMAIL, full_name="Administrador SOC", role="admin", password_hash=hash_password("postgres")))
            db.commit()
    yield

app = FastAPI(
    title="AntiPhishing Bank API",
    version="1.1.0",
    description="API defensiva para análisis, respuesta, auditoría y automatización de amenazas de phishing.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def audit(db: Session, actor: str, action: str, resource: str, details: dict | None = None):
    db.add(AuditLog(actor=actor, action=action, resource=resource, details=details or {}))


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok", "service": "antiphishing-api", "version": app.version}


@app.post("/api/v1/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if user and user.failed_attempts >= 5:
        raise HTTPException(status_code=423, detail="Usuario bloqueado temporalmente por intentos fallidos")
    if not user or not verify_password(payload.password, user.password_hash):
        if user:
            try:
                user.failed_attempts = (user.failed_attempts or 0) + 1
                audit(db, user.email, "auth.login_failed", "session", {"attempts": user.failed_attempts})
                db.commit()
            except Exception:
                db.rollback()
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    token = create_access_token(user)
    try:
        user.failed_attempts = 0
        audit(db, user.email, "auth.login", "session")
        db.commit()
    except Exception:
        # El login no debe quedar bloqueado por una tabla de auditoría antigua.
        db.rollback()
    return TokenResponse(access_token=token)


@app.get("/api/v1/auth/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@app.get("/api/v1/dashboard/stats", response_model=StatsOut)
def dashboard_stats(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    total = db.scalar(select(func.count(Detection.id))) or 0
    high = db.scalar(select(func.count(Detection.id)).where(Detection.risk_score >= 50)) or 0
    open_cases = db.scalar(select(func.count(Incident.id)).where(Incident.status != "closed")) or 0
    avg = db.scalar(select(func.avg(Detection.risk_score))) or 0
    return StatsOut(detections=total, high_risk=high, open_incidents=open_cases, average_risk=round(float(avg), 2))


@app.get("/api/v1/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = list(db.scalars(select(Detection).order_by(Detection.created_at.desc()).limit(200)))
    channels = {channel: sum(1 for row in rows if row.channel == channel) for channel in ("web", "email", "sms", "qr")}
    verdicts = {verdict: sum(1 for row in rows if row.verdict == verdict) for verdict in ("low", "medium", "high", "critical")}
    recent = [{"id": row.id, "input_value": row.input_value, "channel": row.channel, "risk_score": row.risk_score, "verdict": row.verdict, "created_at": row.created_at} for row in rows[:10]]
    return {"channels": channels, "verdicts": verdicts, "recent": recent, "generated_at": datetime.now(timezone.utc)}


@app.post("/api/v1/detections/analyze", response_model=DetectionOut)
def create_detection(payload: DetectionRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    score, verdict, reasons = analyze(payload.value)
    matched_indicator = db.scalar(select(Indicator).where(func.lower(Indicator.value) == payload.value.strip().lower()))
    if matched_indicator:
        score = max(score, 90.0)
        verdict = "critical"
        reasons.append(f"Coincide con indicador importado desde {matched_indicator.source}")
    detection = Detection(input_value=payload.value, channel=payload.channel, risk_score=score, verdict=verdict, reasons=reasons)
    db.add(detection)
    audit(db, user.email, "detection.created", "detection", {"channel": payload.channel, "verdict": verdict})
    db.commit()
    db.refresh(detection)
    return detection


@app.get("/api/v1/detections", response_model=list[DetectionOut])
def list_detections(
    limit: int = Query(100, ge=1, le=500),
    channel: str | None = None,
    verdict: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(Detection).order_by(Detection.created_at.desc()).limit(limit)
    if channel:
        query = query.where(Detection.channel == channel)
    if verdict:
        query = query.where(Detection.verdict == verdict)
    return list(db.scalars(query))


@app.post("/api/v1/etl/import")
def import_indicators(payload: dict, x_etl_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    if not x_etl_key or not secrets.compare_digest(x_etl_key, ETL_API_KEY):
        raise HTTPException(status_code=401, detail="Clave ETL inválida")
    records = payload.get("records", []) if isinstance(payload, dict) else []
    if isinstance(records, dict):
        records = [records]
    imported = 0
    for record in records[:500]:
        if not isinstance(record, dict):
            continue
        value = record.get("url") or record.get("phish_url") or record.get("value")
        if value:
            db.add(Indicator(value=str(value)[:500], indicator_type="url", source=str(payload.get("source", "public"))[:120], metadata_json={"batch": payload.get("batch", "manual")}))
            imported += 1
    db.commit()
    return {"status": "accepted", "imported": imported, "source": payload.get("source", "unknown")}


@app.get("/api/v1/indicators")
def list_indicators(limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return list(db.scalars(select(Indicator).order_by(Indicator.created_at.desc()).limit(limit)))


@app.get("/api/v1/dataset")
def dataset_info(_: User = Depends(get_current_user)):
    return {
        "name": "PhishTank Online Valid",
        "source": "https://phishtank.org/",
        "license": "Consultar términos vigentes de PhishTank antes de redistribuir datos",
        "format": "JSON",
        "pipeline": ["descarga programada n8n", "validación", "deduplicación", "almacenamiento como Indicator", "auditoría de lote"],
        "versioning": "batch timestamp + source metadata",
        "status": "ready_for_import",
    }


@app.post("/api/v1/alerts/webhook")
def receive_alert(payload: dict, x_alert_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    if not x_alert_key or not secrets.compare_digest(x_alert_key, ALERT_API_KEY):
        raise HTTPException(status_code=401, detail="Clave de alertas inválida")
    severity = str(payload.get("severity", "high"))
    if severity not in {"low", "medium", "high", "critical"}:
        severity = "high"
    incident = Incident(title=str(payload.get("title", "Alerta antiphishing recibida"))[:240], severity=severity, assignee="soc-automation")
    db.add(incident)
    audit(db, "n8n", "alert.received", "incident", {"source": payload.get("source", "webhook"), "severity": severity})
    db.commit()
    db.refresh(incident)
    return {"status": "accepted", "incident_id": incident.id}

@app.post("/api/v1/incidents", response_model=IncidentOut)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.detection_id is not None and not db.get(Detection, payload.detection_id):
        raise HTTPException(status_code=404, detail="Detección asociada no encontrada")
    incident = Incident(title=payload.title, severity=payload.severity, detection_id=payload.detection_id, assignee=user.email)
    db.add(incident)
    audit(db, user.email, "incident.created", "incident", {"severity": payload.severity})
    db.commit()
    db.refresh(incident)
    return incident


@app.get("/api/v1/incidents", response_model=list[IncidentOut])
def list_incidents(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return list(db.scalars(select(Incident).order_by(Incident.created_at.desc()).limit(100)))


@app.patch("/api/v1/incidents/{incident_id}", response_model=IncidentOut)
def update_incident(incident_id: int, status: Literal["open", "triage", "investigating", "contained", "closed"], db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    incident.status = status
    incident.updated_at = datetime.now(timezone.utc)
    audit(db, user.email, "incident.updated", "incident", {"id": incident_id, "status": status})
    db.commit()
    db.refresh(incident)
    return incident


@app.get("/api/v1/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    return list(db.scalars(select(User).order_by(User.created_at.desc())))


@app.get("/api/v1/audit")
def list_audit(limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db), _: User = Depends(require_roles("admin", "auditor"))):
    return list(db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)))


@app.get("/api/v1/workflows")
def workflows(_: User = Depends(get_current_user)):
    return [
        {"id": "dataset-ingestion", "name": "Ingesta programada de PhishTank", "trigger": "Cada 24 horas", "output": "Indicadores almacenados en PostgreSQL", "file": "n8n/workflows/dataset-ingestion.json", "status": "auto-imported"},
        {"id": "incident-alert", "name": "Alertas y escalamiento SOC", "trigger": "Webhook de alerta", "output": "Notificación y escalamiento a stakeholders", "file": "n8n/workflows/incident-alert.json", "status": "auto-imported"},
        {"id": "scheduled-report", "name": "Reporte ejecutivo programado", "trigger": "Cada lunes 08:00", "output": "PDF enviado por correo a stakeholders", "file": "n8n/workflows/scheduled-report.json", "status": "auto-imported"},
    ]


@app.get("/api/v1/ai/status")
def ai_status(_: User = Depends(get_current_user)):
    return {
        "langchain": {"status": "design-ready", "use": "cadenas de análisis y RAG con guardrails"},
        "langflow": {"status": "design-ready", "use": "prototipado visual de los flujos SOC"},
        "models": ["Ollama (local)", "OpenAI/Azure OpenAI (opcional)"],
        "guardrails": ["no ejecución automática de acciones críticas", "registro de prompts y respuestas", "revisión humana"],
    }


@app.get("/api/v1/reports/export")
def export_report(format: Literal["csv", "xlsx", "docx", "pdf"] = "csv", db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = list(db.scalars(select(Detection).order_by(Detection.created_at.desc()).limit(1000)))
    headers = ["id", "indicator", "channel", "risk_score", "verdict", "created_at"]
    values = [[row.id, row.input_value, row.channel, row.risk_score, row.verdict, row.created_at.isoformat()] for row in rows]
    filename = f"antiphishing-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    audit(db, user.email, "report.exported", "report", {"format": format, "rows": len(values)})
    db.commit()
    if format == "csv":
        stream = io.StringIO()
        writer = csv.writer(stream)
        writer.writerow(headers); writer.writerows(values)
        return Response(stream.getvalue(), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={filename}.csv"})
    if format == "xlsx":
        from openpyxl import Workbook
        output = io.BytesIO(); workbook = Workbook(); sheet = workbook.active; sheet.title = "Detections"
        sheet.append(headers)
        for value in values: sheet.append(value)
        workbook.save(output); output.seek(0)
        return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment; filename={filename}.xlsx"})
    if format == "docx":
        from docx import Document
        output = io.BytesIO(); document = Document(); document.add_heading("SentinelBank - Reporte Antiphishing", 0); document.add_paragraph(f"Generado: {datetime.now(timezone.utc).isoformat()}")
        table = document.add_table(rows=1, cols=len(headers))
        for cell, header in zip(table.rows[0].cells, headers): cell.text = header
        for value in values[:100]:
            for cell, item in zip(table.add_row().cells, value): cell.text = str(item)
        document.save(output); output.seek(0)
        return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={"Content-Disposition": f"attachment; filename={filename}.docx"})
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    output = io.BytesIO(); pdf = canvas.Canvas(output, pagesize=A4); pdf.setFont("Helvetica-Bold", 16); pdf.drawString(42, 800, "SentinelBank - Reporte Antiphishing"); pdf.setFont("Helvetica", 9); pdf.drawString(42, 782, f"Generado: {datetime.now(timezone.utc).isoformat()}")
    y = 755
    for value in values[:40]:
        pdf.drawString(42, y, f"#{value[0]} | {value[2]} | score={value[3]} | {value[4]} | {str(value[1])[:70]}"); y -= 16
        if y < 45: pdf.showPage(); y = 800
    pdf.save(); output.seek(0)
    return StreamingResponse(output, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={filename}.pdf"})
