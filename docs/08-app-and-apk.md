# The mobile app, analysed

From the app installed on the team phone (Xiaomi Redmi 17), on 16 Nov. The APK was pulled for inspection; it is **not** committed (236 MB, proprietary beta build).

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

The full table with radios and capabilities is in [04-kit-and-access.md](04-kit-and-access.md).

## Live app map (walked on 16 Nov)

Screens captured by driving the app over ADB. Clean screenshots (no account data) are in [`assets/app-screens/`](../assets/app-screens/).

- **Bottom navigation:** Favorites, Areas, Devices, Menu.
- **Devices tab:** home **"Hack 3"**, list "Without room (7)" with the seven devices. A separate "Add-ons" sub-view exists and is empty ("No add-ons" — we have no Wi-Fi extenders).
- **Device detail page:** header (name, room, connection state, favourite star, "⋯" menu), a large device icon with the state, then sections. The sections differ by device:
  - **Plug:** Scenarios, **Energy**, Events, Notifications, About.
  - **Light:** Scenarios, Events, Notifications, About — **no Energy section**.
  - Controls (power, brightness, colour) are hidden while a device is **Disconnected**, so the bulb's colour support could not be read from the app while the kit was offline; its About page shows only a serial UUID. The MCP confirms it is a colour bulb (`workMode` colour / white / music / scene, [10-mcp-in-practice.md](10-mcp-in-practice.md)).
- **Menu tab:** Home (Scenarios, Rooms, Houses management), Account (Profile, Notifications, App settings), Support.
- **App settings:** notification types; App authentication (on), Access code, Biometrics (on); Language, Units; About links (Smart home service — external web portal, Accessibility, Terms). **Version 2.5.0 (2050003)**, build `BP2A.250605.031.A3-…`.
- **No hidden debug menu:** tapping the version line ten times did nothing. No developer/environment switcher was found in the UI.

## Static analysis of the APK

The APK was unpacked and inspected (read-only, nothing executed). Findings:

- **UI string catalogs** ship in the app: `assets/flutter_assets/assets/strings/strings_{enus,ptpt,engb,frfr}.json`, ~2000 strings each. These document every screen and feature of the platform. The full capability model mined from them is in [09-platform-capabilities.md](09-platform-capabilities.md).
- The app is the **full Altice SmartHome / SmartWiFi product**, not a hackathon cut-down: it includes device control, a scenario rules engine, security, energy, camera recordings, Wi-Fi mesh management, parental control and user management.
- Dart code is AOT-compiled into `lib/*/libapp.so`, so business logic is not readily readable; the string catalogs and asset configs are the useful surface.

## How this was accessed

- Phone connected over USB with debugging on; only the `pt.altice.smarthome.beta` package was touched.
- Input injection (`adb shell input`) is **blocked** by HyperOS without "USB debugging (Security settings)", so screens are driven by hand on the phone and captured read-only with `adb exec-out screencap`.
