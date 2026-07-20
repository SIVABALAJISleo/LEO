import { createFileRoute } from "@tanstack/react-router";
import { useAuth } from "@/lib/auth-context";

export const Route = createFileRoute("/_authenticated/app/security")({
  head: () => ({ meta: [{ title: "Security — LEO AI" }] }),
  component: Page,
});

function Page() {
  const { user, token } = useAuth();
  const scopes = user?.permissions ?? ["orchestrate", "memory", "kg"];
  return (
    <div className="p-10 max-w-4xl">
      <p className="eyebrow">Access</p>
      <h1 className="mt-2 font-display text-4xl font-bold">Security</h1>

      <div className="mt-8 grid gap-px bg-border md:grid-cols-2">
        <Card title="Session" body={user?.email ?? "Unknown"} />
        <Card title="Auth" body="JWT Bearer" />
      </div>

      <div className="mt-8 border border-border">
        <div className="border-b border-border bg-surface px-4 py-2 eyebrow">Scopes</div>
        <div className="p-4 flex flex-wrap gap-2">
          {scopes.map((s) => (
            <span key={s} className="border border-leo px-2 py-1 font-mono text-xs text-leo">
              {s}
            </span>
          ))}
        </div>
      </div>

      <div className="mt-8 border border-border">
        <div className="border-b border-border bg-surface px-4 py-2 eyebrow">Rate limits</div>
        <ul className="p-4 text-sm space-y-1 font-mono text-xs">
          <li>
            Global: <span className="text-leo">600 req / 60s</span>
          </li>
          <li>
            Chat: <span className="text-leo">100 req / min</span>
          </li>
          <li>
            Embeddings: <span className="text-leo">1000 req / min</span>
          </li>
          <li>
            Memory/KG: <span className="text-leo">500 req / min</span>
          </li>
        </ul>
      </div>

      {token && (
        <details className="mt-8 border border-border">
          <summary className="cursor-pointer bg-surface px-4 py-2 eyebrow">JWT token</summary>
          <pre className="overflow-auto p-4 font-mono text-[11px] break-all">{token}</pre>
        </details>
      )}
    </div>
  );
}

function Card({ title, body }: { title: string; body: string }) {
  return (
    <div className="bg-background p-5">
      <div className="eyebrow">{title}</div>
      <div className="mt-2 font-display text-lg font-bold">{body}</div>
    </div>
  );
}
