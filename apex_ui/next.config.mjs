/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  distDir: "static_hud",
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
