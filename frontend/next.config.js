// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',     // ensures build generates static HTML in /out
  distDir: 'out',       // optional: explicitly use 'out' for clarity
  reactStrictMode: true, // safe default
  trailingSlash: true,  // ensures all routes end with / for static hosting
  images: {
    unoptimized: true   // required for static export
  },
  // Force static generation of all pages
  exportPathMap: async function (
    defaultPathMap,
    { dev, dir, outDir, distDir, buildId }
  ) {
    return {
      '/': { page: '/' },
      '/agency': { page: '/agency' },
      '/api-check': { page: '/api-check' },
      '/calendar': { page: '/calendar' },
      '/competitive': { page: '/competitive' },
      '/content': { page: '/content' },
      '/executive': { page: '/executive' },
      '/ingest': { page: '/ingest' },
      '/intelligence': { page: '/intelligence' },
      '/media': { page: '/media' },
      '/shopify': { page: '/shopify' },
      '/summary': { page: '/summary' },
      '/upload': { page: '/upload' }
    }
  }
}

module.exports = nextConfig
