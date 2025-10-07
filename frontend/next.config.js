/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',  // Enable static HTML export
  images: {
    unoptimized: true  // Required for static export
  },
  // API calls should point to your Render backend
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://crooks-command-center-v2.onrender.com/api'
  },
  trailingSlash: true,  // Helps with static file serving
}

module.exports = nextConfig