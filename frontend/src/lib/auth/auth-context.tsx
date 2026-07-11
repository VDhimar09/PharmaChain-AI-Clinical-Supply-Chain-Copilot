import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import { authApi } from "@/lib/api/endpoints";
import { ApiError } from "@/lib/api/types";
import {
  clearStoredAuthSession,
  getStoredAuthSession,
  setStoredAuthSession,
  subscribeToAuthStorage,
  type AuthenticatedUser,
} from "@/lib/auth/token-storage";

type AuthContextValue = {
  user: AuthenticatedUser | null;
  isAuthenticated: boolean;
  isHydrated: boolean;
  isWorking: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshCurrentUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [isHydrated, setIsHydrated] = useState(false);
  const [isWorking, setIsWorking] = useState(false);

  useEffect(() => {
    const unsubscribe = subscribeToAuthStorage(() => {
      const session = getStoredAuthSession();
      setUser(session?.user ?? null);
    });

    void restoreSession();

    return unsubscribe;
  }, []);

  async function restoreSession() {
    const session = getStoredAuthSession();

    if (!session) {
      setUser(null);
      setIsHydrated(true);
      return;
    }

    setUser(session.user);

    try {
      const currentUser = await authApi.me();
      setStoredAuthSession({
        ...session,
        user: currentUser,
      });
      setUser(currentUser);
    } catch (error) {
      if (
        error instanceof ApiError &&
        error.status === 401 &&
        session.refreshToken
      ) {
        try {
          const refreshed = await authApi.refresh(session.refreshToken);
          setStoredAuthSession({
            accessToken: refreshed.access_token,
            refreshToken: refreshed.refresh_token,
            user: refreshed.user,
          });
          setUser(refreshed.user);
        } catch {
          clearStoredAuthSession();
          setUser(null);
        }
      } else {
        clearStoredAuthSession();
        setUser(null);
      }
    } finally {
      setIsHydrated(true);
    }
  }

  async function login(email: string, password: string) {
    setIsWorking(true);
    try {
      const response = await authApi.login({
        email,
        password,
      });

      setStoredAuthSession({
        accessToken: response.access_token,
        refreshToken: response.refresh_token,
        user: response.user,
      });
      setUser(response.user);
      setIsHydrated(true);
    } finally {
      setIsWorking(false);
    }
  }

  async function logout() {
    const session = getStoredAuthSession();

    setIsWorking(true);
    try {
      if (session?.refreshToken) {
        await authApi.logout(session.refreshToken);
      }
    } catch {
      // Best effort logout to avoid trapping the user in a bad session.
    } finally {
      clearStoredAuthSession();
      setUser(null);
      setIsWorking(false);
      setIsHydrated(true);
    }
  }

  async function refreshCurrentUser() {
    const currentUser = await authApi.me();
    const session = getStoredAuthSession();

    if (session) {
      setStoredAuthSession({
        ...session,
        user: currentUser,
      });
    }

    setUser(currentUser);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: user !== null,
        isHydrated,
        isWorking,
        login,
        logout,
        refreshCurrentUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (context === null) {
    throw new Error("useAuth must be used within an AuthProvider.");
  }

  return context;
}
