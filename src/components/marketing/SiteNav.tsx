import { Link, useRouterState } from "@tanstack/react-router";
import { useState } from "react";
import { useAuth } from "../../lib/auth-context";
import { Menu, X } from "lucide-react";

const links = [
  { to: "/platform", label: "Platform" },
  { to: "/features", label: "Features" },
  { to: "/benchmarks", label: "Benchmarks" },
  { to: "/docs", label: "Docs" },
  { to: "/about", label: "About" },
];

export function SiteNav() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const { isAuthenticated } = useAuth();
  const [open, setOpen] = useState(false);
  const isApp = pathname.startsWith("/app");
  if (isApp) return null;

  return (
    <header className="sticky top-0 z-50 border-b border-border/60 bg-background/80 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-[1440px] items-center gap-8 px-6">
        <Link to="/" className="flex items-center gap-2 font-display text-lg font-bold">
          <span className="text-leo">LEO</span>
          <span className="text-foreground">AI</span>
        </Link>
        <nav className="hidden md:flex items-center gap-6 text-sm">
          {links.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              className="relative text-muted-foreground hover:text-foreground transition-colors"
              activeProps={{ className: "text-foreground" }}
            >
              {l.label}
            </Link>
          ))}
        </nav>
        <div className="ml-auto flex items-center gap-3">
          {isAuthenticated ? (
            <Link
              to="/app"
              className="hidden sm:inline-flex items-center gap-1 bg-leo px-4 py-2 text-sm font-semibold text-leo-foreground hover:brightness-110"
            >
              Open app <span>›</span>
            </Link>
          ) : (
            <>
              <Link
                to="/login"
                className="hidden sm:inline text-sm text-muted-foreground hover:text-foreground"
              >
                Sign in
              </Link>
              <Link
                to="/signup"
                className="inline-flex items-center gap-1 bg-leo px-4 py-2 text-sm font-semibold text-leo-foreground hover:brightness-110"
              >
                Get LEO <span>›</span>
              </Link>
            </>
          )}
          <button
            onClick={() => setOpen(!open)}
            className="md:hidden p-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
            aria-label={open ? "Close menu" : "Open menu"}
            aria-expanded={open}
          >
            {open ? (
              <X className="h-5 w-5" aria-hidden="true" />
            ) : (
              <Menu className="h-5 w-5" aria-hidden="true" />
            )}
          </button>
        </div>
      </div>
      {open && (
        <nav className="md:hidden border-t border-border bg-background px-6 py-4 flex flex-col gap-3">
          {links.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              onClick={() => setOpen(false)}
              className="text-sm text-muted-foreground hover:text-foreground"
            >
              {l.label}
            </Link>
          ))}
        </nav>
      )}
    </header>
  );
}
