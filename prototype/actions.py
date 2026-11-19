"""Device actions through the Connected Home MCP (our client in mcp/client/chmcp.py).

DRY RUN BY DEFAULT: the exact calls that would be made are returned and logged, nothing changes in the home.
Set TT_LIVE_ACTIONS=1 to act on the real Light and Plug, and only with the team's explicit go-ahead.
The alarm, scenarios and timers are deliberately not wired: the only tool here is update_device_capabilities,
with the payloads of mcp/tools-schema.json (power on/off, color_rgb 0-255 per channel).
"""
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mcp" / "client"))

LIVE = os.environ.get("TT_LIVE_ACTIONS") == "1"

# The kit's devices by id (from get_home_devices, 16 Nov): the MCP prefers deviceId to a name lookup.
LIGHT = "00e038d4-0da7-45c2-b61f-f38c9ff9df82"
PLUG = "bc891629-98bc-44f7-99a8-1aa61428a9bf"
TOOL = "update_device_capabilities"


def _calls(device, *bodies):
    return [(TOOL, {"deviceId": device, "body": b}) for b in bodies]


ON, OFF = {"type": "power", "value": "on"}, {"type": "power", "value": "off"}
rgb = lambda r, g, b: {"type": "color_rgb", "redValue": r, "greenValue": g, "blueValue": b}
# A colour is sent after "power on", so the bulb shows it even if it was off (colour writes were never tested live:
# 10-mcp-in-practice.md). Each action is a list of calls, made in order.
CALLS = {
    "light_red": _calls(LIGHT, ON, rgb(255, 0, 0)),
    "light_blue": _calls(LIGHT, ON, rgb(0, 132, 214)),
    "light_green": _calls(LIGHT, ON, rgb(0, 200, 80)),
    "light_off": _calls(LIGHT, OFF),
    "plug_off": _calls(PLUG, OFF),
    "plug_on": _calls(PLUG, ON),
}

LABELS = {
    "notify": "aviso no telemóvel", "light_red": "luz vermelha", "light_blue": "luz azul", "light_green": "luz verde",
    "light_off": "desligar a luz", "plug_off": "desligar a tomada", "plug_on": "ligar a tomada",
    "alarm_on": "alarme (simulado)", "alarm_off": "desligar o alarme (simulado)",
}
# The alarm is ThingTracker's own simulated state, ALWAYS: no MCP call is ever built for it, live or not (AGENTS.md
# rule 1: never touch the alarm; patch_home_security_status is a write tool and only changes the arming mode anyway).
SIMULATED = {"alarm_on": "simulated: the alarm sounds in the app only; the Altice alarm is never called",
             "alarm_off": "simulated: the alarm is off in the app; the Altice alarm is never called"}


def run(action):
    """Returns {"action", "label", "live", "calls": [{"tool", "arguments", "result"}], "result"}; never raises.
    "tool" and "arguments" repeat the first call, for older readers of the event log."""
    if action in SIMULATED:
        return {"action": action, "label": LABELS[action], "live": False, "calls": [], "tool": None, "arguments": None,
                "result": SIMULATED[action]}
    if action == "notify" or action not in CALLS:
        return {"action": action, "label": LABELS.get(action, action), "live": False, "calls": [], "tool": None,
                "arguments": None, "result": "notification only"}
    calls = [{"tool": t, "arguments": a} for t, a in CALLS[action]]
    out = {"action": action, "label": LABELS.get(action, action), "live": LIVE, "calls": calls,
           "tool": calls[0]["tool"], "arguments": calls[0]["arguments"]}
    if not LIVE:
        for c in calls:
            c["result"] = "dry run: not sent"
        out["result"] = "dry run: not sent"
        return out
    try:
        from chmcp import Upstream  # imported lazily: needs mcp/client/.tokens.json from `chmcp.py login`
        up = Upstream()
        for i, c in enumerate(calls):
            if i:
                time.sleep(0.5)      # let the bulb take "power on" before the colour
            res = up.request("tools/call", {"name": c["tool"], "arguments": c["arguments"]})
            c["result"] = json.dumps(res.get("result", res), ensure_ascii=False)[:300]
            if "error" in res or (res.get("result") or {}).get("isError"):
                break                # a failed step stops the rest
        out["result"] = calls[-1].get("result") or calls[0].get("result", "")
    except (Exception, SystemExit) as e:  # noqa: BLE001 - chmcp exits when not logged in; report, never crash
        out["result"] = f"error: {e}"[:300]
    return out


_upstream = None   # one MCP session kept across polls, so each poll is a single request
# Tests only: read the devices from this JSON file (the shape of get_home_devices) instead of the MCP, so the live
# door path can be exercised without a session (prototype/test_scenarios.py).
DEVICES_FILE = os.environ.get("TT_DEVICES_FILE")


def poll_devices():
    """READ-ONLY: the home's devices from the MCP tool get_home_devices, through one kept session; None when the
    session is not live (not logged in, expired, offline). This is the only tool it ever calls."""
    global _upstream
    if DEVICES_FILE:
        try:
            return json.loads(Path(DEVICES_FILE).read_text())
        except (OSError, ValueError):
            return None
    try:
        from chmcp import Upstream
        if _upstream is None:
            _upstream = Upstream()
        res = _upstream.request("tools/call", {"name": "get_home_devices", "arguments": {}})
        return json.loads(res["result"]["content"][0]["text"])
    except (Exception, SystemExit):  # noqa: BLE001 - not logged in or offline: the caller keeps the simulated door
        _upstream = None
        return None


def devices():
    """Read-only device list: live from the MCP if logged in, else the 16 Nov sample."""
    sample = ROOT / "mcp" / "samples" / "get_home_devices.json"
    try:
        from chmcp import Upstream
        res = Upstream().request("tools/call", {"name": "get_home_devices", "arguments": {}})
        text = res["result"]["content"][0]["text"]
        return {"source": "live", "data": json.loads(text)}
    except (Exception, SystemExit):  # noqa: BLE001 - not logged in or offline: fall back to the sample
        return {"source": "sample 16 Nov", "data": json.loads(sample.read_text())}
