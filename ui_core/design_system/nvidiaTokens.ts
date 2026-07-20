/**
 * src/design-system/tokens/nvidia-tokens.ts
 * LEO Quantum Frontend — NVIDIA Design DNA Tokens
 */

export const nvidiaTokens = {
  colors: {
    primary: {
      black: '#000000',
      darkGray: '#0a0a0a',
      gray: '#1a1a1a',
      lightGray: '#888888',
      white: '#ffffff',
    },
    accent: {
      nvidiaGreen: '#76b900',
      neonGreen: '#95d500',
      electricGreen: '#a4ff00',
      darkGreen: '#5a8e00',
    },
    semantic: {
      success: '#76b900',
      warning: '#ffaa00',
      error: '#ff3333',
      info: '#00aaff',
    },
    gradients: {
      primary: 'linear-gradient(135deg, #000000 0%, #1a1a1a 100%)',
      accent: 'linear-gradient(135deg, #76b900 0%, #95d500 100%)',
      glass: 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)',
      glow: 'radial-gradient(circle at 30% 50%, rgba(118, 185, 0, 0.15) 0%, transparent 60%)',
    },
  },
  typography: {
    fontFamily: {
      primary: '"NVIDIA Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      mono: '"NVIDIA Mono", "Fira Code", "Courier New", monospace',
      display: '"NVIDIA Display", -apple-system, sans-serif',
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
      '5xl': '3rem',
      '6xl': '4rem',
    },
    fontWeight: {
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
      extrabold: '800',
    },
  },
  spacing: {
    px: '1px',
    0: '0',
    1: '0.25rem',
    2: '0.5rem',
    3: '0.75rem',
    4: '1rem',
    5: '1.25rem',
    6: '1.5rem',
    8: '2rem',
    10: '2.5rem',
    12: '3rem',
    16: '4rem',
    20: '5rem',
    24: '6rem',
  },
  borderRadius: {
    none: '0',
    sm: '0.125rem',
    base: '0.25rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
    '2xl': '1rem',
    full: '9999px',
  },
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    glow: '0 0 20px rgba(118, 185, 0, 0.5)',
  },
  animation: {
    duration: {
      fast: '150ms',
      base: '300ms',
      slow: '500ms',
    },
    easing: {
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
      easeOut: 'cubic-bezier(0.0, 0, 0.2, 1)',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    },
  },
};
