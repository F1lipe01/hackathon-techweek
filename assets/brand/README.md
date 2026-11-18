# Track Things · brand

Decided 18 Nov 2026: **logo Trail**, **typeface Switzer**, **colour Altice Labs**: ink `#000000` (the Altice Labs logo), blue `#0084D6`, deep blue `#003399`, light blue `#02A1EA` on deep blue. MEO and the Altice app colours below were the alternatives.

| What | File |
|---|---|
| Options sheet (logo, typeface, colour, live preview) | [`options/brand-options.html`](options/brand-options.html) |
| Animated logo, mark ⇄ wordmark (source, plays in a browser, has controls) | [`animation/logo-reveal.html`](animation/logo-reveal.html) |
| Animated logo as 4K video (3840 × 2160): 60 fps for slides, plus a 120 fps version of the main one for 120 Hz screens; a still of the last frame for each | [`animation/out/`](animation/out/) |
| Earlier logo exports (Trail, teal) | [`../logo/`](../logo/) |

Re-render the videos after changing the animation: `node animation/render.mjs` (Node 22+, Chrome, ffmpeg). Pick variants with `mode:theme`, for example `node animation/render.mjs expand:labs-deep collapse:labs`. Themes: `labs` (default), `labs-deep`, `meo-blue`, `meo-light`, `meo-navy`, `app`.

## Colours and where each one comes from

Read on 18 Nov 2026. Nothing below was picked by eye.

| Palette | Role | Value | Source |
|---|---|---|---|
| MEO | Logo blue (frame, field) | `#2E26FF` | `logo-meo.svg`, the logo in the meo.pt header |
| MEO | Navy (ink) | `#000032` | meo.pt `theme.css` (`.bg-color-6`, navigation tabs) |
| MEO | Mint ("found") | `#00FF9D` | meo.pt `theme.css`, the `:focus-visible` outline: MEO's colour for "you are here" |
| MEO | Greys | `#F2F2F2`, `#E3E3E3`, `#42414F` | meo.pt `theme.css` |
| MEO | Blue, hover | `#2620D4` | meo.pt `theme.css` |
| Altice app | Page, card, ink | `#EEF3FB`, `#E4EBF7`, `#1A2233` | Our screenshot of the Cognitive Home app, 16 Nov (`assets/app-screens/device-list.png`) |
| Altice app | Status blue, grey | `#175BCC`, `#73727C` | Same screenshot |
| Altice app | Dark-mode teal | `#5FBEB5` | Altice Connected Home brochure render (`assets/altice-app/security.png`) |
| Altice Labs | Logo | `#000000` | `logo_alticelabs.png` on alticelabs.com |
| Altice Labs | Blues | `#0084D6`, `#003399`, `#02A1EA` | alticelabs.com page styles |

The app's grey `#73727C` and MEO's grey `#747380` are almost identical: the app in Portugal follows MEO's palette.

**Contrast.** MEO's lighter grey `#747380` and the app grey fail 4.5 : 1 on their own light surfaces, so small text uses `#42414F` (MEO) or `#555555` (Altice Labs). White text on Altice Labs `#0084D6` is 4.2 : 1: large text and shapes only. Mint `#00FF9D` never carries text on white.

**Caution.** These are MEO's and Altice's own colours, used here for a concept inside their product. Do not put the MEO or Altice logos on our material.

## Typeface

Switzer (Indian Type Foundry, via Fontshare), free for commercial use. Not available in Google Slides: install it on the presenting laptop, or embed it in the PowerPoint file. The 2-page report keeps the organisers' template fonts (Lato headings, Arial text).
