# ADR-013: Clerk Login

## Context
Studio and engine are public (Vercel and Fly). Generation costs money, so every `/api` call must come from a known user, and billing (prepaid balance) needs a user id to attach to.

## Decision
- Login is hosted by Clerk. Studio wraps the app in `AuthGate` (`frontend/src/AuthGate.tsx`); `engine.ts` adds the session token as a Bearer header on every `/api` call.
- The engine verifies the token (RS256, issuer, expiry) in `adapters/clerk_auth.py` against the issuer's JWKS. `entrypoints/auth.py` exposes `require_user`, applied to every router in `app.py`.
- Auth is off when it is not configured: no `VITE_CLERK_PUBLISHABLE_KEY` in Studio, no `CLERK_ISSUER` in the engine. Local development and tests need no Clerk account.

## Configuration
- Vercel (Studio): `VITE_CLERK_PUBLISHABLE_KEY`.
- Fly (engine): `CLERK_ISSUER`, the Clerk Frontend API URL (`https://<name>.clerk.accounts.dev`).

## Not yet done
Hosted builds run on the user's own LLM key ([[ADR-016 Users Bring Their Own LLM Key]]). Every user still shares one workspace. Per-user workspaces and the prepaid balance (Stripe top-ups, a ledger, $1 per proved app) come next.
