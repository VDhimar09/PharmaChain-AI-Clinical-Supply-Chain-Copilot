import { Navigate } from "@tanstack/react-router";
import type { ReactNode } from "react";

import { useAuth } from "@/lib/auth/auth-context";


export function RouteGuard({ children }: { children: ReactNode }) {
  const { isAuthenticated, isHydrated } = useAuth();

  if (!isHydrated) {
    return null;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return <>{children}</>;
}
