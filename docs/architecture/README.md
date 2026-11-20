# Architecture figures

## Current views

`build_views.py` draws the twelve views of the final design (20 Nov 2026: fully local, all perception and inference on the home device, the Altice platform as a text-only control and data plane), used by [docs/14-architecture.md](../14-architecture.md), [docs/pt/14-arquitetura.md](../pt/14-arquitetura.md) and the integration spec ([docs/15](../15-integration-spec.md), [docs/pt/15](../pt/15-especificacao-integracao.md)). `diagram_kit.py` holds the drawing rules: text measured with the font Chrome renders and wrapped to its box (the build stops if a text does not fit), and straight one-way arrows.

```
python3 docs/architecture/build_views.py                       # every view, PT (name.svg/png) and EN (name.en.svg/png)
python3 docs/architecture/build_views.py --only implantacao --lang pt
```

| File | View |
|---|---|
| `c4-1-contexto` | C4 level 1: context |
| `c4-2-contentores` | C4 level 2: containers |
| `c4-3-componentes` | C4 level 3: components, from capture to alert |
| `implantacao` | Deployment, the chosen design's costs, the alternative not chosen (vision on Altice's L4 servers) and the rejected option |
| `presenca-estados` | The presence state machine and its timings |
| `seq-livro-esquecido` | Sequence: the book left behind |
| `seq-pessoa-desconhecida` | Sequence: an unknown person and the 112 suggestion |
| `seq-casa-vazia` | Sequence: the empty home and the door left open |
| `er-casa`, `er-plataforma` | Data models: the home device's SQLite and the platform's PostgreSQL (text only) |
| `dfd-fronteiras` | Data flow with trust boundaries |
| `fluxo-app` | The flows in the app |

## Superseded: the first design (18 Nov), kept on purpose

These two figures and their scripts describe the first design (18 Nov). It also ran the vision models and the rules engine in the home, but its components, labels and flows are older than the current views, and no architecture document embeds them; they are kept only because other files still copy or serve them.

| Files | Built by | Still used by | Current view instead |
|---|---|---|---|
| `thingtracker-architecture.*` | `build_diagram.py` | the submitted executive summary (`deliverables/executive-summary/figuras.py`, `deliverables/build_pdfs.py`), the prototype's documentation pages (`prototype/build_doc_pages.py`, `prototype/server.py`) | `implantacao`, `c4-2-contentores` |
| `sequencia-regra.*` | `build_sequence.py` | the prototype's page list (`prototype/server.py`, `prototype/web/site.js`) | `seq-livro-esquecido` |
