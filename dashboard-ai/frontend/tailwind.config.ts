import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Surface System - Syntactic Slate Design System
        surface: {
          DEFAULT: '#0f131c',
          dim: '#0f131c',
          bright: '#353942',
          'container-lowest': '#0a0e16',
          'container-low': '#181c24',
          container: '#1c2028',
          'container-high': '#262a33',
          'container-highest': '#31353e',
        },
        // Text Colors
        'on-surface': {
          DEFAULT: '#dfe2ee',
          variant: '#c2c6d6',
        },
        'on-background': '#dfe2ee',
        'inverse-surface': '#dfe2ee',
        'inverse-on-surface': '#2c3039',
        // Borders & Outlines
        outline: {
          DEFAULT: '#8c909f',
          variant: '#424754',
        },
        'border-subtle': '#1e293b',
        'border-default': '#26354a',
        'border-focus': '#3b82f6',
        // Primary Colors
        primary: {
          DEFAULT: '#adc6ff',
          container: '#4d8eff',
          fixed: '#d8e2ff',
          'fixed-dim': '#adc6ff',
        },
        'on-primary': {
          DEFAULT: '#002e6a',
          container: '#00285d',
          fixed: '#001a42',
          'fixed-variant': '#004395',
        },
        'inverse-primary': '#005ac2',
        'surface-tint': '#adc6ff',
        // Secondary Colors
        secondary: {
          DEFAULT: '#4edea3',
          container: '#00a572',
          fixed: '#6ffbbe',
          'fixed-dim': '#4edea3',
        },
        'on-secondary': {
          DEFAULT: '#003824',
          container: '#00311f',
          fixed: '#002113',
          'fixed-variant': '#005236',
        },
        // Tertiary Colors
        tertiary: {
          DEFAULT: '#ffb95f',
          container: '#ca8100',
          fixed: '#ffddb8',
          'fixed-dim': '#ffb95f',
        },
        'on-tertiary': {
          DEFAULT: '#472a00',
          container: '#3e2400',
          fixed: '#2a1700',
          'fixed-variant': '#653e00',
        },
        // Semantic Colors
        error: {
          DEFAULT: '#ffb4ab',
          container: '#93000a',
        },
        'on-error': {
          DEFAULT: '#690005',
          container: '#ffdad6',
        },
        // Functional Semantic
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
      },
      fontFamily: {
        display: ['var(--font-inter)'],
        'headline-lg': ['var(--font-inter)'],
        'headline-md': ['var(--font-inter)'],
        'headline-sm': ['var(--font-inter)'],
        'body-lg': ['var(--font-inter)'],
        'body-md': ['var(--font-inter)'],
        'body-sm': ['var(--font-inter)'],
        'label-md': ['var(--font-mono)'],
        'label-sm': ['var(--font-mono)'],
        'code-block': ['var(--font-mono)'],
      },
      fontSize: {
        display: ['32px', { lineHeight: '40px', letterSpacing: '-0.02em', fontWeight: '600' }],
        'headline-lg': ['24px', { lineHeight: '32px', letterSpacing: '-0.015em', fontWeight: '600' }],
        'headline-md': ['20px', { lineHeight: '28px', letterSpacing: '-0.01em', fontWeight: '600' }],
        'headline-sm': ['16px', { lineHeight: '24px', letterSpacing: '-0.005em', fontWeight: '600' }],
        'body-lg': ['15px', { lineHeight: '24px', letterSpacing: '-0.005em', fontWeight: '400' }],
        'body-md': ['13px', { lineHeight: '20px', letterSpacing: '0em', fontWeight: '400' }],
        'body-sm': ['12px', { lineHeight: '18px', letterSpacing: '0em', fontWeight: '400' }],
        'label-md': ['12px', { lineHeight: '16px', letterSpacing: '-0.01em', fontWeight: '500' }],
        'label-sm': ['11px', { lineHeight: '14px', letterSpacing: '0.02em', fontWeight: '400' }],
        'code-block': ['12px', { lineHeight: '20px', letterSpacing: '0em', fontWeight: '400' }],
      },
      borderRadius: {
        sm: '0.125rem',    // 2px
        DEFAULT: '0.25rem', // 4px
        md: '0.375rem',     // 6px
        lg: '0.5rem',       // 8px
        xl: '0.75rem',      // 12px
        '2xl': '1rem',      // 16px
        full: '9999px',
      },
      spacing: {
        'gutter': '1rem',
        'gutter-compact': '0.5rem',
        'margin': '1.5rem',
        'margin-mobile': '0.75rem',
        'space-xs': '0.25rem',
        'space-sm': '0.5rem',
        'space-md': '0.75rem',
        'space-lg': '1rem',
        'space-xl': '1.5rem',
        'space-2xl': '2rem',
      },
    },
  },
  plugins: [],
}

export default config
