#!/usr/bin/env python3
"""Build the architecture views of docs/14-architecture.md (English) and docs/pt/14-arquitetura.md (Portuguese).

    python3 docs/architecture/build_views.py                 # every view, in both languages
    python3 docs/architecture/build_views.py --only implantacao presenca-estados --lang pt

Each view is written as <name>.svg / <name>.png (Portuguese, for the deck) and <name>.en.svg / <name>.en.png.
The drawing rules live in diagram_kit.py: text measured and wrapped to its box, straight one-way arrows.
The design drawn here is the TARGET design of 19 Nov 2026 (hybrid: motion, regions and faces at home; vision,
presence and rules at Altice); docs/14 section 12 says what the prototype does today.
"""
import argparse

from diagram_kit import (ALTICE_BG, BLUE, BODY, DEEP, EXT_BG, FAINT, HOME_BG, INK, LINE, MUTED, NOTE_BG, NOTE_LINE,
                         PHONE_BG, WARN, Canvas, Grid, sequence, width, wrap)

VIEWS = {}


def view(fn):
    VIEWS[fn.__name__.replace("_", "-")] = fn
    return fn


def stack(cv, x, y, w, items, gap=18):
    """Draw cards one under the other; returns [(top, bottom)]. An item is a dict of box() arguments; 'h' may be set."""
    spans = []
    for it in items:
        h = cv.box(x, y, w, **it)
        spans.append((y, y + h))
        y += h + gap
    return spans


def mid_overlap(a, b, margin=14):
    """The middle of the vertical overlap of two spans, asserting there is room for an arrow."""
    lo, hi = max(a[0], b[0]) + margin, min(a[1], b[1]) - margin
    assert hi >= lo, f"spans do not overlap: {a} {b}"
    return (lo + hi) / 2


# ====================================================================== deployment
@view
def implantacao(lang):
    cv = Canvas(2040, lang, "Implantação do ThingTracker" if lang == "pt" else "ThingTracker deployment")
    L = cv.L
    HB, AB, PB = (20, 470), (610, 1730), (1800, 2020)
    HX, HW = HB[0] + 24, HB[1] - HB[0] - 48
    COLS = [634 + i * (254 + 18) for i in range(4)]
    CW = 254
    PX, PW = PB[0] + 20, PB[1] - PB[0] - 40
    Y0 = 108

    # ---- the home: the equipment that is already there
    cam = stack(cv, HX, Y0, HW, [dict(
        title=L("Câmaras do kit", "Kit cameras"),
        body=[L("_Tuya SC034-WNV3_ · H.265 · 2304 × 1296 · 20 fps",
                "Tuya SC034-WNV3 · H.265 · 2304 × 1296 · 20 fps"),
              L("Vídeo por RTSP só na rede da casa, com uma ligação mantida aberta",
                "Video over RTSP on the home network only, one connection kept open")])])[0]
    A0 = COLS[0]
    note_item = dict(title=L("Porque ficam aqui os balanceadores", "Why the load balancers are here"), fill=NOTE_BG, stroke=NOTE_LINE,
                     body=[L("É na Altice que se juntam as 500 000 casas. Em casa há um só agente, sem nada para distribuir.",
                             "This is where 500,000 homes meet. A home has one agent, with nothing to spread.")])
    note_h = cv.box_h(254, note_item["title"], note_item["body"])
    ry = max(cam[1] + 70, Y0 + note_h + 18)
    stack(cv, A0, Y0, 254, [note_item])
    router_items = [dict(
        title=L("_Router_ Altice · CPU, sem acelerador de IA", "Altice router · CPU, no AI accelerator"),
        sub=L("Agente da casa (_ThingTracker_)", "Home agent (ThingTracker)"),
        stroke=BLUE, sw=2,
        body=[L("Máscaras de privacidade: zonas nunca analisadas", "Privacy masks: areas never analysed"),
              L("Filtro de movimento: imagem cinzenta de 160 × 90, a cada 0,5 s",
                "Motion gate: a 160 × 90 grey picture, every 0.5 s"),
              L("Região que mudou: recortada, no máximo 640 × 640, cerca de 1 por segundo enquanto há movimento",
                "Changed region: cut out, at most 640 × 640, about 1 a second while there is motion"),
              L("Rostos (opcional, com consentimento): _YuNet_ encontra, _SFace_ compara; semelhança ≥ 0,363 dá um nome",
                "Faces (opt-in, with consent): YuNet finds, SFace compares; similarity ≥ 0.363 gives a name"),
              L("Padrões faciais cifrados, guardados só aqui", "Face templates encrypted, kept only here"),
              L("Guarda só em memória os últimos 3 s, para o juiz", "Keeps the last 3 s in memory only, for the judge"),
              L("Fila de saída: guarda os eventos enquanto não há internet; sem internet, não há análise de imagem",
                "Outbox: keeps events while offline; without internet there is no image analysis"),
              L("Wi-Fi: o _router_ sabe que telemóveis da Família estão ligados",
                "Wi-Fi: the router knows which Family phones are connected")])]
    # ---- Altice, column A: what faces the homes
    A, B, C, D = COLS
    lbh = stack(cv, A, ry, CW, [dict(
        title=L("Balanceador de carga (casas)", "Load balancer (homes)"),
        body=[L("Distribui as ligações das casas pelos mediadores e retira os que falham",
                "Spreads the homes’ connections over the brokers and drops any that fail")])])[0]
    broker = stack(cv, A, lbh[1] + 18, CW, [dict(
        title=L("Mediador de ligações", "Connection broker"),
        sub=L("MQTT sobre mTLS", "MQTT over mTLS"),
        body=[L("Uma ligação de saída por casa e um tópico por casa, para as regiões e os pedidos",
                "One outbound connection per home, one topic per home, for regions and requests")])])[0]
    hub_item = dict(
        title=L("Central de segurança e sensor da porta", "Security hub and door contact sensor"),
        body=[L("_MS-WES1AS_ (LTE) e _MS-D3D_; comunicam com a plataforma Altice, como hoje",
                "MS-WES1AS (LTE) and MS-D3D; they report to the Altice platform, as today")])
    plat_item = dict(
        title=L("Plataforma Connected Home (existente)", "Connected Home platform (existing)"),
        fill="#F7F7F7",
        body=[L("Dispositivos, cenários e segurança; servidor MCP com 18 ferramentas",
                "Devices, scenarios and security; MCP server with 18 tools"),
              L("Pedidos à Altice: eventos da porta e do Wi-Fi, a ferramenta de presença no Wi-Fi e as ferramentas _Things_",
                "Asked of Altice: door and Wi-Fi events, the Wi-Fi presence tool and the Things tools")])
    plat_y = broker[1] + 18
    rneed = cv.box_h(HW, router_items[0]["title"], router_items[0]["body"], sub=router_items[0]["sub"])
    router = stack(cv, HX, ry, HW, [dict(router_items[0], h=max(rneed, plat_y + 70 - ry))])[0]
    plat_need = cv.box_h(CW, plat_item["title"], plat_item["body"])
    hub_y = router[1] + 24
    hub_h = max(cv.box_h(HW, hub_item["title"], hub_item["body"]), plat_y + plat_need - hub_y)
    hub = stack(cv, HX, hub_y, HW, [dict(hub_item, h=hub_h)])[0]
    plat = stack(cv, A, plat_y, CW, [dict(plat_item, h=hub[1] - plat_y)])[0]

    # ---- column B: the ThingTracker service, its queues and its cache
    svc = stack(cv, B, Y0, CW, [
        dict(title=L("Serviço _ThingTracker_", "ThingTracker service"), stroke=BLUE, sw=2,
             sub=L("N instâncias sem estado, em contentores", "N stateless instances, in containers"),
             body=[L("API da aplicação e _host_ MCP", "App API and MCP host"),
                   L("Motor de presença e motor de regras: por casa, a cada evento e a cada temporizador",
                     "Presence engine and rules engine: per home, on every event and every timer"),
                   L("Compara os vetores com as assinaturas visuais (_pgvector_): semelhança ≥ 0,62 é o seu",
                     "Matches the vectors with the fingerprints (pgvector): similarity ≥ 0.62 means yours"),
                   L("Seguimento das caixas entre análises", "Tracking of boxes between analyses"),
                   L("Chama os modelos só para frases, perguntas e, raramente, o juiz",
                     "Calls the models only for sentences, questions and, rarely, the judge")]),
        dict(title=L("Filas e fluxo de eventos", "Queues and event stream"),
             body=[L("Visão urgente: verificações das regras", "Urgent vision: rule checks"),
                   L("Visão em lote: o resto, nas horas calmas", "Batch vision: the rest, in quiet hours"),
                   L("Eventos de cada casa, por ordem (partição por casa)", "Each home’s events, in order (partitioned by home)"),
                   L("Pedidos ao modelo de linguagem", "Language-model requests")]),
        dict(title=L("_Cache_ (_Redis_)", "Cache (Redis)"),
             body=[L("Estado de cada casa em uso: presença, trajetos, contadores e temporizadores",
                     "Each home’s live state: presence, tracks, counters and timers")]),
    ])

    # ---- column C: vision and data
    vis = stack(cv, C, Y0, CW, [
        dict(title=L("Servidores de visão", "Vision workers"), sub=L("GPU NVIDIA L4", "NVIDIA L4 GPUs"),
             body=[L("_OWLv2_: encontra objetos, pessoas e superfícies na região",
                     "OWLv2: finds things, people and surfaces in the region"),
                   L("_DINOv2_: calcula o vetor de cada candidato", "DINOv2: computes each candidate’s vector"),
                   L("Sem estado: leem as filas e devolvem caixas e vetores", "Stateless: read the queues, return boxes and vectors")]),
        dict(title=L("PostgreSQL com _pgvector_", "PostgreSQL with pgvector"), sub=L("primário e réplica", "primary and replica"),
             body=[L("Por cliente: objetos, assinaturas visuais, regras, eventos, observações e presença",
                     "Per customer: things, fingerprints, rules, events, sightings and presence")]),
        dict(title=L("Armazenamento de objetos", "Object storage"),
             body=[L("Miniaturas das observações, 30 dias (proposta)", "Sighting thumbnails, 30 days (proposal)")]),
    ])

    # ---- column D: what faces the phones, the language model and the numbers
    lba = stack(cv, D, Y0, CW, [
        dict(title=L("Balanceador de carga (aplicação)", "Load balancer (app)"),
             body=[L("HTTPS da aplicação para as instâncias do serviço", "The app’s HTTPS to the service instances")]),
        dict(title=L("Notificações (existente)", "Notifications (existing)"),
             body=[L("O serviço que a aplicação Altice já usa", "The service the Altice app already uses")]),
        dict(title=L("Modelos de linguagem e de visão-linguagem", "Language and vision-language models"),
             sub=L("servidores GPU, atrás de uma fila", "GPU servers, behind a queue"),
             body=[L("Texto: frases em regras e respostas (alojado pela Altice ou fornecedor sob contrato na UE)",
                     "Text: sentences into rules, and answers (hosted by Altice, or a provider under contract in the EU)"),
                   L("Juiz, na Altice: raramente, 2 a 3 s da região num momento duvidoso",
                     "Judge, at Altice: rarely, 2 to 3 s of the region at an ambiguous moment")]),
    ])
    bottom = max(hub[1], svc[-1][1], vis[-1][1], lba[-1][1])
    num_y = lba[-1][1] + 18
    num_item = dict(
        title=L("A 500 000 casas (estimativas)", "At 500,000 homes (estimates)"), fill="#F7F9FD", stroke="#C9D2E3",
        body=[L("Visão: ≈ 0,49 € por casa e por mês com 1 câmara; 1 427 placas L4 (documento 17)",
                "Vision: ≈ €0.49 per home a month with 1 camera; 1,427 L4 cards (document 17)"),
              L("Modelo de linguagem: ≈ 0,43 € por casa e por mês (documento 16)",
                "Language model: ≈ €0.43 per home a month (document 16)"),
              L("Pressupostos: 2 h de movimento por dia, 1 imagem por segundo, GPU a 25 % do seu pico",
                "Assumptions: 2 h of motion a day, 1 frame a second, GPUs at 25 % of their peak")])
    num_h = max(cv.box_h(CW, num_item["title"], num_item["body"]), bottom - num_y)
    stack(cv, D, num_y, CW, [dict(num_item, h=num_h)])
    band_bottom = max(bottom, num_y + num_h) + 26
    # bands go under the cards: insert them at the start of the drawing
    bands = Canvas(cv.w, lang, "")
    bands.band(HB[0], 20, HB[1] - HB[0], band_bottom - 20, L("Em casa", "In the home"),
               L("Equipamento que já lá está: movimento, regiões e rostos", "Equipment already there: motion, regions and faces"),
               fill=HOME_BG)
    bands.band(AB[0], 20, AB[1] - AB[0], band_bottom - 20, L("Altice · centro de dados", "Altice · datacentre"),
               L("Visão, presença, regras e os dados de cada cliente", "Vision, presence, rules and each customer’s data"),
               fill=ALTICE_BG)
    bands.band(PB[0], 20, PB[1] - PB[0], band_bottom - 20, L("Telemóvel", "Phone"), None, fill=PHONE_BG)
    cv.o = bands.o + cv.o

    app = stack(cv, PX, Y0, PW, [dict(
        title=L("Aplicação Altice", "Altice app"), h=lba[1][1] - Y0,
        body=[L("Separador _Things_ e assistente", "Things tab and assistant"),
              L("Avisos com cartões de ação", "Alerts with action cards"),
              L("Vídeo em direto, como hoje, fora do _ThingTracker_", "Live video, as today, outside ThingTracker")])])[0]

    # ---- arrows across the boundaries (labels in the gaps)
    gx0, gx1 = HX + HW, A
    lw = gx1 - gx0 - 20
    ya = router[0] + 34
    cv.arrow(gx0, ya, gx1, ya, BLUE, 2)
    cv.label(gx0 + 10, ya - 8, L("1 ligação de saída mTLS: regiões e rótulos de rostos; nunca vídeo contínuo",
                                 "1 outbound mTLS connection: regions and face labels; never continuous video"), lw, bold=True)
    yb = lbh[1] - 14
    cv.arrow(gx1, yb, gx0, yb, BLUE, 2)
    cv.label(gx0 + 10, yb + 17, L("pedidos: verificação ativa, atualização", "requests: active check, refresh"), lw, below=True)
    yc = mid_overlap(router, plat)
    cv.arrow(gx0, yc, gx1, yc, BODY)
    cv.label(gx0 + 10, yc - 8, L("telemóveis da Família no Wi-Fi (ferramenta proposta)", "Family phones on the Wi-Fi (proposed tool)"), lw, fill=BODY)
    yd = mid_overlap(hub, plat)
    cv.arrow(gx0, yd, gx1, yd, BODY)
    cv.label(gx0 + 10, yd - 8, L("porta aberta e fechada, como hoje", "door open and closed, as today"), lw, fill=BODY)
    cv.arrow(HX + HW / 2, cam[1], HX + HW / 2, router[0], BODY)
    cv.label(HX + HW / 2 + 12, (cam[1] + router[0]) / 2 + 4, L("vídeo, só dentro de casa", "video, inside the home only"), 200, fill=BODY)
    px0, px1 = D + CW, PX
    y1 = mid_overlap(lba[0], app, 20)
    cv.arrow(px1, y1, px0, y1, BODY)
    cv.label(px0 + 8, y1 - 8, L("frases, perguntas, “Sim”", "sentences, questions, “Yes”"), px1 - px0 - 14, fill=BODY, size=11)
    y2 = mid_overlap(lba[1], app, 20)
    cv.arrow(px0, y2, px1, y2, BODY)
    cv.label(px0 + 8, y2 - 8, L("avisos (_push_)", "alerts (push)"), px1 - px0 - 14, fill=BODY, size=11)

    # ---- the options below
    oy = band_bottom + 30
    ow = (2040 - 40 - 2 * 24) / 3
    panels = [
        (L("Evolução prevista (A1 no documento 17)", "Upgrade path (A1 in document 17)"), BLUE, "#FFFFFF",
         [L("Se os _routers_ ou as câmaras da Altice tiverem uma NPU capaz de correr um detetor, a visão passa para casa "
            "e só saem eventos, miniaturas e assinaturas visuais.",
            "If Altice’s routers or cameras have an NPU that can run a detector, vision moves into the home and only "
            "events, thumbnails and fingerprints leave it."),
          L("≈ 0,36 € por casa e por mês (prémio de 15 € no _router_, um pressuposto). É a primeira pergunta para a Altice.",
            "≈ €0.36 per home a month (a €15 router premium, an assumption). It is the first question for Altice.")]),
        (L("Rejeitada: uma caixa em cada casa, com o modelo de linguagem", "Rejected: a box in every home, language model included"),
         WARN, "#FFFFFF",
         [L("_Raspberry Pi 5_ com _AI HAT+_ (200 €) ou _Jetson Orin Nano Super_ (269 €): 6,55 a 8,64 € por casa e por mês, "
            "e 107,5 a 142,0 M€ de equipamento para 500 000 casas (documento 17).",
            "A Raspberry Pi 5 with AI HAT+ (€200) or a Jetson Orin Nano Super (€269): €6.55 to €8.64 per home a month, "
            "and €107.5 M to €142.0 M of hardware for 500,000 homes (document 17)."),
          L("O modelo de linguagem exige ainda mais memória (cerca de 1 GB o do protótipo, 2,1 GB o de 4B testado, três vezes "
            "mais lento) e cada atualização chega a 500 000 caixas.",
            "The language model needs more memory again (about 1 GB for the prototype’s, 2.1 GB for the 4B one tried, three "
            "times slower), and every update has to reach 500,000 boxes.")]),
        (L("Rejeitada: vídeo ou imagens completas para a nuvem", "Rejected: video or full frames to the cloud"), WARN, "#FFFFFF",
         [L("Vídeo contínuo a 2 Mbps (pressuposto): 657 GB por câmara e por mês e 1 000 Gbps no pico com 500 000 câmaras. "
            "Imagens completas durante o movimento: 2,41 € por casa e por mês nos servidores da Altice e 3,93 a 4,26 € em GPU "
            "de _hyperscalers_, a pedido (documento 17).",
            "A continuous stream at 2 Mbps (assumption): 657 GB per camera a month and 1,000 Gbps at the peak with 500,000 "
            "cameras. Full frames during motion: €2.41 per home a month on Altice’s servers and €3.93 to €4.26 on hyperscaler "
            "GPUs on demand (document 17)."),
          L("Toda a imagem da casa sairia de casa.", "The whole picture of the home would leave it.")]),
    ]
    hs = [cv.box_h(ow, t, b, 16, 14.5, 12.5) for t, c, f, b in panels]
    for i, (t, c, f, b) in enumerate(panels):
        cv.box(20 + i * (ow + 24), oy, ow, t, b, h=max(hs), pad=16, stroke=c, sw=1.5, title_color=c if c == WARN else DEEP)
    cv.save("implantacao", round(oy + max(hs) + 20))


