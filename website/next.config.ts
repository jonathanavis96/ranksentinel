import type { NextConfig } from 'next';

const basePath = process.env.NEXT_PUBLIC_BASE_PATH || '';

const nextConfig: NextConfig = {
  output: 'export',

  // GitHub Pages serves project sites from a sub-path (e.g. /ranksentinel).
  // For a real domain deployment, leave NEXT_PUBLIC_BASE_PATH unset.
  basePath,
  assetPrefix: basePath ? `${basePath}/` : undefined,

  // Disable image optimization for static export
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
