import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    container: {
      center: true,
      padding: "1.5rem",
      screens: { "2xl": "1400px" },
    },
    extend: {
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        display: ["var(--font-display)", "var(--font-sans)", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        success: {
          DEFAULT: "hsl(var(--success))",
          foreground: "hsl(var(--success-foreground))",
        },
        // Aurora accent ramp
        aurora: {
          violet: "hsl(247 90% 67%)",
          indigo: "hsl(233 84% 63%)",
          cyan: "hsl(187 85% 53%)",
          fuchsia: "hsl(292 84% 61%)",
          emerald: "hsl(158 74% 52%)",
        },
      },
      borderRadius: {
        "4xl": "2rem",
        "3xl": "1.5rem",
        lg: "var(--radius)",
        md: "calc(var(--radius) - 4px)",
        sm: "calc(var(--radius) - 8px)",
      },
      boxShadow: {
        soft: "0 1px 2px rgba(0,0,0,0.2), 0 8px 30px rgba(0,0,0,0.25)",
        glow: "0 0 0 1px hsl(var(--primary) / 0.25), 0 8px 40px hsl(var(--primary) / 0.25)",
        "glow-cyan": "0 0 40px hsl(187 85% 53% / 0.35)",
        card: "0 1px 0 0 rgba(255,255,255,0.04) inset, 0 20px 50px -20px rgba(0,0,0,0.6)",
      },
      backgroundImage: {
        "aurora-radial":
          "radial-gradient(60% 60% at 20% 10%, hsl(247 90% 67% / 0.28), transparent 60%), radial-gradient(50% 50% at 85% 15%, hsl(187 85% 53% / 0.22), transparent 60%), radial-gradient(60% 60% at 60% 100%, hsl(292 84% 61% / 0.18), transparent 60%)",
        "aurora-line":
          "linear-gradient(120deg, hsl(247 90% 67%), hsl(233 84% 63%), hsl(187 85% 53%), hsl(292 84% 61%))",
        "glass-sheen":
          "linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02) 40%, transparent 70%)",
        grid: "linear-gradient(hsl(var(--border) / 0.4) 1px, transparent 1px), linear-gradient(90deg, hsl(var(--border) / 0.4) 1px, transparent 1px)",
      },
      keyframes: {
        "aurora-shift": {
          "0%,100%": { transform: "translate3d(0,0,0) rotate(0deg)", opacity: "0.9" },
          "50%": { transform: "translate3d(2%,3%,0) rotate(8deg)", opacity: "1" },
        },
        float: {
          "0%,100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
        "gradient-pan": {
          "0%,100%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
        },
        "fade-up": {
          from: { opacity: "0", transform: "translateY(12px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        aurora: "aurora-shift 14s ease-in-out infinite",
        float: "float 6s ease-in-out infinite",
        shimmer: "shimmer 1.8s infinite",
        "gradient-pan": "gradient-pan 6s ease infinite",
        "fade-up": "fade-up 0.5s ease forwards",
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
