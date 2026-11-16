#!/usr/bin/env python3
"""Minimal client for the Connected Home MCP server (Altice Labs, ATC Hackathon 2026).

The server needs two things on every request: the X-API-Key header and an OAuth
bearer token from its Keycloak realm. Its Keycloak client only accepts the
callback http://mcp-redirect.futurelabsinnovations.com:5434/callback (that host
resolves to 127.0.0.1), which is why generic MCP clients with a localhost
callback cannot log in. This client uses that callback.

Standard library only. Reads settings from the repo's .env.

    python3 mcp/client/chmcp.py login               # browser login with the team account
    python3 mcp/client/chmcp.py tools               # list tools
    python3 mcp/client/chmcp.py call TOOL '{...}'   # call one tool, JSON arguments
    python3 mcp/client/chmcp.py serve               # stdio MCP proxy (for Claude Code)
"""
import base64, hashlib, http.server, json, os, secrets, sys, threading, time
import urllib.error, urllib.parse, urllib.request, webbrowser

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TOKENS = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".tokens.json")
PROTOCOL = "2025-06-18"


def load_env():
    env = {}
    with open(os.path.join(ROOT, ".env")) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


ENV = load_env()
MCP_URL = ENV["CONNECTED_HOME_MCP_URL"].rstrip("/")
API_KEY = ENV["CONNECTED_HOME_API_KEY"]
CLIENT_ID = ENV.get("CONNECTED_HOME_OAUTH_CLIENT_ID", "mcp-client")
PORT = int(ENV.get("CONNECTED_HOME_OAUTH_CALLBACK_PORT", "5434"))
REDIRECT = f"http://{ENV.get('CONNECTED_HOME_OAUTH_REDIRECT_HOST', 'mcp-redirect.futurelabsinnovations.com')}:{PORT}/callback"


def log(*a):
    print(*a, file=sys.stderr, flush=True)


USER_AGENT = "it-porto-chmcp/0.1"  # Cloudflare in front of the server rejects Python's default UA


def fetch(method, url, data=None, headers=None, timeout=30):
    headers = {"User-Agent": USER_AGENT, **(headers or {})}
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


def get_json(url):
    status, _, body = fetch("GET", url)
    if status != 200:
        raise SystemExit(f"GET {url} -> {status}")
    return json.loads(body)


# ---------------------------------------------------------------- OAuth

def discover():
    prm = get_json(f"{MCP_URL}/.well-known/oauth-protected-resource")
    issuer = prm["authorization_servers"][0]
    return get_json(f"{issuer}/.well-known/openid-configuration")


