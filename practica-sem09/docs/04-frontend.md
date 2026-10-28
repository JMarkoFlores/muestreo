# 4. Frontend

React 19 + TypeScript + Vite. `src/main.tsx` contiene el flujo de login, navegación y vistas: resumen operativo, alertas, incidentes, reportes y auditoría. `src/api.ts` añade Bearer JWT y descarga exportaciones. Los KPIs, tabla, severidades y orígenes consultan `/api/dashboard/summary` y `/api/alerts`; no usan datos embebidos salvo credenciales de demo.

La interfaz muestra `sin datos` para MTTT y falsos positivos cuando no existen observaciones humanas. El rol se muestra en el perfil; el backend sigue siendo la autoridad RBAC.
