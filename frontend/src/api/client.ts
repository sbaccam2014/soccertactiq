/**
 * Thin fetch wrapper for talking to the Django backend.
 *
 * Session cookie auth + Django CSRF protection: every request includes
 * credentials so the sessionid/csrftoken cookies travel with it, and
 * every non-GET request echoes the csrftoken cookie back as the
 * X-CSRFToken header (Django's documented SPA pattern). In dev, Vite's
 * proxy (see vite.config.ts) forwards /api, /_allauth, /admin, /static
 * to the Django dev server so this is always same-origin from the
 * browser's point of view, exactly like production.
 */

export class ApiError extends Error {
  status: number;
  // DRF/allauth error shapes vary by endpoint; keep the raw body for
  // callers that want to extract field-specific messages.
  body: unknown;

  constructor(status: number, body: unknown, message: string) {
    super(message);
    this.status = status;
    this.body = body;
  }
}

function getCookie(name: string): string | null {
  const match = document.cookie.match(
    new RegExp(`(?:^|; )${name.replace(/([.$?*|{}()[\]\\/+^])/g, '\\$1')}=([^;]*)`),
  );
  return match ? decodeURIComponent(match[1]) : null;
}

const UNSAFE_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

async function request<T>(
  path: string,
  options: { method?: string; body?: unknown } = {},
): Promise<T> {
  const method = options.method ?? 'GET';
  const headers: Record<string, string> = { Accept: 'application/json' };

  if (options.body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }
  if (UNSAFE_METHODS.has(method)) {
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
      headers['X-CSRFToken'] = csrfToken;
    }
  }

  let response: Response;
  try {
    response = await fetch(path, {
      method,
      headers,
      credentials: 'include',
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    });
  } catch {
    throw new ApiError(0, null, 'Network error. Check your connection and try again.');
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const text = await response.text();
  const data = text ? JSON.parse(text) : null;

  if (!response.ok) {
    throw new ApiError(response.status, data, extractErrorMessage(data, response.status));
  }
  return data as T;
}

function extractErrorMessage(body: unknown, status: number): string {
  if (body && typeof body === 'object') {
    const asRecord = body as Record<string, unknown>;
    // allauth headless error shape: { status, errors: [{message, code, param}] }
    if (Array.isArray(asRecord.errors) && asRecord.errors.length > 0) {
      const first = asRecord.errors[0] as Record<string, unknown>;
      if (typeof first.message === 'string') return first.message;
    }
    // DRF error shape: { detail: "..." } or field-keyed arrays
    if (typeof asRecord.detail === 'string') return asRecord.detail;
    if (Array.isArray(asRecord.non_field_errors) && asRecord.non_field_errors.length > 0) {
      return String(asRecord.non_field_errors[0]);
    }
  }
  if (status === 401 || status === 403) return 'Please log in to continue.';
  if (status === 404) return 'Not found.';
  return 'Something went wrong. Please try again.';
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) => request<T>(path, { method: 'POST', body }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
};

interface AllauthFieldError {
  message: string;
  code: string;
  param?: string;
}

/**
 * allauth headless validation errors come back as
 * { status, errors: [{ message, code, param }] }. Pull out a
 * field-name -> message map so forms can show inline errors (e.g.
 * "username" -> "A user with that username already exists.").
 * Returns null if `err` isn't that shape, or if none of the errors
 * named a field.
 */
export function extractAllauthFieldErrors(err: unknown): Record<string, string> | null {
  if (!(err instanceof ApiError)) return null;
  const body = err.body as { errors?: AllauthFieldError[] } | null;
  if (!body || !Array.isArray(body.errors)) return null;

  const fieldErrors: Record<string, string> = {};
  for (const fieldError of body.errors) {
    if (fieldError.param) {
      fieldErrors[fieldError.param] = fieldError.message;
    }
  }
  return Object.keys(fieldErrors).length > 0 ? fieldErrors : null;
}