# ====================================================================== presence
@view
def presenca_estados(lang):
    W = 1640
    cv = Canvas(W, lang, "Estados de presença" if lang == "pt" else "Presence states")
    L = cv.L
    # the four states: UNSURE across the top, then OCCUPIED, LEAVING, EMPTY
    U = (40, W - 40)
    O, LV, E = (40, 460), (610, 1030), (1180, 1600)
    uy = 24
    st = dict(pad=16, title_size=16, body_size=12.5, sw=2)
    u_body = [L("Os sinais não concordam: os telemóveis estão fora mas uma câmara vê uma pessoa (um estranho, uma visita ou alguém "
                "da Família sem telemóvel), ou um telemóvel está em casa sem ninguém visto nem uso da porta há T_parado "
                "(um telemóvel esquecido?).",
                "The signals disagree: the phones are away but a camera sees a person (a stranger, a guest, or Family without a "
                "phone), or a phone is home with nobody seen and no door use for T_stale (a phone left behind?)."),
            L("Nas regras: as que precisam de certeza perguntam à família em vez de agir; um rosto desconhecido em 3 análises "
              "seguidas continua a dar o alarme.",
              "In the rules: those that need certainty ask the family instead of acting; an unknown face on 3 consecutive "
              "analyses still raises the alarm.")]
    uh = cv.box(U[0], uy, U[1] - U[0], L("INCERTA", "UNSURE"), u_body, stroke=WARN, title_color=WARN, **st)
    ry = uy + uh + 150
    o_body = [L("Alguém da Família está em casa: um telemóvel da Família está no Wi-Fi, ou uma câmara viu uma pessoa há "
                "menos de T_visto.",
                "Someone from the Family is home: a Family phone is on the Wi-Fi, or a camera saw a person in the last T_seen."),
              L("Nas regras: as de “casa vazia” esperam; um rosto desconhecido só dá alarme se a regra o pedir.",
                "In the rules: “empty home” rules wait; an unknown face raises the alarm only if the rule asks for it.")]
    l_body = [L("A porta abriu e fechou. Durante T_saída, o serviço vê quem saiu: um telemóvel que sai do Wi-Fi, ou menos "
                "pessoas nas câmaras.",
                "The door opened and closed. For T_leave, the service checks who left: a phone that leaves the Wi-Fi, or fewer "
                "people on the cameras."),
              L("Se saiu alguém da Família, corre a verificação do objeto esquecido.",
                "If a Family member left, the left-behind check runs.")]
    e_body = [L("Todos os telemóveis da Família estão fora, a porta abriu e fechou e nenhuma câmara viu uma pessoa durante "
                "T_vazia, depois de atualizar os últimos lugares onde havia pessoas.",
                "All Family phones are away, the door opened and closed, and no camera saw a person for T_empty, after a "
                "refresh of the last places where people were."),
              L("Nas regras: as de “casa vazia” agem (propor desligar o que ficou ligado); uma pessoa vista passa a INCERTA.",
                "In the rules: “empty home” rules act (offer to turn off what is on); a person seen moves the state to UNSURE.")]
    w3 = O[1] - O[0]
    ho = cv.box_h(w3, "X", o_body, 16, 16, 12.5)
    he = cv.box_h(w3, "X", e_body, 16, 16, 12.5)
    hl = cv.box_h(w3, "X", l_body, 16, 16, 12.5)
    tall = max(ho, he, hl + 74)
    cv.box(O[0], ry, w3, L("OCUPADA", "OCCUPIED"), o_body, h=tall, stroke=BLUE, title_color=DEEP, **st)
    cv.box(LV[0], ry, w3, L("A SAIR", "LEAVING"), l_body, h=hl, stroke=BLUE, title_color=DEEP, **st)
    cv.box(E[0], ry, w3, L("VAZIA", "EMPTY"), e_body, h=tall, stroke=BLUE, title_color=DEEP, **st)
    ub, lb, ob = uy + uh, ry + hl, ry + tall

    def side(x0, x1, y, s, below=False, anchor="start", w=None):
        cv.label(x0, y, s, w or (x1 - x0), size=12, fill=BODY, below=below, anchor=anchor)

    # OCCUPIED <-> LEAVING, LEAVING -> EMPTY
    gw = LV[0] - O[1] - 24
    y1 = ry + 40
    cv.arrow(O[1], y1, LV[0], y1, INK)
    side(O[1] + 12, LV[0] - 12, y1 - 8, L("a porta abre e depois fecha", "the door opens, then closes"))
    y2 = ry + hl - 26
    cv.arrow(LV[0], y2, O[1], y2, INK)
    side(O[1] + 12, LV[0] - 12, y2 + 18, L("passado T_saída, um telemóvel da Família continua em casa",
                                          "after T_leave, a Family phone is still home"), below=True)
    y3 = ry + 50
    cv.arrow(LV[1], y3, E[0], y3, INK)
    side(LV[1] + 12, E[0] - 12, y3 + 18, L("todos os telemóveis fora e nenhuma pessoa durante T_vazia",
                                          "all phones away and no person for T_empty"), below=True)
    # EMPTY -> OCCUPIED under LEAVING
    y4 = lb + 42
    assert y4 < ob - 20
    cv.arrow(E[0], y4, O[1], y4, INK)
    cv.label((O[1] + E[0]) / 2, y4 - 8, L("chegada: um telemóvel da Família entra no Wi-Fi, ou um rosto da Família é reconhecido",
                                          "arrival: a Family phone joins the Wi-Fi, or a Family face is recognised"),
             E[0] - O[1] - 40, size=12, fill=BODY, anchor="middle")
    # vertical: OCCUPIED <-> UNSURE, LEAVING -> UNSURE, EMPTY <-> UNSURE
    xo1, xo2 = O[0] + 150, O[0] + 210
    cv.arrow(xo1, ry, xo1, ub, INK)
    side(O[0], xo1 - 10, (ub + ry) / 2 - 20, L("telemóvel em casa, mas ninguém visto nem porta usada durante T_parado",
                                               "a phone is home, but nobody seen and no door use for T_stale"), w=xo1 - O[0] - 14)
    cv.arrow(xo2, ub, xo2, ry, INK)
    side(xo2 + 12, O[1], (ub + ry) / 2 - 20, L("um telemóvel da Família entra no Wi-Fi, ou um rosto da Família é reconhecido",
                                               "a Family phone joins the Wi-Fi, or a Family face is recognised"), w=O[1] - xo2 - 14)
    xl = (LV[0] + LV[1]) / 2
    cv.arrow(xl, ry, xl, ub, INK)
    side(xl + 12, LV[1], (ub + ry) / 2 - 4, L("telemóveis fora, mas uma pessoa é vista", "phones away, but a person is seen"),
         w=LV[1] - xl - 14)
    xe1, xe2 = E[0] + 150, E[0] + 210
    cv.arrow(xe1, ry, xe1, ub, INK)
    side(E[0], xe1 - 10, (ub + ry) / 2 - 20, L("uma pessoa vista (rosto desconhecido ou não visível)",
                                               "a person seen (unknown face or face not visible)"), w=xe1 - E[0] - 14)
    cv.arrow(xe2, ub, xe2, ry, INK)
    side(xe2 + 12, E[1], (ub + ry) / 2 - 20, L("telemóveis fora e nenhuma pessoa durante T_vazia, depois da atualização",
                                               "phones away and no person for T_empty, after the refresh"), w=E[1] - xe2 - 14)

    # ---- below: signals, the count and the timings
    by = ob + 40
    bw = (W - 80 - 2 * 24) / 3
    sig = [L("Telemóveis: o _router_ diz que telemóveis da Família estão no Wi-Fi (ferramenta MCP proposta; simulada no protótipo).",
             "Phones: the router says which Family phones are on the Wi-Fi (a proposed MCP tool; simulated in the prototype)."),
           L("Porta: o sensor de contacto envia “aberta” e “fechada” à plataforma, como hoje.",
             "Door: the contact sensor sends “open” and “closed” to the platform, as today."),
           L("Câmaras: pessoas encontradas pelo _OWLv2_ e, com consentimento, o rótulo do rosto calculado em casa.",
             "Cameras: people found by OWLv2 and, with consent, the face label worked out in the home.")]
    cnt = [L("Pessoas em casa = pessoas da Família em casa (telemóvel no Wi-Fi ou rosto reconhecido desde a última vez que a "
             "porta abriu) + pessoas com rosto desconhecido vistas agora.",
             "People home = Family members home (phone on the Wi-Fi, or face recognised since the door last opened) + people "
             "with an unknown face seen now."),
           L("Uma pessoa de rosto não visível conta como alguém da Família, se houver alguém da Família em casa; senão, o "
             "estado passa a INCERTA.",
             "A person whose face is not visible counts as a Family member if one is home; otherwise the state becomes UNSURE."),
           L("Divisão sem câmara: cobrem-na os telemóveis. Pessoa parada: cobrem-na os telemóveis e a atualização periódica.",
             "A room without a camera: the phones cover it. A still person: the phones and the periodic refresh cover them.")]
    h1 = cv.box_h(bw, "X", sig, 16, 14.5, 12.5)
    h2 = cv.box_h(bw, "X", cnt, 16, 14.5, 12.5)
    rows = [("T_telemóvel", "T_phone", L("telemóvel ausente conta como fora*", "a missing phone counts as away*"), "10 s", "10 min"),
            ("T_visto", "T_seen", L("uma pessoa vista mantém OCUPADA", "a person seen keeps OCCUPIED"), "30 s", "15 min"),
            ("T_saída", "T_leave", L("A SAIR espera por quem saiu", "LEAVING waits for a leaver"), "30 s", "5 min"),
            ("T_vazia", "T_empty", L("ninguém visto antes de VAZIA", "nobody seen before EMPTY"), "20 s", "3 min"),
            ("T_atualizar", "T_refresh", L("revê onde as pessoas estavam", "re-checks where people were"), "10 s", "2 min"),
            ("T_parado", "T_stale", L("telemóvel em casa sem sinais", "phone home with no other sign"), "60 s", "180 min")]
    h3 = 16 + 22 + 24 + len(rows) * 21 + 50
    hb = max(h1, h2, h3)
    cv.box(40, by, bw, L("Sinais", "Signals"), sig, h=hb, pad=16)
    cv.box(40 + bw + 24, by, bw, L("Contagem de pessoas", "Count of people"), cnt, h=hb, pad=16)
    tx = 40 + 2 * (bw + 24)
    cv.rect(tx, by, bw, hb)
    cv.text(tx + 16, by + 30, L("Tempos: demonstração / produção", "Timings: demo / production"), 14.5, True, INK)
    c1, c2, c3 = tx + 16, tx + bw - 150, tx + bw - 76
    yy = by + 56
    cv.text(c2, yy, L("demo", "demo"), 11.5, True, MUTED)
    cv.text(c3, yy, L("produção", "production"), 11.5, True, MUTED)
    for pt, en, what, demo, prod in rows:
        yy += 21
        name = pt if lang == "pt" else en
        cv.text(c1, yy, f"{name} · {what}", 12, False, BODY, max_w=c2 - c1 - 8)
        cv.text(c2, yy, demo if lang == "en" else demo, 12, True, INK)
        cv.text(c3, yy, prod, 12, True, INK)
    cv.para(c1, yy + 26, L("* Em A SAIR, logo que sai do Wi-Fi. Valores de produção propostos, a afinar num piloto.",
                           "* In LEAVING, as soon as it leaves the Wi-Fi. Production values are proposals, to tune in a pilot."),
            bw - 32, 11.5, fill=MUTED)
    foot = L("Corre no serviço _ThingTracker_, na Altice: um estado por casa, recalculado a cada evento (porta, Wi-Fi, resultado "
             "da visão) e a cada temporizador.",
             "Runs in the ThingTracker service, at Altice: one state per home, recomputed on every event (door, Wi-Fi, vision "
             "result) and every timer.")
    end = cv.para(40, by + hb + 30, foot, W - 80, 12.5, fill=MUTED)
    cv.save("presenca-estados", round(end))


