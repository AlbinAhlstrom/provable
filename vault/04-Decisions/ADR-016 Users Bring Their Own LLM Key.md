# ADR-016: Users Bring Their Own LLM Key

## Context
The repository is public and anyone can sign up through Clerk ([[ADR-013 Clerk Login]]). Every hosted build ran on the operator's key, so any user could spend the operator's money. Generated code also runs on the engine's machine, and it inherited the engine's environment, so a pitch could have that key read.

## Decision
- **A hosted engine (`CLERK_ISSUER` set) spends the signed-in user's own key.** The user adds it in the Studio (`LlmKeyButton.tsx`, `/api/llm-key`) and names a provider: `gemini`, `openai` or `anthropic`. A user never names an endpoint.
- **The operator's key is never a fallback.** Only users listed in `LLM_HOUSE_USERS` run on the operator's settings. A user without a key gets a call that fails and says where to add one.
- **Keys rest encrypted.** `adapters/llm_key_store.py` seals them with `PROVABLE_KEY_SECRET` (Fernet) in `PROVABLE_KEYS_DB`, outside the workspace, so a reset keeps them. Each sealed value names its owner, so a copied row is refused. The full key never leaves the engine again; the Studio sees the last four characters.
- **One user at a time.** A run's calls come from pool threads, so the key is held for the whole process, like `run_options.py`. `entrypoints/llm_lease.py` holds it for each writing request, background work included. Another user's writing request is answered 409 while it is held. Reads and `/api/llm-key` are never refused.
- **Generated code gets no secrets.** `llm_credentials.seal_environment` moves the secrets out of `os.environ` when the app loads, and bars other processes from reading the engine (`PR_SET_DUMPABLE`). `deploy/start.sh` runs everything as the unprivileged user `provable` and starts the generated API and preview with a bare environment.
- Traces scrub every key: the sealed ones and the held user's.

A local engine (no `CLERK_ISSUER`) is unchanged: the `.env` decides, and `/api/llm-key` answers `managed: false`.

## Consequences
- Run time and token cost per build do not change. The cost moves from the operator to the user. Prepaid balance (ADR-013) stays possible on top of this.
- One writing user at a time: the engine has one workspace anyway, so a second build would have tangled with the first.
- A key is not tried against its provider when saved: a wrong key shows as a failed build, with the provider's reason.
- Generated code runs as the same user as the engine. It can read the ciphertext and could delete the key file, but it holds no secret to open it.
- Users still share one workspace: they can see and overwrite each other's app.
- Without a Fly volume on `/data`, saved keys disappear on every deploy.

## Configuration
Fly (engine): `PROVABLE_KEY_SECRET`, optionally `LLM_HOUSE_USERS`. Make the secret with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`. Changing it makes every saved key unreadable, and users must save theirs again.

## Status
Accepted.
