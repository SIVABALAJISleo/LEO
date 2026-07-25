import { Link, useRouterState } from "@tanstack/react-router";

export function SiteFooter() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  if (pathname.startsWith("/app")) return null;
  return (
    <footer className="border-t border-border/60 bg-background">
      <div className="mx-auto max-w-[1440px] px-6 py-16">
        <div className="grid gap-10 md:grid-cols-5">
          <div className="md:col-span-2">
            <div className="font-display text-xl font-bold">
              <span className="text-leo">LEO</span> AI
            </div>
            <p className="mt-3 max-w-sm text-sm text-muted-foreground">
              Local-first AI runtime. Fast, private, offline inference on commodity Intel CPU + iGPU
              hardware.
            </p>
          </div>
          <FooterCol
            title="Product"
            links={[
              ["/platform", "Platform"],
              ["/features", "Features"],
              ["/benchmarks", "Benchmarks"],
            ]}
          />
          <FooterCol
            title="Developers"
            links={[
              ["/docs", "Docs"],
              ["/docs", "API reference"],
              ["/app", "Console"],
            ]}
          />
          <FooterCol
            title="Company"
            links={[
              ["/about", "About"],
              ["/signup", "Get LEO"],
            ]}
          />
        </div>
        <div className="mt-14 flex flex-col gap-2 border-t border-border/60 pt-6 text-xs text-muted-foreground md:flex-row md:justify-between">
          <div>© {new Date().getFullYear()} LEO AI. All rights reserved.</div>
          <div>Built for commodity hardware.</div>
        </div>
      </div>
    </footer>
  );
}

function FooterCol({ title, links }: { title: string; links: [string, string][] }) {
  return (
    <div>
      <div className="eyebrow mb-4">{title}</div>
      <ul className="space-y-2 text-sm">
        {links.map(([to, label]) => (
          <li key={to + label}>
            <Link to={to} className="text-muted-foreground hover:text-foreground">
              {label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