def save_tokens(tok, token_endpoint):
    now = time.time()
    data = {
        "access_token": tok["access_token"],
        "refresh_token": tok.get("refresh_token"),
        "expires_at": now + int(tok.get("expires_in", 300)) - 30,
        "refresh_expires_at": now + int(tok.get("refresh_expires_in", 1800)) - 30,
        "token_endpoint": token_endpoint,
    }
    fd = os.open(TOKENS, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(data, f)
    return data


def login():
    meta = discover()
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(16)
    url = meta["authorization_endpoint"] + "?" + urllib.parse.urlencode({
        "client_id": CLIENT_ID, "response_type": "code", "scope": "openid",
        "redirect_uri": REDIRECT, "code_challenge": challenge,
        "code_challenge_method": "S256", "state": state, "resource": MCP_URL,
    })
    result = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if not self.path.startswith("/callback"):
                self.send_response(404); self.end_headers(); return
            result.update({k: v[0] for k, v in q.items()})
            ok = "code" in result and result.get("state") == state
            self.send_response(200 if ok else 400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            msg = "Login complete. You can close this tab." if ok else f"Login failed: {result.get('error_description') or result.get('error') or 'state mismatch'}"
            self.wfile.write(f"<html><body style='font-family:sans-serif'><h2>{msg}</h2></body></html>".encode())

        def log_message(self, *a):
            pass

    server = http.server.HTTPServer(("127.0.0.1", PORT), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    log("Opening the login page in your browser. If it does not open, visit:\n" + url)
    webbrowser.open(url)
    deadline = time.time() + 600
    while "code" not in result and "error" not in result and time.time() < deadline:
        time.sleep(0.3)
    server.shutdown()
    if "code" not in result or result.get("state") != state:
        raise SystemExit(f"Login failed: {result.get('error_description') or result.get('error') or 'timeout or state mismatch'}")
    status, _, body = fetch("POST", meta["token_endpoint"], urllib.parse.urlencode({
        "grant_type": "authorization_code", "code": result["code"], "redirect_uri": REDIRECT,
        "client_id": CLIENT_ID, "code_verifier": verifier,
    }).encode(), {"Content-Type": "application/x-www-form-urlencoded"})
    if status != 200:
        raise SystemExit(f"Token exchange failed ({status}): {body[:300]!r}")
    save_tokens(json.loads(body), meta["token_endpoint"])
    log("Logged in. Tokens saved to mcp/client/.tokens.json (gitignored).")


def access_token():
    if not os.path.exists(TOKENS):
        raise SystemExit("Not logged in. Run: python3 mcp/client/chmcp.py login")
    with open(TOKENS) as f:
        t = json.load(f)
    if time.time() < t["expires_at"]:
        return t["access_token"]
    if not t.get("refresh_token") or time.time() > t["refresh_expires_at"]:
        raise SystemExit("Session expired. Run: python3 mcp/client/chmcp.py login")
    status, _, body = fetch("POST", t["token_endpoint"], urllib.parse.urlencode({
        "grant_type": "refresh_token", "refresh_token": t["refresh_token"], "client_id": CLIENT_ID,
    }).encode(), {"Content-Type": "application/x-www-form-urlencoded"})
    if status != 200:
        raise SystemExit(f"Token refresh failed ({status}). Run: python3 mcp/client/chmcp.py login")
    return save_tokens(json.loads(body), t["token_endpoint"])["access_token"]


# ---------------------------------------------------------------- MCP (streamable HTTP)

class Upstream:
    def __init__(self):
        self.session = None
        self.next_id = 1

    def _post(self, msg):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "X-Client-Type": "core",
            "X-API-Key": API_KEY,
            "Authorization": f"Bearer {access_token()}",
            "MCP-Protocol-Version": PROTOCOL,
        }
        if self.session:
            headers["Mcp-Session-Id"] = self.session
        status, rh, body = fetch("POST", MCP_URL, json.dumps(msg).encode(), headers, timeout=60)
        sid = {k.lower(): v for k, v in rh.items()}.get("mcp-session-id")
        if sid:
            self.session = sid
        if status == 202 or not body:
            return status, None
        ctype = {k.lower(): v for k, v in rh.items()}.get("content-type", "")
        if "text/event-stream" in ctype:
            found = None
            for line in body.decode("utf-8", "replace").splitlines():
                if line.startswith("data:"):
                    try:
                        ev = json.loads(line[5:].strip())
                    except ValueError:
                        continue
                    if isinstance(ev, dict) and ev.get("id") == msg.get("id"):
                        found = ev
            return status, found
        try:
            return status, json.loads(body)
        except ValueError:
            return status, {"error": {"code": status, "message": body[:500].decode("utf-8", "replace")}}

    def initialize(self):
        self.session = None
        status, res = self._post({"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {
            "protocolVersion": PROTOCOL, "capabilities": {},
            "clientInfo": {"name": "it-porto-chmcp", "version": "0.1"}}})
        if status >= 400 or not res or "error" in res:
            raise SystemExit(f"initialize failed ({status}): {res}")
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return res["result"]

    def request(self, method, params=None):
        if self.session is None:
            self.initialize()
        self.next_id += 1
        msg = {"jsonrpc": "2.0", "id": self.next_id, "method": method, "params": params or {}}
        status, res = self._post(msg)
        if status in (400, 404) and self.session:  # session expired: start a new one once
            self.initialize()
            status, res = self._post(msg)
        if res is None:
            return {"error": {"code": status, "message": "empty response"}}
        return res


# ---------------------------------------------------------------- stdio proxy

def serve():
    up = Upstream()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        mid, method = msg.get("id"), msg.get("method", "")
        if mid is None:
            continue  # notifications: nothing to forward
        if method == "initialize":
            reply = {"jsonrpc": "2.0", "id": mid, "result": {
                "protocolVersion": msg.get("params", {}).get("protocolVersion", PROTOCOL),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "connected-home-proxy", "version": "0.1"}}}
        elif method == "ping":
            reply = {"jsonrpc": "2.0", "id": mid, "result": {}}
        else:
            try:
                res = up.request(method, msg.get("params"))
                reply = {"jsonrpc": "2.0", "id": mid}
                reply.update({"error": res["error"]} if "error" in res else {"result": res.get("result", {})})
            except SystemExit as e:
                reply = {"jsonrpc": "2.0", "id": mid, "error": {"code": -32000, "message": str(e)}}
        sys.stdout.write(json.dumps(reply) + "\n")
        sys.stdout.flush()


# ---------------------------------------------------------------- CLI

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "login":
        login()
    elif cmd == "tools":
        res = Upstream().request("tools/list")
        if "error" in res:
            raise SystemExit(json.dumps(res["error"]))
        for t in res["result"].get("tools", []):
            props = list((t.get("inputSchema") or {}).get("properties", {}).keys())
            print(f"{t['name']}({', '.join(props)})\n    {(t.get('description') or '').strip()}\n")
    elif cmd == "call":
        args = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        res = Upstream().request("tools/call", {"name": sys.argv[2], "arguments": args})
        print(json.dumps(res.get("result", res), indent=2, ensure_ascii=False))
    elif cmd == "raw":
        res = Upstream().request("tools/list")
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif cmd == "serve":
        serve()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
