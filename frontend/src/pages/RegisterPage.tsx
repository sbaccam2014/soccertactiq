import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { extractAllauthFieldErrors } from '../api/client';
import { PrimaryButton, TextField } from '../components/ui';

export function RegisterPage() {
  const { user, isLoading, register } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState('');
  const [password1, setPassword1] = useState('');
  const [password2, setPassword2] = useState('');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isLoading && user) {
    return <Navigate to="/dashboard" replace />;
  }

  function validate(): boolean {
    const errors: Record<string, string> = {};
    if (username.trim().length < 3) {
      errors.username = 'Username must be at least 3 characters.';
    }
    if (password1.length < 8) {
      errors.password1 = 'Password must be at least 8 characters.';
    }
    if (password1 !== password2) {
      errors.password2 = 'Passwords do not match.';
    }
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setFormError('');
    if (!validate()) return;

    setIsSubmitting(true);
    try {
      await register(username.trim(), password1);
      navigate('/dashboard', { replace: true });
    } catch (err) {
      const allauthErrors = extractAllauthFieldErrors(err);
      if (allauthErrors) {
        // The API's single confirmed password field is named "password";
        // our form has two local fields (password1/password2) for the
        // confirmation UX, so surface any password-related API error
        // on the first password field.
        if (allauthErrors.password) {
          allauthErrors.password1 = allauthErrors.password;
          delete allauthErrors.password;
        }
        setFieldErrors(allauthErrors);
      } else {
        setFormError(err instanceof Error ? err.message : 'Registration failed.');
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="flex flex-1 flex-col items-center justify-center">
      <form onSubmit={handleSubmit} className="flex w-full max-w-xs flex-col gap-4" noValidate>
        <h1 className="text-center text-2xl font-bold text-[var(--bsa-pitch-700)]">
          Create your account
        </h1>
        <p className="text-center text-sm text-[var(--bsa-text-muted)]">
          Just a username and password — no email needed.
        </p>

        <TextField
          id="username"
          label="Username"
          autoComplete="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          error={fieldErrors.username}
          required
        />
        <TextField
          id="password1"
          label="Password"
          type="password"
          autoComplete="new-password"
          value={password1}
          onChange={(e) => setPassword1(e.target.value)}
          error={fieldErrors.password1}
          required
        />
        <TextField
          id="password2"
          label="Confirm password"
          type="password"
          autoComplete="new-password"
          value={password2}
          onChange={(e) => setPassword2(e.target.value)}
          error={fieldErrors.password2}
          required
        />

        {formError && (
          <p role="alert" className="text-sm text-[var(--bsa-danger)]">
            {formError}
          </p>
        )}

        <PrimaryButton type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Creating account…' : 'Create account'}
        </PrimaryButton>

        <p className="text-center text-sm text-[var(--bsa-text-muted)]">
          Already have an account?{' '}
          <Link to="/login" className="font-semibold text-[var(--bsa-pitch-600)]">
            Log in
          </Link>
        </p>
      </form>
    </div>
  );
}
