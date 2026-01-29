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

- Static export enabled via `output: 'export'` in `next.config.ts`
- Image optimization disabled for static compatibility
- TypeScript enabled
- Tailwind CSS configured
