import React from 'react';
import { SpecTestStatus } from '../../types/api';

const LABELS: Record<SpecTestStatus, string> = {
  not_run: 'Test not run',
  pass: 'Test passed',
  broken: 'Test could not run',
  fail: 'Test failed',
};

export const testStatusLabel = (status: SpecTestStatus) => LABELS[status];

// What a red or yellow light means for the person reading the spec; the technical reason sits under Page test.
const SUMMARIES: Partial<Record<SpecTestStatus, string>> = {
  fail: 'The app does not do this yet.',
  broken: 'The test for this could not run.',
};

export const testStatusSummary = (status: SpecTestStatus) => SUMMARIES[status] ?? LABELS[status];

const TESTING_LABEL = 'Being worked on';

/** One light per spec: grey (not run), green (pass), yellow (broken), red (fail). While a build is working on the
 *  spec the light pulses instead. */
export const SpecStatusLight: React.FC<{ status: SpecTestStatus; large?: boolean; testing?: boolean }> = ({ status, large, testing }) => (
  <span
    className={`status-light status-light-${testing ? 'testing' : status}${large ? ' status-light-large' : ''}`}
    role="img"
    aria-label={testing ? TESTING_LABEL : LABELS[status]}
    title={testing ? TESTING_LABEL : LABELS[status]}
  />
);
