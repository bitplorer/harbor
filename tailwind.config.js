/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{py,html,js}", "./assets/**/*.{html,js}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["Fraunces", "Iowan Old Style", "Palatino", "Georgia", "serif"],
        sans: ["Sora", "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
