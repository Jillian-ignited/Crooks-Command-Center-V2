/** @type {import('next').NextConfig} */
const nextConfig = {
  // Your existing config...
  webpack: (config) => {
    config.module.rules.push({
      test: /\.css$/,
      use: ['style-loader', 'css-loader']
    });
    return config;
  }
}
