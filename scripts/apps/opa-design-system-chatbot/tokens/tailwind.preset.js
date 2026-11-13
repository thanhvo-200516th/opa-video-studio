/** @type {import('tailwindcss').Config} */
module.exports = {
  theme: {
    extend: {
      colors: {
        opa: {
          DEFAULT: '#0068FF',
          hover: '#0052CC',
          dark: '#003C99',
          light: '#E6F0FF',
          black: '#0A0A0A',
          white: '#FFFFFF',
          surface: '#F8FAFC',
          border: '#E2E8F0',
          muted: '#64748B',
        },
      },
      fontFamily: {
        opa: ['var(--opa-font-primary)', 'sans-serif'],
        'opa-accent': ['var(--opa-font-accent)', 'serif'],
      },
      borderRadius: {
        'opa-sm': '6px',
        'opa-md': '10px',
        'opa-lg': '16px',
        'opa-xl': '24px',
      },
      transitionTimingFunction: {
        'opa-in': 'cubic-bezier(0.2, 0.8, 0.2, 1)',
        'opa-out': 'cubic-bezier(0.6, 0, 0.8, 0.2)',
      },
    },
  },
};
