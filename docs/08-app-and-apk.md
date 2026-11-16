# The mobile app, analysed

From the app installed on the team phone (Xiaomi Redmi 17), on 16 Nov. The APK was pulled for inspection; it is **not** committed (236 MB, proprietary beta build). It lives in the session scratchpad only.

## Identity

| | |
|---|---|
| Package | `pt.altice.smarthome.beta` |
| Name on the login page | SMARTHOME-PRO-BETA-APP |
| Version | 2.5.0 (build 2050003) |
| Min / target Android | 9 / 16 (SDK 27 / 36) |
| UI framework | **Flutter** (so screen text is drawn on a canvas; read it from screenshots, not `uiautomator`) |
| Installed on the phone | 16 Nov 2026, 18:23 |

## Backend, from strings in the APK

The app is a skin over Altice Labs' **"Cognitive Home"** platform. Hosts found in the binary:

| Host | What it is |
|---|---|
| `api.beta.sh.cognitive-home.cloud` | **The beta API**, the environment our kit is on |
| `api.dev.tst…`, `api.int.tst…`, `api.meo…`, `api.sfr…`, `api.omt…`, `api.truespeed…` | Other tenant and test environments of the same platform |
| `smartwifi.alticelabs.com`, `smartwifi.meo.pt`, `app.smartwifi.*` | Altice SmartWiFi backends |
| `on.dcl.csa-iot.org` | Matter Distributed Compliance Ledger — the platform does Matter device attestation |

The MCP server from the challenge guide, `cognitive-home.futurelabsinnovations.com`, is the hackathon-specific front end to this same Cognitive Home platform. So the app and the MCP act on the same home.

## What the app shows per device

Each device has a detail page with these sections: **Scenarios, Energy, Events, Notifications, About**, plus a room and a connection state.

The full device roster read from the app on 16 Nov (home **"Hack 3"**, all "Without room"):

| App name | State | = our device |
|---|---|---|
| Security hub | On | Gateway MS-WES1AS |
| Temperature sensor | On, 20.8 °C / 48.3 % | Nedis ZBSC10WT |
| Smoke sensor | On | Photoelectric smoke alarm |
| Contact sensor | Open | MS-D3D |
| Camera | Disconnected | Tuya SC034-WNV3 |
| Plug | Disconnected | Smart plug (has an **Energy** page → meters energy) |
| Light | Disconnected | Smart bulb |

The full table with radios and capabilities is in [04-kit-and-access.md](04-kit-and-access.md). Each device detail page has Scenarios, Energy, Events, Notifications, About.

## Static analysis of the APK

The APK was unpacked and inspected (read-only, nothing executed). Findings:

- **UI string catalogs** ship in the app: `assets/flutter_assets/assets/strings/strings_{enus,ptpt,engb,frfr}.json`, ~2000 strings each. These document every screen and feature of the platform. The full capability model mined from them is in [09-platform-capabilities.md](09-platform-capabilities.md).
- The app is the **full Altice SmartHome / SmartWiFi product**, not a hackathon cut-down: it includes device control, a scenario rules engine, security, energy, camera recordings, Wi-Fi mesh management, parental control and user management.
- Dart code is AOT-compiled into `lib/*/libapp.so`, so business logic is not readily readable; the string catalogs and asset configs are the useful surface.

## How this was accessed

- Phone connected over USB with debugging on; only the `pt.altice.smarthome.beta` package was touched.
- Input injection (`adb shell input`) is **blocked** by HyperOS without "USB debugging (Security settings)", so screens are driven by hand on the phone and captured read-only with `adb exec-out screencap`.
