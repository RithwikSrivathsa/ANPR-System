/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#071014",
        panel: "rgba(15, 23, 32, 0.72)",
        line: "rgba(255,255,255,0.11)",
        mint: "#35f0b1",
        amber: "#f9c74f",
        coral: "#ff6b6b"
      },
      boxShadow: {
        glow: "0 18px 70px rgba(53, 240, 177, 0.12)"
      }
    }
  },
  plugins: []
};
