// Sound for video 2: the music bed and the sfx from public/audio/ (listed in its manifest.json; sfx/v2 is the second
// kit). Keys are the cues the scenes ask for. Gains are linear; the bed is -18 LUFS and the sfx peak at -3 dBFS
// before these gains.
import { theme } from "../theme";

/** The bed starts 5 bars in (100 BPM, 2.4 s a bar), so its resolve (43.2 s) lands near the door and its last chord
 *  dies away under the end card. */
export const BED = { file: "audio/music/bed-real.wav", from: 12.0 * theme.fps, volume: 0.85 };

/** A daytime room under everything, looped, at about -30 LUFS (the file is -20.4). */
export const ROOM = { file: "audio/sfx/v2/room-tone-bright.wav", volume: 0.32 };

/** Every sfx plays this many frames before its action. */
export const LEAD_FRAMES = 2;

export const SFX: Record<string, { file: string; volume: number }> = {
  shutter: { file: "audio/sfx/v2/shutter-3.wav", volume: 0.7 },     // each photo: a real camera's shutter
  shutterCam: { file: "audio/sfx/v2/shutter-2.wav", volume: 0.45 }, // the kit frame the edge service analyses
  whoosh: { file: "audio/sfx/v2/whoosh-1.wav", volume: 0.3 },       // a card arriving, a camera move
  whooshBig: { file: "audio/sfx/v2/whoosh-2.wav", volume: 0.22 },   // a new scene
  whip: { file: "audio/sfx/v2/whoosh-4.wav", volume: 0.28 },        // a cut between passages of the app
  swipe: { file: "audio/sfx/v2/swipe-1.wav", volume: 0.55 },        // a crop or an app card lifting out
  swipeAlt: { file: "audio/sfx/v2/swipe-2.wav", volume: 0.55 },
  tap: { file: "audio/sfx/v2/tap-1.wav", volume: 0.55 },            // send, a line of the analysis
  tapAlt: { file: "audio/sfx/v2/tap-2.wav", volume: 0.55 },         // a view landing in its slot
  lockon: { file: "audio/sfx/v2/lockon-1.wav", volume: 0.45 },      // a detection box
  lockonBig: { file: "audio/sfx/v2/lockon-2.wav", volume: 0.5 },    // the lock on the book
  lockonSoft: { file: "audio/sfx/v2/lockon-3.wav", volume: 0.4 },   // the fingerprint complete
  notify: { file: "audio/sfx/v2/notify-2.wav", volume: 0.5 },       // the message on the phone
  typing: { file: "audio/sfx/typing-soft.wav", volume: 0.4 },       // typing in the app
  door: { file: "audio/sfx/door-open.wav", volume: 0.8 },           // the contact sensor's door
  paper: { file: "audio/sfx/v2/paper-photo.wav", volume: 0.5 },    // a photo landing in its slot
  page: { file: "audio/sfx/v2/page-flip.wav", volume: 0.35 },       // the book, named in the opening
  logo: { file: "audio/sfx/v2/boom-stop.wav", volume: 0.32 },       // end card
};
