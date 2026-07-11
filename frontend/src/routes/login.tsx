import { useEffect, useState, type FormEvent } from "react";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { LockKeyhole, Pill } from "lucide-react";

import { useAuth } from "@/lib/auth/auth-context";
import { ApiError } from "@/lib/api/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";


export const Route = createFileRoute("/login")({
  head: () => ({
    meta: [
      { title: "Login | PharmaChain" },
      {
        name: "description",
        content: "Secure access to PharmaChain clinical supply chain operations.",
      },
    ],
  }),
  component: LoginPage,
});


function LoginPage() {
  const navigate = useNavigate();
  const { isAuthenticated, isHydrated, isWorking, login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isHydrated && isAuthenticated) {
      void navigate({
        to: "/",
        replace: true,
      });
    }
  }, [isAuthenticated, isHydrated, navigate]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    try {
      await login(email, password);
      await navigate({
        to: "/",
        replace: true,
      });
    } catch (caughtError) {
      if (
        caughtError instanceof ApiError &&
        typeof caughtError.body?.detail === "string"
      ) {
        setError(caughtError.body.detail);
        return;
      }

      setError("Unable to sign in. Please verify your credentials.");
    }
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_right,color-mix(in_oklab,var(--color-primary)_16%,transparent),transparent_32%),linear-gradient(135deg,color-mix(in_oklab,var(--color-teal)_8%,var(--color-background)),var(--color-background))] px-4 py-10">
      <div className="mx-auto grid min-h-[calc(100vh-5rem)] max-w-6xl items-center gap-8 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-[28px] border border-border/50 bg-card/70 p-8 shadow-[0_24px_80px_-40px_color-mix(in_oklab,var(--color-primary)_35%,transparent)] backdrop-blur">
          <div className="inline-flex items-center gap-3">
            <div className="size-12 rounded-2xl bg-gradient-to-br from-teal to-info text-white grid place-items-center shadow-lg shadow-teal/25">
              <Pill className="size-6" />
            </div>
            <div>
              <div className="text-2xl font-bold font-[family-name:var(--font-heading)] tracking-tight text-foreground">
                PharmaChain
              </div>
              <div className="text-xs uppercase tracking-[0.24em] text-muted-foreground">
                Enterprise Operations Console
              </div>
            </div>
          </div>

          <div className="mt-10 max-w-xl">
            <div className="text-[11px] font-bold uppercase tracking-[0.24em] text-primary">
              Secure Access
            </div>
            <h1 className="mt-3 text-4xl font-bold font-[family-name:var(--font-heading)] tracking-tight text-foreground">
              Clinical supply operations with authenticated access
            </h1>
            <p className="mt-4 text-sm leading-7 text-muted-foreground">
              Sign in to access inventory, warehouse, shipment, procurement, and executive copilot workflows protected by JWT authentication.
            </p>
          </div>

          <div className="mt-10 grid gap-4 sm:grid-cols-3">
            {[
              "JWT access tokens",
              "Refresh token rotation",
              "Role-aware enterprise access",
            ].map((item) => (
              <div
                key={item}
                className="rounded-2xl border border-border/60 bg-background/70 px-4 py-4 text-sm font-medium text-foreground"
              >
                {item}
              </div>
            ))}
          </div>
        </section>

        <Card className="overflow-hidden border-border/60 shadow-[0_24px_80px_-45px_color-mix(in_oklab,var(--color-foreground)_45%,transparent)]">
          <div className="border-b border-border/60 bg-gradient-to-br from-primary/10 via-card to-teal/10 px-6 py-6">
            <div className="inline-flex size-11 items-center justify-center rounded-2xl bg-foreground text-background shadow-sm">
              <LockKeyhole className="size-5" />
            </div>
            <h2 className="mt-4 text-2xl font-bold font-[family-name:var(--font-heading)] tracking-tight text-foreground">
              Sign in
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Use your PharmaChain enterprise credentials.
            </p>
          </div>
          <CardContent className="p-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium text-foreground">
                  Email
                </label>
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="name@pharmachain.com"
                  required
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium text-foreground">
                  Password
                </label>
                <Input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Enter your password"
                  required
                />
              </div>

              {error && (
                <div className="rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                  {error}
                </div>
              )}

              <Button
                type="submit"
                disabled={isWorking}
                className="h-11 w-full bg-gradient-to-r from-primary to-teal shadow-lg shadow-primary/20 hover:opacity-95"
              >
                {isWorking ? "Signing in..." : "Sign in to PharmaChain"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
