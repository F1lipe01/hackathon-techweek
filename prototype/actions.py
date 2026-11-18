"""Device actions through the Connected Home MCP (our client in mcp/client/chmcp.py).

DRY RUN BY DEFAULT: the call that would be made is returned and logged, nothing changes in the home.
Set TT_LIVE_ACTIONS=1 to act on the real Light and Plug. The alarm is deliberately not wired.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mcp" / "client"))

LIVE = os.environ.get("TT_LIVE_ACTIONS") == "1"

CALLS = {
    "light_red": ("update_device_capabilities", {"deviceName": "Light", "body": {"type": "color_rgb", "redValue": 255, "greenValue": 0, "blueValue": 0}}),
    "light_blue": ("update_device_capabilities", {"deviceName": "Light", "body": {"type": "color_rgb", "redValue": 0, "greenValue": 132, "blueValue": 214}}),
    "light_green": ("update_device_capabilities", {"deviceName": "Light", "body": {"type": "color_rgb", "redValue": 0, "greenValue": 200, "blueValue": 80}}),
    "light_off": ("update_device_capabilities", {"deviceName": "Light", "body": {"type": "power", "value": "off"}}),
    "plug_off": ("update_device_capabilities", {"deviceName": "Plug", "body": {"type": "power", "value": "off"}}),
    "plug_on": ("update_device_capabilities", {"deviceName": "Plug", "body": {"type": "power", "value": "on"}}),
}

LABELS = {
    "notify": "aviso no telemóvel", "light_red": "luz vermelha", "light_blue": "luz azul", "light_green": "luz verde",
    "light_off": "desligar a luz", "plug_off": "desligar a tomada", "plug_on": "ligar a tomada",
}


def run(action):
    """Returns {"action", "live", "tool", "arguments", "result"}; never raises."""
    if action == "notify" or action not in CALLS:
        return {"action": action, "live": False, "tool": None, "arguments": None, "result": "notification only"}
    tool, args = CALLS[action]
    out = {"action": action, "live": LIVE, "tool": tool, "arguments": args}
    if not LIVE:
        out["result"] = "dry run: not sent"
        return out
    try:
        from chmcp import Upstream  # imported lazily: needs mcp/client/.tokens.json from `chmcp.py login`
        res = Upstream().request("tools/call", {"name": tool, "arguments": args})
        out["result"] = json.dumps(res.get("result", res), ensure_ascii=False)[:300]
    except (Exception, SystemExit) as e:  # noqa: BLE001 - chmcp exits when not logged in; report, never crash
        out["result"] = f"error: {e}"[:300]
    return out


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
