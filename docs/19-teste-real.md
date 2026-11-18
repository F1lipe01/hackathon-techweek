# Teste real no laboratório: o livro esquecido em casa

Lista de verificação para quinta-feira, 19 de novembro de 2026. Objetivo: gravar o cenário completo com o _kit_, sem nada simulado. O livro amarelo (_O ano da morte de Ricardo Reis_) está registado na câmara do _kit_; alguém sai pela porta, onde está o sensor de contacto real, sem o livro; a lâmpada do _kit_ fica vermelha e o alerta chega à aplicação com a fotografia do livro e o último lugar onde foi visto.

Duas regras valem durante todo o teste:

- A lâmpada só muda realmente de cor com `TT_LIVE_ACTIONS=1`, e só depois de a equipa o aprovar explicitamente na conversa. Sem essa variável, o servidor escreve a chamada exata ao MCP na atividade e não a envia.
- Um trabalho pesado de cada vez: durante o teste não há _renders_, codificações de vídeo nem modelos a correr sobre clips (ver `video/tools/heavy.sh` e a regra 5 do `AGENTS.md`).

## 1. Antes de começar

1. O _gateway_ está ligado ao cabo de rede do laboratório e o _hotspot_ de 2,4 GHz do Redmi 17 está ligado, com o SSID do _kit_ (os dispositivos Wi-Fi, como a lâmpada, a câmara e a tomada, só funcionam com ele).
2. O sensor de contacto e o íman estão colados na porta do laboratório, alinhados. Com a porta fechada, a aplicação Altice mostra “Closed”; ao abrir, “Open”.
3. A lâmpada está num casquilho com corrente.

## 2. Sessão do MCP

1. `python3 mcp/client/chmcp.py login`. Abre-se o navegador: entrar com a conta da equipa. Os _tokens_ ficam em `mcp/client/.tokens.json` (fora do repositório) e duram cerca de 24 horas.
2. Confirmar com uma leitura (ferramenta só de leitura): `python3 mcp/client/chmcp.py call get_home_devices '{}'`. No “Contact sensor”, `sensorState` deve ser `normal` com a porta fechada e `alarm` com a porta aberta.
3. Não é preciso reiniciar o servidor: este tenta a sessão a cada 15 s. Quando a deteta, a etiqueta no topo da página passa a dizer “devices live from the MCP” e o botão “Simulate: door opens” desaparece. A partir daí, o servidor lê o sensor a cada 4 s com `get_home_devices`, que é só de leitura.

## 3. Voltar a ligar a lâmpada

A lâmpada aparece “Disconnected” desde 4 de novembro (`docs/11-project-baseline.md`).

1. Com o _hotspot_ ligado, desligar a lâmpada no interruptor durante 10 s e voltar a ligá-la. Um dispositivo que passou horas sem rede espera mais tempo antes de tentar outra vez; reiniciá-lo faz com que tente logo.
2. Esperar 1 a 2 minutos e confirmar na aplicação Altice, ou no separador _Devices_ da página, que deixou de estar “Disconnected”. A atividade da página regista “Light is online.”
3. Se continuar desligada ao fim de 5 minutos, a lâmpada pode ter de ser emparelhada de novo na aplicação Altice. Não há procedimento testado: falar com a Altice Labs.
4. A escrita de cor nunca foi testada com a lâmpada ligada. Antes de gravar, fazer um único teste acompanhado, com a aprovação da equipa (passo 5.4).

## 4. Arrancar os serviços, por esta ordem

```
prototype/.venv-llm/bin/python prototype/llm_local.py       # 1. modelo de texto local, porta 8766
prototype/.venv/bin/python prototype/server.py              # 2. aplicação e API, http://127.0.0.1:8765
prototype/.venv-vision/bin/python prototype/edge.py         # 3. serviço da câmara (OWLv2 e DINOv2)
```

Abrir http://127.0.0.1:8765 no Chrome. Sobre a imagem da câmara deve aparecer a etiqueta “Camera idle” (ou “Camera analysing”, quando há movimento).

## 5. Preparar o cenário

