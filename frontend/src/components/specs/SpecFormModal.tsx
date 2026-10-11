import React, { useState } from 'react';
import CloseIcon from '@mui/icons-material/Close';
import { RuleCardDTO } from '../../types/api';

export interface SpecFormValues {
  title: string;
  chapter: string;
  target: string;
  given_clause: string;
  when_clause: string;
  then_clause: string;
  unless_clause: string;
}

export interface SpecFormModalProps {
  card: RuleCardDTO | null;   // the specification being edited, or null for a new one
  chapters: string[];
  saving: boolean;
  onSave: (values: SpecFormValues) => void;
  onClose: () => void;
}

const DEFAULT_CHAPTER = 'General';
const DEFAULT_TARGET = 'global';

/** Add or edit one specification. */
export const SpecFormModal: React.FC<SpecFormModalProps> = ({ card, chapters, saving, onSave, onClose }) => {
  const [values, setValues] = useState<SpecFormValues>({
    title: card?.title || '',
    chapter: card?.chapter || DEFAULT_CHAPTER,
    target: card?.target || DEFAULT_TARGET,
    given_clause: card?.given_clause || '',
    when_clause: card?.when_clause || '',
    then_clause: card?.then_clause || '',
    unless_clause: card?.unless_clause || '',
  });
  const set = (key: keyof SpecFormValues) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setValues(prev => ({ ...prev, [key]: e.target.value }));

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!values.title.trim()) return;
    onSave({
      ...values,
      title: values.title.trim(),
      chapter: values.chapter.trim() || DEFAULT_CHAPTER,
      target: values.target.trim() || DEFAULT_TARGET,
      given_clause: values.given_clause.trim(),
      when_clause: values.when_clause.trim(),
      then_clause: values.then_clause.trim(),
      unless_clause: values.unless_clause.trim(),
    });
  };

  const field = (key: keyof SpecFormValues, label: string, extra: React.InputHTMLAttributes<HTMLInputElement> = {}) => (
    <label className="spec-form-field">
      <span>{label}</span>
      <input type="text" className="modal-input" value={values[key]} onChange={set(key)} {...extra} />
    </label>
  );

  return (
    <div className="modal-overlay" onClick={onClose}>
      <form className="modal-box spec-form" onClick={e => e.stopPropagation()} onSubmit={submit}>
        <div className="spec-form-header">
          <h3>{card ? 'Edit specification' : 'Add specification'}</h3>
          <button type="button" className="tool-btn" onClick={onClose} aria-label="Close" title="Close">
            <CloseIcon fontSize="inherit" />
          </button>
        </div>

        {field('title', 'Title', { autoFocus: true })}
        {field('target', 'Applies to')}
        {field('chapter', 'Chapter', { list: 'spec-chapter-suggestions' })}
        <datalist id="spec-chapter-suggestions">
          {chapters.map(ch => <option key={ch} value={ch} />)}
        </datalist>
        {field('given_clause', 'Given')}
        {field('when_clause', 'When')}
        {field('then_clause', 'Then')}
        {field('unless_clause', 'Unless')}

        <div className="modal-actions">
          <button type="button" className="btn btn-outline" onClick={onClose}>Cancel</button>
          <button type="submit" className="btn btn-primary" disabled={saving || !values.title.trim()}>
            {saving ? 'Saving…' : 'Save'}
          </button>
        </div>
      </form>
    </div>
  );
};
