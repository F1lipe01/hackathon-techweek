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

## What we are given

| Resource | What it is | More |
|---|---|---|
| Hardware kit | Real devices, already provisioned on Altice's platform. The kit is "the home" | [04-kit-and-access.md](04-kit-and-access.md) |
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
