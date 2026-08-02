import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { useAuth } from "../lib/auth-context";
import { toast } from "sonner";

export const Route = createFileRoute("/login")({
  head: () => ({
    meta: [
      { title: "Sign in — LEO AI" },
      { name: "description", content: "Sign in to the LEO AI console." },
    ],
  }),
  component: LoginPage,
});

function LoginPage() {
  const auth = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [manualToken, setManualToken] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (auth.isAuthenticated) {
      navigate({ to: "/app" });
    }
  }, [auth.isAuthenticated, navigate]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await auth.login(email, password);
      navigate({ to: "/app" });
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  function useToken() {
    if (!manualToken.trim()) return;
    auth.setSession(manualToken.trim(), { email: email || "developer" });
    navigate({ to: "/app" });
  }

  return (
    <div className="mx-auto max-w-md px-6 py-24">
      <p className="eyebrow">Console</p>
      <h1 className="mt-3 font-display text-4xl font-bold">Sign in</h1>
      <p className="mt-2 text-sm text-muted-foreground">Access your LEO AI runtime.</p>
      <form onSubmit={onSubmit} className="mt-10 space-y-4">
        <Field label="Email" type="email" value={email} onChange={setEmail} />
        <Field label="Password" type="password" value={password} onChange={setPassword} />
        <button
          disabled={loading}
          className="w-full bg-leo px-4 py-3 text-sm font-semibold text-leo-foreground hover:brightness-110 disabled:opacity-60"
        >
          {loading ? "Signing in…" : "Sign in ›"}
        </button>
      </form>
      <div className="mt-8 border-t border-border pt-6">
        <div className="eyebrow">Have a JWT?</div>
        <p className="mt-2 text-xs text-muted-foreground">
          Paste your existing bearer token to skip the login endpoint.
        </p>
        <input
          value={manualToken}
          onChange={(e) => setManualToken(e.target.value)}
          placeholder="eyJhbGciOi..."
          className="mt-3 w-full bg-input px-3 py-2 font-mono text-xs"
        />
        <button
          type="button"
          onClick={useToken}
          className="mt-3 w-full border border-border px-4 py-2 text-sm hover:border-leo"
        >
          Use token ›
        </button>
      </div>
      <p className="mt-8 text-sm text-muted-foreground">
        No account?{" "}
        <Link to="/signup" className="text-leo">
          Create one ›
        </Link>
      </p>
    </div>
  );
}

function Field({
  label,
  type,
  value,
  onChange,
}: {
  label: string;
  type: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <label className="block">
      <span className="eyebrow">{label}</span>
      <input
        required
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-2 w-full bg-input px-3 py-3 text-sm outline-none focus:ring-1 focus:ring-leo"
      />
    </label>
  );
}
