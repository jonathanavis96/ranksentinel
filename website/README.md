# RankSentinel Marketing Website

Next.js App Router site configured for static export, compatible with GitHub Pages.

## Local Development

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the site.

## Build & Export

```bash
npm run build
```

Static files are generated in the `out/` directory, ready for deployment to GitHub Pages or any static host.

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build and export static site
- `npm run lint` - Run ESLint
- `npm run start` - Start production server (not needed for static export)

## Configuration

### Environment Variables

Copy `.env.local.example` to `.env.local` and configure:

```bash
cp .env.local.example .env.local
```

**Required variables:**

- `NEXT_PUBLIC_SITE_URL` - Base URL for canonical links and Open Graph metadata
  - Local: `http://localhost:3000`
  - Production: `https://ranksentinel.com`
- `NEXT_PUBLIC_API_BASE_URL` - Backend API endpoint
  - Local: `http://localhost:8000`
  - Production: TBD (configure before deployment)

**Optional variables:**

- `NEXT_PUBLIC_GTM_ID` - Google Tag Manager container ID (format: `GTM-XXXXXXX`)
  - Leave empty to disable analytics in development
  - Configure for production tracking

### Build Configuration

- Static export enabled via `output: 'export'` in `next.config.ts`
- Image optimization disabled for static compatibility
- TypeScript enabled
- Tailwind CSS configured

### Production Deployment

Before deploying to production:

1. Set `NEXT_PUBLIC_SITE_URL` to your production domain
2. Set `NEXT_PUBLIC_API_BASE_URL` to your production API endpoint
3. Configure `NEXT_PUBLIC_GTM_ID` if using Google Analytics
4. Run `npm run build` to generate static files in `out/`
5. Deploy `out/` directory to your static host (GitHub Pages, Vercel, etc.)
