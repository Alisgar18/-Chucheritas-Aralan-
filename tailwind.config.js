/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{html,js,svelte,ts}"],

  theme: {
    extend: {
      animation: {
        latido: 'latido 2s infinite',
      },
      keyframes: {
        latido: {
          '0%, 100%': { transform: 'scale(1)' },
          '50%':      { transform: 'scale(1.06)' },
        }
      }
    }
  },

  plugins: [require("@tailwindcss/typography")]
};
