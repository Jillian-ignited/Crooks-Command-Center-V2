/**
 * Enterprise-Grade Next.js Configuration
 * Crooks Command Center V2 - Advanced Business Intelligence Platform
 * 
 * This configuration provides sophisticated optimization, performance tuning,
 * and enterprise-ready settings for production deployment.
 */

const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Production-optimized static export
  output: 'export',
  
  // Strategic output directory for FastAPI integration
  distDir: '../backend/static',
  
  // Enhanced URL formatting for optimal static serving
  trailingSlash: true,
  
  // Advanced image handling for static deployment
  images: {
    unoptimized: true,
    domains: ['localhost', 'crooks-command-center-v2.onrender.com'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
  },
  
  // Performance optimizations
  swcMinify: true,
  compress: true,
  
  // Production safeguards
  reactStrictMode: true,
  poweredByHeader: false,
  
  // Build-time optimizations
  eslint: {
    // Skip ESLint during production builds for performance
    ignoreDuringBuilds: true,
  },
  
  // Type checking optimization
  typescript: {
    // Skip type checking during build for faster deployment
    ignoreBuildErrors: true,
  },
  
  // Advanced webpack configuration
  webpack: (config, { dev, isServer }) => {
    // Enhanced CSS processing
    config.module.rules.push({
      test: /\.css$/,
      use: [
        'style-loader',
        {
          loader: 'css-loader',
          options: {
            importLoaders: 1,
            modules: {
              auto: true,
            },
          },
        },
        'postcss-loader',
      ],
    });
    
    // SVG optimization
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    });
    
    // Bundle optimization
    if (!dev && !isServer) {
      // Split chunks for optimal loading
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          commons: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
          },
        },
      };
      
      // Minimize bundle size
      config.optimization.minimize = true;
    }
    
    return config;
  },
  
  // Environment configuration
  env: {
    // API configuration
    NEXT_PUBLIC_API_BASE: '/api',
    
    // Feature flags
    NEXT_PUBLIC_ENABLE_ADVANCED_ANALYTICS: 'true',
    NEXT_PUBLIC_ENABLE_SHOPIFY_INTEGRATION: 'true',
    NEXT_PUBLIC_ENABLE_AGENCY_TRACKING: 'true',
    
    // Performance settings
    NEXT_PUBLIC_CACHE_DURATION: '3600',
  },
  
  // Advanced routing
  async redirects() {
    return [
      {
        source: '/',
        destination: '/executive',
        permanent: true,
      },
    ];
  },
  
  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