# ====================================================================== sequences
def legend(lang):
    return ("Cinzento: em casa. Azul: Altice. Laranja: telemóvel. Os tempos de produção são propostas, a afinar num piloto."
            if lang == "pt" else
            "Grey: in the home. Blue: Altice. Orange: the phone. Production timings are proposals, to tune in a pilot.")


@view
def seq_livro_esquecido(lang):
    pt = lang == "pt"
    L = (lambda a, b: a if pt else b)
    cols = [(L("Sensor da porta e _router_", "Door sensor and router"), L("em casa, ligados à Altice", "in the home, on Altice"), "home"),
            (L("Agente da casa", "Home agent"), L("no _router_", "on the router"), "home"),
            (L("Plataforma Altice", "Altice platform"), L("dispositivos e eventos", "devices and events"), "altice"),
            (L("Servidores de visão", "Vision workers"), L("_OWLv2_ e _DINOv2_, GPU L4", "OWLv2 and DINOv2, L4 GPUs"), "altice"),
            (L("Serviço _ThingTracker_", "ThingTracker service"), L("presença e regras, por casa", "presence and rules, per home"), "altice"),
            (L("Aplicação Altice", "Altice app"), L("no telemóvel", "on the phone"), "phone")]
    rows = [
        ("g", L("Estado: OCUPADA (o telemóvel do Filipe está no Wi-Fi). O livro foi visto pela última vez na secretária da Sala 1, às 18h02.",
                "State: OCCUPIED (Filipe’s phone is on the Wi-Fi). The book was last seen on the desk in Living room 1, at 18:02.")),
        ("m", 0, 2, L("porta aberta (`sensorState: alarm`)", "door open (`sensorState: alarm`)")),
        ("m", 2, 4, L("`door.opened` (hoje: `get_home_devices` a cada 4 s)", "`door.opened` (today: `get_home_devices` every 4 s)")),
        ("m", 0, 2, L("porta fechada, 8 s depois", "door closed, 8 s later")),
        ("m", 2, 4, L("`door.closed`", "`door.closed`")),
        ("n", 4, 4, L("A porta abriu e fechou: OCUPADA → A SAIR. Espera até T_saída (30 s na demonstração, 5 min em produção) por quem saiu",
                      "The door opened and closed: OCCUPIED → LEAVING. Waits up to T_leave (30 s in the demo, 5 min in production) for whoever left")),
        ("m", 0, 2, L("o telemóvel do Filipe saiu do Wi-Fi", "Filipe’s phone left the Wi-Fi")),
        ("m", 2, 4, L("`wifi.left`: Filipe (ferramenta proposta)", "`wifi.left`: Filipe (proposed tool)")),
        ("n", 4, 4, L("Saiu alguém da Família: verificação ativa do lugar habitual do livro, sem esperar por movimento",
                      "A Family member left: an active check of the book’s usual place, without waiting for motion")),
        ("m", 4, 1, L("envia a região da secretária: 3 imagens, 1 por segundo", "send the desk’s region: 3 frames, 1 a second")),
        ("m", 1, 3, L("3 regiões, na fila urgente", "3 regions, on the urgent queue")),
        ("m", 3, 4, L("3 resultados: caixas de “livro” e vetores _DINOv2_", "3 results: “book” boxes and DINOv2 vectors")),
        ("n", 4, 4, L("Comparados com as 8 vistas do livro (_pgvector_): 0,70 ≥ 0,62 em 3 de 3 imagens. Regra “avisa-me se sair sem o "
                      "livro” cumprida, porque bastam 2 de 3",
                      "Matched with the book’s 8 views (pgvector): 0.70 ≥ 0.62 in 3 of 3 frames. Rule “tell me if I leave without "
                      "my book” met, since 2 of 3 are enough")),
        ("m", 4, 5, L("aviso: “O livro ficou em casa”, com a miniatura e “na secretária, às 18h02”",
                      "alert: “Your book stayed at home”, with the thumbnail and “on the desk, at 18:02”")),
        ("g", L("Se o livro aparecer em menos de 2 das 3 imagens (meio tapado, por exemplo), o motor de regras pode chamar o juiz: um modelo "
                "de visão-linguagem na Altice vê 2 a 3 s da região e responde sim, não ou incerto, com uma frase. “Sim” dá o aviso; “não” "
                "não dá; “incerto” faz a aplicação perguntar à família, sem alarme.",
                "If the book is seen in fewer than 2 of the 3 frames (half hidden, say), the rules engine may call the judge: a "
                "vision-language model at Altice looks at 2 to 3 s of the region and answers yes, no or unsure, with a sentence. “Yes” "
                "gives the alert; “no” does not; “unsure” makes the app ask the family, with no alarm.")),
        ("g", L("Uma chegada (a porta abre e fecha e um telemóvel entra no Wi-Fi) não inicia a verificação.",
                "An arrival (the door opens and closes and a phone joins the Wi-Fi) does not start the check.")),
        ("g", L("Sem sensor de porta, o mesmo teste começa quando um telemóvel da Família sai do Wi-Fi (passado T_telemóvel, por isso "
                "mais tarde) ou quando uma câmara que vê a porta de saída vê alguém sair por ela.",
                "Without a door sensor, the same check starts when a Family phone leaves the Wi-Fi (after T_phone, so later) or "
                "when a camera that sees the exit door sees someone leave through it.")),
    ]
    sequence(lang, "seq-livro-esquecido", L("Sequência: o livro esquecido", "Sequence: the book left behind"), cols, rows, legend(lang),
             colw=[200, 190, 210, 200, 250, 290])


@view
def seq_pessoa_desconhecida(lang):
    pt = lang == "pt"
    L = (lambda a, b: a if pt else b)
    cols = [(L("Câmara", "Camera"), L("Sala 1, rede da casa", "Living room 1, home network"), "home"),
            (L("Agente da casa", "Home agent"), L("no _router_, com _YuNet_ e _SFace_", "on the router, with YuNet and SFace"), "home"),
            (L("Servidores de visão", "Vision workers"), L("_OWLv2_, GPU L4", "OWLv2, L4 GPUs"), "altice"),
            (L("Serviço _ThingTracker_", "ThingTracker service"), L("presença e regras, por casa", "presence and rules, per home"), "altice"),
            (L("Aplicação Altice", "Altice app"), L("no telemóvel", "on the phone"), "phone"),
            (L("Servidor MCP", "MCP server"), L("plataforma Altice", "Altice platform"), "altice")]
    rows = [
        ("g", L("Estado: VAZIA desde as 14h10 (nenhum telemóvel da Família no Wi-Fi). Regra ativa: “Toca o alarme quando entrar alguém "
                "que não seja da Família”, com a escolha “perguntar primeiro”.",
                "State: EMPTY since 14:10 (no Family phone on the Wi-Fi). Active rule: “Sound the alarm when someone who isn’t Family "
                "comes in”, with the choice “ask first”.")),
        ("m", 0, 1, L("imagens RTSP, só na rede da casa", "RTSP frames, on the home network only")),
        ("n", 1, 1, L("Movimento: recorta a região que mudou. _YuNet_ encontra um rosto; _SFace_ dá 0,21 contra o padrão mais "
                      "parecido, abaixo de 0,363: “rosto desconhecido”",
                      "Motion: cuts out the changed region. YuNet finds a face; SFace gives 0.21 against the closest template, "
                      "below 0.363: “unknown face”")),
        ("m", 1, 2, L("região + “rosto desconhecido” e a sua caixa (fila urgente)", "region + “unknown face” and its box (urgent queue)")),
        ("m", 2, 3, L("uma pessoa; o rosto está dentro da sua caixa", "a person; the face is inside their box")),
        ("n", 3, 3, L("3 análises seguidas (cerca de 3 s) com o mesmo rosto desconhecido: VAZIA → INCERTA, e a regra cumpre-se",
                      "3 consecutive analyses (about 3 s) with the same unknown face: EMPTY → UNSURE, and the rule is met")),
        ("m", 3, 4, L("aviso urgente: “Está alguém que não é da Família na Sala 1”, com o recorte da pessoa",
                      "urgent alert: “Someone who isn’t Family is in Living room 1”, with the crop of the person")),
        ("n", 4, 4, L("Cartões do aviso: “Tocar a sirene”, “Ligar à polícia (112)” e “Ver em direto”",
                      "The alert’s cards: “Sound the siren”, “Call the police (112)” and “See live”")),
        ("m", 4, 3, L("“Sim” em “Tocar a sirene”", "“Yes” on “Sound the siren”")),
        ("m", 3, 5, L("`update_device_capabilities`: `sirenSwitch` da câmara ligado", "`update_device_capabilities`: camera `sirenSwitch` on")),
        ("n", 4, 4, L("“Ligar à polícia (112)” abre a chamada no telemóvel e é a pessoa quem liga. O sistema nunca marca o número",
                      "“Call the police (112)” opens the call on the phone and the person places it. The system never dials")),
        ("g", L("Rosto da Família (semelhança ≥ 0,363): nenhum aviso, e INCERTA → OCUPADA. Rosto não visível: a aplicação pergunta "
                "“Está alguém na Sala 1. É alguém conhecido?”, sem alarme, e só sugere o 112 se a resposta for “não”.",
                "A Family face (similarity ≥ 0.363): no alert, and UNSURE → OCCUPIED. Face not visible: the app asks “Someone is in "
                "Living room 1. Do you know them?”, with no alarm, and suggests 112 only if the answer is “no”.")),
    ]
    sequence(lang, "seq-pessoa-desconhecida", L("Sequência: pessoa desconhecida", "Sequence: an unknown person"), cols, rows, legend(lang),
             colw=[190, 230, 200, 250, 290, 200])


