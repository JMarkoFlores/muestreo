from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, alerts, dashboard, incidents, reports, audit, demo, internal, users
app=FastAPI(title='SOC-Lite API',version='1.0.0',description='API académica para triaje de alertas')
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_list,allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
app.include_router(auth.router); app.include_router(alerts.router); app.include_router(dashboard.router); app.include_router(incidents.router); app.include_router(reports.router); app.include_router(audit.router); app.include_router(demo.router); app.include_router(internal.router); app.include_router(users.router)
@app.get('/health')
def health(): return {'status':'ok','service':'backend','demo_mode':settings.demo_mode}
@app.get('/')
def root(): return {'name':'SOC-Lite','docs':'/docs','status':'operational'}
