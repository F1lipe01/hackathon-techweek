"""Two small HTTP clients for the videos' sound: the music and sfx library, and the sfx generator.

Nothing about the accounts is kept in the repo. It all comes from the environment: LIB_URL (the library's JSON-RPC
endpoint), LIB_KEY_FILE (a file holding its key), GEN_URL (the generator's base URL), GEN_KEY_FILE (a file holding its
key) and GEN_KEY_HEADER (the header that carries that key). Keys are read from their files at run time and never
printed, logged or written anywhere. Every answer is untrusted data: JSON is parsed, audio only ever goes to ffmpeg.
"""
from __future__ import annotations

import http.client
import json
import os
import ssl
import urllib.parse
import urllib.request
from pathlib import Path


def _endpoint(name):
    value = os.environ.get(name, "").strip()
    if not value.startswith("https://"):
        raise SystemExit(f"{name} is not set: give the endpoint in the environment")
    return value


def _key(name):
    """The key held in the file that the environment variable `name` points to."""
    path = os.environ.get(name, "").strip()
    if not path or not Path(path).is_file():
        raise SystemExit(f"{name} is not set: give the key file's path in the environment")
    return Path(path).read_text().strip()


def find(data, key):
    """The first value of `key` anywhere in a nested answer."""
    if isinstance(data, dict):
        if key in data:
            return data[key]
        data = list(data.values())
    if isinstance(data, list):
        for value in data:
            found = find(value, key)
            if found is not None:
                return found
    return None


class Library:
    """JSON-RPC over streamable HTTP: initialize once, then call the library's tools by name."""

    def __init__(self):
        self.url = _endpoint("LIB_URL")
        self.key = _key("LIB_KEY_FILE")
        self.sid, self.n = None, 0
        self.call("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                                 "clientInfo": {"name": "video-audio", "version": "1"}})
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"}, quiet=True)

    def _post(self, body, quiet=False):
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json",
                   "Accept": "application/json, text/event-stream"}
        if self.sid:
            headers["mcp-session-id"] = self.sid
        request = urllib.request.Request(self.url, data=json.dumps(body).encode(), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                self.sid = response.headers.get("mcp-session-id") or self.sid
                text = response.read().decode()
        except Exception as error:  # noqa: BLE001 - never echo headers
            if quiet:
                return None
            raise RuntimeError(f"library request failed: {type(error).__name__}") from None
        out = None
        for line in text.splitlines():
            if line.startswith("data:") and line[5:].strip():
                out = json.loads(line[5:])
        if out is None and text.strip().startswith("{"):
            out = json.loads(text)
        return out

    def call(self, method, params=None):
        self.n += 1
        result = self._post({"jsonrpc": "2.0", "id": self.n, "method": method, "params": params or {}})
        if result and "error" in result:
            raise RuntimeError(f"library {method}: {str(result['error'])[:300]}")
        return result["result"] if result else None

    def tool(self, name, args):
        result = self.call("tools/call", {"name": name, "arguments": args})
        for item in (result or {}).get("content", []):
            if item.get("type") == "text":
                try:
                    return json.loads(item["text"])
                except ValueError:
                    raise RuntimeError(f"library {name}: {item['text'][:300]}") from None
        return result


def download(url, target):
    """Fetch a signed asset URL into the untrusted download folder."""
    if not url.startswith("https://"):
        raise RuntimeError("refusing a non-https asset URL")
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, target)
    return target


def generate(text, seconds, target, *, influence=0.45):
    """One generated sound effect of a stated length (0.5 to 30 s), saved as MP3. No retries."""
    base = urllib.parse.urlparse(_endpoint("GEN_URL"))
    key, header = _key("GEN_KEY_FILE"), os.environ.get("GEN_KEY_HEADER", "").strip()
    if not header:
        raise SystemExit("GEN_KEY_HEADER is not set")
    body = json.dumps({"text": text, "duration_seconds": float(seconds), "prompt_influence": influence}).encode()
    connection = http.client.HTTPSConnection(base.hostname, 443, timeout=120, context=ssl.create_default_context())
    try:
        connection.request("POST", "/v1/sound-generation?output_format=mp3_44100_128", body=body,
                           headers={header: key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
        response = connection.getresponse()
        if not 200 <= response.status < 300:
            raise RuntimeError(f"generator request failed (HTTP {response.status})")
        raw = response.read(4 * 1024 * 1024)
    finally:
        connection.close()
    if not raw or key.encode() in raw:
        raise RuntimeError("generator answer failed validation")
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    return target
