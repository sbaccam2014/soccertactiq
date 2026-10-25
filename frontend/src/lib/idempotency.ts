/**
 * A fresh random key per "submission attempt" from the user's point of
 * view. Reused across network retries of the *same* submit action so
 * the backend can recognize a retried request and avoid creating a
 * duplicate Attempt; a brand new key is generated only when the player
 * starts a genuinely new attempt (e.g. retrying the whole lesson).
 */
export function generateIdempotencyKey(): string {
  if ('randomUUID' in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}
