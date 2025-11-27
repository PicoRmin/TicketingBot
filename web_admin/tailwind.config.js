/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // Enable class-based dark mode
  theme: {
    extend: {
      colors: {
        // Use CSS Variables for colors to maintain theme switching
        bg: 'var(--bg)',
        'bg-secondary': 'var(--bg-secondary)',
        fg: 'var(--fg)',
        'fg-secondary': 'var(--fg-secondary)',
        link: 'var(--link)',
        'link-hover': 'var(--link-hover)',
        muted: 'var(--muted)',
        border: 'var(--border)',
        'border-hover': 'var(--border-hover)',
        success: 'var(--success)',
        warning: 'var(--warning)',
        error: 'var(--error)',
        info: 'var(--info)',
        primary: 'var(--primary)',
        'primary-hover': 'var(--primary-hover)',
      },
      borderRadius: {
        DEFAULT: 'var(--radius)',
        lg: 'var(--radius-lg)',
      },
      boxShadow: {
        DEFAULT: '0 1px 3px 0 var(--shadow)',
        md: '0 4px 6px -1px var(--shadow)',
        lg: '0 10px 15px -3px var(--shadow-lg)',
        xl: '0 20px 25px -5px var(--shadow-lg)',
      },
      fontFamily: {
        sans: [
          'Vazirmatn',
          'Tahoma',
          'Arial',
          'sans-serif',
        ],
        mono: [
          'Vazir Code',
          'Courier New',
          'monospace',
        ],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      screens: {
        'xs': '475px',
      },
    },
  },
  plugins: [],
};

