import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1a1410",
        parchment: "#f4ebd9",
        accent: "#9c3a2e",
        rust: "#b8553e",
        oak: "#5c3a1f",
        cream: "#ebe0c8",
      },
      fontFamily: {
        serif: ['"Cormorant Garamond"', "Georgia", "ui-serif", "serif"],
        sans: ['"Inter"', "ui-sans-serif", "system-ui", "sans-serif"],
      },
      letterSpacing: {
        widest2: "0.25em",
      },
    },
  },
  plugins: [],
};

export default config;