@view
def seq_casa_vazia(lang):
    pt = lang == "pt"
    L = (lambda a, b: a if pt else b)
    cols = [(L("Sensor da porta e _router_", "Door sensor and router"), L("em casa, ligados à Altice", "in the home, on Altice"), "home"),
            (L("Agente da casa", "Home agent"), L("no _router_", "on the router"), "home"),
            (L("Plataforma Altice", "Altice platform"), L("eventos e servidor MCP", "events and MCP server"), "altice"),
            (L("Servidores de visão", "Vision workers"), L("_OWLv2_, GPU L4", "OWLv2, L4 GPUs"), "altice"),
            (L("Serviço _ThingTracker_", "ThingTracker service"), L("presença e regras, por casa", "presence and rules, per home"), "altice"),
            (L("Aplicação Altice", "Altice app"), L("no telemóvel", "on the phone"), "phone")]
    rows = [
        ("g", L("Estado: OCUPADA. Regras ativas: “Quando não estiver ninguém, propõe desligar o que ficou ligado” e “Avisa-me se a "
                "porta ficar aberta sem ninguém por perto”.",
                "State: OCCUPIED. Active rules: “When nobody is home, offer to turn off what is still on” and “Tell me if the "
                "door is left open with nobody around”.")),
        ("m", 0, 2, L("porta aberta e fechada; os 2 telemóveis da Família saem do Wi-Fi", "door opened and closed; both Family phones leave the Wi-Fi")),
        ("m", 2, 4, L("`door.opened`, `door.closed`, `wifi.left` × 2", "`door.opened`, `door.closed`, `wifi.left` × 2")),
        ("n", 4, 4, L("OCUPADA → A SAIR. Nenhuma pessoa vista desde que a porta fechou; falta confirmar que ninguém ficou parado",
                      "OCCUPIED → LEAVING. No person seen since the door closed; it still has to confirm that nobody stayed still")),
        ("m", 4, 1, L("atualização: as regiões onde as pessoas foram vistas por último", "refresh: the regions where people were last seen")),
        ("m", 1, 3, L("regiões (fila urgente)", "regions (urgent queue)")),
        ("m", 3, 4, L("nenhuma pessoa", "no person")),
        ("n", 4, 4, L("T_vazia cumprido: A SAIR → VAZIA. Ligados, segundo `get_home_devices`: as luzes (na tomada) e o ar condicionado",
                      "T_empty met: LEAVING → EMPTY. On, according to `get_home_devices`: the lights (on the plug) and the air conditioner")),
        ("m", 4, 5, L("aviso: “Não está ninguém em casa e há 2 aparelhos ligados”, com dois cartões “Sim”",
                      "alert: “Nobody is home and 2 appliances are on”, with two “Yes” cards")),
        ("m", 5, 4, L("“Sim”: desligar as luzes", "“Yes”: turn off the lights")),
        ("m", 4, 2, L("`update_device_capabilities`: tomada desligada", "`update_device_capabilities`: plug off")),
        ("m", 5, 4, L("“Sim”: desligar o ar condicionado", "“Yes”: turn off the air conditioner")),
        ("m", 4, 2, L("`update_device_capabilities`: ar condicionado desligado", "`update_device_capabilities`: air conditioner off")),
        ("g", L("Noutro dia, a porta da entrada fica aberta", "Another day, the front door is left open")),
        ("m", 0, 2, L("porta aberta", "door open")),
        ("m", 2, 4, L("`door.opened`", "`door.opened`")),
        ("n", 4, 4, L("Porta aberta há T_porta (20 s na demonstração, 2 min em produção), sem movimento nem pessoas em nenhuma câmara "
                      "desde que abriu",
                      "Door open for T_door (20 s in the demo, 2 min in production), with no motion and no person on any camera "
                      "since it opened")),
        ("m", 4, 5, L("aviso: “A porta da entrada está aberta e não está ninguém por perto”, com a faixa da porta e “Ver em direto”",
                      "alert: “The front door is open and nobody is around”, with the door banner and “See live”")),
    ]
    sequence(lang, "seq-casa-vazia", L("Sequência: casa vazia e porta aberta", "Sequence: empty home and open door"), cols, rows, legend(lang),
             colw=[200, 190, 210, 200, 250, 290])


# ====================================================================== C4
PERSON = dict(stroke=DEEP, sw=1.6, fill="#FFFFFF", sub_bold=False, sub_color=MUTED)
SYSTEM = dict(stroke=BLUE, sw=2.4, fill="#EAF4FC", sub_bold=False, sub_color=MUTED)
EXTERNAL = dict(stroke="#B8BEC6", sw=1.2, fill="#F2F3F5", sub_bold=False, sub_color=MUTED)
CONTAINER = dict(stroke=BLUE, sw=1.6, fill="#FFFFFF", sub_bold=False, sub_color=MUTED)


def bands_under(cv, draw):
    """Draw zone bands under everything drawn so far."""
    b = Canvas(cv.w, cv.lang, "")
    draw(b)
    cv.o = b.o + cv.o


@view
def c4_1_contexto(lang):
    W = 1580
    cv = Canvas(W, lang, "C4, nível 1: contexto" if lang == "pt" else "C4, level 1: context")
    L = cv.L
    g = Grid(cv, [40, 600, 1180], [360, 360, 360], 30, row_gap=130)
    g.place({
        "family": (0, 0, 1, dict(title=L("Família", "Family"), sub=L("[pessoa]", "[person]"),
                                 body=[L("Regista objetos e pessoas, escreve regras numa frase, pergunta e responde aos avisos",
                                         "Registers things and people, writes rules in one sentence, asks, and answers alerts")], **PERSON)),
        "app": ((1, 2), 0, 1, dict(title=L("Aplicação Altice", "Altice app"), sub=L("[sistema existente · no telemóvel]", "[existing system · on the phone]"),
                                   body=[L("A aplicação que a família já usa, com um novo separador _Things_ e o assistente em todos os separadores",
                                           "The app the family already uses, with a new Things tab and the assistant on every tab")], **EXTERNAL)),
        "cams": (0, 1, 1, dict(title=L("Câmaras do kit", "Kit cameras"), sub=L("[sistema existente · em casa]", "[existing system · in the home]"),
                               body=[L("Vídeo RTSP na rede da casa", "RTSP video on the home network")], **EXTERNAL)),
        "tt": (1, 1, 1, dict(title="_ThingTracker_" if lang == "pt" else "ThingTracker", sub=L("[sistema descrito]", "[the system described]"),
                             body=[L("Torna a câmara uma fonte de informação: encontra os objetos registados e as pessoas, sabe quem está "
                                     "em casa e cumpre regras escritas numa frase",
                                     "Makes the camera a source of information: finds the registered things and people, knows who is "
                                     "home, and keeps rules written in one sentence"),
                                   L("Duas partes: o agente da casa, no _router_, e o serviço com a visão, na Altice",
                                     "Two parts: the home agent, on the router, and the service with the vision, at Altice")], **SYSTEM)),
        "plat": (2, 1, 1, dict(title=L("Plataforma Connected Home", "Connected Home platform"), sub=L("[sistema existente · Altice]", "[existing system · Altice]"),
                               body=[L("Dispositivos, cenários, segurança e notificações; servidor MCP com 18 ferramentas",
                                       "Devices, scenarios, security and notifications; MCP server with 18 tools")], **EXTERNAL)),
        "visitor": (0, 2, 1, dict(title=L("Visita ou desconhecido", "Guest or stranger"), sub=L("[pessoa]", "[person]"),
                                  body=[L("Aparece nas imagens; sem registo nem consentimento, nunca recebe um nome",
                                          "Appears in the frames; without registration and consent, never gets a name")], **PERSON)),
        "llm": (1, 2, 1, dict(title=L("Modelos de linguagem e de visão-linguagem", "Language and vision-language models"),
                              sub=L("[o de texto pode ser de um fornecedor sob contrato]", "[the text model may be a provider under contract]"),
                              body=[L("Compilam frases em regras e redigem respostas; o juiz vê, raramente, 2 a 3 s de um momento duvidoso",
                                      "Compile sentences into rules and word answers; the judge rarely sees 2 to 3 s of an ambiguous moment")],
                              dash="6 4", **EXTERNAL)),
        "router": (2, 2, 1, dict(title=L("_Router_ e sensores do kit", "Router and kit sensors"), sub=L("[sistemas existentes · em casa]", "[existing systems · in the home]"),
                                 body=[L("Wi-Fi com os telemóveis da Família; sensor da porta; luz, tomada e sirene",
                                         "Wi-Fi with the Family phones; door sensor; light, plug and siren")], **EXTERNAL)),
    })
    g.h2("family", "app", L("usa: regista, pergunta, escreve regras, diz “Sim”", "uses it: registers, asks, writes rules, says “Yes”"),
         L("mostra avisos e respostas", "shows alerts and answers"))
    g.v2("app", "tt", L("frases, perguntas, fotografias, vídeo do rosto, “Sim”", "sentences, questions, photos, face video, “Yes”"),
         L("respostas", "answers"), lw=160)
    g.v("plat", "app", L("notificações com os avisos", "notifications with the alerts"), lw=160)
    g.h("cams", "tt", L("vídeo, lido em casa pelo agente no _router_", "video, read in the home by the agent on the router"))
    g.h2("tt", "plat", L("chamadas MCP: ações após “Sim”, leitura dos dispositivos; avisos", "MCP calls: actions after “Yes”, device reads; alerts"),
         L("eventos da porta e do Wi-Fi", "door and Wi-Fi events"))
    g.v2("tt", "llm", L("texto; raramente, um clipe curto", "text; rarely, a short clip"), L("regras, respostas, veredictos", "rules, answers, verdicts"), lw=150)
    g.v2("plat", "router", L("comandos: luz, tomada, sirene", "commands: light, plug, siren"),
         L("porta aberta e fechada; telemóveis no Wi-Fi (ferramenta proposta)", "door open and closed; phones on the Wi-Fi (proposed tool)"), lw=155)
    g.v("visitor", "cams", L("aparece nas imagens", "appears in the frames"), lw=150)
    end = max(r[3] for r in g.r.values())
    end = cv.para(40, end + 40, L("Notação C4 (c4model.com), nível 1. Azul: o sistema descrito; cinzento: sistemas existentes; contorno "
                                  "azul-escuro: pessoas; tracejado: pode ser externo à Altice.",
                                  "C4 notation (c4model.com), level 1. Blue: the system described; grey: existing systems; dark blue "
                                  "outline: people; dashed: may be outside Altice."), W - 80, 12.5, fill=MUTED)
    cv.save("c4-1-contexto", round(end))


