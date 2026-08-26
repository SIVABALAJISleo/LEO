import { describe, it, expect } from "vitest";
import { sanitizeHTML } from "../utils/sanitize";

describe("XSS Prevention & HTML Sanitization", () => {
  it("should remove script tags and malicious executable scripts", () => {
    const dirty = '<div><script>alert("xss")</script><p>Hello safe text</p></div>';
    const clean = sanitizeHTML(dirty);
    expect(clean).not.toContain("<script>");
    expect(clean).not.toContain('alert("xss")');
    expect(clean).toContain("<p>Hello safe text</p>");
  });

  it("should strip inline event handlers (onerror, onload, onclick)", () => {
    const dirty =
      '<img src="invalid-image" onerror="alert(1)" /><span onclick="stealData()">Click</span>';
    const clean = sanitizeHTML(dirty);
    expect(clean).not.toContain("onerror");
    expect(clean).not.toContain("onclick");
    expect(clean).not.toContain("stealData");
    expect(clean).toContain("<span>Click</span>");
  });

  it("should allow safe links and formatting tags", () => {
    const dirty =
      '<p>Check <a href="https://example.com" target="_blank">our docs</a> for <strong>details</strong>.</p>';
    const clean = sanitizeHTML(dirty);
    expect(clean).toContain('<a href="https://example.com" target="_blank">our docs</a>');
    expect(clean).toContain("<strong>details</strong>");
  });

  it("should handle empty or non-string inputs safely", () => {
    expect(sanitizeHTML("")).toBe("");
    expect(sanitizeHTML(null as unknown as string)).toBe("");
    expect(sanitizeHTML(undefined as unknown as string)).toBe("");
  });
});
