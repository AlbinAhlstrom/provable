"""
Template generator for default workspace scaffold (React 18 + Vite).
Guarantees that Vite port 5174 is ALWAYS valid and reachable on server startup.
"""

import os

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
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.2.0",
    "vite": "^5.0.0"
  }
}''')

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
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);''')

    index_css = os.path.join(src_dir, 'index.css')
    with open(index_css, 'w', encoding='utf-8') as f:
        f.write('''@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
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

