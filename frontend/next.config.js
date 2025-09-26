/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable static export for deployment
  output: 'export',
  
  // Disable image optimization for static export
  images: {
    unoptimized: true
  },
  
  // Configure trailing slash
  trailingSlash: true,
  
  // Configure asset prefix for production
  assetPrefix: process.env.NODE_ENV === 'production' ? '/static' : '',
  
  // Configure base path if needed
  basePath: process.env.NODE_ENV === 'production' ? '/static' : '',
  
  // Webpack configuration for CSS handling
  webpack: (config, { isServer }) => {
    // Handle CSS files properly
    config.module.rules.push({
      test: /\.css$/,
      use: [
        'style-loader',
        'css-loader'
      ]
    });
    
    return config;
  },
  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE || '/api'
  },
  
  // Experimental features
  experimental: {
    // Enable app directory if using Next.js 13+
    appDir: false
  }
};

module.exports = nextConfig;
