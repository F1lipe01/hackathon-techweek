# Architecture figures

## Current views

`build_views.py` draws the twelve views of the hybrid design (19 Nov 2026), used by [docs/14-architecture.md](../14-architecture.md), [docs/pt/14-arquitetura.md](../pt/14-arquitetura.md) and the integration spec ([docs/15](../15-integration-spec.md), [docs/pt/15](../pt/15-especificacao-integracao.md)). `diagram_kit.py` holds the drawing rules: text measured with the font Chrome renders and wrapped to its box (the build stops if a text does not fit), and straight one-way arrows.

```
python3 docs/architecture/build_views.py                       # every view, PT (name.svg/png) and EN (name.en.svg/png)
python3 docs/architecture/build_views.py --only implantacao --lang pt
```

| File | View |
|---|---|
| `c4-1-contexto` | C4 level 1: context |
| `c4-2-contentores` | C4 level 2: containers |
| `c4-3-componentes` | C4 level 3: components, from capture to alert |
| `implantacao` | Deployment, the A1 upgrade and the two rejected options |
| `presenca-estados` | The presence state machine and its timings |
| `seq-livro-esquecido` | Sequence: the book left behind |
| `seq-pessoa-desconhecida` | Sequence: an unknown person and the 112 suggestion |
| `seq-casa-vazia` | Sequence: the empty home and the door left open |
| `er-casa`, `er-plataforma` | Data models: the router's SQLite and the platform's PostgreSQL |
| `dfd-fronteiras` | Data flow with trust boundaries |
| `fluxo-app` | The flows in the app |

## Superseded, kept on purpose

These describe the first design (18 Nov), in which the vision models and the rules engine ran in the home. No living document embeds them any more.

| Files | Built by | Why they are kept |
|---|---|---|
| `thingtracker-architecture.*` | `build_diagram.py` | The submitted executive summary copies it (`deliverables/executive-summary/figuras.py`), and the prototype's documentation pages still use it (`prototype/build_doc_pages.py`). Replaced, for the current design, by `implantacao` and `c4-2-contentores` |
| `sequencia-regra.*` | `build_sequence.py` | Kept as the history of the first integration spec. Replaced by `seq-livro-esquecido` |
