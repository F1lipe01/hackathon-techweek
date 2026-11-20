// Reading the video's assets: licensed stock clips (public/stock/stock.json, boxes/<clip>.json with real
// OWLv2 boxes sampled every 0,5 s) and the audio (public/audio/manifest.json: the music bed and the sfx).
// Until a file exists, the hooks return null and the shots draw placeholders.
import React, { useEffect, useState } from "react";
import { AbsoluteFill, continueRender, delayRender, staticFile } from "remotion";
import { theme } from "../theme";
import { alpha } from "./tokens";

const cache = new Map<string, unknown>();
const pending = new Map<string, Promise<unknown>>();

/** A JSON file from public/, or null if it is missing. Rendering waits for the answer. */
export const useJson = <T,>(path: string): T | null => {
  const [data, setData] = useState<T | null>((cache.get(path) as T | undefined) ?? null);
  const [handle] = useState(() => (cache.has(path) ? null : delayRender(`Reading ${path}`)));
  useEffect(() => {
    if (handle === null) return;
    if (!pending.has(path)) {
      pending.set(
        path,
        fetch(staticFile(path))
          .then((r) => (r.ok ? r.json() : null))
          .catch(() => null),
      );
    }
    pending.get(path)!.then((d) => {
      cache.set(path, d);
      setData(d as T | null);
      continueRender(handle);
    });
  }, [handle, path]);
  return data;
};

/** Stand-in for a stock clip that has not arrived yet: a dark frame with the clip's name. */
export const Placeholder: React.FC<{ name: string; note?: string }> = ({ name, note }) => (
  <AbsoluteFill style={{ background: `linear-gradient(160deg, ${theme.colors.code}, ${theme.colors.ink})`, alignItems: "center", justifyContent: "center" }}>
    <div style={{ fontFamily: theme.fonts.mono, fontSize: 26, color: alpha(theme.colors.white, 0.5), textAlign: "center", lineHeight: 1.6 }}>
      stock: {name}
      {note ? <div style={{ fontSize: 20, opacity: 0.7 }}>{note}</div> : null}
    </div>
  </AbsoluteFill>
);
