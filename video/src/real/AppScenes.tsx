// 3 · Na app: our app (a copy of the Altice app, simulated data), recorded on screen, in a phone over the bright home.
// Three passages at real speed; in each the camera moves into the phone, onto the element that matters (the answer, the
// sensor, the notification), so it can be read. The caption on the left says it in Portuguese, on a fixed grid.
import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { IPHONE, IPhone, VideoAt } from "./devices";
import { Chip, Heading, Overline } from "./layers";
import { appUi, clamp, Cue, look, warm } from "./look";
import { BlurIn, ContactShadow, Glass } from "./stage";

const { c, a } = look;

// footage/app-book.mp4 from 33 s, re-encoded with regular keyframes (the original's sparse full-range keyframes made
// Remotion show frames seconds off). Times below stay in the original recording's seconds.
const APP = "real/app-book-33s.mp4";
const APP_T0 = 33;
// app-book.marks.json, plus moments measured on the frames: the replies appear at 39.2 and 48.2 and stay put, the
// sensor fires at 53.94 (mark "alert") and the notification banner has slid in by 54.8.
const MARK = { sentQ: 37.73, answerQ: 39.2, sentS: 46.752, answerS: 48.2, door: 53.943, banner: 54.55, bannerIn: 54.8 };
// regions of the recording (px of 1206 x 2622)
type Region = { x: number; y: number; w: number; h: number };
const REPLY: Region = { x: 66, y: 1827, w: 924, h: 441 };       // the assistant's reply bubble (answer, then sensor)
const BANNER: Region = { x: 30, y: 156, w: 1146, h: 246 };      // the notification banner
// the sensor card's icon and title (measured on the frame at 49.6 s): the title is cut off with an ellipsis
const ICON = { x: 160, y: 2080, w: 106, h: 98 };
const TITLE = { x: 300, y: 2060, w: 630, h: 62, textX: 313 };

const PASSAGES = [
  { from: 36.55, to: 42.1, zoomAt: MARK.answerQ + 0.1, region: REPLY, width: 860 },
  { from: 45.7, to: 51.1, zoomAt: MARK.answerS + 0.1, region: REPLY, width: 860 },
  { from: 53.4, to: 57.4, zoomAt: MARK.bannerIn, region: BANNER, width: 860 },
].map((p) => ({ ...p, len: Math.round((p.to - p.from) * theme.fps) }));
const LEAD = 8;
const START = PASSAGES.reduce<number[]>((acc, p, i) => [...acc, i === 0 ? LEAD : acc[i - 1] + PASSAGES[i - 1].len], []);
const at = (i: number, t: number) => START[i] + Math.round((t - PASSAGES[i].from) * theme.fps);
const ZOOM_LEN = 28;
const MORPH = at(1, MARK.answerS) + ZOOM_LEN + 6;
export const APP_FRAMES = START[2] + PASSAGES[2].len;
export const APP_CUES: Cue[] = [
  { at: START[0], file: "typing", dur: at(0, MARK.sentQ) - START[0] - 2 },
  { at: at(0, MARK.sentQ), file: "send" },
  ...PASSAGES.map((p, i) => ({ at: at(i, p.zoomAt), file: "slideUi" })),
  { at: START[1] - 1, file: "transCut" },
  { at: START[1], file: "typing", dur: at(1, MARK.sentS) - START[1] - 2 },
  { at: at(1, MARK.sentS), file: "send" },
  { at: START[2] - 1, file: "transCut" },
  { at: at(2, MARK.door), file: "door" },
  { at: at(2, MARK.banner), file: "notify" },
];

// the phone at rest, and the point where a zoomed element is centred
const PH = 900;
const PK = PH / IPHONE.h;
const PW = IPHONE.w * PK;
const PHONE_C = { x: 1320, y: 548 };
const TARGET = { x: 1260, y: 548 };                            // the zoomed element's centre: clear of the caption column
const GRID_X = 140;

