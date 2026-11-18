// Sound for video 2: the music bed and the sfx from public/audio/ (listed in its manifest.json; v2 and v3 are the
// later kits, and the manifest marks the sounds to avoid). Keys are the cues the scenes ask for. Gains are linear;
// the bed is -18 LUFS and the sfx peak at -3 dBFS before these gains.
import { theme } from "../theme";

/** The bed starts 5 bars in (100 BPM, 2.4 s a bar), so its last chord dies away under the end card. */
export const BED = { file: "audio/music/bed-real.wav", from: 12.0 * theme.fps, volume: 0.9 };

/** A daytime room under everything, looped, at about -30 LUFS (the file is -20.4). */
export const ROOM = { file: "audio/sfx/v2/room-tone-bright.wav", volume: 0.32 };

/** Every sfx plays this many frames before its action. */
export const LEAD_FRAMES = 2;

/** trans-4 rises and stops dead: it is laid so that its end falls on the cut. */
export const TRANS_IN_FRAMES = Math.round(1.12 * theme.fps);

export const SFX: Record<string, { file: string; volume: number }> = {
  trans: { file: "audio/sfx/v3/trans-2.wav", volume: 0.28 },        // a new scene
  transLong: { file: "audio/sfx/v3/trans-3.wav", volume: 0.4 },     // into the app, with a soft tail
  transCut: { file: "audio/sfx/v3/trans-1.wav", volume: 0.3 },      // a cut between passages of the app
  transIn: { file: "audio/sfx/v3/trans-4.wav", volume: 0.3 },       // the swell into the end card
  shutter: { file: "audio/sfx/v3/shutter-soft.wav", volume: 0.7 },  // each photo taken
  slide: { file: "audio/sfx/v3/slide-1.wav", volume: 0.38 },        // a photo gliding into its slot
  slideUi: { file: "audio/sfx/v3/slide-2.wav", volume: 0.32 },      // the camera moving into the phone
  capture: { file: "audio/sfx/v3/click-2.wav", volume: 0.35 },      // the kit frame the edge service analyses
  click: { file: "audio/sfx/v3/click-1.wav", volume: 0.45 },        // the brackets closing on the book
  send: { file: "audio/sfx/v3/click-3.wav", volume: 0.45 },         // send in the app
  typing: { file: "audio/sfx/typing-soft.wav", volume: 0.35 },      // typing in the app
  door: { file: "audio/sfx/door-open.wav", volume: 0.7 },           // the contact sensor's door
  notify: { file: "audio/sfx/v2/notify-2.wav", volume: 0.45 },      // the message on the phone
  logo: { file: "audio/sfx/v2/boom-stop.wav", volume: 0.26 },       // end card
};
