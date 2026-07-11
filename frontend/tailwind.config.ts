import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#005f6b",
        secondary: "#f4a261",
        accent: "#2a9d8f",
        danger: "#e76f51",
        background: "#f8fafc",
        surface: "#ffffff",
      },
      fontFamily: {
        sans: ["Noto Sans Arabic", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
