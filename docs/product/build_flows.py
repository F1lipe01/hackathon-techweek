#!/usr/bin/env python3
"""Draw the product spec's flow figures (docs/pt/20-produto.md and docs/20-product.md), in Portuguese and English.

    python3 docs/product/build_flows.py              # all four flows, PT and EN: SVG, then PNG with Chrome
    python3 docs/product/build_flows.py --lang pt    # Portuguese only
    python3 docs/product/build_flows.py --no-png     # SVG only (no Chrome)

Run it through video/tools/heavy.sh: it starts Chrome once per figure.

Each figure is a sequence of rows between lifelines, in the style of docs/architecture/build_diagram.py:
- a message is one straight, one-way arrow between two lifelines, labelled above its line (a two-way exchange is two
  arrows, each with its own label);
- a note is a box on one lifeline, for what happens inside that component;
- a band marks a jump in time.
Every string is measured with the font Chrome renders (Helvetica Neue) and wrapped to its box or its arrow; a string
that cannot fit stops the build. Words between underscores are drawn in italics (_ThingTracker_), as in the reports.
"""
import argparse
import re
import subprocess
from pathlib import Path

from PIL import ImageFont

HERE = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONT = "/System/Library/Fonts/HelveticaNeue.ttc"
INK, MUTED, BLUE, DEEP, LINE, SOFT = "#111", "#555", "#0084D6", "#003399", "#D0D0D0", "#EEF3FB"
NOTE_FILL, NOTE_LINE = "#E6F2FB", "#B9D7EE"            # what happens inside a component
FIRE_FILL, FIRE_LINE = "#FFF7EC", "#E8710A"            # a rule that fires
W = 1200
SIDE = 132                                              # x of the first and the last lifeline, from each edge
HEAD = 10                                               # arrowhead length

_fonts = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(FONT, size, index=1 if bold else 0)
    return _fonts[key]


def width(s, size=13.5, bold=False):
    return font(size, bold).getlength(s.replace("_", ""))


def wrap(s, max_w, size=13.5, bold=False):
    lines, cur = [], ""
    for word in s.split(" "):
        trial = f"{cur} {word}".strip()
        if cur and width(trial, size, bold) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    lines += [cur] if cur else []
    if len(lines) > 1:                                  # balance the lines, so no word is left alone on the last
        lo, hi = 0.0, max_w
        for _ in range(24):
            mid = (lo + hi) / 2
            lo, hi = (lo, mid) if len(_greedy(s, mid, size, bold)) <= len(lines) else (mid, hi)
        lines = _greedy(s, hi, size, bold)
    for ln in lines:
        assert width(ln, size, bold) <= max_w, f"'{ln}' is {width(ln, size, bold):.0f} wide, room {max_w:.0f}"
    return lines