@view
def c4_2_contentores(lang):
    cv = Canvas(2260, lang, "C4, nível 2: contentores" if lang == "pt" else "C4, level 2: containers")
    L = cv.L
    xs = [40, 430, 790, 1180, 1590, 1970]
    ws = [250, 220, 250, 270, 240, 250]
    g = Grid(cv, xs, ws, 96, row_gap=96)
    C = CONTAINER
    g.place({
        "cams": (0, 0, 1, dict(title=L("Câmaras do kit", "Kit cameras"), sub=L("[sistema existente]", "[existing system]"),
                               body=[L("RTSP, H.265", "RTSP, H.265")], **EXTERNAL)),
        "app": ((3, 5), 0, 1, dict(title=L("Aplicação Altice", "Altice app"), sub=L("[sistema existente · telemóvel]", "[existing system · phone]"),
                                   body=[L("Separador _Things_, assistente e avisos com cartões de ação", "Things tab, assistant, and alerts with action cards")], **EXTERNAL)),
        "agent": (0, 1, 2, dict(title=L("Agente da casa", "Home agent"), sub=L("[_Python_ no CPU do _router_]", "[Python on the router’s CPU]"),
                                body=[L("Máscaras, filtro de movimento, recorte da região que mudou", "Masks, motion gate, cutting out the changed region"),
                                      L("Rostos com _YuNet_ e _SFace_ (opcional)", "Faces with YuNet and SFace (opt-in)"),
                                      L("Lê a pedido do serviço, mesmo sem movimento", "Reads on the service’s request, even without motion"),
                                      L("Guarda só em memória os últimos 3 s, para o juiz", "Keeps the last 3 s in memory only, for the judge")], **C)),
        "vision": (2, 1, 1, dict(title=L("Servidores de visão", "Vision workers"), sub=L("[_PyTorch_, GPU L4]", "[PyTorch, L4 GPUs]"),
                                 body=[L("_OWLv2_: caixas; _DINOv2_: um vetor por candidato", "OWLv2: boxes; DINOv2: one vector per candidate")], **C)),
        "broker": (1, 2, 1, dict(title=L("Mediador de ligações", "Connection broker"), sub=L("[MQTT sobre mTLS]", "[MQTT over mTLS]"),
                                 body=[L("Uma ligação por casa, atrás de um balanceador", "One connection per home, behind a load balancer")], **C)),
        "queues": (2, 2, 1, dict(title=L("Filas e fluxo de eventos", "Queues and event stream"), sub=L("[corretor de mensagens]", "[message broker]"),
                                 body=[L("Visão urgente e em lote; eventos de cada casa por ordem; pedidos ao modelo",
                                         "Urgent and batch vision; each home’s events in order; model requests")], **C)),
        "svc": (3, 2, 3, dict(title=L("Serviço _ThingTracker_", "ThingTracker service"), sub=L("[contentores sem estado, atrás de um balanceador]",
                                                                                            "[stateless containers, behind a load balancer]"),
                              body=[L("API da aplicação e _host_ MCP", "App API and MCP host"),
                                    L("Comparação com as assinaturas visuais", "Matching with the fingerprints"),
                                    L("Seguimento: na mão, levado, mudado", "Tracking: in hand, taken, moved"),
                                    L("Motor de presença e motor de regras, por casa; o motor de regras decide", "Presence engine and rules engine, per home; the rules engine decides"),
                                    L("Avisos; um “Sim” vira uma chamada MCP", "Alerts; a “Yes” becomes an MCP call")], stroke=BLUE, sw=2.4,
                              fill="#FFFFFF", sub_bold=False, sub_color=MUTED)),
        "plat": (5, 2, 1, dict(title=L("Plataforma Connected Home", "Connected Home platform"), sub=L("[sistema existente]", "[existing system]"),
                               body=[L("Servidor MCP, eventos da porta e do Wi-Fi, notificações", "MCP server, door and Wi-Fi events, notifications")], **EXTERNAL)),
        "faces": (0, 3, 1, dict(title=L("Padrões faciais", "Face templates"), sub=L("[_SQLite_ cifrado, no _router_]", "[encrypted SQLite, on the router]"),
                                body=[L("Até 8 por pessoa; nunca saem de casa", "Up to 8 per person; never leave the home")], **C)),
        "cache": (2, 3, 1, dict(title=L("_Cache_", "Cache"), sub=L("[_Redis_]", "[Redis]"),
                                body=[L("Estado de cada casa em uso: presença, trajetos, temporizadores", "Each home’s live state: presence, tracks, timers")], **C)),
        "pg": (4, 3, 1, dict(title="PostgreSQL", sub=L("[com _pgvector_]", "[with pgvector]"),
                             body=[L("Por cliente: objetos, assinaturas, regras, avisos, observações", "Per customer: things, fingerprints, rules, alerts, sightings")], **C)),
        "llm": (2, 4, 1, dict(title=L("Modelos de linguagem e de visão-linguagem", "Language and vision-language models"),
                              sub=L("[servidores GPU atrás de uma fila]", "[GPU servers behind a queue]"),
                              body=[L("Texto e, raramente, clipes curtos para o juiz", "Text and, rarely, short clips for the judge")], **C)),
        "store": (4, 4, 1, dict(title=L("Armazenamento de objetos", "Object storage"), sub=L("[compatível com S3]", "[S3-compatible]"),
                                body=[L("Miniaturas, 30 dias (proposta)", "Thumbnails, 30 days (proposal)")], **C)),
    })
    g.v("cams", "agent", L("vídeo RTSP, rede da casa", "RTSP video, home network"), lw=110)
    g.v2("agent", "faces", L("guarda padrões", "stores templates"), L("padrões para comparar", "templates to compare"), lw=100)
    g.h2("agent", "broker", L("regiões e rótulos de rostos", "regions and face labels"), L("pedidos, vídeo de registo", "requests, registration video"))
    g.h2("broker", "queues", L("regiões", "regions"), L("pedidos às casas", "requests to homes"))
    g.v2("vision", "queues", L("caixas e vetores", "boxes and vectors"), L("regiões", "regions"), lw=100)
    g.h2("queues", "svc", L("eventos de cada casa, por ordem", "each home’s events, in order"), L("pedidos às casas e ao modelo", "requests to homes and the model"))
    g.h2("cache", "svc", L("estado", "state"), L("estado e temporizadores", "state and timers"))
    g.h2("llm", "svc", L("regra, resposta, veredicto", "rule, answer, verdict"), L("texto ou clipe curto, pela fila", "text or a short clip, through the queue"))
    g.h2("svc", "pg", L("objetos, regras, avisos", "things, rules, alerts"), L("assinaturas (_pgvector_)", "fingerprints (pgvector)"))
    g.h("svc", "store", L("miniaturas", "thumbnails"))
    g.h2("svc", "plat", L("chamadas MCP: ações, leitura", "MCP calls: actions, reads"), L("eventos: porta, Wi-Fi", "events: door, Wi-Fi"))
    g.v2("app", "svc", L("pedidos HTTPS, pelo balanceador", "HTTPS requests, through the load balancer"), L("respostas, miniaturas", "answers, thumbnails"), lw=120)
    g.v("plat", "app", L("notificações", "notifications"), lw=110)
    top, bot = g.ys[1] - 50, max(r[3] for r in g.r.values()) + 24
    app = g.r["app"]

    def zones(b):
        b.band(20, 24, xs[0] + ws[0] + 20 - 20, bot - 24, L("Em casa", "In the home"), None, fill=HOME_BG)
        b.band(app[0] - 20, 24, app[2] - app[0] + 40, app[3] + 18 - 24, L("Telemóvel", "Phone"), None, fill=PHONE_BG)
        b.band(xs[1] - 20, top, xs[5] + ws[5] + 20 - (xs[1] - 20), bot - top, L("Altice", "Altice"), None, fill=ALTICE_BG)
    bands_under(cv, zones)
    end = cv.para(40, bot + 34, L("Notação C4, nível 2. Contorno azul: contentores do _ThingTracker_; cinzento: sistemas existentes. Cada seta "
                                  "é um sentido do fluxo, com o que leva.",
                                  "C4 notation, level 2. Blue outline: ThingTracker containers; grey: existing systems. Each arrow is one "
                                  "direction of a flow, with what it carries."), 2180, 12.5, fill=MUTED)
    cv.save("c4-2-contentores", round(end))


@view
def c4_3_componentes(lang):
    cv = Canvas(2060, lang, "C4, nível 3: componentes" if lang == "pt" else "C4, level 3: components")
    L = cv.L
    xs = [40, 350, 730, 1060, 1430, 1800]
    ws = [190, 250, 200, 240, 260, 220]
    g = Grid(cv, xs, ws, 110, row_gap=56)
    C = dict(CONTAINER, sw=1.4)
    X = EXTERNAL
    g.place({
        "cams": (0, 0, 1, dict(title=L("Câmaras", "Cameras"), sub=L("[existente]", "[existing]"), body=[L("RTSP na rede da casa", "RTSP on the home network")], **X)),
        "cap": (1, 0, 1, dict(title=L("Captura", "Capture"), sub="[_ffmpeg_, _OpenCV_]" if lang == "pt" else "[ffmpeg, OpenCV]",
                              body=[L("Uma ligação aberta por câmara; só os últimos 3 s, em memória, para o juiz", "One open connection per camera; only the last 3 s, in memory, for the judge")], **C)),
        "mask": (1, 1, 1, dict(title=L("Máscaras de privacidade", "Privacy masks"),
                               body=[L("Apaga as zonas que a família marcou, antes de qualquer análise", "Blanks the areas the family marked, before any analysis")], **C)),
        "gate": (1, 2, 1, dict(title=L("Filtro de movimento", "Motion gate"), sub=L("[160 × 90, cinzento, a cada 0,5 s]", "[160 × 90, grey, every 0.5 s]"),
                               body=[L("Abre se mais de 0,6 % dos píxeis mudar e fica aberto 6 s; abre também a pedido",
                                       "Opens if more than 0.6 % of the pixels change and stays open 6 s; also opens on request")], **C)),
        "reg": (1, 3, 1, dict(title=L("Recorte da região", "Region cutter"),
                              body=[L("A região que mudou, ou a pedida, no máximo 640 × 640; cerca de 1 por segundo",
                                      "The changed region, or the requested one, at most 640 × 640; about 1 a second")], **C)),
        "face": (1, 4, 1, dict(title=L("Rostos (opcional)", "Faces (opt-in)"), sub=L("[_YuNet_ + _SFace_, no CPU]", "[YuNet + SFace, on the CPU]"),
                               body=[L("Encontra, alinha e compara: ≥ 0,363 dá o nome; abaixo, “rosto desconhecido”",
                                       "Finds, aligns and compares: ≥ 0.363 gives the name; below, “unknown face”")], **C)),
        "tpl": (0, 4, 1, dict(title=L("Padrões faciais", "Face templates"), sub=L("[_SQLite_ cifrado]", "[encrypted SQLite]"),
                              body=[L("Até 8 por pessoa; nunca saem de casa", "Up to 8 per person; never leave")], **C)),
        "chan": (2, 2, 4, dict(title=L("Canal seguro", "Secure channel"), sub=L("[MQTT sobre mTLS]", "[MQTT over mTLS]"),
                               body=[L("Uma ligação de saída", "One outbound connection"),
                                     L("Envia regiões e rótulos; recebe pedidos", "Sends regions and labels; receives requests"),
                                     L("Sem internet, guarda eventos e rótulos numa fila, nunca imagens", "Offline, queues events and labels, never images")], **C)),
        "brk": (3, 5, 1, dict(title=L("Mediador", "Broker"), sub="[MQTT]",
                              body=[L("Recebe as regiões de cada casa e entrega-lhe os pedidos", "Takes each home’s regions and delivers its requests")], **C)),
        "q": (3, 4, 1, dict(title=L("Filas de visão", "Vision queues"),
                            body=[L("Urgente: pedidos, registos, clipes para o juiz e casas com regra de segurança ativa",
                                    "Urgent: requests, registrations, clips for the judge, homes with an active safety rule"),
                                  L("Lote: o resto, nas horas calmas", "Batch: the rest, in quiet hours")], **C)),
        "owl": (3, 3, 1, dict(title=L("Deteção", "Detection"), sub=L("[_OWLv2_, GPU L4]", "[OWLv2, L4 GPU]"),
                              body=[L("Objetos registados da casa, “a person” e superfícies (secretária, mesa)",
                                      "The home’s registered things, “a person” and surfaces (desk, table)")], **C)),
        "dino": (3, 2, 1, dict(title=L("Vetores", "Vectors"), sub=L("[_DINOv2 small_, GPU L4]", "[DINOv2 small, L4 GPU]"),
                               body=[L("Um vetor de 384 números por candidato", "One 384-number vector per candidate")], **C)),
        "judge": (3, 0, 1, dict(title=L("Juiz", "Judge"), sub=L("[visão-linguagem, GPU, raramente]", "[vision-language, GPU, rarely]"),
                                body=[L("Vê 2 a 3 s da região num momento duvidoso; responde sim, não ou incerto, com uma frase",
                                        "Looks at 2 to 3 s of the region at an ambiguous moment; answers yes, no or unsure, with a sentence")], **C)),
        "stream": (3, 1, 1, dict(title=L("Fluxo da casa", "Home stream"), sub=L("[partição por casa]", "[partitioned by home]"),
                                 body=[L("Resultados de cada casa, pela ordem de chegada", "Each home’s results, in arrival order")], **C)),
        "match": (4, 1, 1, dict(title=L("Comparação", "Matching"), sub="[_pgvector_]" if lang == "pt" else "[pgvector]",
                                body=[L("Cada vetor contra as 8 vistas de cada objeto: ≥ 0,62 é o seu", "Each vector against each thing’s 8 views: ≥ 0.62 means yours")], **C)),
        "track": (4, 2, 1, dict(title=L("Seguimento", "Tracking"),
                                body=[L("Sobre uma pessoa: na mão. Ausente 3 análises depois: levado. Noutro sítio: mudado",
                                        "Over a person: in hand. Gone 3 analyses later: taken. Elsewhere: moved")], **C)),
        "pres": (4, 3, 1, dict(title=L("Motor de presença", "Presence engine"),
                               body=[L("OCUPADA, A SAIR, VAZIA ou INCERTA; pede atualizações se só as câmaras o sustentam",
                                       "OCCUPIED, LEAVING, EMPTY or UNSURE; asks for refreshes when only cameras support it")], **C)),
        "rules": (4, 4, 1, dict(title=L("Motor de regras", "Rules engine"),
                                body=[L("Decide: regras compiladas, a cada evento e temporizador; pede verificações ativas e, num momento duvidoso, o juiz",
                                        "Decides: compiled rules, on every event and timer; asks for active checks and, at an ambiguous moment, the judge")], **C)),
        "alert": (4, 5, 2, dict(title=L("Avisos e ações", "Alerts and actions"),
                                body=[L("Título, mensagem, miniatura, cartões de ação, faixa da porta, sugestão",
                                        "Title, message, thumbnail, action cards, door banner, suggestion"),
                                      L("Um “Sim” vira uma chamada MCP; a sirene segue a escolha da família; armar o alarme pergunta sempre",
                                        "A “Yes” becomes an MCP call; the siren follows the family’s choice; arming always asks")], **C)),
        "pg": (5, 1, 2, dict(title="PostgreSQL", sub="[_pgvector_]" if lang == "pt" else "[pgvector]",
                             body=[L("Assinaturas, observações, regras, avisos", "Fingerprints, sightings, rules, alerts")], **C)),
        "plat": (5, 3, 1, dict(title=L("Plataforma Altice", "Altice platform"), sub=L("[existente]", "[existing]"),
                               body=[L("Eventos da porta e telemóveis no Wi-Fi", "Door events and phones on the Wi-Fi")], **X)),
        "cache": (5, 4, 1, dict(title=L("_Cache_", "Cache"), sub="[_Redis_]" if lang == "pt" else "[Redis]",
                                body=[L("Presença, trajetos, contadores, temporizadores", "Presence, tracks, counters, timers")], **C)),
        "notif": (5, 5, 1, dict(title=L("Notificações e aplicação", "Notifications and app"), sub=L("[existente]", "[existing]"),
                                body=[L("Mostram o aviso e devolvem o “Sim”", "Show the alert, return the “Yes”")], **X)),
        "mcp": (5, 6, 1, dict(title=L("Servidor MCP", "MCP server"), sub=L("[existente]", "[existing]"),
                              body=["`update_device_capabilities`"], **X)),
    })
    S = 11
    g.h("cams", "cap", "RTSP", size=S)
    g.v("cap", "mask", L("imagem", "frame"), size=S, lw=100)
    g.v("mask", "gate", L("imagem com máscaras", "masked frame"), size=S, lw=100)
    g.v("gate", "reg", L("aberto", "open"), size=S, lw=100)
    g.v("reg", "face", L("região", "region"), size=S, lw=100)
    g.h2("tpl", "face", L("padrões", "templates"), L("registo", "registration"), size=S)
    g.h("face", "chan", L("região e rótulos", "region and labels"), size=S)
    g.h("chan", "gate", L("pedido: analisar já", "request: analyse now"), size=S)
    g.h2("chan", "brk", L("regiões e rótulos", "regions and labels"), L("pedidos", "requests"), size=S)
    g.v2("q", "brk", L("pedidos às casas", "requests to homes"), L("regiões", "regions"), size=S, lw=110)
    g.v("q", "owl", L("regiões", "regions"), size=S, lw=110)
    g.v("owl", "dino", L("caixas", "boxes"), size=S, lw=110)
    g.v("dino", "stream", L("caixas e vetores", "boxes and vectors"), size=S, lw=110)
    g.h("stream", "match", L("por ordem", "in order"), size=S)
    g.v("match", "track", L("objetos reconhecidos, pessoas e rótulos", "recognised things, people and labels"), size=S, lw=120)
    g.v("track", "pres", L("pessoas e rostos", "people and faces"), size=S, lw=120)
    g.v("pres", "rules", L("estado da casa", "home state"), size=S, lw=120)
    g.v("rules", "alert", L("regra cumprida", "rule met"), size=S, lw=120)
    g.h("rules", "q", L("verificação ativa, atualização, juiz", "active check, refresh, judge"), size=S)
    g.v("judge", "stream", L("veredicto", "verdict"), size=S, lw=110)
    g.h("pg", "match", L("assinaturas", "fingerprints"), size=S)
    g.h("track", "pg", L("observações, quando algo muda", "sightings, when something changes"), size=S)
    g.h("plat", "pres", L("porta, Wi-Fi", "door, Wi-Fi"), size=S)
    g.h2("rules", "cache", L("estado", "state"), L("temporizadores", "timers"), size=S)
    g.h2("alert", "notif", L("aviso", "alert"), L("“Sim”", "“Yes”"), size=S)
    g.h("alert", "mcp", L("ação após “Sim”", "action after “Yes”"), size=S)
    bot = max(r[3] for r in g.r.values()) + 24

    def zones(b):
        b.band(20, 24, xs[2] + ws[2] + 20 - 20, bot - 24, L("Em casa · agente da casa, no _router_", "In the home · home agent, on the router"),
               L("Sem acelerador de IA", "No AI accelerator"), fill=HOME_BG)
        b.band(xs[3] - 20, 24, xs[5] + ws[5] + 20 - (xs[3] - 20), bot - 24,
               L("Altice · visão e serviço _ThingTracker_, por casa", "Altice · vision and ThingTracker service, per home"),
               L("Os componentes da coluna do meio correm no serviço, para cada casa", "The middle column’s components run in the service, for each home"),
               fill=ALTICE_BG)
    bands_under(cv, zones)
    end = cv.para(40, bot + 34, L("Notação C4, nível 3. Cada componente diz o que decide e com que limiar. Valores do filtro de movimento: os "
                                  "do protótipo.",
                                  "C4 notation, level 3. Each component says what it decides and with which threshold. Motion gate values: "
                                  "the prototype’s."), 1980, 12.5, fill=MUTED)
    cv.save("c4-3-componentes", round(end))


