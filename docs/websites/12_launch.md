# Step 12 — Launch

## Required reading (agents must open these)

- `skills/domains/websites/launch/deployment.md`
- `skills/domains/websites/launch/finishing-pass.md`

## Deployment Steps (GitHub Pages)

### 1. Custom Domain Setup

**CNAME File:**

- Location: `website/public/CNAME`
- Content: `ranksentinel.com` (single line, no protocol)
- This file is automatically copied to the build output

**DNS Configuration (at registrar):**

```text
A record:    @     →  185.199.108.153
A record:    @     →  185.199.109.153
A record:    @     →  185.199.110.153
A record:    @     →  185.199.111.153
CNAME:       www   →  <username>.github.io
```

### 2. GitHub Pages Configuration

**Repository Settings:**

1. Go to Settings → Pages
2. Source: GitHub Actions (already configured via `.github/workflows/deploy.yml`)
3. Custom domain: `ranksentinel.com`
4. Enforce HTTPS: ✓ (wait ~24h for SSL to provision after DNS propagates)

### 3. Deployment Process

**Automatic Deployment:**

- Push to `main` branch triggers deployment via GitHub Actions
- Workflow builds Next.js site and publishes to GitHub Pages
- Custom domain is preserved via CNAME file

**Manual Deployment (if needed):**

```bash
cd website
npm run build
# GitHub Actions handles the rest
```

### 4. Verification Checklist

```markdown
## Post-Deployment Verification

### DNS
- [ ] `dig ranksentinel.com` returns GitHub Pages IPs
- [ ] `dig www.ranksentinel.com` returns CNAME to GitHub Pages
- [ ] DNS propagation complete (use dnschecker.org)

### GitHub Pages
- [ ] Repository Settings → Pages shows custom domain
- [ ] SSL certificate active (HTTPS badge green)
- [ ] Build workflow completed successfully

### Site Functionality
- [ ] https://ranksentinel.com loads correctly
- [ ] https://www.ranksentinel.com redirects to non-www
- [ ] All pages accessible (/pricing, /sample-report, /schedule)
- [ ] Lead capture form submits successfully
- [ ] Google Tag Manager fires (check via GTM preview mode)
- [ ] No mixed content warnings (all resources via HTTPS)

### Content
- [ ] All placeholder content replaced
- [ ] Contact email correct: support@ranksentinel.com
- [ ] Footer links working (Privacy, Terms)
- [ ] Social proof elements present
```

## Environment Configuration

**Next.js Environment Variables:**

- `NEXT_PUBLIC_API_BASE_URL`: API endpoint for lead submission
- `NEXT_PUBLIC_GTM_ID`: Google Tag Manager container ID

**Current Setup:**

- Local dev: Uses local API defaults
- Production: Configure via Vercel environment variables (if migrating from GitHub Pages)

**Note:** GitHub Pages serves static output only. API calls go directly from browser to backend.

## Rollback Procedure

If deployment breaks:

```bash
# Revert the commit
git revert HEAD
git push origin main

# Or redeploy previous working commit
git revert <bad-commit-sha>
git push origin main
```

GitHub Actions will automatically rebuild and deploy the previous version.

## Staging Environment

**Option 1: GitHub Pages (separate repo/branch)**

- Use `gh-pages` branch for staging
- Configure separate DNS: `staging.ranksentinel.com`

**Option 2: Vercel/Netlify preview**

- Connect repo to Vercel for preview deployments
- Every PR gets a preview URL
- Production still on GitHub Pages

## Security Headers

GitHub Pages provides basic security headers. For custom headers, consider:

- Cloudflare (free tier) as CDN/proxy
- Vercel/Netlify for advanced header control

**Recommended Headers (if migrating to Vercel):**

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" }
      ]
    }
  ]
}
```

## Troubleshooting

**"Domain's DNS record could not be retrieved":**

- Wait 24-48h for DNS propagation
- Verify A records point to all 4 GitHub IPs
- Check CNAME file exists in build output

**"404 on refresh":**

- Next.js static export handles this automatically
- Ensure `next.config.ts` has `output: 'export'`

**SSL Certificate not provisioning:**

- DNS must be fully propagated first
- Remove and re-add custom domain in GitHub Settings
- Wait 24h, GitHub uses Let's Encrypt

**Build failing:**

- Check GitHub Actions logs: Repository → Actions
- Common issues: Node version, dependency install, build errors
- Test locally: `cd website && npm run build`
