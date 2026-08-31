/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        base: "#DC2626",
        surface: "#FFFFFF",
        surface2: "#F3F4F6",
        border: "#E5E7EB",
        ink: "#1F2937",
        muted: "#6B7280",
        signal: "#E11D2E",
        signalDim: "#FCA5A5",
        data: "#0E7C86",
        dataDim: "#CFFAFE",
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Inter'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      keyframes: {
        pulseTally: {
          "0%, 100%": { opacity: 1, boxShadow: "0 0 0 0 rgba(255,75,75,0.5)" },
          "50%": { opacity: 0.6, boxShadow: "0 0 0 6px rgba(255,75,75,0)" },
        },
        scan: {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(100%)" },
        },
      },
      animation: {
        tally: "pulseTally 2s ease-in-out infinite",
        scan: "scan 1.4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
