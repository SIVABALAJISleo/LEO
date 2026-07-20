import "@testing-library/jest-dom/vitest";
import { afterEach, vi } from "vitest";

afterEach(() => {
  window.localStorage.clear();
  vi.restoreAllMocks();
});
