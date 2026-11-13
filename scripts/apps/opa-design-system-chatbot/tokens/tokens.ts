/**
 * OPA Official Design Tokens
 * OverPowers Agency (OPA)
 */

export const OPA_COLORS = {
  primary: {
    default: "#0068FF",
    hover: "#0052CC",
    dark: "#003C99",
    light: "#E6F0FF",
  },
  neutral: {
    black: "#0A0A0A",
    white: "#FFFFFF",
    surface: "#F8FAFC",
    border: "#E2E8F0",
    muted: "#64748B",
  },
} as const;

export const OPA_TYPOGRAPHY = {
  primaryFont: "'Be Vietnam Pro', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  accentFont: "'Fraunces', serif",
  scale: {
    display: { fontSize: "48px", fontWeight: "800", lineHeight: "1.15" },
    h1: { fontSize: "36px", fontWeight: "800", lineHeight: "1.2" },
    h2: { fontSize: "28px", fontWeight: "700", lineHeight: "1.25" },
    h3: { fontSize: "20px", fontWeight: "700", lineHeight: "1.3" },
    body: { fontSize: "15px", fontWeight: "500", lineHeight: "1.5" },
    bodySmall: { fontSize: "13px", fontWeight: "400", lineHeight: "1.45" },
    caption: { fontSize: "11px", fontWeight: "500", lineHeight: "1.4" },
  },
} as const;

export const OPA_RADII = {
  none: "0px",
  sm: "6px",
  md: "10px",
  lg: "16px",
  xl: "24px",
  full: "9999px",
} as const;

export const OPA_MOTION = {
  easeIn: "cubic-bezier(0.2, 0.8, 0.2, 1)",
  easeOut: "cubic-bezier(0.6, 0, 0.8, 0.2)",
  springPop: { damping: 12, stiffness: 100, mass: 1 },
} as const;

export const OPA_CONTRAST = {
  mascotOn: {
    white: OPA_COLORS.primary.default,
    light: OPA_COLORS.primary.default,
    blue: OPA_COLORS.neutral.white,
    dark: OPA_COLORS.neutral.white,
    black: OPA_COLORS.neutral.white,
  },
  textOn: {
    blue: OPA_COLORS.neutral.white,
    dark: OPA_COLORS.neutral.white,
    white: OPA_COLORS.neutral.black,
    light: OPA_COLORS.neutral.black,
  },
} as const;
