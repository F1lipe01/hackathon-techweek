// Sound for video 2: the music bed and the sfx from public/audio/ (listed in its manifest.json). Keys are the cues the
// scenes ask for. Gains are linear; the bed is -18 LUFS and the sfx peak at -3 dBFS before these gains. The mix measures
// about -17.5 LUFS integrated with true peaks under -1.5 dBFS.
import { theme } from "../theme";

/** The bed starts 5 bars in (100 BPM, 2.4 s a bar), so its resolve (43.2 s) lands as the front door opens and its
 *  last chord dies away under the end card. */
export const BED = { file: "audio/music/bed-real.wav", from: 12.0 * theme.fps, volume: 0.95 };

export const SFX: Record<string, { file: string; volume: number }> = {
  shutter: { file: "audio/sfx/shutter.wav", volume: 0.6 },     // each photo taken on the phone
  capture: { file: "audio/sfx/tap-2.wav", volume: 0.54 },      // the kit frame the edge service analyses
  confirm: { file: "audio/sfx/lock-on.wav", volume: 0.65 },    // "Livro · é o teu"
  tick: { file: "audio/sfx/tap-1.wav", volume: 0.54 },         // send, and the negative control
  typing: { file: "audio/sfx/typing-soft.wav", volume: 0.42 }, // typing in the app
  door: { file: "audio/sfx/door-open.wav", volume: 0.83 },      // the contact sensor's door
  notify: { file: "audio/sfx/notify-info.wav", volume: 0.71 },  // the message on the phone
  logo: { file: "audio/sfx/hit-soft.wav", volume: 0.42 },      // end card
};
