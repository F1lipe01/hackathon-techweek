// The one theme for both ThingTracker videos. Never inline a colour, easing or spring in a component.
// Colours follow the ThingTracker brand (Altice Labs blue) and the Altice app copy (teal); the look is light.
import { Easing } from "remotion";

export const theme = {
  colors: {
    bg: "#F2F5FA",          // page
    bgAlt: "#E6ECF5",       // cards, panels
    ink: "#111320",         // text
    inkDim: "#56606C",      // secondary text
    labs: "#0084D6",        // THE hero colour: detection boxes, the one highlight per frame
    labsDeep: "#003399",
    teal: "#2ABE9E",        // the Altice app's primary (buttons, the assistant)
    alert: "#D2403A",       // alerts only
    code: "#0E1726",        // the "thinking" code panel
    codeInk: "#D7E3F4",
    codeDim: "#7C8BA1",
    codeOk: "#3DDC97",
    white: "#FFFFFF",
  },
  fonts: {
    display: "Switzer, Inter, 'Helvetica Neue', Arial, sans-serif",  // load Switzer: https://api.fontshare.com/v2/css?f[]=switzer@400,500,600,700&display=swap
    app: "Montserrat, 'Helvetica Neue', Arial, sans-serif",           // the Altice app's font
    mono: "'JetBrains Mono', ui-monospace, Menlo, monospace",
  },
  ease: {
    out: Easing.bezier(0.16, 1, 0.3, 1),      // entrances
    inOut: Easing.bezier(0.83, 0, 0.17, 1),   // camera moves, Ken Burns
    in: Easing.bezier(0.7, 0, 0.84, 0),       // exits only
  },
  spring: {
    snappy: { damping: 14, stiffness: 160, mass: 0.6 },
    smooth: { damping: 20, stiffness: 90, mass: 1 },
    bouncy: { damping: 11, stiffness: 170, mass: 0.7 },
  },
  fps: 30,
  width: 1920,
  height: 1080,
} as const;
