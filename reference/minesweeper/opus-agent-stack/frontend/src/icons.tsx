export function FlagIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} aria-hidden="true">
      <path d="M7 3v18" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" fill="none" />
      <path d="M8 4h10.5l-3 4 3 4H8z" fill="var(--flag)" />
    </svg>
  );
}

export function MineIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} aria-hidden="true">
      <g stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
        <path d="M12 2.5v19M2.5 12h19M5.3 5.3l13.4 13.4M18.7 5.3L5.3 18.7" />
      </g>
      <circle cx="12" cy="12" r="6.2" fill="currentColor" />
      <circle cx="9.8" cy="9.8" r="1.6" fill="var(--open)" opacity="0.85" />
    </svg>
  );
}

export function WrongFlagIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} aria-hidden="true">
      <path d="M7 3v18" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" fill="none" opacity="0.45" />
      <path d="M8 4h10.5l-3 4 3 4H8z" fill="var(--flag)" opacity="0.45" />
      <path d="M4 4l16 16M20 4L4 20" stroke="var(--bad)" strokeWidth="2.6" strokeLinecap="round" />
    </svg>
  );
}

export function ClockIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <circle cx="12" cy="13" r="8" />
      <path d="M12 9v4l2.5 2M9.5 2.5h5" />
    </svg>
  );
}
