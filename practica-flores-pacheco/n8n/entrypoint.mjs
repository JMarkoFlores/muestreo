import { existsSync, writeFileSync } from 'node:fs'
import { spawn, spawnSync } from 'node:child_process'

const n8n = '/usr/local/bin/n8n'
const marker = '/home/node/.n8n/.sentinelbank-workflows-imported'

if (!existsSync(marker)) {
  const imported = spawnSync(n8n, ['import:workflow', '--separate', '--input=/seed/workflows'], { stdio: 'inherit', env: process.env })
  if (imported.status !== 0) process.exit(imported.status ?? 1)
  writeFileSync(marker, new Date().toISOString())
}

const server = spawn(n8n, ['start'], { stdio: 'inherit', env: process.env })
for (const signal of ['SIGTERM', 'SIGINT']) process.on(signal, () => server.kill(signal))
server.on('exit', (code, signal) => process.exit(code ?? (signal ? 1 : 0)))
