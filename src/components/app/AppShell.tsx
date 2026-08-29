import { Link, useRouterState, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { useAuth } from "../../lib/auth-context";
import {
  Activity,
  Brain,
  Database,
  Gamepad2,
  GitBranch,
  LayoutDashboard,
  LogOut,
  Menu,
  MessageSquare,
  Network,
  Settings,
  Shield,
  Sparkles,
  Zap,
  X,
} from "lucide-react";
import type { ReactNode } from "react";

const nav = [
  { to: "/app", label: "Dashboard", icon: LayoutDashboard, exact: true },
  { to: "/app/caao-breakthrough", label: "100% Parity (CAAO)", icon: Zap },
  { to: "/app/cyberpunk-cgfp", label: "Cyberpunk (CGFP)", icon: Gamepad2 },
  { to: "/app/chat", label: "Chat", icon: MessageSquare },
  { to: "/app/orchestrate", label: "Orchestrate", icon: GitBranch },
  { to: "/app/memory", label: "Memory", icon: Brain },
  { to: "/app/knowledge-graph", label: "Knowledge Graph", icon: Network },
  { to: "/app/embeddings", label: "Embeddings", icon: Sparkles },
  { to: "/app/benchmarks", label: "Benchmarks", icon: Activity },
  { to: "/app/security", label: "Security", icon: Shield },
  { to: "/app/settings", label: "Settings", icon: Settings },
];


export function AppShell({ children }: { children: ReactNode }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const auth = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  function isActive(to: string, exact?: boolean) {
    return exact ? pathname === to : pathname === to || pathname.startsWith(to + "/");
  }

  function logout() {
    auth.logout();
    navigate({ to: "/login" });
  }

  const sidebar = (
    <>
      <Link
        to="/"
        className="flex items-center gap-2 border-b border-border px-6 py-4 font-display text-lg font-bold focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
        aria-label="LEO AI home"
      >
        <span className="text-leo">LEO</span>
        <span>AI</span>
        <span className="ml-auto font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
          Console
        </span>
      </Link>
      <nav className="flex-1 py-4 flex flex-col justify-between" aria-label="Console navigation">
        <div className="space-y-0.5">
          {nav.slice(0, 10).map((n) => {
            const active = isActive(n.to, n.exact);
            return (
              <Link
                key={n.to}
                to={n.to}
                onClick={() => setMobileOpen(false)}
                aria-current={active ? "page" : undefined}
                className={`flex items-center gap-3 border-l-2 px-6 py-2.5 text-sm transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-leo focus-visible:ring-inset ${
                  active
                    ? "border-leo bg-background text-foreground"
                    : "border-transparent text-muted-foreground hover:text-foreground hover:bg-background/50"
                }`}
              >
                <n.icon className="h-4 w-4" aria-hidden="true" />
                {n.label}
              </Link>
            );
          })}
        </div>

        {/* Settings Navigation Link */}
        <div className="pt-3 mt-3 border-t border-border/60 px-4 space-y-2">
          {nav.slice(10).map((n) => {
            const active = isActive(n.to, n.exact);


            return (
              <Link
                key={n.to}
                to={n.to}
                onClick={() => setMobileOpen(false)}
                aria-current={active ? "page" : undefined}
                className={`flex items-center gap-3 border-l-2 px-2 py-2 text-sm transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-leo focus-visible:ring-inset ${
                  active
                    ? "border-leo bg-background text-foreground"
                    : "border-transparent text-muted-foreground hover:text-foreground hover:bg-background/50"
                }`}
              >
                <n.icon className="h-4 w-4" aria-hidden="true" />
                {n.label}
              </Link>
            );
          })}
        </div>
      </nav>
      <div className="border-t border-border p-4">
        <div className="mb-3 flex items-center gap-2 text-xs">
          <Database className="h-3 w-3 text-leo" aria-hidden="true" />
          <span className="truncate text-muted-foreground">{auth.user?.email ?? "signed in"}</span>
        </div>
        <button
          onClick={logout}
          className="flex w-full items-center gap-2 border border-border px-3 py-2 text-xs hover:border-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
        >
          <LogOut className="h-3 w-3" aria-hidden="true" /> Sign out
        </button>
      </div>
    </>
  );

  return (
    <div className="flex min-h-dvh bg-background">
      {/* Mobile top bar */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-40 flex items-center justify-between border-b border-border bg-background px-4 h-14">
        <Link to="/app" className="font-display text-lg font-bold" aria-label="LEO AI console home">
          <span className="text-leo">LEO</span> AI
        </Link>
        <button
          onClick={() => setMobileOpen(true)}
          aria-label="Open navigation menu"
          aria-expanded={mobileOpen}
          className="p-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
        >
          <Menu className="h-5 w-5" aria-hidden="true" />
        </button>
      </div>

      {/* Desktop sidebar */}
      <aside
        className="hidden md:flex w-60 shrink-0 border-r border-border bg-surface flex-col"
        aria-label="Console sidebar"
      >
        {sidebar}
      </aside>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div
          className="md:hidden fixed inset-0 z-50 flex"
          role="dialog"
          aria-modal="true"
          aria-label="Console navigation"
        >
          <div
            className="absolute inset-0 bg-black/60"
            onClick={() => setMobileOpen(false)}
            aria-hidden="true"
          />
          <aside className="relative w-72 max-w-[85vw] border-r border-border bg-surface flex flex-col">
            <button
              onClick={() => setMobileOpen(false)}
              aria-label="Close navigation menu"
              className="absolute top-3 right-3 p-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
            >
              <X className="h-5 w-5" aria-hidden="true" />
            </button>
            {sidebar}
          </aside>
        </div>
      )}

      <main className="flex-1 min-w-0 pt-14 md:pt-0" id="main">
        {children}
      </main>
    </div>
  );
}
