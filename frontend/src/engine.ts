/** Base URL of the engine API. Empty in development (Vite proxies /api); set VITE_ENGINE_URL when hosted. */
export const ENGINE_URL: string = (import.meta.env.VITE_ENGINE_URL ?? '').replace(/\/$/, '');

/** Origin of the generated app's preview server. */
export const PREVIEW_URL: string = import.meta.env.VITE_PREVIEW_URL ?? 'http://localhost:5174';

const nativeFetch = window.fetch.bind(window);

/** Sends relative /api/* calls to the engine; everything else is untouched. */
export function installEngineFetch(): void {
  if (!ENGINE_URL) return;
  window.fetch = (input, init) =>
    typeof input === 'string' && input.startsWith('/api/')
      ? nativeFetch(ENGINE_URL + input, init)
      : nativeFetch(input, init);
}
