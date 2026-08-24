# Bug Reproduction & Live Stack Testing Policy

## Översikt & Syfte
För att säkerställa hög tillförlitlighet, förhindra regressionsfel och eliminera runtime-överraskningar (såsom utebliven serveranslutning på `localhost:5174` eller brutna build-scripts), gäller en strikt policy för alla AI-agenter och utvecklare: **Varje fel som identifieras ska omedelbart förses med ett automatiserat regressionstest som reproducerar och verifierar lösningen.**

---

## De 3 Gyllene Reglerna för Felhantering

### 1. Reproduktion via Automatiserat Integrationstest
När en bugg upptäcks (t.ex. en felande endpoint, saknad CLI-beroende, trasig TypeScript-typning eller timeout vid dev-serverstart):
1. Skriv **alltid** ett automatiserat test först i `backend/tests/integration/` eller `backend/tests/unit/`.
2. Kör testet och bekräfta att det fångar problemet.
3. Genomför fixen i backend-källkoden / generatorerna (aldrig direkt i `workspace/`).
4. Verifiera att testet blir 100% grönt (`PASS`).

### 2. Tri-Service Live Stack Invariant
AppGen-plattformen består av tre sammankopplade tjänster som alltid ska vara verifierade:
- **Port 8000 (FastAPI Backend Engine)**: REST-endpoints, DDD-servicelager och OpenAPI-schema (`/openapi.json`).
- **Port 5173 (PM Studio Frontend)**: React 18 / TypeScript / Vite-användargränssnittet (`frontend/`).
- **Port 5174 (Workspace Live Preview)**: Sandlådemiljön som kör den genererade koden (`workspace/`).

### 3. Noll "Phantom Node Modules" & Fullständig Scaffolding
- `workspace/` måste alltid innehålla giltig `package.json`, `tsconfig.json` och `vite.config.ts`.
- `run.py` och testsviter verifierar att både `frontend/node_modules/vite` och `workspace/node_modules/vite` är installerade och redo.
- Start-processen väntar in och bekräftar att alla tre portar (`8000`, `5173`, `5174`) lyssnar innan sessionen lämnas över till användaren.

---

## Relevanta Testfiler
- `backend/tests/integration/test_app_startup_and_preview_connectivity.py`: Verifierar komplett scaffolding, TypeScript-konfiguration och felfri Vite-kompilering för både PM Studio och Workspace Preview.
- `backend/tests/integration/test_jsx_compilation_integrity.py`: Verifierar AST- och JSX-kompileringsintegritet för genererade React-komponenter.
