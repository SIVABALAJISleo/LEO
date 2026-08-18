import DOMPurify from "dompurify";

/**
 * Sanitize untrusted HTML to prevent Cross-Site Scripting (XSS) attacks.
 * Whitelists common formatting tags and safe attributes.
 */
export const sanitizeHTML = (dirtyHTML: string): string => {
  if (!dirtyHTML || typeof dirtyHTML !== "string") {
    return "";
  }
  return DOMPurify.sanitize(dirtyHTML, {
    ALLOWED_TAGS: ["b", "i", "em", "strong", "a", "p", "span", "ul", "ol", "li", "code", "pre", "blockquote"],
    ALLOWED_ATTR: ["href", "title", "target", "rel", "class"],
    KEEP_CONTENT: true,
  });
};
