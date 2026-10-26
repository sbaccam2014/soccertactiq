import { api, ApiError } from './client';
import type { CurrentUser } from '../types';

/**
 * Registration/login/logout go straight to django-allauth's headless
 * browser-client API rather than a custom /api/ route, per the backend
 * design (see backend/soccertactiq/urls.py). /api/auth/me/ is our own thin
 * convenience endpoint for "who is logged in right now".
 */

interface AllauthSessionResponse {
  status: number;
  data: {
    user?: {
      id: number;
      username: string;
      display: string;
    };
  };
  meta: { is_authenticated: boolean };
}

// A GET to the session endpoint also establishes the csrftoken cookie
// for a fresh browser — call this once on app load before anything else.
export async function fetchSession(): Promise<AllauthSessionResponse> {
  const response = await fetch('/_allauth/browser/v1/auth/session', {
    credentials: 'include',
    headers: { Accept: 'application/json' },
  });
  return response.json();
}

export async function register(username: string, password: string) {
  // allauth headless's signup endpoint takes a single `password` field —
  // "password confirmation" (per the brief) is enforced client-side in
  // RegisterPage before this is ever called; the API itself has no
  // separate password1/password2 confirmation step.
  return api.post<AllauthSessionResponse>('/_allauth/browser/v1/auth/signup', {
    username,
    password,
  });
}

export async function login(username: string, password: string) {
  return api.post<AllauthSessionResponse>('/_allauth/browser/v1/auth/login', {
    username,
    password,
  });
}

export async function logout() {
  // allauth headless's DELETE /auth/session responds with the resulting
  // (now unauthenticated) session state — which, by its own convention,
  // is a 401 with {meta: {is_authenticated: false}}. That's the expected
  // *successful* outcome of logging out, not a failure, so swallow the
  // 401 here rather than let it surface as an error to the caller.
  try {
    return await api.delete<AllauthSessionResponse>('/_allauth/browser/v1/auth/session');
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) {
      return err.body as AllauthSessionResponse;
    }
    throw err;
  }
}

export async function fetchCurrentUser(): Promise<CurrentUser> {
  return api.get<CurrentUser>('/api/auth/me/');
}
