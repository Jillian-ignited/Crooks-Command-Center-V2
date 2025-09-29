// frontend/next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Static HTML export
  output: 'export',

  // Needed so Next/Image doesn’t rely on the Image Optimization server
  images: { unoptimized: true },

  // Optional: if you deep-link a lot, keeps nice URLs for static export
  trailingSlash: false,
};

module.exports = nextConfig;