export const App: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const i = Math.max(0, START.filter((s) => frame >= s).length - 1);
  const P = PASSAGES[i];
  const local = Math.max(0, frame - START[i]);
  const src = Math.min(P.to, P.from + local / fps);

  // the phone turns in once; then each passage starts on the whole phone and moves into its element
  const enter = spring({ frame: frame - 2, fps, config: { damping: 20, stiffness: 70, mass: 1.1 } });
  const zStart = at(i, P.zoomAt);
  // in on the element, then (before a cut to the next passage) back out to the whole phone, so the cut is calm
  const zIn = interpolate(frame, [zStart, zStart + ZOOM_LEN], [0, 1], { ...clamp, easing: theme.ease.inOut });
  const zOut = i < 2 ? interpolate(frame, [START[i] + P.len - 22, START[i] + P.len - 2], [0, 1], { ...clamp, easing: theme.ease.inOut }) : 0;
  const zp = zIn * (1 - zOut);
  const Z = P.width / (P.region.w * PK);
  const scale = (0.9 + 0.1 * enter) * (1 + (Z - 1) * zp);
  // flat on purpose: a 3D-rotated layer is rasterised soft when it is scaled up, and the zoom must stay sharp
  // the element's centre in the phone's own coordinates, and where it sits on the frame with the phone at rest
  const lx = (IPHONE.sx + P.region.x + P.region.w / 2) * PK;
  const ly = (IPHONE.sy + P.region.y + P.region.h / 2) * PK;
  const left = PHONE_C.x - PW / 2;
  const top = PHONE_C.y - PH / 2;
  const dx = (TARGET.x - (left + lx)) * zp + 160 * (1 - enter);
  const dy = (TARGET.y - (top + ly)) * zp;
  const phoneTransform = `translate(${dx}px, ${dy + Math.sin(frame / 50) * 3 * (1 - zp)}px) scale(${scale})`;

  const doorP = interpolate(frame, [at(2, MARK.door), at(2, MARK.door) + 8, at(2, MARK.bannerIn), at(2, MARK.bannerIn) + 8], [0, 1, 1, 0], { ...clamp, easing: theme.ease.out });
  const morph = interpolate(frame, [MORPH, MORPH + 16], [0, 1], { ...clamp, easing: theme.ease.inOut });
  const END = APP_FRAMES + 30;

  return (
    <AbsoluteFill>
      <div style={{ opacity: 1 - zp }}>
        <ContactShadow x={PHONE_C.x + 26} y={PHONE_C.y + PH / 2 + 34} w={520} opacity={0.38 * enter} />
      </div>

      <div style={{ position: "absolute", left, top, transformOrigin: `${lx}px ${ly}px`, transform: phoneTransform,
        opacity: interpolate(enter, [0, 0.25], [0, 1], clamp) }}>
        <IPhone height={PH}>
          <VideoAt src={APP} second={src - APP_T0} />
          {/* on the sensor card: the wand becomes a book, and the title is shown in full */}
          {i === 1 && morph > 0 ? (
            <div style={{ position: "absolute", left: 0, top: 0, width: 1206, height: 2622, transform: `scale(${PK})`, transformOrigin: "0 0" }}>
              <div style={{ position: "absolute", left: ICON.x, top: ICON.y, width: ICON.w, height: ICON.h, background: appUi.card, opacity: Math.min(1, morph * 1.6) }} />
              <svg viewBox="0 0 24 24" width={74} height={74} style={{ position: "absolute", left: ICON.x + (ICON.w - 74) / 2, top: ICON.y + (ICON.h - 74) / 2,
                transform: `rotate(${-30 * (1 - morph)}deg) scale(${0.7 + 0.3 * morph})`, opacity: morph }}>
                <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20" fill="none" stroke={c.teal} strokeWidth={2}
                  strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - morph} />
                <path d="M9 7h7" fill="none" stroke={c.teal} strokeWidth={2} strokeLinecap="round" opacity={morph} />
              </svg>
              <div style={{ position: "absolute", left: TITLE.x, top: TITLE.y, width: TITLE.w, height: TITLE.h, background: appUi.card,
                display: "flex", alignItems: "center" }}>
                <div style={{ marginLeft: TITLE.textX - TITLE.x, fontFamily: theme.fonts.app, fontWeight: 600, fontSize: 41, color: appUi.ink, whiteSpace: "nowrap",
                  letterSpacing: "-0.005em" }}>{fullTitle(morph)}</div>
              </div>
            </div>
          ) : null}
        </IPhone>
      </div>

      {doorP > 0 ? (
        <div style={{ position: "absolute", left: PHONE_C.x, top: 760, transform: `translate(-50%, -50%) translateY(${(1 - doorP) * 14}px)`, opacity: doorP }}>
          <Glass strong style={{ borderRadius: 999, display: "flex", alignItems: "center", gap: 14, padding: "14px 26px 14px 16px", whiteSpace: "nowrap" }}>
            <div style={{ width: 42, height: 42, borderRadius: 42, background: a(c.labs, 0.12), display: "flex", alignItems: "center", justifyContent: "center" }}>
              <div style={{ width: 15, height: 22, border: `3px solid ${c.labs}`, borderRadius: 2, boxSizing: "border-box",
                transform: "perspective(60px) rotateY(-35deg)", transformOrigin: "left center" }} />
            </div>
            <div style={{ fontFamily: theme.fonts.display, fontSize: 27, fontWeight: 600, color: c.ink }}>Sensor de contacto · porta aberta</div>
          </Glass>
        </div>
      ) : null}

      <div style={{ position: "absolute", left: GRID_X, top: 360 }}>
        <BlurIn at={6}><Overline>3 · Na app</Overline></BlurIn>
      </div>
      <Caption from={START[0]} to={START[1]} heading="“Onde está o meu livro?”" note="Na secretária, na Work Room, às 16:30." noteAt={at(0, PASSAGES[0].zoomAt) + ZOOM_LEN - 6} />
      <Caption from={START[1]} to={START[2]} heading="“Avisa-me se eu sair de casa sem o livro.”" note="Sensor criado: sair de casa sem o livro." noteAt={MORPH} />
      <Caption from={START[2]} to={END} heading="A porta abre e o livro fica." note="Mensagem: saíste sem o livro." noteAt={at(2, PASSAGES[2].zoomAt) + ZOOM_LEN - 6} alert />

      <div style={{ position: "absolute", left: GRID_X, top: 930 }}>
        <BlurIn at={12}>
          <Chip mono bg={a(c.white, 0.85)} color={c.inkDim} style={{ fontSize: 18 }}>Interface: protótipo · dados simulados</Chip>
        </BlurIn>
      </div>
    </AbsoluteFill>
  );
};

