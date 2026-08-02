import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { useAuth } from "../lib/auth-context";
import { toast } from "sonner";

export const Route = createFileRoute("/signup")({
  head: () => ({
    meta: [
      { title: "Create account — LEO AI" },
      { name: "description", content: "Get access to LEO AI." },
    ],
  }),
  component: SignupPage,
});

function SignupPage() {
  const auth = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
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
      await auth.signup(email, password);
      toast.success("Account created");
      navigate({ to: "/app" });
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Signup failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-md px-6 py-24">
      <p className="eyebrow">Get started</p>
      <h1 className="mt-3 font-display text-4xl font-bold">Create your account</h1>
      <p className="mt-2 text-sm text-muted-foreground">Free during preview.</p>
      <form onSubmit={onSubmit} className="mt-10 space-y-4">
        <label className="block">
          <span className="eyebrow">Email</span>
          <input
            required
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-2 w-full bg-input px-3 py-3 text-sm outline-none focus:ring-1 focus:ring-leo"
          />
        </label>
        <label className="block">
          <span className="eyebrow">Password</span>
          <input
            required
            type="password"
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-2 w-full bg-input px-3 py-3 text-sm outline-none focus:ring-1 focus:ring-leo"
          />
        </label>
        <button
          disabled={loading}
          className="w-full bg-leo px-4 py-3 text-sm font-semibold text-leo-foreground hover:brightness-110 disabled:opacity-60"
        >
          {loading ? "Creating…" : "Create account ›"}
        </button>
      </form>
      <p className="mt-8 text-sm text-muted-foreground">
        Already have an account?{" "}
        <Link to="/login" className="text-leo">
          Sign in ›
        </Link>
      </p>
    </div>
  );
}
