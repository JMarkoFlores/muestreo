import { existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { spawnSync } from 'node:child_process'

const root = process.cwd()
const dist = join(root, 'dist')
rmSync(dist, { recursive: true, force: true })
mkdirSync(join(dist, 'assets'), { recursive: true })
const pnpmEsbuild = join(root, 'node_modules', '.pnpm', '@esbuild+win32-x64@0.25.12', 'node_modules', '@esbuild', 'win32-x64', 'esbuild.exe')
const npmWindowsEsbuild = join(root, 'node_modules', '@esbuild', 'win32-x64', 'esbuild.exe')
const directEsbuild = join(root, 'node_modules', 'esbuild', 'bin', process.platform === 'win32' ? 'esbuild.exe' : 'esbuild')
const candidates = process.platform === 'win32' ? [pnpmEsbuild, npmWindowsEsbuild, directEsbuild, join(root, 'node_modules', 'esbuild', 'bin', 'esbuild')] : [directEsbuild, pnpmEsbuild]
const esbuild = candidates.find(existsSync)
if (!esbuild) throw new Error(`No se encontró esbuild. Rutas revisadas: ${candidates.join(', ')}`)
const result = spawnSync(esbuild, ['src/main.tsx', '--bundle', '--minify', '--format=esm', '--outfile=dist/assets/app.js', '--loader:.tsx=tsx', '--loader:.ts=ts', '--loader:.css=css'], { stdio: 'inherit', shell: false })
if (result.status !== 0) process.exit(result.status ?? 1)
const html = readFileSync(join(root, 'index.html'), 'utf8').replace('/src/main.tsx', '/assets/app.js').replace('</head>', '<link rel="stylesheet" href="/assets/app.css" /></head>')
writeFileSync(join(dist, 'index.html'), html)
console.log('Frontend compilado en dist/')
