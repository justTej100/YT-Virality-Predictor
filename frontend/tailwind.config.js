/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        base: "#0B0D12",
        surface: "#14171F",
        surface2: "#1A1E28",
        border: "#262B36",
        ink: "#ECEDF0",
        muted: "#9AA1AE",
        signal: "#FF4B4B",
        signalDim: "#7A2A2A",
        data: "#3DD9D6",
        dataDim: "#1E4B4A",
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
