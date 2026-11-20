#!/usr/bin/env python3
"""Build the architecture views of docs/14-architecture.md (English) and docs/pt/14-arquitetura.md (Portuguese).

    python3 docs/architecture/build_views.py                 # every view, in both languages
    python3 docs/architecture/build_views.py --only implantacao presenca-estados --lang pt

Each view is written as <name>.svg / <name>.png (Portuguese, for the deck) and <name>.en.svg / <name>.en.png.
The drawing rules live in diagram_kit.py: text measured and wrapped to its box, straight one-way arrows.
The design drawn here is the FINAL design of 20 Nov 2026 (fully local: all perception and inference on the home device;
the Altice platform as a text-only control and data plane); docs/14 says what the prototype does today.
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
    HB, AB, PB = (20, 960), (1040, 1730), (1800, 2020)
    H1X, H1W = HB[0] + 24, 300
    H2X = H1X + H1W + 90
    H2W = HB[1] - 24 - H2X
    AX, AW = AB[0] + 24, 260
    BX = AX + AW + 100
    BW = AB[1] - 24 - BX
    PX, PW = PB[0] + 20, PB[1] - PB[0] - 40
    Y0 = 108

    # ---- the home: the home device does all the perception and inference
    dev = stack(cv, H2X, Y0, H2W, [dict(
        title=L("Equipamento da casa", "Home device"),
        sub=L("O _router_, se tiver NPU, ou uma caixa dedicada: _Raspberry Pi 5_ com acelerador de IA, ou _Jetson Orin Nano Super_",
              "The router, if it has an NPU, or a dedicated box: a Raspberry Pi 5 with an AI accelerator, or a Jetson Orin Nano Super"),
        stroke=BLUE, sw=2, sub_bold=False, sub_color=MUTED,
        body=[L("Recebe o vídeo das câmaras na rede da casa", "Takes in the cameras’ video on the home network"),
              L("Filtro de movimento: imagem cinzenta de 160 × 90, a cada 0,5 s; só analisa quando há movimento ou um pedido",
                "Motion gate: a 160 × 90 grey picture, every 0.5 s; analyses only on motion or on request"),
              L("Visão: deteção e reidentificação com a assinatura visual (≥ 0,62). _OWLv2_ + _DINOv2_ no protótipo; detetores mais leves, "
                "como o _YOLOv8n_, em equipamentos pequenos",
                "Vision: detection and re-identification against the fingerprint (≥ 0.62). OWLv2 + DINOv2 in the prototype; lighter "
                "detectors, such as YOLOv8n, on small devices"),
              L("Rostos (opcional, com consentimento): _YuNet_ encontra, _SFace_ compara; os padrões ficam no equipamento",
                "Faces (opt-in, with consent): YuNet finds, SFace compares; the templates stay on the device"),
              L("Memória local: onde e quando cada objeto foi visto", "Local memory: where and when each thing was seen"),
              L("Motor de presença e motor de regras: o motor de regras decide", "Presence engine and rules engine: the rules engine decides"),
              L("Modelo de linguagem (_Qwen3-1.7B_ no protótipo): frase em regra, pergunta em resposta; nunca decide",
                "Language model (Qwen3-1.7B in the prototype): sentence into rule, question into answer; it never decides"),
              L("Constrói a assinatura visual a partir das fotografias de registo", "Builds the fingerprint from the registration photos"),
              L("Imagens, vídeo, assinaturas visuais e padrões faciais nunca saem daqui", "Images, video, fingerprints and face templates never leave it")])])[0]
    cam = stack(cv, H1X, Y0, H1W, [dict(
        title=L("Câmaras do kit", "Kit cameras"),
        body=[L("_Tuya SC034-WNV3_ · H.265 · 2304 × 1296 · 20 fps", "Tuya SC034-WNV3 · H.265 · 2304 × 1296 · 20 fps"),
              L("Vídeo por RTSP só na rede da casa", "Video over RTSP on the home network only")])])[0]
    hub_y = dev[1] + 24
    hub = stack(cv, H2X, hub_y, H2W, [
        dict(title=L("Central de segurança e sensor da porta", "Security hub and door contact sensor"),
             body=[L("_MS-WES1AS_ (LTE) e _MS-D3D_; comunicam com a plataforma Altice, como hoje",
                     "MS-WES1AS (LTE) and MS-D3D; they report to the Altice platform, as today")]),
        dict(title=L("_Router_ Altice · Wi-Fi", "Altice router · Wi-Fi"),
             body=[L("Sabe que telemóveis da família estão ligados", "Knows which family phones are connected")])])

    # ---- Altice: control and data plane, text only
    relay = stack(cv, AX, Y0, AW, [dict(
        title=L("Retransmissão e mediador", "Relay and connection broker"), sub=L("MQTT sobre mTLS", "MQTT over mTLS"),
        body=[L("Uma ligação de saída por casa, atrás de um balanceador", "One outbound connection per home, behind a load balancer"),
              L("Leva a aplicação até casa quando a família está fora", "Lets the app reach the home when the family is away"),
              L("As fotografias de registo passam cifradas de ponta a ponta: a Altice não as lê",
                "Registration photos pass encrypted end to end: Altice cannot read them")])])[0]
    plat_y = hub[0][0]
    plat = stack(cv, AX, plat_y, AW, [dict(
        title=L("Plataforma _Connected Home_ (existente)", "Connected Home platform (existing)"), fill="#F7F7F7",
        h=hub[-1][1] - plat_y,
        body=[L("Dispositivos, cenários e segurança; servidor MCP com 18 ferramentas", "Devices, scenarios and security; MCP server with 18 tools"),
              L("Pedidos à Altice: eventos do Wi-Fi e a ferramenta de presença no Wi-Fi",
                "Asked of Altice: Wi-Fi events and the Wi-Fi presence tool")])])[0]
    svc_item = dict(title=L("Serviço _ThingTracker_", "ThingTracker service"), stroke=BLUE, sw=2, sub=L("só texto", "text only"),
                    body=[L("Contas, identidade e permissões da família", "Accounts, identity and family permissions"),
                          L("Registo de eventos em texto (“livro, secretária, 18h02”)", "Event log as structured text (“book, desk, 18:02”)"),
                          L("Notificações para a aplicação, pelo serviço que ela já usa", "Push notifications to the app, through the service it already uses"),
                          L("Um “Sim” vira uma ação pelo MCP", "A “Yes” becomes an action through the MCP")])
    svc = stack(cv, BX, Y0, BW, [
        dict(svc_item, h=max(cv.box_h(BW, svc_item["title"], svc_item["body"], sub=svc_item["sub"]), hub[-1][1] - Y0)),
        dict(title=L("PostgreSQL · metadados", "PostgreSQL · metadata"),
             body=[L("Objetos, pessoas (só nomes), donos e cenários: cópia de segurança, sincronização entre telemóveis e reposição se a "
                     "caixa for trocada",
                     "Things, people (names only), owners and scenarios: backup, sync across phones, and restore if the box is replaced")]),
    ])
    bottom = max(cam[1], hub[-1][1], plat[1], svc[-1][1])
    band_bottom = bottom + 26
    bands = Canvas(cv.w, lang, "")
    bands.band(HB[0], 20, HB[1] - HB[0], band_bottom - 20, L("Em casa", "In the home"),
               L("Toda a perceção e inferência", "All the perception and inference"), fill=HOME_BG)
    bands.band(AB[0], 20, AB[1] - AB[0], band_bottom - 20, L("Altice · só texto", "Altice · text only"),
               L("Contas, metadados, eventos, notificações, ações", "Accounts, metadata, events, push, actions"), fill=ALTICE_BG)
    bands.band(PB[0], 20, PB[1] - PB[0], band_bottom - 20, L("Telemóvel", "Phone"), None, fill=PHONE_BG)
    cv.o = bands.o + cv.o

    app = stack(cv, PX, Y0, PW, [dict(
        title=L("Aplicação Altice", "Altice app"), h=svc[-1][1] - Y0,
        body=[L("Separador _Things_ e assistente", "Things tab and assistant"),
              L("Avisos com cartões de ação", "Alerts with action cards"),
              L("Fotografias de registo: para o equipamento da casa, no Wi-Fi ou cifradas pela retransmissão",
                "Registration photos: to the home device, on the Wi-Fi or encrypted through the relay"),
              L("Vídeo em direto, como hoje, fora do _ThingTracker_", "Live video, as today, outside ThingTracker")])])[0]

    # ---- arrows across the boundaries (labels in the gaps)
    cv.arrow(H1X + H1W, mid_overlap(cam, dev), H2X, mid_overlap(cam, dev), BODY)
    cv.label(H1X + H1W + 8, mid_overlap(cam, dev) - 8, L("vídeo, só em casa", "video, home only"), 76, fill=BODY, size=11)
    gx0, gx1 = H2X + H2W, AX
    lw = gx1 - gx0 - 16
    ya = relay[0] + 40
    cv.arrow(gx0, ya, gx1, ya, BLUE, 2)
    cv.label(gx0 + 8, ya - 8, L("só texto: eventos, avisos", "text only: events, alerts"), lw, bold=True)
    yb = relay[1] - 30
    cv.arrow(gx1, yb, gx0, yb, BLUE, 2)
    cv.label(gx0 + 8, yb + 17, L("pedidos, comandos, fotografias cifradas", "requests, commands, encrypted photos"), lw, below=True)
    yd = mid_overlap(hub[0], plat)
    cv.arrow(gx0, yd, gx1, yd, BODY)
    cv.label(gx0 + 8, yd - 8, L("porta, como hoje", "door, as today"), lw, fill=BODY)
    yc = mid_overlap(hub[1], plat)
    cv.arrow(gx0, yc, gx1, yc, BODY)
    cv.label(gx0 + 8, yc - 8, L("telemóveis no Wi-Fi", "phones on the Wi-Fi"), lw, fill=BODY)
    ax0, ax1 = AX + AW, BX
    alw = ax1 - ax0 - 14
    y3 = relay[0] + 50
    cv.arrow(ax0, y3, ax1, y3, BODY)
    cv.label(ax0 + 7, y3 - 8, L("eventos, avisos", "events, alerts"), alw, fill=BODY, size=11)
    y3b = relay[1] - 40
    cv.arrow(ax1, y3b, ax0, y3b, BODY)
    cv.label(ax0 + 7, y3b + 16, L("pedidos da aplicação", "app requests"), alw, fill=BODY, size=11, below=True)
    y4 = plat[0] + 50
    cv.arrow(ax0, y4, ax1, y4, BODY)
    cv.label(ax0 + 7, y4 - 8, L("porta, Wi-Fi", "door, Wi-Fi"), alw, fill=BODY, size=11)
    y4b = plat[1] - 30
    cv.arrow(ax1, y4b, ax0, y4b, BODY)
    cv.label(ax0 + 7, y4b + 16, L("ações MCP após “Sim”", "MCP actions after “Yes”"), alw, fill=BODY, size=11, below=True)
    px0, px1 = BX + BW, PX
    y1 = Y0 + 60
    cv.arrow(px1, y1, px0, y1, BODY)
    cv.label(px0 + 8, y1 - 8, L("frases, perguntas, “Sim”", "sentences, questions, “Yes”"), px1 - px0 - 14, fill=BODY, size=11)
    y2 = svc[0][1] - 60
    cv.arrow(px0, y2, px1, y2, BODY)
    cv.label(px0 + 8, y2 - 8, L("respostas, avisos (_push_)", "answers, alerts (push)"), px1 - px0 - 14, fill=BODY, size=11)

    # ---- the costs and the options below
    oy = band_bottom + 30
    ow = (2040 - 40 - 2 * 24) / 3
    panels = [
        (L("Custos do desenho escolhido (estimativas da equipa, 20 nov.)", "Costs of the chosen design (team estimates, 20 Nov)"), BLUE, "#FFFFFF",
         [L("Equipamento, comprado uma vez: câmara interior ≈ 45 €; _Raspberry Pi 5_ ≈ 200 €; _Jetson Orin Nano Super_ ≈ 345 €; ou "
            "_router_ com NPU, + 15 € (estimativa). Em 5 anos, 3,33 ou 5,75 € por mês pelo equipamento.",
            "Equipment, bought once: indoor camera ≈ €45; Raspberry Pi 5 ≈ €200; Jetson Orin Nano Super ≈ €345; or a router with an "
            "NPU, + €15 (an estimate). Over 5 years, €3.33 or €5.75 a month for the device."),
          L("Energia dos modelos: _YOLOv8n_ abaixo de 0,01 € por mês; _OWLv2_ até 0,72 € com 12 h de movimento por dia (num _Jetson Orin Nano_).",
            "Model energy: YOLOv8n below €0.01 a month; OWLv2 up to €0.72 at 12 h of motion a day (on a Jetson Orin Nano).")]),
        (L("Alternativa avaliada, não escolhida: visão nos servidores L4 da Altice", "Alternative evaluated, not chosen: vision on Altice’s L4 servers"),
         WARN, "#FFFFFF",
         [L("Regiões da imagem enviadas para GPU L4 da Altice: ≈ 0,49 € por casa e por mês com 1 câmara (documento 17).",
            "Image regions sent to Altice’s L4 GPUs: ≈ €0.49 per home a month with 1 camera (document 17)."),
          L("Não escolhida: as imagens sairiam de casa.", "Not chosen: images would leave the home.")]),
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
    end = cv.para(20, oy + max(hs) + 30,
                  L("Uma caixa paga pela Altice não se paga a 3,99 € por mês (−4,81 a −6,90 € por casa e por mês, documento 17): o modelo "
                    "funciona com a IA no _router_ ou com equipamento comprado pelo cliente.",
                    "A box paid for by Altice does not pay back at €3.99 a month (−€4.81 to −€6.90 per home a month, document 17): the "
                    "model works with the AI on the router, or with equipment the customer buys."), 2000, 12.5, fill=MUTED)
    cv.save("implantacao", round(end + 10))


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
                "da família sem telemóvel), ou um telemóvel está em casa sem ninguém visto nem uso da porta há T_parado "
                "(um telemóvel esquecido?).",
                "The signals disagree: the phones are away but a camera sees a person (a stranger, a guest, or family without a "
                "phone), or a phone is home with nobody seen and no door use for T_stale (a phone left behind?)."),
            L("Nas regras: as que precisam de certeza perguntam à família em vez de agir; um rosto desconhecido em 3 análises "
              "seguidas continua a gerar o aviso de segurança.",
              "In the rules: those that need certainty ask the family instead of acting; an unknown face on 3 consecutive "
              "analyses still raises the security alert.")]
    uh = cv.box(U[0], uy, U[1] - U[0], L("INCERTA", "UNSURE"), u_body, stroke=WARN, title_color=WARN, **st)
    ry = uy + uh + 150
    o_body = [L("Alguém da família está em casa: um telemóvel da família está no Wi-Fi, ou uma câmara viu uma pessoa há "
                "menos de T_visto.",
                "Someone from the family is home: a family phone is on the Wi-Fi, or a camera saw a person in the last T_seen."),
              L("Nas regras: as de “casa vazia” esperam; um rosto desconhecido só dá alarme se a regra o pedir.",
                "In the rules: “empty home” rules wait; an unknown face raises the alarm only if the rule asks for it.")]
    l_body = [L("A porta abriu e fechou. Durante T_saída, o serviço vê quem saiu: um telemóvel que sai do Wi-Fi, ou menos "
                "pessoas nas câmaras.",
                "The door opened and closed. For T_leave, the service checks who left: a phone that leaves the Wi-Fi, or fewer "
                "people on the cameras."),
              L("Se saiu alguém da família, corre a verificação do objeto esquecido.",
                "If a family member left, the left-behind check runs.")]
    e_body = [L("Todos os telemóveis da família estão fora, a porta abriu e fechou, nenhum rosto da família foi visto há menos de "
                "T_rosto e nenhuma câmara vê uma pessoa, depois de atualizar os últimos lugares onde havia pessoas.",
                "All family phones are away, the door opened and closed, no family face was seen in the last T_face, and no "
                "camera sees a person, after a refresh of the last places where people were."),
              L("Nas regras: as de “casa vazia” agem (propor desligar o que ficou ligado); uma pessoa vista passa a INCERTA.",
                "In the rules: “empty home” rules act (offer to turn off what is on); a person seen moves the state to UNSURE.")]
    w3 = O[1] - O[0]
    ho = cv.box_h(w3, "X", o_body, 16, 16, 12.5)
    he = cv.box_h(w3, "X", e_body, 16, 16, 12.5)
    hl = cv.box_h(w3, "X", l_body, 16, 16, 12.5)
    tall = max(ho, he, hl + 100)
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
    side(O[1] + 12, LV[0] - 12, y2 + 18, L("passado T_saída, um telemóvel da família continua em casa",
                                          "after T_leave, a family phone is still home"), below=True)
    y3 = ry + 50
    cv.arrow(LV[1], y3, E[0], y3, INK)
    side(LV[1] + 12, E[0] - 12, y3 + 18, L("passado T_saída, telemóveis fora e ninguém nas câmaras",
                                          "after T_leave, phones away and nobody on the cameras"), below=True)
    # EMPTY -> OCCUPIED under LEAVING
    y4 = lb + 70
    assert y4 < ob - 20
    cv.arrow(E[0], y4, O[1], y4, INK)
    cv.label((O[1] + E[0]) / 2, y4 - 8, L("chegada: um telemóvel da família entra no Wi-Fi, ou um rosto da família é reconhecido",
                                          "arrival: a family phone joins the Wi-Fi, or a family face is recognised"),
             E[0] - O[1] - 40, size=12, fill=BODY, anchor="middle")
    # vertical: OCCUPIED <-> UNSURE, LEAVING -> UNSURE, EMPTY <-> UNSURE
    xo1, xo2 = O[0] + 150, O[0] + 210
    cv.arrow(xo1, ry, xo1, ub, INK)
    side(O[0], xo1 - 10, (ub + ry) / 2 - 20, L("telemóvel em casa, mas ninguém visto nem porta usada durante T_parado",
                                               "a phone is home, but nobody seen and no door use for T_stale"), w=xo1 - O[0] - 14)
    cv.arrow(xo2, ub, xo2, ry, INK)
    side(xo2 + 12, O[1], (ub + ry) / 2 - 20, L("um telemóvel da família entra no Wi-Fi, ou um rosto da família é reconhecido",
                                               "a family phone joins the Wi-Fi, or a family face is recognised"), w=O[1] - xo2 - 14)
    xl = (LV[0] + LV[1]) / 2
    cv.arrow(xl, ry, xl, ub, INK)
    side(xl + 12, LV[1], (ub + ry) / 2 - 4, L("telemóveis fora, mas uma pessoa é vista", "phones away, but a person is seen"),
         w=LV[1] - xl - 14)
    xe1, xe2 = E[0] + 150, E[0] + 210
    cv.arrow(xe1, ry, xe1, ub, INK)
    side(E[0], xe1 - 10, (ub + ry) / 2 - 20, L("uma pessoa vista (rosto desconhecido ou não visível)",
                                               "a person seen (unknown face or face not visible)"), w=xe1 - E[0] - 14)
    cv.arrow(xe2, ub, xe2, ry, INK)
    side(xe2 + 12, E[1], (ub + ry) / 2 - 20, L("telemóveis fora e ninguém nas câmaras, depois da atualização",
                                               "phones away and nobody on the cameras, after the refresh"), w=E[1] - xe2 - 14)

    # ---- below: signals, the count and the timings
    by = ob + 40
    bw = (W - 80 - 2 * 24) / 3
    sig = [L("Telemóveis: o _router_ diz que telemóveis da família estão no Wi-Fi (ferramenta MCP proposta, `get_home_wifi_clients`; "
             "simulada no protótipo).",
             "Phones: the router says which family phones are on the Wi-Fi (a proposed MCP tool, `get_home_wifi_clients`; simulated "
             "in the prototype)."),
           L("Porta: o sensor de contacto envia “aberta” e “fechada” à plataforma, como hoje.",
             "Door: the contact sensor sends “open” and “closed” to the platform, as today."),
           L("Câmaras: pessoas encontradas pelo _OWLv2_ e, com consentimento, o rótulo do rosto calculado em casa.",
             "Cameras: people found by OWLv2 and, with consent, the face label worked out in the home.")]
    cnt = [L("Pessoas em casa = família em casa (telemóvel no Wi-Fi, ou rosto visto há menos de T_rosto sem o telemóvel ter saído "
             "depois) + visitas registadas vistas agora + rostos desconhecidos vistos agora.",
             "People home = family home (phone on the Wi-Fi, or face seen in the last T_face with no phone leaving since) + "
             "registered guests seen now + unknown faces seen now."),
           L("Uma pessoa sem rosto visível só se soma se não puder ser alguém da família já contado; com a família fora, o "
             "estado passa a INCERTA.",
             "A person with no visible face is added only if they cannot be a family member already counted; with the family "
             "away, the state becomes UNSURE."),
           L("Divisão sem câmara: cobrem-na os telemóveis. Pessoa parada: cobrem-na os telemóveis e a atualização periódica.",
             "A room without a camera: the phones cover it. A still person: the phones and the periodic refresh cover them.")]
    h1 = cv.box_h(bw, "X", sig, 16, 14.5, 12.5)
    h2 = cv.box_h(bw, "X", cnt, 16, 14.5, 12.5)
    rows = [("T_visto", "T_seen", L("uma pessoa vista conta como “agora”", "a person seen counts as “now”"), "15 s", "2 min"),
            ("T_rosto", "T_face", L("um rosto da família conta em casa", "a family face counts as home"), "2 min", "30 min"),
            ("T_saída", "T_leave", L("A SAIR espera por quem saiu", "LEAVING waits for a leaver"), "10 s", "5 min"),
            ("T_atraso", "T_lag", L("telemóvel sai do Wi-Fi após a porta", "a phone leaves the Wi-Fi after the door"), "30 s", "5 min"),
            ("T_telemóvel", "T_phone", L("ausência que conta como fora*", "absence that counts as away*"), L("simulado", "simulated"), "10 min"),
            ("T_atualizar", "T_refresh", L("revê onde as pessoas estavam", "re-checks where people were"), "30 s", "30 s"),
            ("T_verificar", "T_check", L("espera pela verificação ativa", "waits for the active check"), "15 s", "60 s"),
            ("T_parado", "T_stale", L("telemóvel em casa sem outros sinais", "phone home with no other sign"), "15 min", "4 h")]
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
    cv.para(c1, yy + 26, L("* Fora de A SAIR; em A SAIR conta logo. Valores do protótipo (presence.py); os de produção são propostas.",
                           "* Outside LEAVING; in LEAVING it counts at once. The prototype’s values (presence.py); production ones are proposals."),
            bw - 32, 11.5, fill=MUTED)
    foot = L("Corre no equipamento da casa: um estado por casa, recalculado a cada evento (porta, Wi-Fi, resultado "
             "da visão) e a cada temporizador.",
             "Runs on the home device: one state per home, recomputed on every event (door, Wi-Fi, vision "
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
    cols = [(L("Equipamento da casa", "Home device"), L("visão, memória e regras", "vision, memory and rules"), "home"),
            (L("Sensor da porta e _router_", "Door sensor and router"), L("em casa, ligados à Altice", "in the home, on Altice"), "home"),
            (L("Plataforma Altice", "Altice platform"), L("eventos, retransmissão, notificações", "events, relay, notifications"), "altice"),
            (L("Aplicação Altice", "Altice app"), L("no telemóvel", "on the phone"), "phone")]
    rows = [
        ("g", L("Estado: OCUPADA (o telemóvel do dono do livro está no Wi-Fi). O livro foi visto pela última vez na secretária da Sala 1, às 18h02.",
                "State: OCCUPIED (the book owner’s phone is on the Wi-Fi). The book was last seen on the desk in Living room 1, at 18:02.")),
        ("m", 1, 2, L("porta aberta (`sensorState: alarm`)", "door open (`sensorState: alarm`)")),
        ("m", 2, 0, L("`door.opened`, em texto, pela retransmissão", "`door.opened`, as text, through the relay")),
        ("m", 1, 2, L("porta fechada, 8 s depois", "door closed, 8 s later")),
        ("m", 2, 0, L("`door.closed`", "`door.closed`")),
        ("n", 0, 0, L("A porta abriu e fechou: OCUPADA → A SAIR. Espera até T_saída (10 s na demonstração, 5 min em produção) por quem saiu",
                      "The door opened and closed: OCCUPIED → LEAVING. Waits up to T_leave (10 s in the demo, 5 min in production) for whoever left")),
        ("m", 1, 2, L("o telemóvel do dono do livro saiu do Wi-Fi", "the book owner’s phone left the Wi-Fi")),
        ("m", 2, 0, L("`wifi.left`: o dono do livro (evento proposto)", "`wifi.left`: the book owner (proposed event)")),
        ("n", 0, 0, L("Saiu alguém da família: verificação ativa do lugar habitual do livro, sem esperar por movimento. Lê 3 imagens da "
                      "secretária, 1 por segundo, na rede da casa",
                      "A family member left: an active check of the book’s usual place, without waiting for motion. Reads 3 frames of "
                      "the desk, 1 a second, on the home network")),
        ("n", 0, 0, L("Caixas de “livro” e vetores _DINOv2_, comparados com as 8 fotos do livro: 0,70 ≥ 0,62 em 3 de 3 imagens. Regra "
                      "“avisa-me se sair sem o livro” cumprida, porque bastam 2 de 3",
                      "“Book” boxes and DINOv2 vectors, matched with the book’s 8 photos: 0.70 ≥ 0.62 in 3 of 3 frames. Rule “tell me "
                      "if I leave without my book” met, since 2 of 3 are enough")),
        ("m", 0, 2, L("aviso, só texto: “livro, secretária, 18h02”", "alert, text only: “book, desk, 18:02”")),
        ("m", 2, 3, L("notificação: “O livro ficou em casa, na secretária, às 18h02”",
                      "push: “Your book stayed at home, on the desk, at 18:02”")),
        ("g", L("Se o livro aparecer em menos de 2 das 3 imagens (meio tapado, por exemplo), o motor de regras pode chamar o juiz: um modelo "
                "de visão-linguagem opcional, no equipamento da casa, vê 2 a 3 s da região e responde sim, não ou incerto. “Sim” dá o aviso; "
                "“não” não dá; “incerto” faz a aplicação perguntar à família, sem alarme. As imagens não saem de casa.",
                "If the book is seen in fewer than 2 of the 3 frames (half hidden, say), the rules engine may call the judge: an optional "
                "vision-language model on the home device looks at 2 to 3 s of the region and answers yes, no or unsure. “Yes” gives the "
                "alert; “no” does not; “unsure” makes the app ask the family, with no alarm. The images do not leave the home.")),
        ("g", L("Uma chegada (a porta abre e fecha e um telemóvel entra no Wi-Fi) não inicia a verificação.",
                "An arrival (the door opens and closes and a phone joins the Wi-Fi) does not start the check.")),
        ("g", L("Sem sensor de porta, o mesmo teste começa quando um telemóvel da família sai do Wi-Fi (passado T_telemóvel, por isso "
                "mais tarde) ou quando uma câmara que vê a porta de saída vê alguém sair por ela.",
                "Without a door sensor, the same check starts when a family phone leaves the Wi-Fi (after T_phone, so later) or "
                "when a camera that sees the exit door sees someone leave through it.")),
    ]
    sequence(lang, "seq-livro-esquecido", L("Sequência: o livro esquecido", "Sequence: the book left behind"), cols, rows, legend(lang),
             colw=[340, 250, 330, 340])


@view
def seq_pessoa_desconhecida(lang):
    pt = lang == "pt"
    L = (lambda a, b: a if pt else b)
    cols = [(L("Câmara", "Camera"), L("Sala 1, rede da casa", "Living room 1, home network"), "home"),
            (L("Equipamento da casa", "Home device"), L("visão, rostos com _YuNet_ e _SFace_, regras", "vision, faces with YuNet and SFace, rules"), "home"),
            (L("Plataforma Altice", "Altice platform"), L("retransmissão, notificações, servidor MCP", "relay, notifications, MCP server"), "altice"),
            (L("Aplicação Altice", "Altice app"), L("no telemóvel", "on the phone"), "phone")]
    rows = [
        ("g", L("Estado: VAZIA desde as 14h10 (nenhum telemóvel da família no Wi-Fi). Regra ativa: “Toca o alarme quando entrar alguém "
                "que não seja da família”, com a escolha “perguntar primeiro”.",
                "State: EMPTY since 14:10 (no family phone on the Wi-Fi). Active rule: “Sound the alarm when someone who isn’t family "
                "comes in”, with the choice “ask first”.")),
        ("m", 0, 1, L("imagens RTSP, só na rede da casa", "RTSP frames, on the home network only")),
        ("n", 1, 1, L("Movimento: o detetor encontra uma pessoa. _YuNet_ encontra o rosto dentro da sua caixa; _SFace_ dá 0,21 contra o "
                      "padrão mais parecido, abaixo de 0,363: “rosto desconhecido”",
                      "Motion: the detector finds a person. YuNet finds the face inside their box; SFace gives 0.21 against the closest "
                      "template, below 0.363: “unknown face”")),
        ("n", 1, 1, L("3 análises seguidas (cerca de 3 s) com o mesmo rosto desconhecido: VAZIA → INCERTA, e a regra cumpre-se",
                      "3 consecutive analyses (about 3 s) with the same unknown face: EMPTY → UNSURE, and the rule is met")),
        ("m", 1, 2, L("aviso urgente, só texto: “desconhecido, Sala 1”", "urgent alert, text only: “unknown, Living room 1”")),
        ("m", 2, 3, L("notificação urgente no telemóvel: “Está alguém que não é da família na Sala 1”",
                      "push: “Someone who isn’t family is in Living room 1”")),
        ("n", 3, 3, L("Cartões do aviso: “Tocar a sirene”, “Ligar à polícia (112)” e “Ver em direto”",
                      "The alert’s cards: “Sound the siren”, “Call the police (112)” and “See live”")),
        ("m", 3, 2, L("“Sim” em “Tocar a sirene”", "“Yes” on “Sound the siren”")),
        ("m", 2, 0, L("servidor MCP, `update_device_capabilities`: `sirenSwitch` da câmara ligado",
                      "MCP server, `update_device_capabilities`: camera `sirenSwitch` on")),
        ("n", 3, 3, L("“Ligar à polícia (112)” abre a chamada no telemóvel e é a pessoa quem liga. O sistema nunca marca o número",
                      "“Call the police (112)” opens the call on the phone and the person places it. The system never dials")),
        ("g", L("Rosto da família (semelhança ≥ 0,363): nenhum aviso, e INCERTA → OCUPADA. Rosto não visível: a aplicação pergunta "
                "“Está alguém na Sala 1. É alguém conhecido?”, sem alarme, e só sugere o 112 se a resposta for “não”.",
                "A family face (similarity ≥ 0.363): no alert, and UNSURE → OCCUPIED. Face not visible: the app asks “Someone is in "
                "Living room 1. Do you know them?”, with no alarm, and suggests 112 only if the answer is “no”.")),
    ]
    sequence(lang, "seq-pessoa-desconhecida", L("Sequência: pessoa desconhecida", "Sequence: an unknown person"), cols, rows, legend(lang),
             colw=[260, 360, 360, 330])


@view
def seq_casa_vazia(lang):
    pt = lang == "pt"
    L = (lambda a, b: a if pt else b)
    cols = [(L("Equipamento da casa", "Home device"), L("visão, presença e regras", "vision, presence and rules"), "home"),
            (L("Sensor da porta e _router_", "Door sensor and router"), L("em casa, ligados à Altice", "in the home, on Altice"), "home"),
            (L("Plataforma Altice", "Altice platform"), L("eventos, servidor MCP, notificações", "events, MCP server, notifications"), "altice"),
            (L("Aplicação Altice", "Altice app"), L("no telemóvel", "on the phone"), "phone")]
    rows = [
        ("g", L("Estado: OCUPADA. Regras ativas: “Quando não estiver ninguém, propõe desligar o que ficou ligado” e “Avisa-me se a "
                "porta ficar aberta sem ninguém por perto”.",
                "State: OCCUPIED. Active rules: “When nobody is home, offer to turn off what is still on” and “Tell me if the "
                "door is left open with nobody around”.")),
        ("m", 1, 2, L("porta aberta e fechada; os 2 telemóveis da família saem do Wi-Fi", "door opened and closed; both family phones leave the Wi-Fi")),
        ("m", 2, 0, L("`door.opened`, `door.closed`, `wifi.left` × 2, em texto", "`door.opened`, `door.closed`, `wifi.left` × 2, as text")),
        ("n", 0, 0, L("OCUPADA → A SAIR. Nenhuma pessoa vista desde que a porta fechou; falta confirmar que ninguém ficou parado",
                      "OCCUPIED → LEAVING. No person seen since the door closed; it still has to confirm that nobody stayed still")),
        ("n", 0, 0, L("Atualização: lê as câmaras onde as pessoas foram vistas por último, na rede da casa. Nenhuma pessoa",
                      "Refresh: reads the cameras where people were last seen, on the home network. No person")),
        ("m", 0, 2, L("que aparelhos estão ligados? (`get_home_devices`)", "which appliances are on? (`get_home_devices`)")),
        ("m", 2, 0, L("as luzes (na tomada) e o ar condicionado", "the lights (on the plug) and the air conditioner")),
        ("n", 0, 0, L("Passado T_saída, ninguém nas câmaras: A SAIR → VAZIA, com 2 aparelhos ligados",
                      "After T_leave, nobody on the cameras: LEAVING → EMPTY, with 2 appliances on")),
        ("m", 0, 2, L("aviso, só texto, com as 2 ações propostas", "alert, text only, with the 2 proposed actions")),
        ("m", 2, 3, L("notificação: “Não está ninguém em casa e há 2 aparelhos ligados”, com dois cartões “Sim”",
                      "push: “Nobody is home and 2 appliances are on”, with two “Yes” cards")),
        ("m", 3, 2, L("“Sim”: desligar as luzes", "“Yes”: turn off the lights")),
        ("m", 2, 1, L("`update_device_capabilities`: tomada desligada", "`update_device_capabilities`: plug off")),
        ("m", 3, 2, L("“Sim”: desligar o ar condicionado", "“Yes”: turn off the air conditioner")),
        ("m", 2, 1, L("`update_device_capabilities`: ar condicionado desligado", "`update_device_capabilities`: air conditioner off")),
        ("g", L("Noutro dia, a porta da entrada fica aberta", "Another day, the front door is left open")),
        ("m", 1, 2, L("porta aberta", "door open")),
        ("m", 2, 0, L("`door.opened`", "`door.opened`")),
        ("n", 0, 0, L("Porta aberta há T_porta (5 s na demonstração, 2 min em produção, proposta), sem ninguém em nenhuma câmara "
                      "desde que abriu",
                      "Door open for T_door (5 s in the demo, 2 min in production, a proposal), with nobody on any camera "
                      "since it opened")),
        ("m", 0, 2, L("aviso, só texto: “porta da entrada aberta, ninguém por perto”", "alert, text only: “front door open, nobody around”")),
        ("m", 2, 3, L("notificação: “A porta da entrada está aberta e não está ninguém por perto”, com a faixa da porta e “Ver em direto”",
                      "push: “The front door is open and nobody is around”, with the door banner and “See live”")),
    ]
    sequence(lang, "seq-casa-vazia", L("Sequência: casa vazia e porta aberta", "Sequence: empty home and open door"), cols, rows, legend(lang),
             colw=[340, 250, 330, 340])


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
                                   L("Corre todo no equipamento da casa (o _router_, se tiver NPU, ou uma pequena caixa): imagens, assinaturas visuais e padrões faciais nunca saem de casa",
                                     "Runs entirely on the home device (the router, if it has an NPU, or a small box): images, fingerprints and face templates never leave the home")], **SYSTEM)),
        "plat": (2, 1, 1, dict(title=L("Plataforma _Connected Home_", "Connected Home platform"), sub=L("[sistema existente · Altice]", "[existing system · Altice]"),
                               body=[L("Dispositivos, cenários, segurança e notificações; servidor MCP com 18 ferramentas",
                                       "Devices, scenarios, security and notifications; MCP server with 18 tools"),
                                     L("Para o _ThingTracker_, só texto: contas, nomes, cenários e registo de eventos",
                                       "For ThingTracker, text only: accounts, names, scenarios and the event log")], **EXTERNAL)),
        "visitor": (0, 2, 1, dict(title=L("Visita ou desconhecido", "Guest or stranger"), sub=L("[pessoa]", "[person]"),
                                  body=[L("Aparece nas imagens; sem registo nem consentimento, nunca recebe um nome",
                                          "Appears in the frames; without registration and consent, never gets a name")], **PERSON)),
        "llm": (1, 2, 1, dict(title=L("Modelo de linguagem externo", "External language model"),
                              sub=L("[possível no futuro, por opção do cliente; não agora]", "[a possible future opt-in; not now]"),
                              body=[L("Por exemplo, o _ChatGPT_ ou o _Claude_ do próprio cliente; só texto. Hoje, o modelo de linguagem corre no equipamento da casa",
                                      "For example, the customer’s own ChatGPT or Claude; text only. Today the language model runs on the home device")],
                              dash="6 4", **EXTERNAL)),
        "router": (2, 2, 1, dict(title=L("_Router_ e sensores do kit", "Router and kit sensors"), sub=L("[sistemas existentes · em casa]", "[existing systems · in the home]"),
                                 body=[L("Wi-Fi com os telemóveis da família; sensor da porta; luz, tomada e sirene",
                                         "Wi-Fi with the family phones; door sensor; light, plug and siren")], **EXTERNAL)),
    })
    g.h2("family", "app", L("usa: regista, pergunta, escreve regras, diz “Sim”", "uses it: registers, asks, writes rules, says “Yes”"),
         L("mostra avisos e respostas", "shows alerts and answers"))
    g.v2("app", "tt", L("frases, perguntas, “Sim”; fotografias e vídeo do rosto, cifrados de ponta a ponta", "sentences, questions, “Yes”; photos and face video, encrypted end to end"),
         L("respostas", "answers"), lw=160)
    g.v("plat", "app", L("notificações com os avisos", "notifications with the alerts"), lw=160)
    g.h("cams", "tt", L("vídeo, lido só em casa, pelo equipamento da casa", "video, read only in the home, by the home device"))
    g.h2("tt", "plat", L("só texto: eventos e avisos; ações após “Sim”, pelo MCP", "text only: events and alerts; actions after “Yes”, through the MCP"),
         L("eventos da porta e do Wi-Fi", "door and Wi-Fi events"))
    g.v2("tt", "llm", L("só texto, se o cliente optar", "text only, if the customer opts in"), L("regras, respostas", "rules, answers"), lw=150)
    g.v2("plat", "router", L("comandos: luz, tomada, sirene", "commands: light, plug, siren"),
         L("porta aberta e fechada; telemóveis no Wi-Fi (ferramenta proposta)", "door open and closed; phones on the Wi-Fi (proposed tool)"), lw=155)
    g.v("visitor", "cams", L("aparece nas imagens", "appears in the frames"), lw=150)
    end = max(r[3] for r in g.r.values())
    end = cv.para(40, end + 40, L("Notação C4 (c4model.com), nível 1. Azul: o sistema descrito; cinzento: sistemas existentes; contorno "
                                  "azul-escuro: pessoas; tracejado: uma opção futura, fora da Altice.",
                                  "C4 notation (c4model.com), level 1. Blue: the system described; grey: existing systems; dark blue "
                                  "outline: people; dashed: a future option, outside Altice."), W - 80, 12.5, fill=MUTED)
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
                               body=[L("RTSP, H.265, só na rede da casa", "RTSP, H.265, on the home network only")], **EXTERNAL)),
        "app": ((3, 5), 0, 1, dict(title=L("Aplicação Altice", "Altice app"), sub=L("[sistema existente · telemóvel]", "[existing system · phone]"),
                                   body=[L("Separador _Things_, assistente e avisos com cartões de ação", "Things tab, assistant, and alerts with action cards")], **EXTERNAL)),
        "ingest": (0, 1, 1, dict(title=L("Captura e filtro de movimento", "Capture and motion gate"), sub="[_ffmpeg_, _OpenCV_]" if lang == "pt" else "[ffmpeg, OpenCV]",
                                 body=[L("Lê as câmaras na rede da casa; máscaras de privacidade; só analisa quando há movimento ou um pedido",
                                         "Reads the cameras on the home network; privacy masks; analyses only on motion or on request")], **C)),
        "vision": (1, 1, 1, dict(title=L("Visão", "Vision"), sub=L("[_OWLv2_ + _DINOv2_ no protótipo]", "[OWLv2 + DINOv2 in the prototype]"),
                                 body=[L("Deteção e reidentificação com a assinatura visual (≥ 0,62); detetores leves, como o _YOLOv8n_, em equipamentos pequenos",
                                         "Detection and re-identification against the fingerprint (≥ 0.62); lighter detectors, such as YOLOv8n, on small devices")], **C)),
        "faces": (0, 2, 1, dict(title=L("Rostos (opcional)", "Faces (opt-in)"), sub=L("[_YuNet_ + _SFace_]", "[YuNet + SFace]"),
                                body=[L("Com consentimento; os padrões faciais ficam guardados no equipamento", "With consent; face templates kept on the device")], **C)),
        "mem": (1, 2, 1, dict(title=L("Memória local", "Local memory"), sub=L("[_SQLite_ cifrado]", "[encrypted SQLite]"),
                              body=[L("Assinaturas visuais, padrões faciais, onde e quando cada objeto foi visto", "Fingerprints, face templates, where and when each thing was seen")], **C)),
        "rules": (2, 1, 2, dict(title=L("Serviço da casa", "Home service"), sub=L("[_Python_, no equipamento da casa]", "[Python, on the home device]"),
                                body=[L("Motor de presença e motor de regras; o motor de regras decide", "Presence engine and rules engine; the rules engine decides"),
                                      L("Seguimento: na mão, levado, mudado", "Tracking: in hand, taken, moved"),
                                      L("Avisos, em texto; um “Sim” vira um pedido de ação MCP", "Alerts, as text; a “Yes” becomes an MCP action request"),
                                      L("Constrói a assinatura a partir das fotografias de registo", "Builds the fingerprint from the registration photos")],
                                stroke=BLUE, sw=2.4, fill="#FFFFFF", sub_bold=False, sub_color=MUTED)),
        "llm": (2, 3, 1, dict(title=L("Modelo de linguagem", "Language model"), sub=L("[_Qwen3-1.7B_ no protótipo]", "[Qwen3-1.7B in the prototype]"),
                              body=[L("Frase em regra, pergunta em resposta; o serviço valida; nunca decide", "Sentence into rule, question into answer; the service checks; it never decides")], **C)),
        "relay": (3, 1, 2, dict(title=L("Retransmissão e mediador", "Relay and connection broker"), sub=L("[MQTT sobre mTLS]", "[MQTT over mTLS]"),
                                body=[L("Uma ligação de saída por casa, atrás de um balanceador", "One outbound connection per home, behind a load balancer"),
                                      L("Leva a aplicação até casa quando a família está fora", "Lets the app reach the home when the family is away"),
                                      L("As fotografias de registo passam cifradas de ponta a ponta: a Altice não as lê", "Registration photos pass encrypted end to end: Altice cannot read them")], **C)),
        "svc": (4, 1, 2, dict(title=L("Serviço _ThingTracker_ na Altice", "ThingTracker service at Altice"), sub=L("[contentores sem estado; só texto]", "[stateless containers; text only]"),
                              body=[L("Contas, identidade e permissões da família", "Accounts, identity and family permissions"),
                                    L("Registo de eventos em texto (“livro, secretária, 18h02”)", "Event log as structured text (“book, desk, 18:02”)"),
                                    L("Cópia de segurança e sincronização entre os telemóveis da família", "Backup and sync across the family’s phones")],
                              stroke=BLUE, sw=2.4, fill="#FFFFFF", sub_bold=False, sub_color=MUTED)),
        "plat": (5, 1, 2, dict(title=L("Plataforma _Connected Home_", "Connected Home platform"), sub=L("[sistema existente]", "[existing system]"),
                               body=[L("Servidor MCP, eventos da porta e do Wi-Fi, notificações", "MCP server, door and Wi-Fi events, notifications")], **EXTERNAL)),
        "pg": (4, 3, 1, dict(title="PostgreSQL", sub=L("[só metadados, em texto]", "[metadata only, as text]"),
                             body=[L("Objetos, pessoas (só nomes), donos, cenários, eventos; repõe-nos se a caixa for trocada",
                                     "Things, people (names only), owners, scenarios, events; restores them if the box is replaced")], **C)),
    })
    g.v("cams", "ingest", L("vídeo RTSP, rede da casa", "RTSP video, home network"), lw=110)
    g.h("ingest", "vision", L("região que mudou", "changed region"))
    g.v("ingest", "faces", L("pessoa na imagem", "person in the frame"), lw=110)
    g.h("faces", "mem", L("nome ou “desconhecido”", "name or “unknown”"))
    g.v2("vision", "mem", L("observações", "sightings"), L("assinaturas", "fingerprints"), lw=100)
    g.h("vision", "rules", L("objetos e pessoas vistos", "things and people seen"))
    g.h2("mem", "rules", L("última vez visto, quem está", "last seen, who is in"), L("eventos, regras", "events, rules"))
    g.v2("rules", "llm", L("frase ou pergunta", "sentence or question"), L("regra proposta, resposta", "draft rule, answer"), lw=100)
    g.h2("rules", "relay", L("só texto: eventos, avisos", "text only: events, alerts"), L("pedidos, comandos, fotografias cifradas", "requests, commands, encrypted photos"))
    g.h2("relay", "svc", L("eventos em texto", "events as text"), L("pedidos da aplicação", "app requests"))
    g.h2("svc", "plat", L("ações MCP após “Sim”; notificações", "MCP actions after “Yes”; push"), L("eventos: porta, Wi-Fi", "events: door, Wi-Fi"))
    g.v2("svc", "pg", L("grava", "writes"), L("lê", "reads"), lw=100)
    g.v2("app", "svc", L("frases, perguntas, “Sim” (HTTPS)", "sentences, questions, “Yes” (HTTPS)"), L("respostas, lista de objetos", "answers, list of things"), lw=120)
    g.v("plat", "app", L("notificações", "notifications"), lw=110)
    top, bot = g.ys[1] - 50, max(r[3] for r in g.r.values()) + 24
    app = g.r["app"]

    def zones(b):
        b.band(20, 24, xs[2] + ws[2] + 20 - 20, bot - 24, L("Em casa · equipamento da casa", "In the home · home device"), None, fill=HOME_BG)
        b.band(app[0] - 20, 24, app[2] - app[0] + 40, app[3] + 18 - 24, L("Telemóvel", "Phone"), None, fill=PHONE_BG)
        b.band(xs[3] - 20, top, xs[5] + ws[5] + 20 - (xs[3] - 20), bot - top, L("Altice · só texto", "Altice · text only"), None, fill=ALTICE_BG)
    bands_under(cv, zones)
    end = cv.para(40, bot + 34, L("Notação C4, nível 2. Contorno azul: contentores do _ThingTracker_; cinzento: sistemas existentes. Cada seta "
                                  "é um sentido do fluxo, com o que leva. Imagens, vídeo, assinaturas visuais e padrões faciais nunca saem de casa.",
                                  "C4 notation, level 2. Blue outline: ThingTracker containers; grey: existing systems. Each arrow is one "
                                  "direction of a flow, with what it carries. Images, video, fingerprints and face templates never leave the home."), 2180, 12.5, fill=MUTED)
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
        "cap": (0, 1, 1, dict(title=L("Captura", "Capture"), sub="[_ffmpeg_, _OpenCV_]" if lang == "pt" else "[ffmpeg, OpenCV]",
                              body=[L("Uma ligação aberta por câmara, só na rede da casa", "One open connection per camera, on the home network only")], **C)),
        "mask": (0, 2, 1, dict(title=L("Máscaras de privacidade", "Privacy masks"),
                               body=[L("Apaga as zonas que a família marcou, antes de qualquer análise", "Blanks the areas the family marked, before any analysis")], **C)),
        "gate": (0, 3, 1, dict(title=L("Filtro de movimento", "Motion gate"), sub=L("[160 × 90, cinzento, a cada 0,5 s]", "[160 × 90, grey, every 0.5 s]"),
                               body=[L("Abre se mais de 0,6 % dos píxeis mudar e fica aberto 6 s; abre também a pedido",
                                       "Opens if more than 0.6 % of the pixels change and stays open 6 s; also opens on request")], **C)),
        "det": (0, 4, 1, dict(title=L("Deteção", "Detection"), sub=L("[_OWLv2_; _YOLOv8n_ em equipamentos pequenos]", "[OWLv2; YOLOv8n on small devices]"),
                              body=[L("Objetos registados, “a person” e superfícies (secretária, mesa)",
                                      "Registered things, “a person” and surfaces (desk, table)")], **C)),
        "face": (1, 3, 1, dict(title=L("Rostos (opcional)", "Faces (opt-in)"), sub=L("[_YuNet_ + _SFace_, no CPU]", "[YuNet + SFace, on the CPU]"),
                               body=[L("Encontra, alinha e compara: ≥ 0,363 dá o nome; abaixo, “rosto desconhecido”",
                                       "Finds, aligns and compares: ≥ 0.363 gives the name; below, “unknown face”")], **C)),
        "tpl": (1, 2, 1, dict(title=L("Padrões faciais", "Face templates"), sub=L("[_SQLite_ cifrado]", "[encrypted SQLite]"),
                              body=[L("Até 8 por pessoa; nunca saem de casa", "Up to 8 per person; never leave the home")], **C)),
        "vec": (1, 4, 1, dict(title=L("Vetores", "Vectors"), sub=L("[_DINOv2 small_]", "[DINOv2 small]"),
                              body=[L("Um vetor de 384 números por candidato", "One 384-number vector per candidate")], **C)),
        "match": (2, 4, 1, dict(title=L("Reidentificação", "Re-identification"),
                                body=[L("Cada vetor contra as 8 fotos de cada objeto: ≥ 0,62 é o seu", "Each vector against each thing’s 8 photos: ≥ 0.62 means yours")], **C)),
        "mem": (2, 5, 1, dict(title=L("Memória local", "Local memory"), sub=L("[_SQLite_ cifrado]", "[encrypted SQLite]"),
                              body=[L("Assinaturas visuais; onde e quando cada objeto foi visto", "Fingerprints; where and when each thing was seen")], **C)),
        "lm": (2, 2, 1, dict(title=L("Modelo de linguagem", "Language model"), sub=L("[_Qwen3-1.7B_ no protótipo]", "[Qwen3-1.7B in the prototype]"),
                             body=[L("Frase em regra, pergunta em resposta; nunca decide", "Sentence into rule, question into answer; never decides")], **C)),
        "track": (3, 4, 1, dict(title=L("Seguimento", "Tracking"),
                                body=[L("Sobre uma pessoa: na mão. Ausente 3 análises depois: levado. Noutro sítio: mudado",
                                        "Over a person: in hand. Gone 3 analyses later: taken. Elsewhere: moved")], **C)),
        "pres": (3, 3, 1, dict(title=L("Motor de presença", "Presence engine"),
                               body=[L("OCUPADA, A SAIR, VAZIA ou INCERTA, com a porta, o Wi-Fi e as câmaras",
                                       "OCCUPIED, LEAVING, EMPTY or UNSURE, from the door, the Wi-Fi and the cameras")], **C)),
        "rules": (3, 2, 1, dict(title=L("Motor de regras", "Rules engine"),
                                body=[L("Decide: regras compiladas, a cada evento e temporizador; valida o que o modelo propõe",
                                        "Decides: compiled rules, on every event and timer; checks what the model proposes")], **C)),
        "alert": (3, 1, 1, dict(title=L("Avisos", "Alerts"),
                                body=[L("Título, mensagem e cartões de ação, em texto", "Title, message and action cards, as text")], **C)),
        "chan": (3, 0, 1, dict(title=L("Canal seguro", "Secure channel"), sub=L("[MQTT sobre mTLS]", "[MQTT over mTLS]"),
                               body=[L("Uma ligação de saída; envia só texto; recebe eventos da porta e do Wi-Fi, pedidos e comandos",
                                       "One outbound connection; sends text only; receives door and Wi-Fi events, requests and commands")], **C)),
        "brk": (4, 0, 1, dict(title=L("Retransmissão", "Relay"), sub="[MQTT]",
                              body=[L("Leva a aplicação até casa; as fotografias de registo passam cifradas de ponta a ponta",
                                      "Lets the app reach the home; registration photos pass encrypted end to end")], **C)),
        "svc": (4, 1, 2, dict(title=L("Serviço na Altice", "Service at Altice"), sub=L("[só texto]", "[text only]"),
                              body=[L("Contas, identidade, permissões da família; registo de eventos; um “Sim” vira uma chamada MCP",
                                      "Accounts, identity, family permissions; event log; a “Yes” becomes an MCP call")], **C)),
        "pg": (4, 3, 1, dict(title="PostgreSQL", sub=L("[metadados, em texto]", "[metadata, as text]"),
                             body=[L("Objetos, pessoas (só nomes), donos, cenários, eventos", "Things, people (names only), owners, scenarios, events")], **C)),
        "plat": (5, 0, 1, dict(title=L("Plataforma Altice", "Altice platform"), sub=L("[existente]", "[existing]"),
                               body=[L("Eventos da porta e telemóveis no Wi-Fi", "Door events and phones on the Wi-Fi")], **X)),
        "notif": (5, 1, 1, dict(title=L("Notificações e aplicação", "Notifications and app"), sub=L("[existente]", "[existing]"),
                                body=[L("Mostram o aviso e devolvem o “Sim”", "Show the alert, return the “Yes”")], **X)),
        "mcp": (5, 2, 1, dict(title=L("Servidor MCP", "MCP server"), sub=L("[existente]", "[existing]"),
                              body=["`update_device_capabilities`"], **X)),
    })
    S = 11
    g.v("cams", "cap", "RTSP", size=S, lw=100)
    g.v("cap", "mask", L("imagem", "frame"), size=S, lw=100)
    g.v("mask", "gate", L("imagem com máscaras", "masked frame"), size=S, lw=100)
    g.v("gate", "det", L("aberto: região", "open: region"), size=S, lw=100)
    g.h("gate", "face", L("pessoa na região", "person in the region"), size=S)
    g.v2("tpl", "face", L("padrões", "templates"), L("registo", "registration"), size=S, lw=100)
    g.h("face", "pres", L("nome ou “rosto desconhecido”", "name or “unknown face”"), size=S)
    g.h("det", "vec", L("caixas", "boxes"), size=S)
    g.h("vec", "match", L("vetores", "vectors"), size=S)
    g.v2("match", "mem", L("observações", "sightings"), L("assinaturas", "fingerprints"), size=S, lw=100)
    g.h("match", "track", L("objetos reconhecidos, pessoas", "recognised things, people"), size=S)
    g.v("track", "pres", L("pessoas", "people"), size=S, lw=110)
    g.v("pres", "rules", L("estado da casa", "home state"), size=S, lw=110)
    g.h2("lm", "rules", L("regra proposta, resposta", "draft rule, answer"), L("frase, pergunta, linhas da memória", "sentence, question, memory lines"), size=S)
    g.v("rules", "alert", L("regra cumprida", "rule met"), size=S, lw=110)
    g.v("alert", "chan", L("aviso em texto", "alert as text"), size=S, lw=110)
    g.h2("chan", "brk", L("só texto: eventos, avisos", "text only: events, alerts"), L("pedidos, comandos", "requests, commands"), size=S)
    g.v2("brk", "svc", L("eventos, avisos", "events, alerts"), L("pedidos da aplicação", "app requests"), size=S, lw=110)
    g.h("plat", "brk", L("porta, Wi-Fi", "door, Wi-Fi"), size=S)
    g.h2("svc", "notif", L("aviso", "alert"), L("“Sim”", "“Yes”"), size=S)
    g.h("svc", "mcp", L("ação após “Sim”", "action after “Yes”"), size=S)
    g.v2("svc", "pg", L("grava", "writes"), L("lê", "reads"), size=S, lw=100)
    bot = max(r[3] for r in g.r.values()) + 24

    def zones(b):
        b.band(20, 24, xs[3] + ws[3] + 20 - 20, bot - 24, L("Em casa · equipamento da casa", "In the home · home device"),
               L("O _router_, se tiver NPU, ou uma caixa dedicada", "The router, if it has an NPU, or a dedicated box"), fill=HOME_BG)
        b.band(xs[4] - 20, 24, xs[5] + ws[5] + 20 - (xs[4] - 20), bot - 24,
               L("Altice · só texto", "Altice · text only"), L("Contas, metadados, eventos, notificações, ações", "Accounts, metadata, events, push, actions"),
               fill=ALTICE_BG)
    bands_under(cv, zones)
    end = cv.para(40, bot + 34, L("Notação C4, nível 3. Cada componente diz o que decide e com que limiar. Valores do filtro de movimento: os "
                                  "do protótipo. Imagens, vídeo, assinaturas visuais e padrões faciais nunca saem de casa.",
                                  "C4 notation, level 3. Each component says what it decides and with which threshold. Motion gate values: "
                                  "the prototype’s. Images, video, fingerprints and face templates never leave the home."), 1980, 12.5, fill=MUTED)
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
        "mem": (0, 1, 1, dict(title=L("Memória local", "Local memory"), sub=L("[arquivo, cifrado]", "[store, encrypted]"),
                              body=[L("Assinaturas, padrões faciais, observações", "Fingerprints, face templates, sightings")], **STO)),
        "dev": (1, 0, 3, dict(title=L("Equipamento da casa", "Home device"), sub=L("[processo]", "[process]"),
                              body=[L("Visão, rostos, memória, presença, regras e modelo de linguagem", "Vision, faces, memory, presence, rules and language model")], **PRO)),
        "router": (0, 3, 1, dict(title=L("_Router_ Wi-Fi", "Wi-Fi router"), sub=L("[entidade externa]", "[external entity]"), **ENT)),
        "door": (0, 4, 1, dict(title=L("Sensor da porta e atuadores", "Door sensor and actuators"), sub=L("[entidades externas]", "[external entities]"), **ENT)),
        "relay": (2, 0, 1, dict(title=L("Retransmissão e mediador", "Relay and broker"), sub=L("[processo]", "[process]"), **PRO)),
        "svc": (2, 1, 2, dict(title=L("Serviço _ThingTracker_", "ThingTracker service"), sub=L("[processo, só texto]", "[process, text only]"),
                              body=[L("Contas, permissões, metadados, registo de eventos", "Accounts, permissions, metadata, event log")], **PRO)),
        "pg": (3, 2, 1, dict(title="PostgreSQL", sub=L("[arquivo, só texto]", "[store, text only]"), **STO)),
        "plat": (2, 3, 2, dict(title=L("Plataforma _Connected Home_", "Connected Home platform"), sub=L("[processo existente]", "[existing process]"),
                               body=[L("Servidor MCP, eventos, dispositivos", "MCP server, events, devices")], **dict(PRO, fill="#F2F3F5", stroke="#B8BEC6"))),
        "notif": (3, 3, 1, dict(title=L("Notificações", "Notifications"), sub=L("[processo existente]", "[existing process]"), **dict(PRO, fill="#F2F3F5", stroke="#B8BEC6"))),
        "app": (4, 0, 4, dict(title=L("Aplicação Altice", "Altice app"), sub=L("[processo existente]", "[existing process]"), **dict(PRO, fill="#F2F3F5", stroke="#B8BEC6"))),
        "fam": (4, 4, 1, dict(title=L("Família", "Family"), sub=L("[entidade externa]", "[external entity]"), **ENT)),
    }, min_row=64)
    for k in ("mem", "pg"):                              # a data store: two parallel lines, open at the sides
        x0, y0, x1, y1 = g.r[k]
        for yy in (y0, y1):
            cv.o.append(f'<line x1="{x0}" y1="{yy:.1f}" x2="{x1}" y2="{yy:.1f}" stroke="{BODY}" stroke-width="1.6"/>')
    B = BLUE
    g.h("cams", "dev", L("vídeo, rede da casa", "video, home network"))
    g.h2("mem", "dev", L("lê, compara", "reads, compares"), L("guarda", "stores"))
    g.h2("dev", "relay", L("F1 só texto", "F1 text only"), L("F2 pedidos, comandos", "F2 requests, commands"), color=B, lcolor=B)
    g.v2("relay", "svc", L("eventos, avisos", "events, alerts"), L("pedidos da aplicação", "app requests"), lw=110)
    g.h2("svc", "pg", L("grava", "writes"), L("lê", "reads"))
    g.h("router", "plat", L("F3 telemóveis no Wi-Fi", "F3 phones on the Wi-Fi"), color=B, lcolor=B)
    g.h2("door", "plat", L("F4 porta", "F4 door"), L("F5 comandos", "F5 commands"), color=B, lcolor=B)
    g.v2("svc", "plat", L("chamadas MCP", "MCP calls"), L("eventos: porta, Wi-Fi", "events: door, Wi-Fi"), lw=110)
    g.h("plat", "notif", L("avisos", "alerts"))
    g.h("notif", "app", L("F9 avisos", "F9 alerts"), color=B, lcolor=B)
    g.h("app", "relay", L("F8 fotografias de registo, cifradas", "F8 registration photos, encrypted"), color=B, lcolor=B)
    r1 = g.ys[1] + g.hs[1] / 2
    g.h("app", "svc", L("F6 frases, perguntas, “Sim”", "F6 sentences, questions, “Yes”"), color=B, lcolor=B, at=r1 - 14)
    g.h("svc", "app", L("F7 respostas, lista de objetos", "F7 answers, list of things"), color=B, lcolor=B, at=r1 + 14, below=True)
    g.v2("app", "fam", L("mostra", "shows"), L("usa", "uses"), lw=100)

    def bounds(b):
        def box(keys, title, fill):
            x0 = min(g.r[k][0] for k in keys) - 12
            y0 = min(g.r[k][1] for k in keys) - 44
            x1 = max(g.r[k][2] for k in keys) + 12
            y1 = max(g.r[k][3] for k in keys) + 18
            b.rect(x0, y0, x1 - x0, y1 - y0, fill=fill, stroke=WARN, rx=14, sw=1.6, dash="7 6")
            b.text(x0 + 14, y0 + 26, title, 13, True, WARN, max_w=x1 - x0 - 28)
        box(["cams", "mem", "dev", "router", "door"], L("Fronteira: casa", "Boundary: home"), HOME_BG)
        box(["relay", "svc", "pg", "plat", "notif"], L("Fronteira: Altice", "Boundary: Altice"), ALTICE_BG)
        box(["app", "fam"], L("Fronteira: telemóvel", "Boundary: phone"), PHONE_BG)
    bands_under(cv, bounds)
    y = max(r[3] for r in g.r.values()) + 46
    y = cv.para(40, y, L("Azul: fluxos que atravessam uma fronteira de confiança, descritos na tabela. Um modelo de linguagem externo (o "
                         "_ChatGPT_ ou o _Claude_ do próprio cliente, só texto) é uma opção futura, não incluída.",
                         "Blue: flows that cross a trust boundary, described in the table. An external language model (the customer’s "
                         "own ChatGPT or Claude, text only) is a possible future opt-in, not included."), W - 80, 12.5, fill=MUTED) + 8
    rows = [
        ("F1", L("equipamento da casa → retransmissão (casa → Altice)", "home device → relay (home → Altice)"),
         L("Só texto: eventos estruturados (“livro, secretária, 18h02”), avisos (título, mensagem, cartões de ação), rótulos (o nome da pessoa "
           "ou “desconhecido”) e o estado das regras. Nunca imagens, vídeo, assinaturas visuais nem padrões faciais",
           "Text only: structured events (“book, desk, 18:02”), alerts (title, message, action cards), labels (the person’s name or "
           "“unknown”) and the rules’ state. Never images, video, fingerprints or face templates"),
         L("mTLS, um certificado por casa", "mTLS, one certificate per home")),
        ("F2", L("retransmissão → equipamento da casa (Altice → casa)", "relay → home device (Altice → home)"),
         L("Eventos da porta e do Wi-Fi, pedidos da aplicação (frases, perguntas, “Sim”), comandos; as fotografias de registo, "
           "cifradas de ponta a ponta, que a Altice não consegue ler",
           "Door and Wi-Fi events, app requests (sentences, questions, “Yes”), commands; the registration photos, encrypted end "
           "to end, which Altice cannot read"), L("mTLS; cifra de ponta a ponta nas fotografias", "mTLS; end-to-end encryption for photos")),
        ("F3", L("_router_ → plataforma (casa → Altice)", "router → platform (home → Altice)"),
         L("Que telemóveis da família estão no Wi-Fi e quando entram ou saem (ferramenta MCP proposta)",
           "Which family phones are on the Wi-Fi, and when they join or leave (proposed MCP tool)"),
         L("O canal de gestão do _router_ da Altice (a confirmar)", "Altice’s router management channel (to confirm)")),
        ("F4", L("sensor da porta → plataforma (casa → Altice)", "door sensor → platform (home → Altice)"),
         L("Porta aberta ou fechada, como hoje", "Door open or closed, as today"), L("O canal da central (LTE), como hoje", "The hub’s channel (LTE), as today")),
        ("F5", L("plataforma → atuadores (Altice → casa)", "platform → actuators (Altice → home)"),
         L("Comandos depois de um “Sim”: luz, tomada, sirene", "Commands after a “Yes”: light, plug, siren"), L("Como hoje", "As today")),
        ("F6", L("aplicação → serviço (telemóvel → Altice)", "app → service (phone → Altice)"),
         L("Frases, perguntas, “Sim”; seguem para casa por F2", "Sentences, questions, “Yes”; passed on to the home through F2"),
         L("HTTPS, com a sessão da aplicação Altice", "HTTPS, with the Altice app’s session")),
        ("F7", L("serviço → aplicação (Altice → telemóvel)", "service → app (Altice → phone)"),
         L("Respostas e a lista de objetos, em texto", "Answers and the list of things, as text"), "HTTPS"),
        ("F8", L("aplicação → equipamento da casa", "app → home device"),
         L("Fotografias de registo: diretamente no Wi-Fi da casa ou pela retransmissão, cifradas de ponta a ponta. O equipamento da casa "
           "constrói a assinatura visual",
           "Registration photos: directly on the home Wi-Fi, or through the relay, encrypted end to end. The home device builds the "
           "fingerprint"), L("Cifra de ponta a ponta", "End-to-end encryption")),
        ("F9", L("notificações → aplicação (Altice → telemóvel)", "notifications → app (Altice → phone)"),
         L("Avisos em texto: título, mensagem, cartões de ação", "Alerts as text: title, message, action cards"),
         L("O serviço de notificações da aplicação", "The app’s notification service")),
    ]
    y = table(cv, 40, y + 10, [70, 380, 1100, W - 80 - 1550], [L("Fluxo", "Flow"), L("De → para", "From → to"), L("O que leva", "What it carries"),
                                                     L("Proteção", "Protection")], rows)
    y = cv.para(40, y + 30, L("Nunca atravessam a fronteira da casa: imagens, vídeo, assinaturas visuais e padrões faciais. Método: diagrama de "
                              "fluxo de dados com fronteiras de confiança, como no Microsoft SDL e no OWASP.",
                              "Never cross the home boundary: images, video, fingerprints and face templates. Method: a data-flow diagram with "
                              "trust boundaries, as in the Microsoft SDL and OWASP threat modelling."), W - 80, 12.5, fill=MUTED)
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
    xs = [40 + i * (cw + gap) for i in range(5)]
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
        "camera": [("PK", "id", "uuid"), ("FK", "home_id", FK("home")), ("", "altice_device_id", "text"), ("", "place", L("“Sala 1”", "“Living room 1”"))],
        "person_seen": [("PK", "id", "uuid"), ("FK", "camera_id", FK("camera")), ("", "ts", "timestamptz"),
                        ("", "label", L("membro, desconhecido…", "member, unknown…")), ("FK", "member_id", FK("member"))],
        "thing": [("PK", "id", "uuid"), ("FK", "home_id", FK("home")), ("", "name", "text"), ("", "query", L("palavra do detetor", "detector word")),
                  ("FK", "owner_id", FK("member")), ("FK", "usual_camera", FK("camera"))],
        "event": [("PK", "id", "uuid"), ("FK", "thing_id", FK("thing")), ("FK", "camera_id", FK("camera")), ("", "ts", "timestamptz"),
                  ("", "surface", L("secretária…", "desk…")), ("", "state", L("pousado, na mão…", "placed, in hand…")),
                  ("FK", "member_id", FK("member"))],
        "rule": [("PK", "id", "uuid"), ("FK", "home_id", FK("home")), ("", "sentence", "text"), ("", "compiled", "jsonb"),
                 ("FK", "owner_id", FK("member")), ("", "active", "bool"), ("", "siren", L("perguntar, logo", "ask, at once")),
                 ("", "scenario_id", "text")],
        "alert": [("PK", "id", "uuid"), ("FK", "rule_id", FK("rule")), ("", "ts", "timestamptz"), ("", "level", "text"), ("", "title", "text"),
                  ("", "message", "text"), ("", "actions", "jsonb"), ("", "answer", "text"),
                  ("FK", "answered_by", FK("member"))],
        "action_log": [("PK", "id", "uuid"), ("FK", "alert_id", FK("alert")), ("", "mcp_tool", "text"), ("", "args", "jsonb"),
                       ("", "result", "text"), ("", "ts", "timestamptz")],
    }
    hgt = lambda n: 32 + len(T[n]) * 21 + 10
    y0 = 30
    cx = lambda c: xs[c] + cw / 2
    hc = 2
    er_table(cv, xs[0], y0, cw, "customer", T["customer"])
    er_table(cv, xs[hc], y0, cw, "home", T["home"])
    er_line(cv, xs[0] + cw, y0 + 60, xs[hc], y0 + 60)
    row1 = {"member": 0, "camera": 1, "thing": 2, "event": 3, "rule": 4}
    y1 = y0 + max(hgt("customer"), hgt("home")) + 90
    bus = y1 - 44
    for n, c in row1.items():
        er_table(cv, xs[c], y1, cw, n, T[n])
    hb = y0 + hgt("home")
    cv.o.append(f'<line x1="{cx(hc):.1f}" y1="{hb}" x2="{cx(hc):.1f}" y2="{bus}" stroke="{BODY}" stroke-width="1.4"/>')
    cv.text(cx(hc) + 6, hb + 16, "1", 11, True, BLUE)
    cv.o.append(f'<line x1="{cx(0):.1f}" y1="{bus}" x2="{cx(4):.1f}" y2="{bus}" stroke="{BODY}" stroke-width="1.4"/>')
    for n in ("member", "camera", "thing", "rule"):
        c = row1[n]
        cv.o.append(f'<line x1="{cx(c):.1f}" y1="{bus}" x2="{cx(c):.1f}" y2="{y1}" stroke="{BODY}" stroke-width="1.4"/>')
        cv.text(cx(c) + 6, y1 - 8, "N", 11, True, BLUE)
    er_line(cv, xs[2] + cw, y1 + 60, xs[3], y1 + 60)
    y2 = y1 + max(hgt(n) for n in row1) + 60
    row2 = {"phone": 0, "person_seen": 1, "alert": 4}
    for n, c in row2.items():
        er_table(cv, xs[c], y2, cw, n, T[n])
    for parent, child, c in (("member", "phone", 0), ("camera", "person_seen", 1), ("rule", "alert", 4)):
        er_line(cv, cx(c), y1 + hgt(parent), cx(c), y2)
    y3 = y2 + max(hgt(n) for n in row2) + 60
    er_table(cv, xs[4], y3, cw, "action_log", T["action_log"])
    er_line(cv, cx(4), y2 + hgt("alert"), cx(4), y3)
    nx = xs[0]
    ny = y3 + 10
    notes = [L("Uma base PostgreSQL, só com texto; cada linha pertence a um cliente, com segurança ao nível da linha. Serve de cópia de "
               "segurança, sincroniza os telemóveis da família e repõe os metadados se a caixa da casa for trocada.",
               "One PostgreSQL database, text only; every row belongs to one customer, with row-level security. It is the backup, "
               "syncs the family’s phones and restores the metadata if the home box is replaced."),
             L("Nenhuma tabela guarda imagens, assinaturas visuais ou dados biométricos: `member` tem o nome, o papel e o registo do "
               "consentimento; as assinaturas visuais e os padrões faciais só existem no equipamento da casa.",
               "No table holds images, fingerprints or biometric data: `member` has the name, the role and the consent record; "
               "fingerprints and face templates exist only on the home device."),
             L("Retenção proposta: eventos e pessoas vistas, 30 dias; avisos e ações, 90 dias.",
               "Proposed retention: events and people seen, 30 days; alerts and actions, 90 days."),
             L("Linhas: 1 e N indicam quantos registos de cada lado. As chaves estrangeiras sem linha estão escritas no campo (→ tabela).",
               "Lines: 1 and N say how many records on each side. Foreign keys without a line are written in the field (→ table).")]
    yy = ny + 20
    for t in notes:
        yy = cv.para(nx, yy, t, xs[4] - gap - nx - 20, 12.5, fill=BODY) + 6
    cv.save("er-plataforma", round(max(yy, y3 + hgt("action_log")) + 24))


@view
def er_casa(lang):
    cw, gap = 250, 40
    xs = [40 + i * (cw + gap) for i in range(5)]
    W = xs[-1] + cw + 40
    cv = Canvas(W, lang, "Modelo de dados: casa" if lang == "pt" else "Data model: home")
    L = cv.L
    T = {
        "person": [("PK", "id", L("= `member.id`", "= `member.id`")), ("", "label", L("nome mostrado", "name shown"))],
        "face_template": [("PK", "id", "integer"), ("FK", "person_id", "→ person"), ("", "view_no", "1–8"),
                          ("", "feature", L("128 números", "128 numbers")), ("", "model", "SFace"), ("", "created_at", "timestamp")],
        "camera": [("PK", "id", "text"), ("", "rtsp_url", L("só na rede local", "local network only")), ("", "masks", "json")],
        "thing": [("PK", "id", L("= `thing.id`", "= `thing.id`")), ("", "name", "text"), ("", "query", L("palavra do detetor", "detector word")),
                  ("", "photo", L("imagem, só aqui", "image, only here"))],
        "fingerprint": [("PK", "id", "integer"), ("FK", "thing_id", "→ thing"), ("", "photo_no", "1–8"), ("", "embedding", L("384 números", "384 numbers")),
                        ("", "model", "DINOv2")],
        "sighting": [("PK", "id", "integer"), ("FK", "thing_id", "→ thing"), ("FK", "camera_id", "→ camera"), ("", "ts", "timestamp"),
                     ("", "surface", L("secretária…", "desk…")), ("", "state", L("pousado, na mão…", "placed, in hand…")),
                     ("", "match", "real"), ("", "thumb", L("imagem, só aqui", "image, only here"))],
        "rule": [("PK", "id", L("= `rule.id`", "= `rule.id`")), ("", "compiled", "json"), ("", "active", "bool")],
        "presence": [("PK", "id", "integer"), ("", "state", L("OCUPADA…", "OCCUPIED…")), ("", "since", "timestamp"),
                     ("", "members_home", "json"), ("", "reason", "text")],
        "outbox": [("PK", "id", "integer"), ("", "ts", "timestamp"), ("", "kind", L("evento, aviso", "event, alert")), ("", "payload", L("json, só texto", "json, text only")),
                   ("", "sent", "bool")],
        "setting": [("PK", "key", "text"), ("", "value", "text")],
    }
    hgt = lambda n: 32 + len(T[n]) * 21 + 10
    y0 = 92
    top = ("person", "camera", "thing", "rule", "setting")
    for c, n in enumerate(top):
        er_table(cv, xs[c], y0, cw, n, T[n])
    y1 = y0 + max(hgt(n) for n in top) + 60
    low = ("face_template", "sighting", "fingerprint", "presence", "outbox")
    for c, n in enumerate(low):
        er_table(cv, xs[c], y1, cw, n, T[n])
    for c, (p, ch) in enumerate((("person", "face_template"), ("camera", "sighting"), ("thing", "fingerprint"))):
        er_line(cv, xs[c] + cw / 2, y0 + hgt(p), xs[c] + cw / 2, y1)
    bot = y1 + max(hgt(n) for n in low)
    notes = [L("Uma base _SQLite_ cifrada no equipamento da casa (o _router_, se tiver NPU, ou uma caixa dedicada). As imagens, as "
               "assinaturas visuais e os padrões faciais só existem aqui.",
               "One encrypted SQLite database on the home device (the router, if it has an NPU, or a dedicated box). Images, "
               "fingerprints and face templates exist only here."),
             L("`face_template`: até 8 padrões por pessoa registada com consentimento; são apagados quando a pessoa retira o consentimento. "
               "`fingerprint`: um vetor por cada uma das 8 fotos do objeto.",
               "`face_template`: up to 8 templates per person registered with consent; deleted when the person withdraws consent. "
               "`fingerprint`: one vector for each of the thing’s 8 photos."),
             L("`outbox`: guarda eventos e avisos, em texto, enquanto não há internet; a análise de imagem continua sem internet. "
               "`thing`, `rule` e `person` usam os mesmos identificadores da plataforma, que guarda os seus nomes e regras.",
               "`outbox`: keeps events and alerts, as text, while offline; image analysis carries on without internet. `thing`, `rule` "
               "and `person` share the platform’s ids; the platform keeps their names and rules.")]
    yy = bot + 30
    for t in notes:
        yy = cv.para(xs[0], yy, t, W - 80, 12.5) + 6

    def zone(b):
        b.band(20, 20, W - 40, yy + 4 - 20, L("Equipamento da casa", "Home device"), None, fill=HOME_BG)
    bands_under(cv, zone)
    cv.save("er-casa", round(yy + 30))


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
            (L("Fotografias ou câmara", "Photos or camera"), L("6 a 8 fotografias com o telemóvel, enviadas ao equipamento da casa, ou mostrá-lo a uma câmara",
                                                             "6 to 8 photos with the phone, sent to the home device, or show it to a camera")),
            (L("Novo objeto", "New thing"), L("As fotos aprendidas e o nome; “Guardar”", "The learnt photos and the name; “Save”")),
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
            (L("Sugestão", "Suggestion"), L("“Tocar o alarme quando entrar alguém que não seja da família?”",
                                           "“Sound the alarm when someone who isn’t family comes in?”")),
        ]),
        (L("Cenário a partir de uma frase", "A scenario from a sentence"), [
            (L("Botão do assistente", "Assistant button"), L("Em qualquer separador", "On any tab")),
            (L("A frase", "The sentence"), L("“Avisa-me se sair de casa sem o livro”", "“Tell me if I leave home without my book”")),
            (L("A regra em palavras simples", "The rule in plain words"), L("O que observa, quando avisa, o que faz e a escolha para a sirene",
                                                                           "What it watches, when it alerts, what it does, and the siren choice")),
            (L("“Guardar”", "“Save”"), L("A regra passa a correr no equipamento da casa, a cada evento", "The rule now runs on the home device, on every event")),
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
            (L("Aviso", "Alert"), L("Título, mensagem e o que o motivou; a faixa da porta, quando é o caso",
                                   "Title, message and what caused it; the door banner, when relevant")),
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