def _greedy(s, max_w, size, bold):
    lines, cur = [], ""
    for word in s.split(" "):
        trial = f"{cur} {word}".strip()
        if cur and width(trial, size, bold) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + ([cur] if cur else [])


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Figure:
    def __init__(self, columns, title):
        self.cols = columns
        self.title = title
        n = len(columns)
        self.x = [SIDE + i * (W - 2 * SIDE) / (n - 1) for i in range(n)]
        self.gap = (W - 2 * SIDE) / (n - 1)
        self.out = []
        self.top = 20
        self.y = self.top + 64 + 34                    # below the header boxes

    def text(self, x, y, s, size=13.5, bold=False, fill=INK, anchor="middle", italic=False):
        body = re.sub(r"(?<![\w])_([^_]+)_(?![\w])", lambda m: f'<tspan font-style="italic">{m.group(1)}</tspan>', esc(s))
        st = ' font-style="italic"' if italic else ""
        self.out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{700 if bold else 400}" '
                        f'fill="{fill}" text-anchor="{anchor}"{st}>{body}</text>')

    def header(self):
        bw = min(self.gap - 16, 220)
        for x, (name, sub) in zip(self.x, self.cols):
            for s, size, bold in ((name, 15, True), (sub, 12.5, False)):
                assert width(s, size, bold) <= bw - 16, f"header '{s}' does not fit"
            self.out.append(f'<rect x="{x - bw / 2:.1f}" y="{self.top}" width="{bw:.1f}" height="64" rx="12" '
                            f'fill="#FFF" stroke="{LINE}" stroke-width="1.2"/>')
            self.text(x, self.top + 28, name, 15, True)
            self.text(x, self.top + 48, sub, 12.5, False, MUTED)

    def msg(self, a, b, label):
        """One straight arrow from lifeline a to lifeline b, its label above the line, wrapped to the span."""
        xa, xb = self.x[a], self.x[b]
        d = 1 if xb > xa else -1
        lines = wrap(label, abs(xb - xa) - 44, 13)
        y0 = self.y + 13
        for i, ln in enumerate(lines):
            lw = width(ln, 13) + 12                    # a white backing, so no lifeline crosses the words
            self.out.append(f'<rect x="{(xa + xb) / 2 - lw / 2:.1f}" y="{y0 + i * 17 - 13:.1f}" width="{lw:.1f}" '
                            f'height="17" fill="#FFF"/>')
            self.text((xa + xb) / 2, y0 + i * 17, ln, 13)
        ay = y0 + (len(lines) - 1) * 17 + 13
        x1, x2 = xa + d * 5, xb - d * (5 + HEAD)       # the line stops at the base of the head
        self.out.append(f'<line x1="{x1:.1f}" y1="{ay:.1f}" x2="{x2:.1f}" y2="{ay:.1f}" stroke="{INK}" '
                        f'stroke-width="1.5" marker-end="url(#ah)"/>')
        self.out.append(f'<circle cx="{xa:.1f}" cy="{ay:.1f}" r="4.5" fill="{BLUE}"/>')
        self.y = ay + 26

    def note(self, col, s, fire=False, width_cols=1.25):
        """A box on one lifeline: what happens inside that component. It may be wider than the gap between
        lifelines (it then covers its neighbours' dashed lines), but never wider than the canvas."""
        bw = min(self.gap * width_cols, 340)
        x = min(max(self.x[col] - bw / 2, 12), W - 12 - bw)
        lines = wrap(s, bw - 28, 13)
        h = 16 + 18 * len(lines)
        fill, line = (FIRE_FILL, FIRE_LINE) if fire else (NOTE_FILL, NOTE_LINE)
        self.out.append(f'<rect x="{x:.1f}" y="{self.y:.1f}" width="{bw:.1f}" height="{h}" rx="9" fill="{fill}" '
                        f'stroke="{line}" stroke-width="1.2"/>')
        for i, ln in enumerate(lines):
            self.text(x + bw / 2, self.y + 22 + i * 18, ln, 13)
        self.y += h + 22

    def band(self, s):
        """A jump in time, across the whole figure."""
        lines = wrap(s, W - 80, 13.5)
        h = 14 + 18 * len(lines)
        self.out.append(f'<rect x="10" y="{self.y:.1f}" width="{W - 20}" height="{h}" rx="7" fill="{SOFT}"/>')
        for i, ln in enumerate(lines):
            self.text(W / 2, self.y + 21 + i * 18, ln, 13.5, False, DEEP, italic=True)
        self.y += h + 24

    def svg(self):
        H = round(self.y + 4)
        lifelines = "".join(f'<line x1="{x:.1f}" y1="{self.top + 64}" x2="{x:.1f}" y2="{H - 12}" stroke="{LINE}" '
                            f'stroke-width="1.2" stroke-dasharray="4 4"/>' for x in self.x)
        self.header()                                  # header boxes last, so the lifelines start under them
        return H, (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
                   f'font-family="Helvetica Neue, Helvetica, Arial, sans-serif" role="img" aria-label="{esc(self.title)}">'
                   f'<title>{esc(self.title)}</title><defs><marker id="ah" viewBox="0 0 10 10" refX="0" refY="5" '
                   f'markerUnits="userSpaceOnUse" markerWidth="{HEAD}" markerHeight="{HEAD}" orient="auto">'
                   f'<path d="M0 1.6 L10 5 L0 8.4 Z" fill="{INK}"/></marker></defs>'
                   f'<rect width="{W}" height="{H}" fill="#FFF"/>{lifelines}' + "".join(self.out) + "</svg>")


