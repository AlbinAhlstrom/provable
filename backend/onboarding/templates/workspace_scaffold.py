"""
Template generator for default workspace scaffold (React 18 + Vite).
Guarantees that Vite port 5174 is ALWAYS valid and reachable on server startup.
"""

import json
import os
import shutil
import subprocess
from typing import Callable, Optional

def _npm_install(cwd: str) -> None:
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if not npm:
        raise RuntimeError("npm is not installed, so the generated app's dependencies cannot be installed.")
    result = subprocess.run([npm, "install", "--no-audit", "--no-fund"], cwd=cwd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(f"npm install failed in the workspace: {(result.stderr or result.stdout)[-800:]}")


def ensure_workspace_dependencies(ws_base: str, runner: Optional[Callable[[str], None]] = None) -> bool:
    """Installs the workspace's declared npm packages when any is missing from node_modules.

    The scaffold's package.json is rewritten on every reset/kickstart, so a package added to it (or a fresh
    clone) would otherwise leave the generated app crashing on an unresolved import. Returns True when an
    install ran; raises if it fails (no silent fallback).
    """
    pkg_path = os.path.join(ws_base, "package.json")
    if not os.path.exists(pkg_path):
        return False
    with open(pkg_path, "r", encoding="utf-8") as f:
        pkg = json.load(f)
    declared = list(pkg.get("dependencies", {})) + list(pkg.get("devDependencies", {}))
    missing = [d for d in declared if not os.path.isdir(os.path.join(ws_base, "node_modules", *d.split("/")))]
    if not missing:
        return False
    (runner or _npm_install)(ws_base)
    return True


def create_default_workspace_scaffold(ws_base: str):
    """Write default clean React 18 + Vite scaffold into workspace so Vite port 5174 is ALWAYS valid."""
    src_dir = os.path.join(ws_base, 'src')
    os.makedirs(src_dir, exist_ok=True)

    package_json = os.path.join(ws_base, 'package.json')
    with open(package_json, 'w', encoding='utf-8') as f:
        f.write('''{
  "name": "workspace-app",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite --port 5174 --host",
    "build": "vite build",
    "preview": "vite preview --port 5174"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lucide-react": "^0.344.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.4",
    "typescript": "^5.2.0",
    "vite": "^5.0.0"
  }
}''')

    # Generated UIs use Tailwind classes: bundle Tailwind in the build instead of relying on a runtime CDN.
    with open(os.path.join(ws_base, 'tailwind.config.js'), 'w', encoding='utf-8') as f:
        f.write('''/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: { extend: {} },
  plugins: [],
}
''')
    with open(os.path.join(ws_base, 'postcss.config.js'), 'w', encoding='utf-8') as f:
        f.write('''export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
''')

    tsconfig_json = os.path.join(ws_base, 'tsconfig.json')
    with open(tsconfig_json, 'w', encoding='utf-8') as f:
        f.write('''{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": false
  },
  "include": ["src"]
}''')

    vite_config = os.path.join(ws_base, 'vite.config.ts')
    with open(vite_config, 'w', encoding='utf-8') as f:
        f.write('''import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    strictPort: true,
    host: true,
    proxy: {
      '/batches': 'http://localhost:8000',
      '/allocate': 'http://localhost:8000',
      '/api': 'http://localhost:8000'
    }
  }
});''')

    index_html = os.path.join(ws_base, 'index.html')
    with open(index_html, 'w', encoding='utf-8') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Provable Clean Workspace</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  </head>
  <body style="margin: 0; background: #0f172a; color: #f8fafc; font-family: 'Outfit', sans-serif;">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>''')

    main_tsx = os.path.join(src_dir, 'main.tsx')
    with open(main_tsx, 'w', encoding='utf-8') as f:
        f.write('''import React from 'react';
import ReactDOM from 'react-dom/client';
import * as AppModule from './App';
import './index.css';

const App = (AppModule as any).default || (AppModule as any).App;

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {App ? <App /> : <div style={{ color: 'red', padding: 20 }}>Failed to load App component</div>}
  </React.StrictMode>
);''')

    index_css = os.path.join(src_dir, 'index.css')
    with open(index_css, 'w', encoding='utf-8') as f:
        f.write('''@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
@tailwind base;
@tailwind components;
@tailwind utilities;

body { margin: 0; background: #0f172a; color: #f8fafc; font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }''')

    app_tsx = os.path.join(src_dir, 'App.tsx')
    with open(app_tsx, 'w', encoding='utf-8') as f:
        f.write('''import React from 'react';

export default function App() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: '#0f172a', color: '#f8fafc', padding: '2rem', textAlign: 'center' }}>
      <div style={{ background: 'rgba(30, 41, 59, 0.7)', border: '1px solid #334155', borderRadius: '1rem', padding: '2.5rem', maxWidth: '600px', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.5)' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 700, margin: '0 0 1rem 0', color: '#38bdf8' }}>
          🌌 Workspace Clean & Ready
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '1rem', lineHeight: 1.6, margin: '0 0 1.5rem 0' }}>
          This workspace is initialized. Enter a business pitch in the <strong>Domain</strong> tab of Provable Studio to discover aggregates and synthesize your live application stack.
        </p>
        <div style={{ background: '#0f172a', padding: '0.75rem 1rem', borderRadius: '0.5rem', border: '1px solid #1e293b', fontSize: '0.85rem', color: '#10b981', fontWeight: 600 }}>
          ● Vite Dev Server Port 5174 Online & Active
        </div>
      </div>
    </div>
  );
}''')

    app_py = os.path.join(src_dir, 'app.py')
    if not os.path.exists(app_py):
        with open(app_py, 'w', encoding='utf-8') as f:
            f.write('''"""
FastAPI Main Application Entrypoint — Instant OpenAPI Generator.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Generated Enterprise Domain API",
    description="Deterministic Domain-Driven API automatically projected from domain models.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "domain-api"}
''')

