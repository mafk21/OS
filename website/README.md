# JARVIS OS website

Static, dependency-free product site for JARVIS OS.

## Preview locally

```bash
python3 -m http.server 4173 --directory website
```

Then open `http://localhost:4173`.

## Deploy

Publish the `website/` directory with GitHub Pages, Netlify, Vercel, Cloudflare Pages, or any static host. No build command is required.

The site uses the existing approved JARVIS Guardian and Confidante visual assets. Product claims are grounded in the project README and the privacy section links to the repository's full data-flow disclosure.

## Production files

- `docs/` is the complete, searchable product and operations guide.
- `_headers` configures security and caching headers on Netlify-compatible hosts.
- `vercel.json` provides the equivalent production headers on Vercel.
- `site.webmanifest`, `robots.txt`, `404.html`, and the SVG favicon provide installability, crawling, and error handling.
- The Content Security Policy blocks third-party scripts, tracking, forms, device permissions, and network requests. The site uses system fonts and makes no analytics or font-provider requests.

Before assigning a custom domain, add its absolute URL to a generated sitemap and canonical metadata. Those values are intentionally not fabricated while the final public domain is unknown.
