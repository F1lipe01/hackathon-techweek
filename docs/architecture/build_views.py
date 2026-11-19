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
                         PHONE_BG, WARN, Canvas, sequence)

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
                   L("Seguimento das caixas entre análises", "Tracking of boxes between analyses"),
                   L("Chama o modelo de linguagem só para frases, perguntas e casos duvidosos",
                     "Calls the language model only for sentences, questions and unclear cases")]),
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
                   L("_DINOv2_: compara cada candidato com as 8 vistas do objeto; semelhança ≥ 0,62 é o seu",
                     "DINOv2: compares each candidate with the thing’s 8 views; similarity ≥ 0.62 means yours"),
                   L("Sem estado: leem as filas e devolvem deteções", "Stateless: read the queues, return detections")]),
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
        dict(title=L("Modelo de linguagem", "Language model"), sub=L("servidores GPU, atrás de uma fila", "GPU servers, behind a queue"),
             body=[L("Modelo _open-weight_ alojado pela Altice, ou um fornecedor sob contrato na UE",
                     "An open-weight model hosted by Altice, or a provider under contract in the EU"),
                   L("Recebe texto; raramente, o recorte de um objeto num caso duvidoso (decisão em aberto)",
                     "Receives text; rarely, one crop of a thing in an unclear case (open decision)")]),
    ])
    bottom = max(hub[1], svc[-1][1], vis[-1][1], lba[-1][1])
    num_y = lba[-1][1] + 18
    stack(cv, D, num_y, CW, [dict(
        title=L("A 500 000 casas (estimativas)", "At 500,000 homes (estimates)"), fill="#F7F9FD", stroke="#C9D2E3",
        h=max(bottom, hub[1]) - num_y if max(bottom, hub[1]) - num_y > 0 else None,
        body=[L("Visão: ≈ 0,49 € por casa e por mês com 1 câmara; 1 427 placas L4 (documento 17)",
                "Vision: ≈ €0.49 per home a month with 1 camera; 1,427 L4 cards (document 17)"),
              L("Modelo de linguagem: ≈ 0,43 € por casa e por mês (documento 16)",
                "Language model: ≈ €0.43 per home a month (document 16)"),
              L("Pressupostos: 2 h de movimento por dia, 1 imagem por segundo, GPU a 25 % do seu pico",
                "Assumptions: 2 h of motion a day, 1 frame a second, GPUs at 25 % of their peak")])])
    band_bottom = max(bottom, hub[1]) + 26
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
    cv.label(gx0 + 10, ya - 8, L("1 ligação de saída mTLS: regiões e rótulos de rostos; nunca vídeo",
                                 "1 outbound mTLS connection: regions and face labels; never video"), lw, bold=True)
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
        ("m", 3, 4, L("livro visto em 3 de 3 imagens, semelhança 0,70 ≥ 0,62, miniatura", "book seen in 3 of 3 frames, similarity 0.70 ≥ 0.62, thumbnail")),
        ("n", 4, 4, L("Regra “avisa-me se sair sem o livro”: cumprida, porque o livro foi visto em pelo menos 2 das 3 imagens",
                      "Rule “tell me if I leave without my book”: met, because the book was seen in at least 2 of the 3 frames")),
        ("m", 4, 5, L("aviso: “O livro ficou em casa”, com a miniatura e “na secretária, às 18h02”",
                      "alert: “Your book stayed at home”, with the thumbnail and “on the desk, at 18:02”")),
        ("g", L("Se o livro não aparecer em pelo menos 2 das 3 imagens, o resultado é “incerto”: não há aviso, só um registo. "
                "Uma chegada (a porta abre e fecha e um telemóvel entra no Wi-Fi) não inicia a verificação.",
                "If the book is not seen in at least 2 of the 3 frames, the result is “unsure”: no alert, only a log entry. An "
                "arrival (the door opens and closes and a phone joins the Wi-Fi) does not start the check.")),
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


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Build the ThingTracker architecture views.")
    ap.add_argument("--only", nargs="*", help="view names: " + ", ".join(VIEWS))
    ap.add_argument("--lang", choices=["pt", "en", "both"], default="both")
    a = ap.parse_args()
    for name in a.only or VIEWS:
        for lg in (["pt", "en"] if a.lang == "both" else [a.lang]):
            VIEWS[name](lg)
