/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',          // replaces `next export`
  images: { unoptimized: true },
  trailingSlash: true,       // safer with static hosting behind FastAPI
};
module.exports = nextConfig;
