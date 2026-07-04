import { Link, Outlet, useRouterState } from "@tanstack/react-router";
import { LayoutDashboard, Package, Warehouse, Truck, Sparkles, Bell, Search, Pill } from "lucide-react";
import type { ReactNode } from "react";

const nav = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/inventory", label: "Inventory", icon: Package },
  { to: "/warehouse", label: "Warehouse Capacity", icon: Warehouse },
  { to: "/shipments", label: "Shipments", icon: Truck },
  { to: "/assistant", label: "AI Procurement", icon: Sparkles },
] as const;

export function AppLayout({ children }: { children?: ReactNode }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const current = nav.find((n) => n.to === pathname) ?? nav[0];

  return (
    <div className="flex min-h-screen bg-background">
      <aside className="hidden md:flex w-64 flex-col bg-sidebar text-sidebar-foreground border-r border-sidebar-border">
        <div className="px-5 py-5 flex items-center gap-3 border-b border-sidebar-border">
          <div className="size-10 rounded-xl bg-gradient-to-br from-teal to-info text-sidebar-primary-foreground grid place-items-center shadow-lg shadow-teal/30 ring-1 ring-white/10">
            <Pill className="size-5" />
          </div>
          <div className="leading-tight">
            <div className="text-2xl font-bold font-[family-name:var(--font-heading)] tracking-tight">PharmaChain</div>
            <div className="text-[11px] text-sidebar-foreground/55 font-[family-name:var(--font-heading)]">AI Clinical Supply Chain</div>
          </div>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {nav.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.to;
            return (
              <Link
                key={item.to}
                to={item.to}
                className={`group relative flex items-center gap-3 px-3 py-2.5 rounded-lg text-[15px] font-semibold transition-all duration-200 font-[family-name:var(--font-heading)] ${
                  active
                    ? "bg-sidebar-accent text-sidebar-primary-foreground shadow-sm"
                    : "text-sidebar-foreground/70 hover:bg-sidebar-accent/60 hover:text-sidebar-foreground"
                }`}
              >
                {active && <span className="absolute left-0 top-1.5 bottom-1.5 w-1 rounded-r-full bg-sidebar-primary" />}
                <Icon className={`size-4 transition-all duration-200 ${active ? "text-sidebar-primary" : "text-sidebar-foreground/60 group-hover:text-sidebar-primary group-hover:scale-110"}`} />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="p-4 border-t border-sidebar-border text-xs text-sidebar-foreground/60">
          <div className="font-medium text-sidebar-foreground/90">System Status</div>
          <div className="mt-1 flex items-center gap-2">
            <span className="relative flex size-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-60" />
              <span className="relative inline-flex size-2 rounded-full bg-success" />
            </span>
            All systems operational
          </div>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-auto py-4 border-b bg-card flex items-center justify-between px-4 md:px-8 gap-4">
          <div>
            <h1 className="text-[32px] font-bold text-foreground tracking-tight font-[family-name:var(--font-heading)]">{current.label}</h1>
            <p className="text-sm font-medium text-muted-foreground font-[family-name:var(--font-heading)]">AI Clinical Supply Chain Copilot</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-2 bg-muted rounded-md px-3 py-1.5 w-72">
              <Search className="size-4 text-muted-foreground" />
              <input
                placeholder="Search SKUs, shipments…"
                className="bg-transparent text-sm outline-none flex-1"
              />
            </div>
            <button className="relative size-9 rounded-md border bg-card hover:bg-muted grid place-items-center">
              <Bell className="size-4" />
              <span className="absolute top-1.5 right-1.5 size-2 rounded-full bg-destructive" />
            </button>
            <div className="size-9 rounded-full bg-gradient-to-br from-primary to-teal text-primary-foreground grid place-items-center text-sm font-semibold">
              DM
            </div>
          </div>
        </header>
        <main className="flex-1 p-4 md:p-8 overflow-x-hidden">{children ?? <Outlet />}</main>
      </div>
    </div>
  );
}
