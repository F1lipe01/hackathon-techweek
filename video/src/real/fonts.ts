// Fonts for video 2: Switzer (display, bundled in public/real/fonts), Inter and JetBrains Mono from Google Fonts.
import { continueRender, delayRender, staticFile } from "remotion";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";
import { loadFont as loadMontserrat } from "@remotion/google-fonts/Montserrat";

loadInter("normal", { weights: ["400", "500", "600"], subsets: ["latin", "latin-ext"] });
loadInter("italic", { weights: ["400", "500"], subsets: ["latin", "latin-ext"] });
loadMono("normal", { weights: ["400", "500", "700"], subsets: ["latin", "latin-ext"] });
loadMontserrat("normal", { weights: ["500", "600"], subsets: ["latin"] });

if (typeof document !== "undefined" && typeof FontFace !== "undefined") {
  const handle = delayRender("Switzer");
  Promise.all(
    [400, 500, 600, 700].map((w) =>
      new FontFace("Switzer", `url(${staticFile(`real/fonts/switzer-${w}.woff2`)}) format("woff2")`, { weight: String(w) })
        .load()
        .then((f) => document.fonts.add(f)),
    ),
  )
    .catch(() => undefined)
    .then(() => continueRender(handle));
}