# ---------------------------------------------------------------- the four flows, in Portuguese and in English
# Rows: ("msg", from, to, label) · ("note", column, text) · ("fire", column, text) · ("band", text)
APP_PT, APP_EN = ("Aplicação", "telemóvel da família"), ("App", "the family's phone")
SVC_PT, SVC_EN = ("Serviço _ThingTracker_", "plataforma Altice"), ("ThingTracker service", "Altice platform")
LLM_PT, LLM_EN = ("Modelo de linguagem", "fornecedor sob contrato"), ("Language model", "provider under contract")
EDGE_PT, EDGE_EN = ("Serviço local", "em casa, junto da câmara"), ("Edge service", "in the home, by the camera")
MCP_PT, MCP_EN = ("Servidor MCP e cenários", "plataforma Altice"), ("MCP server, scenarios", "Altice platform")

FLOWS = {
    "fluxo-animal": {
        "pt": ("Adicionar um animal e aprender a sua rotina", [APP_PT, SVC_PT, LLM_PT, EDGE_PT], [
            ("msg", 0, 1, "Novo animal: Mimi, gata, “cinzenta e tigrada”"),
            ("msg", 1, 2, "a descrição da Mimi, só em texto"),
            ("msg", 2, 1, "pesquisa ao detetor: “a grey tabby cat”"),
            ("msg", 1, 3, "aprender a Mimi: “a cat”, “a grey tabby cat”"),
            ("note", 3, "Durante 1 a 2 dias, guarda o vetor e o recorte de cada gato visto e agrupa os parecidos"),
            ("msg", 3, 1, "4 recortes do grupo maior"),
            ("msg", 1, 0, "“Acho que já conheço a Mimi. É ela?”"),
            ("msg", 0, 1, "“Sim”, e as taças da comida e da água marcadas na imagem"),
            ("msg", 1, 3, "assinatura confirmada; taças registadas"),
            ("band", "Durante 14 dias"),
            ("note", 3, "Uma visita conta quando a gata está sobre a taça durante 20 s ou mais"),
            ("msg", 3, 1, "visitas: taça, início e duração, sem imagens"),
            ("note", 1, "Calcula a rotina por estatística: refeições perto das 8h e das 19h30"),
            ("msg", 1, 2, "a rotina e a regra escolhida, em texto"),
            ("msg", 2, 1, "o texto da sugestão"),
            ("msg", 1, 0, "“Avisa-me se a Mimi não for à taça da comida até às 21h?”"),
            ("msg", 0, 1, "“Ativar”"),
            ("msg", 1, 3, "regra: nenhuma visita à taça da comida até às 21h"),
            ("band", "Num dia em que a Mimi não aparece"),
            ("fire", 3, "Motor de regras, às 21h: nenhuma visita desde as 8h05"),
            ("msg", 3, 1, "regra cumprida, com o recorte da taça"),
            ("msg", 1, 0, "Aviso: “A Mimi não foi à taça da comida desde as 8h05”"),
        ]),
        "en": ("Adding a pet and learning its routine", [APP_EN, SVC_EN, LLM_EN, EDGE_EN], [
            ("msg", 0, 1, "New pet: Mimi, a cat, “grey and tabby”"),
            ("msg", 1, 2, "Mimi’s description, as text only"),
            ("msg", 2, 1, "detector query: “a grey tabby cat”"),
            ("msg", 1, 3, "learn Mimi: “a cat”, “a grey tabby cat”"),
            ("note", 3, "For 1 to 2 days, keeps the vector and crop of every cat it sees and groups the similar ones"),
            ("msg", 3, 1, "4 crops from the largest group"),
            ("msg", 1, 0, "“I think I know Mimi now. Is this her?”"),
            ("msg", 0, 1, "“Yes”, and the food and water bowls marked on the image"),
            ("msg", 1, 3, "fingerprint confirmed; bowls registered"),
            ("band", "For 14 days"),
            ("note", 3, "A visit counts when the cat is over the bowl for 20 s or more"),
            ("msg", 3, 1, "visits: bowl, start and duration, no images"),
            ("note", 1, "Works out the routine with statistics: meals around 8:00 and 19:30"),
            ("msg", 1, 2, "the routine and the chosen rule, as text"),
            ("msg", 2, 1, "the wording of the suggestion"),
            ("msg", 1, 0, "“Tell me if Mimi has not been to the food bowl by 21:00?”"),
            ("msg", 0, 1, "“Turn on”"),
            ("msg", 1, 3, "rule: no visit to the food bowl by 21:00"),
            ("band", "On a day when Mimi does not show up"),
            ("fire", 3, "Rules engine, at 21:00: no visit since 8:05"),
            ("msg", 3, 1, "rule met, with the crop of the bowl"),
            ("msg", 1, 0, "Alert: “Mimi has not been to the food bowl since 8:05”"),
        ]),
    },
    "fluxo-pessoa": {
        "pt": ("Adicionar uma pessoa, com consentimento", [("Administrador", "aplicação do Rui"),
                                                        ("Pessoa convidada", "aplicação da Ana"), SVC_PT, EDGE_PT], [
            ("msg", 0, 2, "convite: Ana, adulta; pedir para a reconhecer"),
            ("msg", 2, 1, "o convite, com o que se guarda, onde e para quê"),
            ("note", 1, "A Ana lê e escolhe. Nada vem pré-selecionado, e recusar não tem outra consequência"),
            ("msg", 1, 2, "“Aceito ser reconhecida”, com a hora e a versão do texto"),
            ("note", 2, "Guarda o registo do consentimento, nunca dados biométricos"),
            ("msg", 2, 3, "inscrever a Ana na câmara da Entrada"),
            ("note", 3, "A Ana vira a cabeça em frente à câmara durante 10 s. O padrão facial fica cifrado, só em casa, "
                        "e as imagens são apagadas"),
            ("msg", 3, 2, "inscrição concluída, sem imagens nem padrão"),
            ("msg", 2, 1, "“Passas a ser reconhecida”"),
            ("msg", 2, 0, "“A Ana passa a ser reconhecida”"),
            ("band", "Mais tarde, alguém entra em casa"),
            ("note", 3, "Compara o rosto com os padrões da casa; um rosto sem correspondência é descartado na própria análise"),
            ("msg", 3, 2, "evento “A Ana chegou”, só com o nome"),
            ("band", "Se a Ana retirar o consentimento"),
            ("msg", 1, 2, "“Deixar de ser reconhecida”"),
            ("msg", 2, 3, "apagar o padrão facial da Ana"),
            ("msg", 3, 2, "apagado: confirmação"),
            ("note", 2, "Registo de auditoria: a retirada e o apagamento, sem dados biométricos"),
            ("band", "Para uma criança, consente quem tem a responsabilidade parental, na sua própria aplicação"),
        ]),
        "en": ("Adding a person, with consent", [("Administrator", "Rui’s app"), ("Invited person", "Ana’s app"),
                                                SVC_EN, EDGE_EN], [
            ("msg", 0, 2, "invitation: Ana, adult; ask to recognise her"),
            ("msg", 2, 1, "the invitation, with what is kept, where and why"),
            ("note", 1, "Ana reads and decides. Nothing is preselected, and saying no has no other consequence"),
            ("msg", 1, 2, "“I agree to be recognised”, with the time and the text version"),
            ("note", 2, "Keeps the record of consent, never biometric data"),
            ("msg", 2, 3, "enrol Ana at the Entrance camera"),
            ("note", 3, "Ana turns her head in front of the camera for 10 s. The face template is encrypted and stays in "
                        "the home; the images are deleted"),
            ("msg", 3, 2, "enrolment done, with no images or template"),
            ("msg", 2, 1, "“You are now recognised”"),
            ("msg", 2, 0, "“Ana is now recognised”"),
            ("band", "Later, someone comes in"),
            ("note", 3, "Compares the face with the home’s templates; a face with no match is discarded within the same analysis"),
            ("msg", 3, 2, "event “Ana is home”, with the name only"),
            ("band", "If Ana withdraws her consent"),
            ("msg", 1, 2, "“Stop recognising me”"),
            ("msg", 2, 3, "delete Ana’s face template"),
            ("msg", 3, 2, "deleted: confirmation"),
            ("note", 2, "Audit log: the withdrawal and the deletion, with no biometric data"),
            ("band", "For a child, a holder of parental responsibility consents, in their own app"),
        ]),
    },
    "fluxo-frase": {
        "pt": ("Da frase às regras e aos avisos", [APP_PT, SVC_PT, LLM_PT, MCP_PT, EDGE_PT], [
            ("msg", 0, 1, "“Avisa-me se a criança estiver em perigo”"),
            ("msg", 1, 2, "frase, perfil da casa, _things_, câmaras, dispositivos e catálogo de deteções, só em texto"),
            ("msg", 2, 1, "plano: as regras e o que não consegue vigiar"),
            ("note", 1, "Valida cada regra: deteções do catálogo, câmaras e dispositivos que existem, ações permitidas",
             1.4),
            ("msg", 1, 0, "o plano em linguagem corrente, para confirmar"),
            ("note", 0, "O utilizador escolhe as regras, os horários e quem é avisado"),
            ("msg", 0, 1, "“Ativar em ensaio”"),
            ("msg", 1, 3, "post_new_scenario, com o acionador thingTracker"),
            ("msg", 3, 4, "condições e pesquisas: “a knife”, “a stove”, “a child”"),
            ("note", 4, "Ensaio de 48 h: regista o que teria avisado, sem avisar"),
            ("msg", 4, 1, "o que teria avisado, com as provas"),
            ("msg", 1, 0, "“Teria avisado 3 vezes. Estava certo?”"),
            ("msg", 0, 1, "as respostas e “Ativar”"),
            ("band", "Mais tarde, na cozinha"),
            ("fire", 4, "Motor de regras: a criança está junto ao fogão há 5 s"),
            ("msg", 4, 1, "regra cumprida, com o recorte do fogão"),
            ("msg", 1, 3, "update_device_capabilities: lâmpada vermelha"),
            ("msg", 1, 0, "aviso urgente, com a prova e “Tocar a sirene?”"),
            ("note", 0, "Sem resposta em 2 min, segue para o segundo contacto; a sirene só toca com um “sim”", 1.4),
        ]),
        "en": ("From a sentence to rules and alerts", [APP_EN, SVC_EN, LLM_EN, MCP_EN, EDGE_EN], [
            ("msg", 0, 1, "“Tell me if the child is in danger”"),
            ("msg", 1, 2, "sentence, home profile, things, cameras, devices and detection catalogue, as text only"),
            ("msg", 2, 1, "plan: the rules and what it cannot watch"),
            ("note", 1, "Checks every rule: detections from the catalogue, cameras and devices that exist, allowed actions",
             1.4),
            ("msg", 1, 0, "the plan in plain words, to confirm"),
            ("note", 0, "The user picks the rules, the hours and who is told"),
            ("msg", 0, 1, "“Turn on in trial”"),
            ("msg", 1, 3, "post_new_scenario, with the thingTracker trigger"),
            ("msg", 3, 4, "conditions and queries: “a knife”, “a stove”, “a child”"),
            ("note", 4, "48 h trial: logs what it would have alerted, without alerting"),
            ("msg", 4, 1, "what it would have alerted, with the evidence"),
            ("msg", 1, 0, "“I would have alerted 3 times. Was I right?”"),
            ("msg", 0, 1, "the answers and “Turn on”"),
            ("band", "Later, in the kitchen"),
            ("fire", 4, "Rules engine: the child has been by the stove for 5 s"),
            ("msg", 4, 1, "rule met, with the crop of the stove"),
            ("msg", 1, 3, "update_device_capabilities: red light"),
            ("msg", 1, 0, "urgent alert, with the evidence and “Sound the siren?”"),
            ("note", 0, "No answer in 2 min: it goes to the second contact; the siren sounds only after a “yes”", 1.4),
        ]),
    },
    "fluxo-linha-do-tempo": {
        "pt": ("A linha do tempo da casa, do evento invulgar à exportação", [APP_PT, SVC_PT, LLM_PT, EDGE_PT], [
            ("band", "4h02, na noite em que a casa da vizinha é assaltada"),
            ("note", 3, "Movimento e latido na Entrada 1, a uma hora em que quase nunca há: evento invulgar"),
            ("msg", 3, 1, "evento invulgar: tipo, hora, câmara e recorte do Bobi; o som não é gravado"),
            ("note", 1, "Entra na linha do tempo como “informação”: não acorda ninguém"),
            ("band", "De manhã, a vizinha conta o que aconteceu"),
            ("msg", 0, 1, "“O que aconteceu às 4h?”"),
            ("note", 1, "O código traduz a pergunta: das 3h45 às 4h15, todas as câmaras"),
            ("msg", 1, 3, "get_home_timeline, das 3h45 às 4h15"),
            ("msg", 3, 1, "os eventos, em texto, e os recortes"),
            ("msg", 1, 2, "as linhas de texto dos eventos"),
            ("msg", 2, 1, "resumo: “O Bobi ladrou e mexeu-se na entrada às 4h02”"),
            ("msg", 1, 0, "o resumo, com os recortes e as horas"),
            ("note", 0, "Fixa o evento, guardado até um ano, e partilha só a hora com a vizinha"),
            ("msg", 0, 1, "“Exportar para as autoridades”, confirmado por um adulto"),
            ("msg", 1, 3, "pedir os ficheiros originais do evento"),
            ("msg", 3, 1, "recortes, resumos criptográficos e assinatura do equipamento"),
            ("msg", 1, 0, "pacote: PDF e ficheiros verificáveis, ligação válida 7 dias"),
            ("note", 1, "Registo de auditoria: quem exportou, o quê e quando"),
        ]),
        "en": ("The home timeline, from an unusual event to an export", [APP_EN, SVC_EN, LLM_EN, EDGE_EN], [
            ("band", "4:02, the night the neighbour’s house is burgled"),
            ("note", 3, "Movement and barking at Entrance 1, at an hour when there almost never is any: unusual event"),
            ("msg", 3, 1, "unusual event: type, time, camera and a crop of Bobi; the sound is not recorded"),
            ("note", 1, "Goes into the timeline as “information”: it wakes no one"),
            ("band", "In the morning, the neighbour tells what happened"),
            ("msg", 0, 1, "“What happened at 4:00?”"),
            ("note", 1, "The code turns the question into a search: 3:45 to 4:15, every camera"),
            ("msg", 1, 3, "get_home_timeline, 3:45 to 4:15"),
            ("msg", 3, 1, "the events, as text, and the crops"),
            ("msg", 1, 2, "the events’ lines of text"),
            ("msg", 2, 1, "summary: “Bobi barked and moved at the entrance at 4:02”"),
            ("msg", 1, 0, "the summary, with the crops and the times"),
            ("note", 0, "Pins the event, kept up to a year, and shares only the time with the neighbour"),
            ("msg", 0, 1, "“Export for the police”, confirmed by an adult"),
            ("msg", 1, 3, "fetch the event’s original files"),
            ("msg", 3, 1, "crops, cryptographic hashes and the device’s signature"),
            ("msg", 1, 0, "package: PDF and verifiable files, link valid for 7 days"),
            ("note", 1, "Audit log: who exported what, and when"),
        ]),
    },
}


