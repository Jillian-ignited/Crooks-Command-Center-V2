// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',     // ensures build generates static HTML in /out
  distDir: 'out',       // optional: explicitly use 'out' for clarity
  reactStrictMode: true // safe default
}

module.exports = nextConfig