# ====================================================================== data flow with trust boundaries
def table(cv, x, y, widths, header, rows, size=12, pad=8):
    """A plain table: bold header, wrapped cells, thin rules. Returns the bottom."""
    lead = round(size * 1.4, 1)
    def row_h(cells, bold=False):
        return max(len(wrap(c, w - 2 * pad, size, bold)) for c, w in zip(cells, widths)) * lead + 2 * pad - 4
    W = sum(widths)
    h = row_h(header, True)
    cv.rect(x, y, W, h, fill="#EEF1F6", stroke=None, rx=4)
    cx = x
    for c, w in zip(header, widths):
        cv.para(cx + pad, y + pad + size * 0.9, c, w - 2 * pad, size, lead, bold=True, fill=INK)
        cx += w
    y += h
    for i, cells in enumerate(rows):
        h = row_h(cells)
        cv.o.append(f'<line x1="{x}" y1="{y:.1f}" x2="{x + W}" y2="{y:.1f}" stroke="#E1E4E8" stroke-width="1"/>')
        cx = x
        for j, (c, w) in enumerate(zip(cells, widths)):
            cv.para(cx + pad, y + pad + size * 0.9, c, w - 2 * pad, size, lead, bold=(j == 0), fill=BLUE if j == 0 else BODY)
            cx += w
        y += h
    cv.o.append(f'<line x1="{x}" y1="{y:.1f}" x2="{x + W}" y2="{y:.1f}" stroke="#E1E4E8" stroke-width="1"/>')
    return y


