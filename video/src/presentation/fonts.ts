// Fonts for the presentation film. Switzer (display) from local files in public/presentation/fonts (Fontshare,
// free licence), so a long 4K render does not depend on the network for it; Montserrat (the Altice app) and
// JetBrains Mono (the thinking panel) from Google Fonts. Rendering waits until every weight is ready.
import { continueRender, delayRender, staticFile } from "remotion";
import { loadFont as loadMontserrat } from "@remotion/google-fonts/Montserrat";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";

loadMontserrat("normal", { weights: ["400", "500", "600", "700"], subsets: ["latin", "latin-ext"] });
loadMono("normal", { weights: ["400", "500", "600"], subsets: ["latin", "latin-ext"] });
loadInter("normal", { weights: ["500"], subsets: ["latin"] }); // "by" on the end card

const WEIGHTS = ["400", "500", "600", "700"] as const;

if (typeof document !== "undefined" && typeof FontFace !== "undefined") {
  const handle = delayRender("Loading Switzer");
  Promise.all(
    WEIGHTS.map((w) => {
      const face = new FontFace("Switzer", `url(${staticFile(`presentation/fonts/switzer-${w}.woff2`)}) format("woff2")`, { weight: w });
      return face.load().then((f) => document.fonts.add(f));
    }),
  ).then(
    () => continueRender(handle),
    (e) => {
      console.error("Switzer failed to load", e);
      continueRender(handle);
    },
  );
}
