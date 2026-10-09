import React from 'react';
import { SpecTestStatus } from '../../types/api';

const LABELS: Record<SpecTestStatus, string> = {
  not_run: 'Test not run',
  pass: 'Test passed',
  broken: 'Test could not run',
  fail: 'Test failed',
};

export const testStatusLabel = (status: SpecTestStatus) => LABELS[status];

/** One light per spec: grey (not run), green (pass), yellow (broken), red (fail). */
export const SpecStatusLight: React.FC<{ status: SpecTestStatus; large?: boolean }> = ({ status, large }) => (
  <span
    className={`status-light status-light-${status}${large ? ' status-light-large' : ''}`}
    role="img"
    aria-label={LABELS[status]}
    title={LABELS[status]}
  />
);
