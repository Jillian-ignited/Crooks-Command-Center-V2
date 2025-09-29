/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',           // static HTML export to ./out
  images: { unoptimized: true }
};
module.exports = nextConfig;
