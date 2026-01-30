export function withBasePath(path: string): string {
  // GitHub Pages serves this site from a sub-path (e.g. /ranksentinel).
  // For real domain deployments, NEXT_PUBLIC_BASE_PATH should be unset.
  const basePath = process.env.NEXT_PUBLIC_BASE_PATH || '';

  if (!path.startsWith('/')) return path;
  if (!basePath) return path;

  return `${basePath}${path}`;
}
