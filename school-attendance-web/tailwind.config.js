/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}", // <-- ESTA LÍNEA ES CLAVE para que detecte el Login.jsx
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}