@view
def dfd_fronteiras(lang):
    W = 1950
    cv = Canvas(W, lang, "Fluxo de dados e fronteiras de confiança" if lang == "pt" else "Data flow and trust boundaries")
    L = cv.L
    xs, ws = [40, 480, 880, 1300, 1700], [250, 250, 270, 230, 270]
    W = cv.w = xs[-1] + ws[-1] + 40
    g = Grid(cv, xs, ws, 100, row_gap=62)
    g.lpad = 24
    ENT = dict(EXTERNAL, rx=2)
    PRO = dict(stroke=BLUE, sw=1.8, fill="#FFFFFF", rx=26, sub_bold=False, sub_color=MUTED)
    STO = dict(stroke=None, fill="#FAFBFC", rx=0, sub_bold=False, sub_color=MUTED)
    g.place({
        "cams": (0, 0, 1, dict(title=L("Câmaras", "Cameras"), sub=L("[entidade externa]", "[external entity]"), **ENT)),
        "agent": (0, 1, 1, dict(title=L("Agente da casa", "Home agent"), sub=L("[processo, no _router_]", "[process, on the router]"), **PRO)),
        "tpl": (0, 2, 1, dict(title=L("Padrões faciais", "Face templates"), sub=L("[arquivo, cifrado]", "[store, encrypted]"), **STO)),
        "router": (0, 3, 1, dict(title=L("_Router_ Wi-Fi", "Wi-Fi router"), sub=L("[entidade externa]", "[external entity]"), **ENT)),
        "door": (0, 4, 1, dict(title=L("Sensor da porta e atuadores", "Door sensor and actuators"), sub=L("[entidades externas]", "[external entities]"), **ENT)),
        "vision": (1, 0, 1, dict(title=L("Servidores de visão", "Vision workers"), sub=L("[processo]", "[process]"), **PRO)),
        "broker": (1, 1, 1, dict(title=L("Mediador e filas", "Broker and queues"), sub=L("[processo]", "[process]"), **PRO)),
        "judge": (1, 2, 1, dict(title=L("Juiz", "Judge"), sub=L("[processo, visão-linguagem]", "[process, vision-language]"), **PRO)),
        "plat": (1, 3, 2, dict(title=L("Plataforma Connected Home", "Connected Home platform"), sub=L("[processo existente]", "[existing process]"),
                               body=[L("Servidor MCP, eventos, dispositivos", "MCP server, events, devices")], **dict(PRO, fill="#F2F3F5", stroke="#B8BEC6"))),
        "svc": (2, 0, 6, dict(title=L("Serviço _ThingTracker_", "ThingTracker service"), sub=L("[processo]", "[process]"),
                              body=[L("Comparação, seguimento, presença, regras e avisos, por casa", "Matching, tracking, presence, rules and alerts, per home")], **PRO)),
        "pg": (3, 1, 1, dict(title="PostgreSQL", sub=L("[arquivo]", "[store]"), **STO)),
        "store": (3, 2, 1, dict(title=L("Miniaturas", "Thumbnails"), sub=L("[arquivo de objetos]", "[object store]"), **STO)),
        "notif": (3, 3, 1, dict(title=L("Notificações", "Notifications"), sub=L("[processo existente]", "[existing process]"), **dict(PRO, fill="#F2F3F5", stroke="#B8BEC6"))),
        "llm": (4, 0, 1, dict(title=L("Modelo de linguagem", "Language model"), sub=L("[processo]", "[process]"), **PRO)),
        "app": (4, 3, 3, dict(title=L("Aplicação Altice", "Altice app"), sub=L("[processo existente]", "[existing process]"), **dict(PRO, fill="#F2F3F5", stroke="#B8BEC6"))),
        "fam": (4, 6, 1, dict(title=L("Família", "Family"), sub=L("[entidade externa]", "[external entity]"), **ENT)),
    }, min_row=64)
    for k in ("tpl", "pg", "store"):                     # a data store: two parallel lines, open at the sides
        x0, y0, x1, y1 = g.r[k]
        for yy in (y0, y1):
            cv.o.append(f'<line x1="{x0}" y1="{yy:.1f}" x2="{x1}" y2="{yy:.1f}" stroke="{BODY}" stroke-width="1.6"/>')
    B, S = BLUE, 11.5
    g.v("cams", "agent", L("vídeo, rede da casa", "video, home network"), lw=110)
    g.v2("agent", "tpl", L("guarda", "stores"), L("compara", "compares"), lw=90)
    g.h2("agent", "broker", L("F1 regiões e rótulos", "F1 regions and labels"), L("F2 pedidos, vídeo do rosto", "F2 requests, face video"), color=B, lcolor=B)
    g.v("broker", "vision", L("regiões", "regions"), lw=110)
    g.h("vision", "svc", L("caixas e vetores", "boxes and vectors"))
    g.h("svc", "broker", L("pedidos às casas, fotografias a analisar", "requests to homes, photos to analyse"), below=True)
    g.h("router", "plat", L("F3 telemóveis no Wi-Fi", "F3 phones on the Wi-Fi"), color=B, lcolor=B)
    g.h2("door", "plat", L("F4 porta", "F4 door"), L("F5 comandos", "F5 commands"), color=B, lcolor=B)
    g.h2("plat", "svc", L("eventos: porta, Wi-Fi", "events: door, Wi-Fi"), L("chamadas MCP", "MCP calls"))
    g.h2("svc", "pg", L("grava", "writes"), L("lê, compara", "reads, matches"))
    g.h2("judge", "svc", L("veredicto", "verdict"), L("clipe de 2 a 3 s", "2 to 3 s clip"))
    g.h("svc", "store", L("miniaturas", "thumbnails"))
    g.h("svc", "notif", L("avisos", "alerts"))
    g.h2("svc", "llm", L("F6 texto", "F6 text"), L("F7 regra, resposta", "F7 rule, answer"), color=B, lcolor=B)
    g.h("notif", "app", L("F9 avisos", "F9 alerts"), color=B, lcolor=B)
    r4 = g.ys[4] + g.hs[4] / 2
    r5 = g.ys[5] + g.hs[5] / 2
    g.h("app", "svc", L("F8 frases, perguntas, fotografias, vídeo do rosto, “Sim”", "F8 sentences, questions, photos, face video, “Yes”"),
        color=B, lcolor=B, at=r4)
    g.h("svc", "app", L("F10 respostas, miniaturas", "F10 answers, thumbnails"), color=B, lcolor=B, at=r5)
    g.v2("app", "fam", L("mostra", "shows"), L("usa", "uses"), lw=100)

    def bounds(b):
        def box(keys, title, fill):
            x0 = min(g.r[k][0] for k in keys) - 12
            y0 = min(g.r[k][1] for k in keys) - 44
            x1 = max(g.r[k][2] for k in keys) + 12
            y1 = max(g.r[k][3] for k in keys) + 18
            b.rect(x0, y0, x1 - x0, y1 - y0, fill=fill, stroke=WARN, rx=14, sw=1.6, dash="7 6")
            b.text(x0 + 14, y0 + 26, title, 13, True, WARN, max_w=x1 - x0 - 28)
        box(["cams", "agent", "tpl", "router", "door"], L("Fronteira: casa", "Boundary: home"), HOME_BG)
        box(["vision", "broker", "judge", "plat", "svc", "pg", "store", "notif"], L("Fronteira: Altice", "Boundary: Altice"), ALTICE_BG)
        box(["llm"], L("Fronteira: fornecedor do modelo*", "Boundary: model provider*"), EXT_BG)
        box(["app", "fam"], L("Fronteira: telemóvel", "Boundary: phone"), PHONE_BG)
    bands_under(cv, bounds)
    y = max(r[3] for r in g.r.values()) + 46
    y = cv.para(40, y, L("* Só existe se o modelo de linguagem não for alojado pela Altice. Azul: fluxos que atravessam uma fronteira de "
                         "confiança, descritos na tabela.",
                         "* Only if the language model is not hosted by Altice. Blue: flows that cross a trust boundary, described "
                         "in the table."), W - 80, 12.5, fill=MUTED) + 8
    rows = [
        ("F1", L("agente da casa → mediador (casa → Altice)", "home agent → broker (home → Altice)"),
         L("A região que mudou (no máximo 640 × 640, cerca de 1 por segundo com movimento) ou a pedida numa verificação; raramente, "
           "2 a 3 s da região para o juiz; os rótulos dos rostos (“Filipe”, “rosto desconhecido”) com as caixas. Nunca vídeo contínuo "
           "nem padrões faciais",
           "The changed region (at most 640 × 640, about 1 a second during motion) or the one asked for in a check; rarely, 2 to 3 s "
           "of the region for the judge; the face labels (“Filipe”, “unknown face”) with their boxes. Never continuous video or face "
           "templates"),
         L("mTLS, um certificado por casa", "mTLS, one certificate per home")),
        ("F2", L("mediador → agente da casa (Altice → casa)", "broker → home agent (Altice → home)"),
         L("Pedidos de verificação ativa e de atualização; o vídeo do rosto no registo de uma pessoa, reencaminhado sem ficar guardado; "
           "máscaras; ordens para apagar padrões",
           "Active-check and refresh requests; the face video when a person is registered, relayed without being stored; masks; "
           "orders to delete templates"), "mTLS"),
        ("F3", L("_router_ → plataforma (casa → Altice)", "router → platform (home → Altice)"),
         L("Que telemóveis da Família estão no Wi-Fi e quando entram ou saem (ferramenta MCP proposta)",
           "Which Family phones are on the Wi-Fi, and when they join or leave (proposed MCP tool)"),
         L("O canal de gestão do _router_ da Altice (a confirmar)", "Altice’s router management channel (to confirm)")),
        ("F4", L("sensor da porta → plataforma (casa → Altice)", "door sensor → platform (home → Altice)"),
         L("Porta aberta ou fechada, como hoje", "Door open or closed, as today"), L("O canal da central (LTE), como hoje", "The hub’s channel (LTE), as today")),
        ("F5", L("plataforma → atuadores (Altice → casa)", "platform → actuators (Altice → home)"),
         L("Comandos depois de um “Sim”: luz, tomada, sirene", "Commands after a “Yes”: light, plug, siren"), L("Como hoje", "As today")),
        ("F6", L("serviço → modelo de linguagem", "service → language model"),
         L("Só texto: a frase ou a pergunta, os nomes dos objetos, lugares e dispositivos, linhas da memória. Os clipes do juiz "
           "ficam na Altice",
           "Text only: the sentence or question, the names of things, places and devices, memory lines. The judge’s clips stay "
           "at Altice"),
         L("TLS; contrato sem treino com os dados, DPA e processamento na UE", "TLS; a contract with no training on the data, a DPA and EU processing")),
        ("F7", L("modelo de linguagem → serviço", "language model → service"), L("A regra estruturada, a resposta ou o veredicto",
                                                                              "The structured rule, the answer or the verdict"), "TLS"),
        ("F8", L("aplicação → serviço (telemóvel → Altice)", "app → service (phone → Altice)"),
         L("Frases, perguntas, fotografias de objetos, o vídeo do rosto, “Sim”", "Sentences, questions, photos of things, the face video, “Yes”"),
         L("HTTPS, com a sessão da aplicação Altice", "HTTPS, with the Altice app’s session")),
        ("F9", L("notificações → aplicação (Altice → telemóvel)", "notifications → app (Altice → phone)"),
         L("Avisos: título, mensagem, cartões de ação, ligação à miniatura", "Alerts: title, message, action cards, link to the thumbnail"),
         L("O serviço de notificações da aplicação", "The app’s notification service")),
        ("F10", L("serviço → aplicação (Altice → telemóvel)", "service → app (Altice → phone)"),
         L("Respostas e miniaturas, por ligações assinadas de curta duração", "Answers and thumbnails, through short-lived signed links"), "HTTPS"),
    ]
    y = table(cv, 40, y + 10, [70, 380, 1100, W - 80 - 1550], [L("Fluxo", "Flow"), L("De → para", "From → to"), L("O que leva", "What it carries"),
                                                     L("Proteção", "Protection")], rows)
    y = cv.para(40, y + 30, L("Nunca atravessam a fronteira da casa: o vídeo contínuo e os padrões faciais. Método: diagrama de fluxo de dados com fronteiras "
                              "de confiança, como no Microsoft SDL e no OWASP.",
                              "Never cross the home boundary: continuous video and face templates. Method: a data-flow diagram with trust boundaries, "
                              "as in the Microsoft SDL and OWASP threat modelling."), W - 80, 12.5, fill=MUTED)
    cv.save("dfd-fronteiras", round(y))


# ====================================================================== entity-relationship
def er_table(cv, x, y, w, name, fields, note=None):
    """A table card: the name in a header band, then one line per field (key, name, type). Returns its height."""
    hh, rh = 32, 21
    h = hh + len(fields) * rh + 10 + (18 if note else 0)
    cv.rect(x, y, w, h, fill="#FFFFFF", stroke="#9DB7D5", rx=8, sw=1.3)
    cv.rect(x, y, w, hh, fill="#E6F0FA", stroke=None, rx=8)
    cv.rect(x, y + hh - 8, w, 8, fill="#E6F0FA", stroke=None, rx=0)
    cv.text(x + 12, y + 21, f"`{name}`", 15, True, INK)
    for i, (key, fname, ftype) in enumerate(fields):
        yy = y + hh + 16 + i * rh
        if key:
            cv.text(x + 10, yy, key, 9.5, True, BLUE)
        tw = width(ftype, 11)
        cv.text(x + 38, yy, f"`{fname}`", 12.5, False, INK, max_w=w - 48 - tw - 12)
        cv.text(x + w - 10, yy, ftype, 11, False, MUTED, anchor="end")
    if note:
        cv.text(x + 12, y + h - 10, note, 10.5, False, FAINT, max_w=w - 24)
    return h


def er_line(cv, x0, y0, x1, y1, a="1", b="N"):
    """A relationship: a plain straight line with the cardinality at each end."""
    assert x0 == x1 or y0 == y1
    cv.o.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{BODY}" stroke-width="1.4"/>')
    if x0 == x1:
        s = 1 if y1 > y0 else -1
        cv.text(x0 + 6, y0 + s * 14 + 4, a, 11, True, BLUE)
        cv.text(x1 + 6, y1 - s * 8 + 4, b, 11, True, BLUE)
    else:
        s = 1 if x1 > x0 else -1
        cv.text(x0 + s * 8, y0 - 6, a, 11, True, BLUE, anchor="start" if s > 0 else "end")
        cv.text(x1 - s * 8, y1 - 6, b, 11, True, BLUE, anchor="end" if s > 0 else "start")


@view
def er_plataforma(lang):
    cw, gap = 262, 40
    xs = [40 + i * (cw + gap) for i in range(6)]
    W = xs[-1] + cw + 40
    cv = Canvas(W, lang, "Modelo de dados: plataforma" if lang == "pt" else "Data model: platform")
    L = cv.L
    FK = lambda t: "→ " + t
    T = {
        "customer": [("PK", "id", "uuid"), ("", "plan", "text"), ("", "created_at", "timestamptz")],
        "home": [("PK", "id", "uuid"), ("FK", "customer_id", FK("customer")), ("", "altice_home_id", "text"), ("", "name", "text")],
        "member": [("PK", "id", "uuid"), ("FK", "home_id", FK("home")), ("", "name", "text"), ("", "role", L("família, visita…", "family, guest…")),
                   ("", "recognition_on", "bool"), ("", "consent_at", "timestamptz"), ("", "consent_text", L("versão", "version"))],
        "phone": [("PK", "id", "uuid"), ("FK", "member_id", FK("member")), ("", "router_device", "text"), ("", "label", "text")],
        "camera": [("PK", "id", "uuid"), ("FK", "home_id", FK("home")), ("", "altice_device_id", "text"), ("", "place", L("“Sala 1”", "“Living room 1”")),
                   ("", "masks", "jsonb")],
        "person_seen": [("PK", "id", "uuid"), ("FK", "camera_id", FK("camera")), ("", "ts", "timestamptz"),
                        ("", "label", L("membro, desconhecido…", "member, unknown…")), ("FK", "member_id", FK("member"))],
        "thing": [("PK", "id", "uuid"), ("FK", "home_id", FK("home")), ("", "name", "text"), ("", "query", L("palavra do detetor", "detector word")),
                  ("", "photo_key", "text"), ("FK", "usual_camera", FK("camera"))],
        "fingerprint": [("PK", "id", "uuid"), ("FK", "thing_id", FK("thing")), ("", "view_no", "1–8"), ("", "embedding", "vector(384)"),
                        ("", "model", "text")],
        "sighting": [("PK", "id", "uuid"), ("FK", "thing_id", FK("thing")), ("FK", "camera_id", FK("camera")), ("", "ts", "timestamptz"),
                     ("", "surface", L("secretária…", "desk…")), ("", "state", L("pousado, na mão…", "placed, in hand…")),
                     ("FK", "member_id", FK("member")), ("", "match", "real"), ("", "thumb_key", "text")],
        "rule": [("PK", "id", "uuid"), ("FK", "home_id", FK("home")), ("", "sentence", "text"), ("", "compiled", "jsonb"),
                 ("FK", "owner_id", FK("member")), ("", "active", "bool"), ("", "siren", L("perguntar, logo", "ask, at once")),
                 ("", "scenario_id", "text")],
        "alert": [("PK", "id", "uuid"), ("FK", "rule_id", FK("rule")), ("", "ts", "timestamptz"), ("", "level", "text"), ("", "title", "text"),
                  ("", "message", "text"), ("", "thumb_key", "text"), ("", "actions", "jsonb"), ("", "answer", "text"),
                  ("FK", "answered_by", FK("member"))],
        "action_log": [("PK", "id", "uuid"), ("FK", "alert_id", FK("alert")), ("", "mcp_tool", "text"), ("", "args", "jsonb"),
                       ("", "result", "text"), ("", "ts", "timestamptz")],
        "presence": [("PK", "home_id", FK("home")), ("", "state", L("OCUPADA…", "OCCUPIED…")), ("", "since", "timestamptz"),
                     ("", "members_home", "jsonb"), ("", "reason", "text")],
        "presence_change": [("PK", "id", "uuid"), ("FK", "home_id", FK("presence")), ("", "ts", "timestamptz"), ("", "from_state", "text"),
                            ("", "to_state", "text"), ("", "reason", "text")],
        "llm_call": [("PK", "id", "uuid"), ("FK", "home_id", FK("home")), ("", "purpose", "text"), ("", "model", "text"),
                     ("", "tokens", "int"), ("", "cost_eur", "real")],
    }
    hgt = lambda n: 32 + len(T[n]) * 21 + 10
    y0 = 30
    cx = lambda c: xs[c] + cw / 2
    hc = 2
    er_table(cv, xs[0], y0, cw, "customer", T["customer"])
    er_table(cv, xs[hc], y0, cw, "home", T["home"])
    er_line(cv, xs[0] + cw, y0 + 60, xs[hc], y0 + 60)
    row1 = {"member": 0, "camera": 1, "thing": 2, "sighting": 3, "rule": 4, "presence": 5}
    y1 = y0 + max(hgt("customer"), hgt("home")) + 90
    bus = y1 - 44
    for n, c in row1.items():
        er_table(cv, xs[c], y1, cw, n, T[n])
    hb = y0 + hgt("home")
    cv.o.append(f'<line x1="{cx(hc):.1f}" y1="{hb}" x2="{cx(hc):.1f}" y2="{bus}" stroke="{BODY}" stroke-width="1.4"/>')
    cv.text(cx(hc) + 6, hb + 16, "1", 11, True, BLUE)
    cv.o.append(f'<line x1="{cx(0):.1f}" y1="{bus}" x2="{cx(5):.1f}" y2="{bus}" stroke="{BODY}" stroke-width="1.4"/>')
    for n in ("member", "camera", "thing", "rule", "presence"):
        c = row1[n]
        cv.o.append(f'<line x1="{cx(c):.1f}" y1="{bus}" x2="{cx(c):.1f}" y2="{y1}" stroke="{BODY}" stroke-width="1.4"/>')
        cv.text(cx(c) + 6, y1 - 8, "1" if n == "presence" else "N", 11, True, BLUE)
    er_line(cv, xs[2] + cw, y1 + 60, xs[3], y1 + 60)
    y2 = y1 + max(hgt(n) for n in row1) + 60
    row2 = {"phone": 0, "person_seen": 1, "fingerprint": 2, "llm_call": 3, "alert": 4, "presence_change": 5}
    for n, c in row2.items():
        er_table(cv, xs[c], y2, cw, n, T[n])
    for parent, child, c in (("member", "phone", 0), ("camera", "person_seen", 1), ("thing", "fingerprint", 2), ("rule", "alert", 4),
                             ("presence", "presence_change", 5)):
        er_line(cv, cx(c), y1 + hgt(parent), cx(c), y2)
    y3 = y2 + max(hgt(n) for n in row2) + 60
    er_table(cv, xs[4], y3, cw, "action_log", T["action_log"])
    er_line(cv, cx(4), y2 + hgt("alert"), cx(4), y3)
    nx = xs[0]
    ny = y3 + 10
    notes = [L("Uma base PostgreSQL com _pgvector_; cada linha pertence a um cliente, com segurança ao nível da linha.",
               "One PostgreSQL database with pgvector; every row belongs to one customer, with row-level security."),
             L("Nenhuma tabela guarda dados biométricos: `member` tem o nome, o papel e o registo do consentimento; os padrões faciais "
               "só existem em casa.",
               "No table holds biometric data: `member` has the name, the role and the consent record; face templates exist only in "
               "the home."),
             L("Retenção proposta: observações, pessoas vistas e miniaturas, 30 dias; avisos e ações, 90 dias.",
               "Proposed retention: sightings, people seen and thumbnails, 30 days; alerts and actions, 90 days."),
             L("Linhas: 1 e N indicam quantos registos de cada lado. As chaves estrangeiras sem linha estão escritas no campo (→ tabela).",
               "Lines: 1 and N say how many records on each side. Foreign keys without a line are written in the field (→ table).")]
    yy = ny + 20
    for t in notes:
        yy = cv.para(nx, yy, t, xs[4] - gap - nx - 20, 12.5, fill=BODY) + 6
    cv.save("er-plataforma", round(max(yy, y3 + hgt("action_log")) + 24))


