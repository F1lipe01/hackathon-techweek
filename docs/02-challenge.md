# Challenge #3 — Altice Labs

**Connected Homes Reimagined: a IA ao serviço da casa**

The title is as spoken at the kick-off. No written challenge statement (enunciado) is filed here. The only challenge document we have is the MCP connection guide, so check the resources folder for a statement.

## The brief

As presented at the kick-off (transcript lines 26–27):

- Rethink the connected home, this time with AI.
- Services that make daily life at home simpler, more useful or safer.
- Solutions people would actually want to use, "não apenas um gimmick".

## What the Altice mentors are looking for

Hugo (Altice Labs), in the challenge room, transcript lines 261–264:

> "Aquilo que nós estamos mesmo à procura é algo que nos surpreenda [...] E como é óbvio, não vai ser implementação de código, isso não nos vai surpreender. [...] quero ser surpreendido com use cases que sejam úteis no dia a dia das pessoas e, pronto, pensar um bocadinho fora da caixa, tirar partido dos vários tipos de sensores e equipamentos e também não menosprezar a fonte de dados que é uma câmara [...] Imaginem tudo o que vocês podem fazer com uma câmara, imaginando que essa câmara está em casa."

In short:

- Surprise them with the **use case**, not with the code.
- It has to be useful in people's everyday life.
- Combine the different sensors and devices.
- Do not underestimate the **camera** as a data source.

## What Altice already sells

Altice Labs' public page for its Connected Home product lists these use cases: https://www.alticelabs.com/products/connected-home/

| Their use case | Their description, shortened |
|---|---|
| Reliable security | Emergency alerts and video playback for intrusion, fire, gas leaks or water leaks |
| Intelligent energy management | Consumption monitoring with alerts, automations and a household Eco Mode |
| Automation and comfort | Smart lighting, plugs and scenario-based automation "powered by AI" |
| Virtual Concierge Assistant | Anticipates users' needs so the home adapts accordingly |
| Aging in place | Assists elderly or disabled people, through smart displays with two-way communication |
| Parental control | Internet schedules and device-level restrictions |
| Seamless connectivity | Monitoring and improving Wi-Fi coverage and speed |
| Entertainment and ambience | Managing set-top boxes and remotes |

This matters for "surprise us". An idea that lands inside one of these rows is something they already pitch to operators. Screens of their app are in [`assets/altice-app/`](../assets/altice-app/).

## What we are given

| Resource | What it is | More |
|---|---|---|
| Hardware kit | An LTE IoT gateway, a camera, a climate sensor, a smoke alarm, a smart plug, a smart bulb and a small sensor that is probably a door contact. Already provisioned on Altice's platform. The kit is "the home" | [04-kit-and-access.md](04-kit-and-access.md) |
| Mobile app | Shows and controls the kit's devices. Use it to check everything is online | [04-kit-and-access.md](04-kit-and-access.md) |
| Connected Home MCP server | 16 tools to read and control the home: devices, rooms, security, scenarios | [03-mcp-connected-home.md](03-mcp-connected-home.md) |
| Camera feed | RTSP stream from the kit's camera, to plug into any image-processing system | [04-kit-and-access.md](04-kit-and-access.md) |
| Team account | Login used when the MCP client authenticates | `.env` |

## Constraints

- **The devices are fixed.** Extra devices would have to be supported by, and provisioned on, Altice's platform, and Altice cannot guarantee that. In practice we build with what is in the kit.
- **The MCP acts on the real kit.** Asking the agent to turn on the light turns on our physical light. There is no simulated home behind it.
- **The camera URL has no authentication.** Anyone holding the URL can watch the feed.
- **Connectivity on Friday is our problem too.** See the event-day notes in [04-kit-and-access.md](04-kit-and-access.md).
- Seven teams are in this challenge. Three reach the final.

## Mentors

Hugo, Ricardo and Gonçalo from Altice Labs. See [06-people.md](06-people.md).
