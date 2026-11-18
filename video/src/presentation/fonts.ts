// Fonts for the presentation film: Switzer (display) from Fontshare, Montserrat (the Altice app) and JetBrains Mono
// (the "thinking" panel) from Google Fonts. Rendering waits until every weight is ready.
import { continueRender, delayRender } from "remotion";
import { loadFont as loadMontserrat } from "@remotion/google-fonts/Montserrat";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";

loadMontserrat("normal", { weights: ["400", "500", "600", "700"], subsets: ["latin", "latin-ext"] });
loadMono("normal", { weights: ["400", "500", "600"], subsets: ["latin", "latin-ext"] });

const SWITZER_CSS = "https://api.fontshare.com/v2/css?f[]=switzer@400,500,600,700&display=swap";

if (typeof document !== "undefined" && !document.querySelector("link[data-switzer]")) {
  const handle = delayRender("Loading Switzer from Fontshare");
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = SWITZER_CSS;
  link.setAttribute("data-switzer", "1");
  let done = false;
  const finish = () => {
    if (!done) {
      done = true;
      continueRender(handle);
    }
  };
  link.onload = () => {
    Promise.all(["400", "500", "600", "700"].map((w) => document.fonts.load(`${w} 64px Switzer`)))
      .then(() => document.fonts.ready)
      .then(finish, finish);
  };
  link.onerror = finish;
  document.head.appendChild(link);
}
