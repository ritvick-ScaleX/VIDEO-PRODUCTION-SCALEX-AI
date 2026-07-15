"use client";

/**
 * Minimal single-user session gate for the local studio.
 * Swap for a real auth provider later — everything goes through these helpers.
 */

const USERNAME = "team@scalex.club";
const PASSWORD = "scalex@255256";
const KEY = "scalex:session";

export function login(username: string, password: string): boolean {
  if (username.trim().toLowerCase() === USERNAME && password === PASSWORD) {
    if (typeof window !== "undefined") {
      localStorage.setItem(KEY, JSON.stringify({ user: USERNAME, at: Date.now() }));
    }
    return true;
  }
  return false;
}

export function isAuthed(): boolean {
  if (typeof window === "undefined") return false;
  try {
    const raw = localStorage.getItem(KEY);
    return !!raw && !!JSON.parse(raw).user;
  } catch {
    return false;
  }
}

export function currentUser(): string | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw).user as string) : null;
  } catch {
    return null;
  }
}

export function logout(): void {
  if (typeof window !== "undefined") localStorage.removeItem(KEY);
}
