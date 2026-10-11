import React from 'react';

/** A short outcome shown to the user; the severity is stated by whoever reports it, never guessed from the text. */
export interface StudioMessage {
  severity: 'success' | 'warning' | 'error';
  text: string;
}

export const StatusMessage: React.FC<{ message: StudioMessage }> = ({ message }) => (
  <div className={`status-message status-message-${message.severity}`} role={message.severity === 'success' ? 'status' : 'alert'}>
    {message.text}
  </div>
);
