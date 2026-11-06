import type { CurrentUser } from '../types';

/** Where a logged-in user's "home" screen is, based on their role. */
export function roleHome(user: CurrentUser): string {
  if (user.is_coach) return '/coach';
  if (user.is_parent) return '/parent';
  return '/dashboard';
}
