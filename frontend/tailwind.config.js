/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        institutional: {
          50: '#f0f5fa',
          100: '#e1ecf5',
          200: '#c3daeb',
          300: '#94bfdc',
          400: '#5e9ec9',
          500: '#3882b3',
          600: '#266896',
          700: '#1f537a',
          800: '#1c4666',
          900: '#0f273d',
          950: '#091827',
        },
      },
    },
  },
  plugins: [],
}
