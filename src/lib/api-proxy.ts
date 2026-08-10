/**
 * Resolves a request URL given a base URL and path.
 * Ensures double slashes are avoided and handles relative paths.
 */
export function resolveRequestUrl(base: string, path: string): string {
  // If path is already a fully qualified URL, return it
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  
  const cleanBase = base.replace(/\/+$/, "");
  const cleanPath = path.replace(/^\/+/, "");
  return `${cleanBase}/${cleanPath}`;
}
