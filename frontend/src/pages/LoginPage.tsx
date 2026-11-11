import { useState } from 'react';
import type { FormEvent } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { roleHome } from '../lib/roleHome';
import { PrimaryButton, TextField } from '../components/ui';
import { EyeIcon, EyeOffIcon } from '../components/icons';

export function LoginPage() {
  const { user, isLoading, login } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [formError, setFormError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isLoading && user) {
    return <Navigate to={roleHome(user)} replace />;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setFormError('');
    setIsSubmitting(true);
    try {
      const me = await login(username.trim(), password);
      navigate(roleHome(me), { replace: true });
    } catch {
      // Generic message on purpose: never reveal whether the username
      // exists, only that the combination was wrong.
      setFormError('Incorrect username or password.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="flex flex-1 flex-col items-center justify-center">
      <form onSubmit={handleSubmit} className="flex w-full max-w-xs flex-col gap-4" noValidate>
        <img
          src={`${import.meta.env.BASE_URL}logo.png`}
          alt=""
          className="mx-auto h-36 w-36 rounded-2xl shadow-sm"
        />
        <h1 className="text-center text-2xl font-bold text-[var(--soccertactiq-pitch-700)]">Log in</h1>

        <TextField
          id="username"
          label="Username"
          autoComplete="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <div className="relative">
          <TextField
            id="password"
            label="Password"
            type={showPassword ? 'text' : 'password'}
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="pr-11"
            required
          />
          <button
            type="button"
            onClick={() => setShowPassword((shown) => !shown)}
            aria-label={showPassword ? 'Hide password' : 'Show password'}
            className="absolute bottom-0 right-0 flex h-11 w-11 items-center justify-center text-[var(--soccertactiq-text-muted)]"
          >
            {showPassword ? <EyeOffIcon className="h-5 w-5" /> : <EyeIcon className="h-5 w-5" />}
          </button>
        </div>

        {formError && (
          <p role="alert" className="text-sm text-[var(--soccertactiq-danger)]">
            {formError}
          </p>
        )}

        <PrimaryButton type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Logging in…' : 'Log in'}
        </PrimaryButton>
      </form>
    </div>
  );
}
