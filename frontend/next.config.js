/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  distDir: '../backend/static',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  env: {
    NEXT_PUBLIC_API_BASE: '/api'
  }
  // Remove the webpack configuration that's causing the error
}

module.exports = nextConfig