@view
def er_casa(lang):
    cw, gap = 290, 50
    xs = [40 + i * (cw + gap) for i in range(4)]
    W = xs[-1] + cw + 40
    cv = Canvas(W, lang, "Modelo de dados: casa" if lang == "pt" else "Data model: home")
    L = cv.L
    T = {
        "person": [("PK", "id", L("= `member.id`", "= `member.id`")), ("", "label", L("nome mostrado", "name shown"))],
        "face_template": [("PK", "id", "integer"), ("FK", "person_id", "→ person"), ("", "view_no", "1–8"),
                          ("", "feature", L("128 números", "128 numbers")), ("", "model", "SFace"), ("", "created_at", "timestamp")],
        "camera": [("PK", "id", "text"), ("", "rtsp_url", L("só na rede local", "local network only")), ("", "masks", "json")],
        "outbox": [("PK", "id", "integer"), ("", "ts", "timestamp"), ("", "kind", L("evento, rótulo", "event, label")), ("", "payload", "json"),
                   ("", "sent", "bool")],
        "setting": [("PK", "key", "text"), ("", "value", "text")],
    }
    hgt = lambda n: 32 + len(T[n]) * 21 + 10
    y0 = 92
    cv.band(20, 20, W - 40, 0, "", None)          # placeholder removed below
    cv.o.pop()
    for n, c in (("person", 0), ("camera", 1), ("outbox", 2), ("setting", 3)):
        er_table(cv, xs[c], y0, cw, n, T[n])
    y1 = y0 + hgt("person") + 60
    er_table(cv, xs[0], y1, cw, "face_template", T["face_template"])
    er_line(cv, xs[0] + cw / 2, y0 + hgt("person"), xs[0] + cw / 2, y1)
    bot = max(y1 + hgt("face_template"), y0 + hgt("outbox"))
    notes = [L("Uma base _SQLite_ cifrada no _router_, gerida pelo agente da casa. Não guarda imagens.",
               "One encrypted SQLite database on the router, kept by the home agent. It holds no images."),
             L("`face_template`: até 8 padrões por pessoa registada com consentimento; nunca saem de casa e são apagados quando a "
               "pessoa retira o consentimento.",
               "`face_template`: up to 8 templates per person registered with consent; they never leave the home and are deleted "
               "when the person withdraws consent."),
             L("`outbox`: guarda eventos e rótulos enquanto não há internet, nunca imagens; `setting` guarda, por exemplo, o limiar 0,363.",
               "`outbox`: keeps events and labels while offline, never images; `setting` holds, for example, the 0.363 threshold.")]
    yy = y1 + 20
    for t in notes:
        yy = cv.para(xs[1], yy, t, W - xs[1] - 40, 12.5) + 6

    def zone(b):
        b.band(20, 20, W - 40, max(bot, yy) + 4 - 20, L("_Router_ da casa · agente da casa", "Home router · home agent"), None, fill=HOME_BG)
    bands_under(cv, zone)
    cv.save("er-casa", round(max(bot, yy) + 30))


# ====================================================================== user flow
@view
def fluxo_app(lang):
    L = (lambda a, b: a if lang == "pt" else b)
    lanew, cw, gap = 180, 224, 46
    xs = [40] + [40 + lanew + gap + i * (cw + gap) for i in range(6)]
    ws = [lanew] + [cw] * 6
    W = xs[-1] + cw + 40
    cv = Canvas(W, lang, "Fluxos na aplicação" if lang == "pt" else "Flows in the app")
    g = Grid(cv, xs, ws, 30, row_gap=34)
    LANE = dict(fill="#EEF1F6", stroke=None)
    SCR = dict(stroke="#C9D2E3", sw=1.2)
    lanes = [
        (L("Adicionar um objeto", "Add a thing"), [
            (L("Separador _Things_", "Things tab"), L("(+) “Adicionar objeto”", "(+) “Add thing”")),
            (L("A procurar nas câmaras", "Looking through the cameras"), L("Propostas do que as câmaras veem, ou um nome escrito",
                                                                        "Proposals of what the cameras see, or a typed name")),
            (L("Fotografias ou câmara", "Photos or camera"), L("6 a 8 fotografias com o telemóvel, ou mostrá-lo a uma câmara (8 vistas diferentes)",
                                                             "6 to 8 photos with the phone, or show it to a camera (8 different views)")),
            (L("Novo objeto", "New thing"), L("As vistas aprendidas e o nome; “Guardar”", "The learnt views and the name; “Save”")),
            (L("Criar um cenário?", "Create a scenario?"), L("Propõe uma regra para o objeto: “avisa-me se sair sem ele”",
                                                            "Offers a rule for the thing: “tell me if I leave without it”")),
        ]),
        (L("Adicionar uma pessoa", "Add a person"), [
            (L("Separador _Things_", "Things tab"), L("(+) “Uma pessoa”", "(+) “A person”")),
            (L("Quem é?", "Who is it?"), L("Família ou Visita; o nome", "Family or Guest; the name")),
            (L("Consentimento", "Consent"), L("A própria pessoa aceita ser reconhecida; nada vem pré-selecionado",
                                             "The person themselves agrees to be recognised; nothing is pre-selected")),
            (L("Vídeo do rosto", "Face video"), L("Um vídeo curto com o telemóvel; em casa, _YuNet_ e _SFace_ fazem até 8 padrões",
                                                 "A short video with the phone; in the home, YuNet and SFace make up to 8 templates")),
            (L("Pessoa adicionada", "Person added"), L("Os padrões ficam só em casa; a aplicação mostra o nome",
                                                      "The templates stay in the home; the app shows the name")),
            (L("Sugestão", "Suggestion"), L("“Tocar o alarme quando entrar alguém que não seja da Família?”",
                                           "“Sound the alarm when someone who isn’t Family comes in?”")),
        ]),
        (L("Cenário a partir de uma frase", "A scenario from a sentence"), [
            (L("Botão do assistente", "Assistant button"), L("Em qualquer separador", "On any tab")),
            (L("A frase", "The sentence"), L("“Avisa-me se sair de casa sem o livro”", "“Tell me if I leave home without my book”")),
            (L("A regra em palavras simples", "The rule in plain words"), L("O que observa, quando avisa, o que faz e a escolha para a sirene",
                                                                           "What it watches, when it alerts, what it does, and the siren choice")),
            (L("“Guardar”", "“Save”"), L("A regra passa a correr na Altice, a cada evento", "The rule now runs at Altice, on every event")),
            (L("Cenários", "Scenarios"), L("Aparece ao lado dos cenários que já existem", "Appears next to the existing scenarios")),
        ]),
        (L("Cenário sugerido", "A suggested scenario"), [
            (L("Sugestão", "Suggestion"), L("Depois de adicionar uma pessoa, ou pelo perfil da casa (criança, cão, gato)",
                                           "After adding a person, or from the home’s profile (child, dog, cat)")),
            (L("A regra proposta", "The proposed rule"), L("Em palavras simples, já compilada", "In plain words, already compiled")),
            (L("Um toque", "One tap"), L("“Ativar”", "“Turn on”")),
            (L("Cenários", "Scenarios"), L("Aparece com os outros cenários", "Appears with the other scenarios")),
        ]),
        (L("Aviso com ações", "An alert with actions"), [
            (L("Notificação", "Notification"), L("Pelo serviço de notificações da aplicação", "Through the app’s notification service")),
            (L("Aviso", "Alert"), L("Título, mensagem, miniatura e o que o motivou; a faixa da porta, quando é o caso",
                                   "Title, message, thumbnail and what caused it; the door banner, when relevant")),
            (L("Cartões de ação", "Action cards"), L("Um “Sim” por ação: desligar as luzes, desligar o ar condicionado, tocar a sirene",
                                                    "One “Yes” per action: turn off the lights, turn off the air conditioner, sound the siren")),
            (L("Ação feita", "Action done"), L("O “Sim” vira uma chamada MCP; o aviso mostra o resultado",
                                              "The “Yes” becomes an MCP call; the alert shows the result")),
            (L("Pessoa desconhecida", "Unknown person"), L("Também “Ligar à polícia (112)”: abre a chamada e quem liga é a pessoa",
                                                          "Also “Call the police (112)”: it opens the call, and the person places it")),
        ]),
    ]
    cells = {}
    for r, (lane, steps) in enumerate(lanes):
        cells[f"l{r}"] = (0, r, 1, dict(title=lane, **LANE))
        for i, (t, b) in enumerate(steps):
            extra = dict(dash="5 4") if (r == 4 and i == 4) else {}
            cells[f"s{r}_{i}"] = (i + 1, r, 1, dict(title=t, body=[b], **SCR, **extra))
    g.place(cells)
    for r, (lane, steps) in enumerate(lanes):
        for i in range(len(steps) - 1):
            if r == 4 and i == 3:
                continue                                  # the unknown-person card is a variant, not a next step
            g.h(f"s{r}_{i}", f"s{r}_{i + 1}")
    end = max(rr[3] for rr in g.r.values())
    end = cv.para(40, end + 34, L("Cada caixa é um ecrã ou um passo na aplicação Altice, com o separador _Things_ e o assistente. Tracejado: "
                                  "uma variante do passo anterior.",
                                  "Each box is a screen or a step in the Altice app, with the Things tab and the assistant. Dashed: a "
                                  "variant of the previous step."), W - 80, 12.5, fill=MUTED)
    cv.save("fluxo-app", round(end))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Build the ThingTracker architecture views.")
    ap.add_argument("--only", nargs="*", help="view names: " + ", ".join(VIEWS))
    ap.add_argument("--lang", choices=["pt", "en", "both"], default="both")
    a = ap.parse_args()
    for name in a.only or VIEWS:
        for lg in (["pt", "en"] if a.lang == "both" else [a.lang]):
            VIEWS[name](lg)
