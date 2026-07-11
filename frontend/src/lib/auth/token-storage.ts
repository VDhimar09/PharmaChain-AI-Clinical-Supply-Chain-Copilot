export type AuthenticatedUser = {
  id: string;
  email: string;
  full_name: string;
  role: string;
  permissions: string[];
};

export type StoredAuthSession = {
  accessToken: string;
  refreshToken: string;
  user: AuthenticatedUser;
};

const STORAGE_KEY = "pharmachain.auth.session";
const AUTH_EVENT = "pharmachain-auth-changed";

export function getStoredAuthSession(): StoredAuthSession | null {
  if (typeof window === "undefined") {
    return null;
  }

  const rawValue = window.localStorage.getItem(STORAGE_KEY);

  if (!rawValue) {
    return null;
  }

  try {
    return JSON.parse(rawValue) as StoredAuthSession;
  } catch {
    clearStoredAuthSession();
    return null;
  }
}

export function setStoredAuthSession(session: StoredAuthSession): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify(session),
  );
  dispatchAuthChanged();
}

export function clearStoredAuthSession(): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.removeItem(STORAGE_KEY);
  dispatchAuthChanged();
}

export function subscribeToAuthStorage(
  callback: () => void,
): () => void {
  if (typeof window === "undefined") {
    return () => undefined;
  }

  const handleStorage = (event: StorageEvent) => {
    if (event.key === STORAGE_KEY) {
      callback();
    }
  };
  const handleCustomEvent = () => callback();

  window.addEventListener("storage", handleStorage);
  window.addEventListener(AUTH_EVENT, handleCustomEvent);

  return () => {
    window.removeEventListener("storage", handleStorage);
    window.removeEventListener(AUTH_EVENT, handleCustomEvent);
  };
}

function dispatchAuthChanged(): void {
  if (typeof window === "undefined") {
    return;
  }

  window.dispatchEvent(
    new Event(AUTH_EVENT),
  );
}