def build(name, lang, png):
    title, cols, rows = FLOWS[name][lang]
    f = Figure(cols, title)
    for row in rows:
        kind = row[0]
        if kind == "msg":
            f.msg(*row[1:])
        elif kind == "note":
            f.note(row[1], row[2], width_cols=row[3] if len(row) > 3 else 1.25)
        elif kind == "fire":
            f.note(row[1], row[2], fire=True)
        else:
            f.band(row[1])
    H, svg = f.svg()
    suffix = ".en" if lang == "en" else ""
    svg_path = HERE / f"{name}{suffix}.svg"
    svg_path.write_text(svg + "\n", encoding="utf8")
    if png:
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                        f"--window-size={W},{H}", f"--screenshot={HERE / f'{name}{suffix}.png'}", svg_path.as_uri()],
                       check=True, capture_output=True)
    print(f"built {svg_path.name}{' and .png' if png else ''} ({W}x{H})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Draw the product spec's flow figures.")
    ap.add_argument("--lang", choices=["pt", "en", "all"], default="all")
    ap.add_argument("--no-png", action="store_true", help="write the SVG files only")
    args = ap.parse_args()
    for name in FLOWS:
        for lang in (["pt", "en"] if args.lang == "all" else [args.lang]):
            build(name, lang, not args.no_png)
