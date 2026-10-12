import { useEffect, type ReactNode } from 'react';
import { ClerkProvider, SignedIn, SignedOut, SignIn, UserButton, useAuth } from '@clerk/clerk-react';
import { setTokenGetter } from './engine';

/** Clerk publishable key; when unset (local development) the Studio opens without a login. */
export const CLERK_KEY: string = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY ?? '';

function TokenBridge({ children }: { children: ReactNode }) {
  const { getToken } = useAuth();
  useEffect(() => {
    setTokenGetter(() => getToken());
    return () => setTokenGetter(null);
  }, [getToken]);
  return <>{children}</>;
}

/** Shows the sign-in page until the visitor is signed in. */
export function AuthGate({ children }: { children: ReactNode }) {
  if (!CLERK_KEY) return <>{children}</>;
  return (
    <ClerkProvider publishableKey={CLERK_KEY}>
      <SignedOut>
        <div style={{ display: 'grid', placeItems: 'center', minHeight: '100vh' }}><SignIn routing="hash" /></div>
      </SignedOut>
      <SignedIn><TokenBridge>{children}</TokenBridge></SignedIn>
    </ClerkProvider>
  );
}

/** Account menu for the header; renders nothing without login. */
export function AccountButton() {
  return CLERK_KEY ? <UserButton /> : null;
}