1. Registar o livro: separador _Things_ → “+” → “Other…” → escrever `yellow book` (o detetor procura o texto em inglês). Segurar o livro a cerca de 50 cm da câmara do _kit_ e rodá-lo devagar durante 10 a 20 s, até às 8 vistas.
2. Verificar a assinatura visual: na página do livro, “Visual fingerprint · 8 views”, e as 8 imagens mostram o livro (não a mão nem a cara). Se não, “Remove thing” e registar de novo.
3. Pousar o livro na mesa, à vista da câmara. Em poucos segundos, o separador _Things_ mostra “On the table” com a hora, e a atividade “… seen on the table”.
4. Criar o sensor: botão do assistente → `avisa-me se eu sair de casa sem o livro`. A atividade regista “New sensor”. O sensor fica do tipo `leave_without`, com a ação `light_red` (alerta mais luz vermelha, como a equipa escolheu).
5. Só com a aprovação da equipa: parar o servidor (`kill $(lsof -t -iTCP:8765 -sTCP:LISTEN)`) e arrancá-lo com `TT_LIVE_ACTIONS=1 prototype/.venv/bin/python prototype/server.py`. A etiqueta do topo passa a dizer “actions LIVE”.

## 6. O teste

1. Porta fechada, livro na mesa, ninguém a mexer-lhe.
2. Começar as gravações (secção 7).
3. Uma pessoa sai pela porta sem o livro.
4. Em cerca de 10 s (até 4 s de leitura do sensor, 5 s de espera e 2 s do motor de regras), espera-se:
   - na atividade, “The door opened (Contact sensor).”;
   - o alerta, com a fotografia do livro e “Última deteção: na mesa (Work Room), hoje às …”, no aviso da aplicação e em _Menu_ → _Notifications_;
   - a lâmpada vermelha, com `TT_LIVE_ACTIONS=1`. Sem essa variável, a atividade mostra “MCP dry run, not sent” e as duas chamadas exatas (abaixo).
5. Fechar a porta. Para repetir, esperar 5 minutos (o sensor não volta a disparar antes disso) ou encurtar a espera para 60 s: `curl -X PATCH http://127.0.0.1:8765/api/rules/<id> -H 'Content-Type: application/json' -d '{"cooldown_s": 60}'` (o `<id>` vem de `curl -s http://127.0.0.1:8765/api/state`, em `rules`).
6. No fim, a equipa repõe a cor da lâmpada na aplicação Altice.

As chamadas que a ação `light_red` faz, por esta ordem (`prototype/actions.py`):

```
update_device_capabilities {"deviceId": "00e038d4-0da7-45c2-b61f-f38c9ff9df82", "body": {"type": "power", "value": "on"}}
update_device_capabilities {"deviceId": "00e038d4-0da7-45c2-b61f-f38c9ff9df82", "body": {"type": "color_rgb", "redValue": 255, "greenValue": 0, "blueValue": 0}}
```

Não filmar como sucesso o caso contrário (a pessoa leva o livro). Sem uma câmara na entrada, o protótipo não vê o livro a sair e também dispara. É uma limitação conhecida e está documentada em `check_leave_without()`, no `server.py`.

## 7. Gravação

- A câmara do _kit_, com as caixas: `prototype/.venv/bin/python prototype/record.py --seconds 120 --name teste-real`. O vídeo e as caixas ficam em `prototype/data/recordings/`, que nunca vai para o repositório.
- A página: gravação do ecrã do Mac (Cmd+Shift+5), com a janela a 1440 px de largura.
- A lâmpada e a porta: um telemóvel a filmar, porque a luz não aparece na câmara do _kit_.
- Pessoas: quem aparece em qualquer das gravações tem de concordar antes de a imagem ser usada no _pitch_, incluindo quem estiver ao fundo, de outras equipas. Sem acordo, desfocar, ou enquadrar só a porta e as mãos.

## 8. Se falhar

| Sintoma | Verificar | O que fazer |
|---|---|---|
| A etiqueta diz “devices: copy of 18 Nov” | A sessão do MCP | Repetir o passo 2.1 e esperar 15 s |
| A porta abre e a atividade não regista nada | `chmcp.py call get_home_devices '{}'`: o `sensorState` muda? | Alinhar o íman; confirmar na aplicação Altice |
| A porta é registada, mas não há alerta | A atividade diz que a câmara nunca viu o livro? O sensor disparou há menos de 5 minutos? | Pôr o livro à vista e esperar por “seen on the table”; encurtar a espera (passo 6.5) |
| Alerta sem luz vermelha | A atividade diz “dry run” ou “sent → error”? | Sem `TT_LIVE_ACTIONS=1`, é o esperado; com erro, a lâmpada está desligada (secção 3) |
| A câmara não vê o livro | A etiqueta da câmara aparece? A luz da sala chega? | Arrancar o `edge.py`; aproximar o livro; registar de novo |
| Nada funciona a tempo | — | Plano B: com a sessão do MCP desligada, o botão “Simulate: door opens” abre a porta simulada e a ação fica em _dry run_. No vídeo, dizer que é uma simulação |
