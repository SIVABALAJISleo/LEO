import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import App from "./App";

// Mock the expensive/complex components to isolate App rendering
vi.mock("@/components/HeroParticles", () => ({
  HeroParticles: () => <div data-testid="hero-particles" />,
}));

vi.mock("@/pages/auth/Login", () => ({
  default: () => <div>Login Page</div>,
}));

// Mock Supabase to prevent network calls during tests
vi.mock("@/integrations/supabase/client", () => ({
  supabase: {
    auth: {
      onAuthStateChange: vi.fn(() => ({ data: { subscription: { unsubscribe: vi.fn() } } })),
      getSession: vi.fn(() => Promise.resolve({ data: { session: null }, error: null })),
    },
    from: vi.fn(() => ({
      select: vi.fn(() => ({
        eq: vi.fn(() => Promise.resolve({ data: [], error: null })),
      })),
    })),
  },
}));

describe("App Component", () => {
  it("renders without crashing", () => {
    // We render the App. Since it has routing, we expect to see the Landing Page content by default
    render(<App />);

    // Check for unique heading
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(/UCSIP/i);
  });
});
