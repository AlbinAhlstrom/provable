/** Base URL of the engine API. Empty in development (Vite proxies /api); set VITE_ENGINE_URL when hosted. */
export const ENGINE_URL: string = (import.meta.env.VITE_ENGINE_URL ?? '').replace(/\/$/, '');

/** Origin of the generated app's preview server. */
export const PREVIEW_URL: string = import.meta.env.VITE_PREVIEW_URL ?? 'http://localhost:5174';

const nativeFetch = window.fetch.bind(window);

type TokenGetter = () => Promise<string | null>;
let getToken: TokenGetter | null = null;

/** Registers the signed-in session's token source; /api calls carry it as a Bearer token. */
export function setTokenGetter(getter: TokenGetter | null): void {
  getToken = getter;
}

/** Sends relative /api/* calls to the engine (with the session token when signed in); everything else is untouched. */
export function installEngineFetch(): void {
  window.fetch = async (input, init) => {
    if (typeof input !== 'string' || !input.startsWith('/api/')) return nativeFetch(input, init);
    const token = getToken ? await getToken() : null;
    const headers = new Headers(init?.headers);
    if (token) headers.set('Authorization', `Bearer ${token}`);
    return nativeFetch(ENGINE_URL + input, { ...init, headers });
  };
}
