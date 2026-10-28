import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { api, download } from './api';
import './styles.css';
import {
  ShieldAlert,
  ShieldCheck,
  Activity,
  Flame,
  CheckCircle2,
  Clock,
  FileText,
  FileSpreadsheet,
  Layers,
  User as UserIcon,
  LogOut,
  Sun,
  Moon,
  RefreshCw,
  Download,
  Search,
  Filter,
  Server,
  Eye,
  X,
  AlertTriangle,
  ChevronRight,
  Database,
  ExternalLink,
  Info,
  SlidersHorizontal
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';

type User = {
  username: string;
  full_name: string;
  roles: string[];
};

type TriageData = {
  severity?: string;
  verdict?: string;
  summary?: string;
  recommendations?: string[];
  confidence?: number;
  provider?: string;
  model?: string;
  error_message?: string;
};

type Alert = {
  id: number;
  external_id?: string;
  title: string;
  description?: string;
  severity: string;
  status: string;
  source: string;
  source_ip?: string;
  destination_ip?: string;
  received_at: string;
  completed_at?: string;
  triage?: TriageData;
  raw_payload?: any;
};

type Incident = {
  id: number;
  alert_id: number;
  title: string;
  status: string;
  notes?: string;
  created_at: string;
};

type AuditEntry = {
  id: number;
  actor: string;
  module: string;
  action: string;
  result: string;
  occurred_at: string;
  resource_id?: number;
};

// Severidad badge helper
const SeverityBadge = ({ severity }: { severity: string }) => {
  const s = (severity || 'low').toLowerCase();
  return (
    <span className={`badge ${s}`}>
      <span className="pulse-dot" style={{
        backgroundColor: s === 'critical' ? '#f43f5e' : s === 'high' ? '#f97316' : s === 'medium' ? '#facc15' : '#10b981',
        boxShadow: 'none'
      }} />
      {s}
    </span>
  );
};

// LOGIN COMPONENT
function Login({ onLogin }: { onLogin: (u: User) => void }) {
  const [u, setU] = useState('analista');
  const [p, setP] = useState('analista-local-2026');
  const [err, setErr] = useState('');
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setErr('');
    try {
      const x = await api('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username: u, password: p })
      });
      localStorage.setItem('soc_token', x.access_token);
      onLogin(x.user);
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  const fillQuick = (user: string, pass: string) => {
    setU(user);
    setP(pass);
  };

  return (
    <div className="login-page">
      <div className="login-box">
        <div className="login-brand">
          <div className="brand-icon">
            <ShieldAlert size={28} />
          </div>
          <h2>SOC-Lite Portal</h2>
          <p>Triaje Inteligente y Automatización de Seguridad</p>
        </div>

        <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div className="form-group">
            <label>Usuario</label>
            <input
              className="form-input"
              value={u}
              onChange={e => setU(e.target.value)}
              placeholder="Ej. analista"
              required
            />
          </div>
          <div className="form-group">
            <label>Contraseña</label>
            <input
              className="form-input"
              type="password"
              value={p}
              onChange={e => setP(e.target.value)}
              required
            />
          </div>

          {err && <div className="error-alert">{err}</div>}

          <button className="btn-primary" disabled={loading}>
            {loading ? 'Accediendo...' : 'Iniciar Sesión'}
          </button>
        </form>

        <div className="quick-users">
          <p>Credenciales de demostración rápida:</p>
          <div className="quick-buttons">
            <button
              type="button"
              className="quick-btn"
              onClick={() => fillQuick('admin', 'admin-local-2026')}
            >
              Admin
            </button>
            <button
              type="button"
              className="quick-btn"
              onClick={() => fillQuick('analista', 'analista-local-2026')}
            >
              Analista
            </button>
            <button
              type="button"
              className="quick-btn"
              onClick={() => fillQuick('lector', 'lector-local-2026')}
            >
              Lector
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// DASHBOARD COMPONENT
function Dashboard({ user, onLogout }: { user: User; onLogout: () => void }) {
  const [tab, setTab] = useState<'dashboard' | 'alerts' | 'incidents' | 'reports' | 'audit'>('dashboard');
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    return (localStorage.getItem('soc_theme') as 'dark' | 'light') || 'dark';
  });
  const [sum, setSum] = useState<any>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [inc, setInc] = useState<Incident[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  // Filtros en pestaña de alertas
  const [searchQuery, setSearchQuery] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('all');

  // Aplicar tema en el documento
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('soc_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  };

  const loadData = async () => {
    setLoading(true);
    setError('');
    try {
      const [sumData, alertsData, incidentsData] = await Promise.all([
        api('/api/dashboard/summary'),
        api('/api/alerts?page_size=50'),
        api('/api/incidents')
      ]);
      setSum(sumData);
      setAlerts(alertsData.items || []);
      setInc(incidentsData || []);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleLogout = async () => {
    await api('/api/auth/logout', { method: 'POST' }).catch(() => {});
    localStorage.removeItem('soc_token');
    onLogout();
  };

  // Filtrado de alertas
  const filteredAlerts = alerts.filter(a => {
    const matchSearch =
      a.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (a.source_ip && a.source_ip.includes(searchQuery)) ||
      (a.source && a.source.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchSeverity = filterSeverity === 'all' || a.severity.toLowerCase() === filterSeverity;
    return matchSearch && matchSeverity;
  });

  return (
    <div className="shell">
      {/* SIDEBAR */}
      <aside>
        <div className="brand-wrapper">
          <div className="brand-icon">
            <ShieldAlert size={22} />
          </div>
          <div className="brand-info">
            <h2>SOC-Lite</h2>
            <span>Centro de Operaciones</span>
          </div>
        </div>

        {/* Profile */}
        <div className="profile-card">
          <div className="avatar-circle">
            <UserIcon size={18} />
          </div>
          <div className="profile-details">
            <b>{user.full_name || user.username}</b>
            <span className="role-badge">{user.roles?.join(', ') || 'Usuario'}</span>
          </div>
        </div>

        {/* Nav Items */}
        <nav className="nav-group">
          <button
            className={`nav-item ${tab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setTab('dashboard')}
          >
            <Activity size={18} />
            <span>Panel General</span>
          </button>
          <button
            className={`nav-item ${tab === 'alerts' ? 'active' : ''}`}
            onClick={() => setTab('alerts')}
          >
            <ShieldAlert size={18} />
            <span>Alertas ({alerts.length})</span>
          </button>
          <button
            className={`nav-item ${tab === 'incidents' ? 'active' : ''}`}
            onClick={() => setTab('incidents')}
          >
            <Flame size={18} />
            <span>Incidentes ({inc.length})</span>
          </button>
          <button
            className={`nav-item ${tab === 'reports' ? 'active' : ''}`}
            onClick={() => setTab('reports')}
          >
            <FileText size={18} />
            <span>Reportes</span>
          </button>
          <button
            className={`nav-item ${tab === 'audit' ? 'active' : ''}`}
            onClick={() => setTab('audit')}
          >
            <Database size={18} />
            <span>Bitácora Auditoría</span>
          </button>
        </nav>

        {/* Sidebar Footer */}
        <div className="sidebar-footer">
          <button className="theme-toggle-btn" onClick={toggleTheme} title="Cambiar tema">
            <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
              {theme === 'dark' ? 'Modo Claro' : 'Modo Oscuro'}
            </span>
          </button>
          <button className="logout-btn" onClick={handleLogout}>
            <LogOut size={16} />
            <span>Cerrar sesión</span>
          </button>
        </div>
      </aside>

      {/* CONTENT */}
      <main className="content">
        <header>
          <div>
            <div className="eyebrow">
              <span className="pulse-dot" />
              SISTEMA AUTOMATIZADO DE TRIAJE · DEMO 2026
            </div>
            <h1>
              {tab === 'dashboard' && 'Resumen Operativo'}
              {tab === 'alerts' && 'Monitor de Alertas de Seguridad'}
              {tab === 'incidents' && 'Gestión de Incidentes Críticos'}
              {tab === 'reports' && 'Exportación de Reportes Oficiales'}
              {tab === 'audit' && 'Registro de Auditoría e Inmutabilidad'}
            </h1>
          </div>

          <div className="header-actions">
            <button
              className={`btn-refresh ${loading ? 'loading' : ''}`}
              onClick={loadData}
              disabled={loading}
            >
              <RefreshCw size={15} />
              <span>{loading ? 'Actualizando...' : 'Actualizar'}</span>
            </button>
          </div>
        </header>

        {error && <div className="error-alert">{error}</div>}

        {/* VIEW: DASHBOARD */}
        {tab === 'dashboard' && (
          <>
            {/* KPI CARDS */}
            <section className="kpis">
              <div className="kpi-card kpi-blue">
                <div className="kpi-header">
                  <span className="kpi-label">Alertas Totales</span>
                  <div className="kpi-icon-bubble">
                    <ShieldAlert size={18} color="#06b6d4" />
                  </div>
                </div>
                <div className="kpi-value">{sum?.total ?? '—'}</div>
                <div className="kpi-subtext">Ingeridas desde Wazuh/OPNsense</div>
              </div>

              <div className="kpi-card kpi-amber">
                <div className="kpi-header">
                  <span className="kpi-label">Pendientes de Triaje</span>
                  <div className="kpi-icon-bubble">
                    <Clock size={18} color="#f59e0b" />
                  </div>
                </div>
                <div className="kpi-value">{sum?.pending ?? '—'}</div>
                <div className="kpi-subtext">En cola de procesamiento</div>
              </div>

              <div className="kpi-card kpi-emerald">
                <div className="kpi-header">
                  <span className="kpi-label">Procesadas por IA</span>
                  <div className="kpi-icon-bubble">
                    <CheckCircle2 size={18} color="#10b981" />
                  </div>
                </div>
                <div className="kpi-value">{sum?.processed ?? '—'}</div>
                <div className="kpi-subtext">Veredicto y triaje asignado</div>
              </div>

              <div className="kpi-card kpi-rose">
                <div className="kpi-header">
                  <span className="kpi-label">Incidentes Abiertos</span>
                  <div className="kpi-icon-bubble">
                    <Flame size={18} color="#f43f5e" />
                  </div>
                </div>
                <div className="kpi-value">{sum?.open_incidents ?? '—'}</div>
                <div className="kpi-subtext">Casos activos para analistas</div>
              </div>
            </section>

            {/* SEVERIDAD Y ORIGENES */}
            <div className="grid-2">
              <div className="panel">
                <div className="panel-header">
                  <h2>
                    <SlidersHorizontal size={18} color="#06b6d4" />
                    Distribución por Severidad
                  </h2>
                </div>
                <div>
                  {sum?.by_severity &&
                    Object.entries(sum.by_severity).map(([sev, count]: any) => {
                      const total = sum.total || 1;
                      const pct = Math.round((Number(count) / total) * 100);
                      return (
                        <div className={`severity-row ${sev}`} key={sev}>
                          <SeverityBadge severity={sev} />
                          <div className="severity-bar-track">
                            <div className="severity-bar-fill" style={{ width: `${pct}%` }} />
                          </div>
                          <span className="severity-count">{count}</span>
                        </div>
                      );
                    })}
                </div>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <h2>
                    <Server size={18} color="#3b82f6" />
                    Principales Orígenes de Detección
                  </h2>
                </div>
                <div className="source-list">
                  {sum?.by_source?.map((src: any) => (
                    <div className="source-item" key={src.source}>
                      <span className="source-name">
                        <Server size={16} color="#60a5fa" />
                        {src.source}
                      </span>
                      <span className="source-badge">{src.count} eventos</span>
                    </div>
                  ))}
                  {(!sum?.by_source || sum.by_source.length === 0) && (
                    <div style={{ color: 'var(--text-dim)', textAlign: 'center', padding: 20 }}>
                      Sin orígenes registrados
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* RECHARTS TIMELINE */}
            <div className="panel">
              <div className="panel-header">
                <h2>
                  <Activity size={18} color="#10b981" />
                  Evolución Temporal de Eventos (Últimos 7 días)
                </h2>
              </div>
              <div className="chart-container">
                {sum?.timeline && sum.timeline.length > 0 ? (
                  <ResponsiveContainer width="100%" height={220}>
                    <AreaChart
                      data={sum.timeline}
                      margin={{ top: 10, right: 20, left: -20, bottom: 0 }}
                    >
                      <defs>
                        <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.6} />
                          <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid
                        strokeDasharray="3 3"
                        stroke={theme === 'dark' ? '#1e2e4a' : '#e2e8f0'}
                        vertical={false}
                      />
                      <XAxis
                        dataKey="date"
                        stroke={theme === 'dark' ? '#64748b' : '#94a3b8'}
                        fontSize={11}
                        tickLine={false}
                        tickFormatter={val => val.slice(5)}
                      />
                      <YAxis
                        stroke={theme === 'dark' ? '#64748b' : '#94a3b8'}
                        fontSize={11}
                        tickLine={false}
                        allowDecimals={false}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: theme === 'dark' ? '#0f172a' : '#ffffff',
                          borderColor: theme === 'dark' ? '#1e293b' : '#cbd5e1',
                          borderRadius: 8,
                          color: theme === 'dark' ? '#f1f5f9' : '#0f172a',
                          fontSize: 12
                        }}
                      />
                      <Area
                        type="monotone"
                        dataKey="count"
                        stroke="#06b6d4"
                        strokeWidth={2.5}
                        fillOpacity={1}
                        fill="url(#colorCount)"
                        name="Alertas"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div style={{ color: 'var(--text-dim)', textAlign: 'center', padding: 40 }}>
                    Sin datos de evolución temporal
                  </div>
                )}
              </div>
            </div>

            {/* TABLA RECIENTES */}
            <div className="panel">
              <div className="panel-header">
                <h2>
                  <Clock size={18} color="#f59e0b" />
                  Últimas Alertas Recibidas
                </h2>
                <button
                  className="row-action-btn"
                  onClick={() => setTab('alerts')}
                >
                  Ver todas las alertas <ChevronRight size={14} />
                </button>
              </div>
              <AlertsTable alerts={alerts.slice(0, 6)} onSelect={setSelectedAlert} />
            </div>
          </>
        )}

        {/* VIEW: ALERTS */}
        {tab === 'alerts' && (
          <div className="panel">
            <div className="panel-header">
              <h2>
                <ShieldAlert size={18} color="#06b6d4" />
                Listado Maestro de Alertas ({filteredAlerts.length})
              </h2>
            </div>

            {/* Search and Filter */}
            <div className="filter-bar">
              <div className="search-input-wrapper">
                <Search size={16} className="search-icon" />
                <input
                  type="text"
                  className="search-input"
                  placeholder="Buscar por título, IP origen o detector..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                />
              </div>

              <select
                className="filter-select"
                value={filterSeverity}
                onChange={e => setFilterSeverity(e.target.value)}
              >
                <option value="all">Todas las severidades</option>
                <option value="critical">Crítica</option>
                <option value="high">Alta</option>
                <option value="medium">Media</option>
                <option value="low">Baja</option>
              </select>
            </div>

            <AlertsTable alerts={filteredAlerts} onSelect={setSelectedAlert} />
          </div>
        )}

        {/* VIEW: INCIDENTS */}
        {tab === 'incidents' && (
          <div className="panel">
            <div className="panel-header">
              <h2>
                <Flame size={18} color="#f43f5e" />
                Incidentes Declarados ({inc.length})
              </h2>
            </div>
            <div className="incidents-grid">
              {inc.map(item => (
                <div className="incident-card" key={item.id}>
                  <div className="incident-card-header">
                    <span className="badge critical">Incidente #{item.id}</span>
                    <span className="status-pill completed">{item.status}</span>
                  </div>
                  <h3 className="incident-title">{item.title}</h3>
                  <div style={{ fontSize: 12, color: 'var(--text-dim)' }}>
                    Alerta vinculada: <b>#{item.alert_id}</b>
                  </div>
                  <div className="incident-notes">
                    <b>Observaciones del analista:</b>
                    <br />
                    {item.notes || 'Sin notas complementarias registradas.'}
                  </div>
                </div>
              ))}
              {inc.length === 0 && (
                <div style={{ color: 'var(--text-dim)', textAlign: 'center', padding: 40 }}>
                  No se registran incidentes abiertos actualmente.
                </div>
              )}
            </div>
          </div>
        )}

        {/* VIEW: REPORTS */}
        {tab === 'reports' && (
          <div className="panel">
            <div className="panel-header">
              <h2>
                <FileText size={18} color="#06b6d4" />
                Centro de Exportaciones y Cumplimiento
              </h2>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: 13, margin: '0 0 20px' }}>
              Los reportes se generan consultando en tiempo real PostgreSQL, incluyendo métricas
              de triaje, tiempos de respuesta y bitácora de eventos conforme a la norma ISO 27001 (A.8.15) y NIST CSF 2.0.
            </p>

            <div className="reports-grid">
              <div className="report-card report-pdf">
                <div className="report-card-icon">
                  <FileText size={26} />
                </div>
                <div>
                  <h3>Reporte Ejecutivo (PDF)</h3>
                  <p>
                    Documento consolidado con indicadores de gestión, desglose de severidad,
                    incidentes y recomendaciones operativas directivas.
                  </p>
                </div>
                <button className="btn-download" onClick={() => download('pdf')}>
                  <Download size={15} /> Descargar PDF
                </button>
              </div>

              <div className="report-card report-docx">
                <div className="report-card-icon">
                  <FileText size={26} />
                </div>
                <div>
                  <h3>Informe Técnico (Word)</h3>
                  <p>
                    Documento editable en formato Microsoft Word con tablas estructuradas,
                    apto para anexos de auditoría de ciberseguridad.
                  </p>
                </div>
                <button className="btn-download" onClick={() => download('docx')}>
                  <Download size={15} /> Descargar Word (.docx)
                </button>
              </div>

              <div className="report-card report-xlsx">
                <div className="report-card-icon">
                  <FileSpreadsheet size={26} />
                </div>
                <div>
                  <h3>Dataset Tabular (Excel)</h3>
                  <p>
                    Libro con 11 pestañas de análisis detallado, alertas procesadas,
                    datos crudos de correlación y fórmulas dinámicas.
                  </p>
                </div>
                <button className="btn-download" onClick={() => download('xlsx')}>
                  <Download size={15} /> Descargar Excel (.xlsx)
                </button>
              </div>
            </div>
          </div>
        )}

        {/* VIEW: AUDIT */}
        {tab === 'audit' && <AuditView />}

        {/* FOOTER */}
        <footer>
          <div className="footer-metrics">
            <div className="footer-metric-item">
              <Clock size={14} color="#06b6d4" />
              <span>Tiempo Medio de Triaje (MTTT):</span>
              <strong>
                {sum?.mttt_seconds == null ? 'sin datos' : `${Math.round(sum.mttt_seconds)} s`}
              </strong>
            </div>
            <div className="footer-metric-item">
              <ShieldCheck size={14} color="#10b981" />
              <span>Tasa Falsos Positivos:</span>
              <strong>
                {sum?.false_positive_rate == null
                  ? 'sin datos'
                  : `${Math.round(sum.false_positive_rate * 100)}%`}
              </strong>
            </div>
          </div>
          <div>
            Entorno de demostración académica · Cumple ISO/IEC 27001 (A.8.15) & NIST CSF
          </div>
        </footer>
      </main>

      {/* DETAIL MODAL */}
      {selectedAlert && (
        <AlertDetailModal alert={selectedAlert} onClose={() => setSelectedAlert(null)} />
      )}
    </div>
  );
}

// ALERT TABLE COMPONENT
function AlertsTable({
  alerts,
  onSelect
}: {
  alerts: Alert[];
  onSelect: (a: Alert) => void;
}) {
  return (
    <div className="table-responsive">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Alerta / Evento</th>
            <th>Origen</th>
            <th>Severidad</th>
            <th>Estado</th>
            <th>Veredicto IA</th>
            <th>Acción</th>
          </tr>
        </thead>
        <tbody>
          {alerts.map(a => (
            <tr key={a.id}>
              <td>
                <span className="audit-chip">#{a.id}</span>
              </td>
              <td>
                <b style={{ color: 'var(--text-main)', display: 'block' }}>{a.title}</b>
                <span className="ip-tag">{a.source_ip || 'IP no identificada'}</span>
              </td>
              <td>
                <span style={{ textTransform: 'uppercase', fontSize: 11, fontWeight: 700 }}>
                  {a.source}
                </span>
              </td>
              <td>
                <SeverityBadge severity={a.severity} />
              </td>
              <td>
                <span className={`status-pill ${a.status}`}>
                  {a.status}
                </span>
              </td>
              <td>
                <span className={`verdict-pill ${a.triage?.verdict || 'pendiente'}`}>
                  {a.triage?.verdict || 'pendiente'}
                </span>
              </td>
              <td>
                <button className="row-action-btn" onClick={() => onSelect(a)}>
                  <Eye size={13} />
                  <span>Detalle</span>
                </button>
              </td>
            </tr>
          ))}
          {alerts.length === 0 && (
            <tr>
              <td colSpan={7} style={{ textAlign: 'center', padding: 30, color: 'var(--text-dim)' }}>
                No se encontraron alertas para los criterios especificados.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

// MODAL DETAIL
function AlertDetailModal({ alert, onClose }: { alert: Alert; onClose: () => void }) {
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-dialog" onClick={e => e.stopPropagation()}>
        <button className="modal-close-btn" onClick={onClose}>
          <X size={20} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
          <span className="audit-chip">Alerta #{alert.id}</span>
          <SeverityBadge severity={alert.severity} />
          <span className={`status-pill ${alert.status}`}>{alert.status}</span>
        </div>

        <h2 style={{ margin: '0 0 14px', fontSize: 20 }}>{alert.title}</h2>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
          <div className="source-item">
            <span style={{ fontSize: 12, color: 'var(--text-dim)' }}>IP Origen:</span>
            <span className="ip-tag">{alert.source_ip || 'N/A'}</span>
          </div>
          <div className="source-item">
            <span style={{ fontSize: 12, color: 'var(--text-dim)' }}>Detector:</span>
            <span style={{ fontWeight: 700, textTransform: 'uppercase' }}>{alert.source}</span>
          </div>
        </div>

        {/* Triage Info */}
        <div className="triage-box">
          <h4>
            <Activity size={16} /> Triaje Automatizado por Inteligencia Artificial
          </h4>
          <div style={{ fontSize: 12.5, lineHeight: 1.5, marginBottom: 10 }}>
            <b>Veredicto: </b>
            <span className={`verdict-pill ${alert.triage?.verdict || 'pendiente'}`} style={{ fontSize: 13 }}>
              {alert.triage?.verdict?.toUpperCase() || 'PENDIENTE DE TRIAJE'}
            </span>
            {alert.triage?.confidence && (
              <span style={{ marginLeft: 12, color: 'var(--text-dim)' }}>
                (Confianza: {Math.round(alert.triage.confidence * 100)}%)
              </span>
            )}
          </div>

          <p style={{ margin: '8px 0', fontSize: 13, color: 'var(--text-main)', lineHeight: 1.5 }}>
            {alert.triage?.summary || 'Alerta pendiente de procesamiento por el microservicio de triaje.'}
          </p>

          {alert.triage?.recommendations && alert.triage.recommendations.length > 0 && (
            <>
              <b style={{ fontSize: 12, color: 'var(--text-muted)' }}>Acciones Recomendadas por la IA:</b>
              <ul className="recommendations-list">
                {alert.triage.recommendations.map((rec, i) => (
                  <li key={i}>{rec}</li>
                ))}
              </ul>
            </>
          )}

          {alert.triage?.provider && (
            <div style={{ marginTop: 10, fontSize: 11, color: 'var(--text-dim)' }}>
              Motor de análisis: <code>{alert.triage.provider}</code>
            </div>
          )}
        </div>

        <div style={{ fontSize: 11.5, color: 'var(--text-dim)', marginTop: 12 }}>
          Recibida el: {new Date(alert.received_at).toLocaleString()}
        </div>
      </div>
    </div>
  );
}

// AUDIT VIEW
function AuditView() {
  const [data, setData] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api('/api/audit')
      .then(res => {
        setData(res || []);
        setLoading(false);
      })
      .catch(() => {
        setData([]);
        setLoading(false);
      });
  }, []);

  return (
    <div className="panel">
      <div className="panel-header">
        <h2>
          <Database size={18} color="#06b6d4" />
          Bitácora de Auditoría Inmutable (ISO 27001 A.8.15)
        </h2>
      </div>
      <p style={{ color: 'var(--text-muted)', fontSize: 13, margin: '0 0 16px' }}>
        Registro forense de cada evento, ingreso, exportación y triaje realizado en la plataforma.
      </p>

      <div className="table-responsive">
        <table>
          <thead>
            <tr>
              <th>Fecha y Hora</th>
              <th>Actor</th>
              <th>Módulo</th>
              <th>Acción</th>
              <th>Resultado</th>
            </tr>
          </thead>
          <tbody>
            {data.map(x => (
              <tr key={x.id}>
                <td style={{ fontFamily: 'DM Mono', fontSize: 12 }}>
                  {new Date(x.occurred_at).toLocaleString()}
                </td>
                <td>
                  <span className="audit-chip" style={{ fontWeight: 700 }}>
                    {x.actor}
                  </span>
                </td>
                <td>
                  <span style={{ textTransform: 'uppercase', fontSize: 11, fontWeight: 600 }}>
                    {x.module}
                  </span>
                </td>
                <td>
                  <code style={{ color: 'var(--primary)', fontSize: 12 }}>{x.action}</code>
                </td>
                <td>
                  <span className={`status-pill ${x.result === 'ok' ? 'completed' : 'pending'}`}>
                    {x.result}
                  </span>
                </td>
              </tr>
            ))}
            {data.length === 0 && (
              <tr>
                <td colSpan={5} style={{ textAlign: 'center', padding: 30, color: 'var(--text-dim)' }}>
                  {loading ? 'Cargando registros...' : 'No hay registros de auditoría disponibles.'}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ROOT APP
function App() {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('soc_token');
    if (token) {
      api('/api/auth/me')
        .then(setUser)
        .catch(() => localStorage.removeItem('soc_token'));
    }
  }, []);

  return user ? (
    <Dashboard user={user} onLogout={() => setUser(null)} />
  ) : (
    <Login onLogin={setUser} />
  );
}

createRoot(document.getElementById('root')!).render(<App />);
