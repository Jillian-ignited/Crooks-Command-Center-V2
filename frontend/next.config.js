/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",              // generate static HTML in /out
  images: { unoptimized: true }, // avoid Next Image optimizer
  experimental: {}               // remove invalid experimental flags
};
module.exports = nextConfig;