/** The sensor's title, cut off in the app ("Left home without th…"), completing itself as the icon turns into a book. */
const TITLE_FULL = "Left home without the book";
const TITLE_CUT = "Left home without th";
const fullTitle = (p: number) => {
  const extra = Math.round((TITLE_FULL.length - TITLE_CUT.length) * p);
  return extra === 0 ? `${TITLE_CUT}…` : TITLE_FULL.slice(0, TITLE_CUT.length + extra);
};

/** One passage's caption, on the left grid: the sentence, then what the app answers, in Portuguese. */
const Caption: React.FC<{ from: number; to: number; heading: string; note: string; noteAt: number; alert?: boolean }> = ({ from, to, heading, note, noteAt, alert }) => {
  const frame = useCurrentFrame();
  if (frame < from || frame > to) return null;
  const out = interpolate(frame, [to - 4, to], [1, 0], clamp);
  return (
    <div style={{ opacity: out }}>
      <div style={{ position: "absolute", left: GRID_X, top: 408, width: 600 }}>
        <BlurIn at={from + 2}><Heading size={64}>{heading}</Heading></BlurIn>
      </div>
      <div style={{ position: "absolute", left: GRID_X, top: 640, width: 600 }}>
        <BlurIn at={noteAt}>
          <div style={{ fontFamily: theme.fonts.display, fontSize: 36, fontWeight: 500, lineHeight: 1.25, color: alert ? c.alert : c.ink }}>{note}</div>
        </BlurIn>
      </div>
    </div>
  );
};
