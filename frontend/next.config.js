/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',        // static export
  trailingSlash: true,     // ensures folder-based paths (…/index.html)
};
module.exports = nextConfig;
