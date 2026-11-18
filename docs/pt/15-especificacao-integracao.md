# _ThingTracker_ · integração com a plataforma _Cognitive Home_

Versão 1, quarta-feira, 18 de novembro de 2026. Documento destinado aos engenheiros da Altice Labs, que descreve o que o _ThingTracker_ acrescenta à plataforma e o que dela necessita. A visão de conjunto da solução encontra-se no documento de arquitetura.

## 1. Resumo

| O que o _ThingTracker_ acrescenta | O que o _ThingTracker_ utiliza, sem alterações |
|---|---|
| Quatro ferramentas MCP (“_Model Context Protocol_”) para objetos: `list_things`, `create_thing`, `get_thing_last_seen`, `get_thing_timeline` | `update_device_capabilities` (lâmpada, tomada) |
| Um serviço _edge_ em cada casa, que só analisa imagens quando há movimento ou som e comunica com a plataforma por um único canal autenticado | `patch_home_security_status` (alarme), sempre com confirmação prévia do utilizador |
| Um separador “_Things_” na aplicação Altice | `post_new_scenario`, `get_home_scenarios` (regras apresentadas como cenários) |
| O Serviço _ThingTracker_, do lado da plataforma, o único componente que chama o modelo de linguagem | `get_home_devices`, `get_home_security_status` (contexto para as regras) |

Não se cria nenhum caminho novo até aos dispositivos, uma vez que todos os comandos continuam a passar pelas ferramentas que a plataforma já disponibiliza.

## 2. As quatro ferramentas _Things_

As novas ferramentas seguem as convenções das já existentes, com argumentos em JSON, âmbito restrito à casa do utilizador autenticado e resultados em texto JSON. São sobretudo de leitura, e só a `create_thing` altera dados.

### `list_things`

Lista os objetos seguidos numa casa, com a última deteção de cada um.

| Argumento | Tipo | Obrigatório | Notas |
|---|---|---|---|
| `homeId` | _string_ | não | Por omissão, a casa atual do utilizador, tal como nas restantes ferramentas |

Resultado:
```json
{ "things": [
  { "id": "keys", "name": "Keys", "photo": "https://…/things/keys.jpg",
    "lastSeen": { "place": "Hall table", "camera": "Living room", "at": "2026-11-18T08:42:10Z" } },
  { "id": "phone", "name": "Phone", "photo": null, "lastSeen": null }
] }
```

### `create_thing`

Inicia o seguimento de um objeto. As assinaturas visuais são calculadas no _edge_ pelo componente Registo de objetos, descrito na secção 4, que reúne o contexto de cada objeto (nome, assinatura visual e lugar habitual). Esta ferramenta guarda o nome e desencadeia esse processo.

| Argumento | Tipo | Obrigatório | Notas |
|---|---|---|---|
| `name` | _string_, de 1 a 40 caracteres | sim | `"Keys"`, `"Mia's water bowl"` |
| `category` | _string_ | não | Indicação para o detetor, como `"keys"`, `"wallet"` ou `"mug"` |
| `enrol` | _enum_ `camera` / `photos` / `none` | não | Por omissão, `camera`, caso em que a aplicação pede ao utilizador que mostre o objeto a uma câmara |

Resultado: `{ "id": "keys", "status": "enrolling" }`. Erros: `409` se o nome já existir e `422` se a casa não tiver nenhuma câmara.

### `get_thing_last_seen`

Responde à pergunta “onde está X?”.

| Argumento | Tipo | Obrigatório |
|---|---|---|
| `thing` | id ou nome | sim |

Resultado:
```json
{ "thing": "keys", "place": "Hall table", "camera": "Living room",
  "at": "2026-11-18T08:42:10Z", "confidence": 0.86,
  "position": "next to the bowl", "thumbnail": "https://…/sightings/9f2c.jpg" }
```
Se o objeto nunca tiver sido visto, os campos vêm a `null` e o resultado inclui `"seen": false`. A miniatura é um recorte que mostra apenas o objeto, nunca a imagem completa.

### `get_thing_timeline`

Indica por onde andou um objeto ao longo de um período, para responder a perguntas como “quando é que tive os óculos comigo pela última vez?”.

| Argumento | Tipo | Obrigatório | Notas |
|---|---|---|---|
| `thing` | id ou nome | sim | |
| `from`, `to` | ISO 8601 | não | Por omissão, as últimas 24 h; no máximo, 30 dias |

Resultado: `{ "thing": "glasses", "sightings": [ { "place": "Desk", "from": "…", "to": "…" }, … ] }`, em que as deteções consecutivas no mesmo lugar são agregadas numa só.

## 3. Serviço _edge_ ↔ plataforma

| Aspeto | Proposta |
|---|---|
| Ligação | O _edge_ abre uma única ligação de saída para a plataforma (WebSocket ou MQTT sobre TLS), pelo que a casa não precisa de nenhuma porta de entrada aberta |
| Identidade | Uma credencial por _edge_, ou seja, por casa, emitida quando a câmara é adicionada na aplicação e revogável a partir desta |
| _Edge_ → plataforma | Eventos (`thing.seen`, `thing.moved`, `sensor.fired`), miniaturas e assinaturas visuais dos objetos e respostas às ferramentas _Things_ |
| Plataforma → _edge_ | Regras (sensores compilados), chamadas às ferramentas _Things_, pedidos para iniciar o registo de um objeto, máscaras e lugares |
| Sem ligação | O _edge_ continua a seguir os objetos e o Motor de regras continua a avaliar as regras locais; os eventos ficam em fila e seguem quando a ligação é restabelecida, mas as ações sobre dispositivos dependem da plataforma |
| Modelo de linguagem | Chamado pelo Serviço _ThingTracker_, na plataforma, que escolhe o modelo e a região utilizados, e nunca pelo _edge_ |

## 4. Registo de objetos na aplicação

A tabela seguinte descreve a forma como a aplicação adiciona hoje um dispositivo, com base numa gravação de ecrã feita no telemóvel da equipa com a versão beta da aplicação Altice, a 18 de novembro de 2026, sem que nenhum dispositivo tenha sido instalado.

| Passo | O que a aplicação mostra |
|---|---|
| “_Devices_” → (+) | O ecrã “_Add device_”, com um cartão de pesquisa em curso (“_Looking for nearby Matter devices…_”), o filtro “_Works with: Matter_” e, a seguir, “_Available devices (20)_”, com um cartão por tipo de dispositivo (ícone e nome, e o selo _Matter_ quando se aplica). Ao percorrer a lista, o título grande recolhe para a barra superior |
| Escolha do tipo | Um passo em ecrã inteiro, com ✕ no canto superior esquerdo, a ilustração do dispositivo, um título centrado (“_Install your camera_”, “_Plug in your plug_”), uma linha de ajuda, o campo ou a opção a escolher e o botão principal fixo no fundo do ecrã, inativo enquanto o passo não for válido |
| Câmara | Número de série introduzido manualmente ou lido com “_Scan label_” (código QR), seguido de “_Next_” |
| Tomada | Modo “_Easy_” ou “_Advanced_” e, depois, um passo de configuração do Wi-Fi a 2,4 GHz (rede e palavra-passe), com “_Previous_” e “_Next_” |
| Sensores | Primeiro, um painel inferior, “_Choose a security hub_”, com as centrais instaladas e o respetivo estado |
| Pré-requisito em falta | Um painel inferior com ilustração e a pergunta “_No smart hub installed… Do you want to install it now?_” |
| ✕ em qualquer passo | Um pedido de confirmação, “_Cancel installation_”, com as opções “_Yes, cancel_” e “_No, continue_” |

O fluxo para adicionar um objeto (“_Add a thing_”) segue o mesmo padrão, para que se integre de forma natural na aplicação.

| Fluxo de um dispositivo | Fluxo de um objeto |
|---|---|
| (+) em “_Devices_” | (+) em “_Things_” |
| Lista de tipos de dispositivo e dispositivos _Matter_ encontrados nas proximidades | “_Suggested_”, com os objetos que a câmara já vê na divisão e os respetivos recortes, ou uma lista de objetos comuns (chaves, carteira, óculos, telemóvel, caneca, portátil, comando da televisão) e “_Other…_” para escrever um nome |
| Painel “_Choose a security hub_” | Painel “_Choose a camera_”, com as câmaras e o respetivo estado |
| Painel “_No smart hub installed_” | Painel “_No camera installed_” (erro `422` da `create_thing`) |
| Número de série ou “_Scan label_” | “_Show it to the camera_” (cerca de 3 s, com o progresso em tempo real) ou 3 fotografias tiradas com o telemóvel |
| Passo final | O recorte aprendido, o nome e, opcionalmente, um lugar (“_usually on the hall table_”), seguidos de “_Done_” |
| “_Cancel installation_” | O mesmo diálogo, com a pergunta “_Cancel adding this thing?_” |

Em seguida, o registo do objeto decorre da seguinte forma:

1. Aplicação: “_Things_” → (+) → nome (ou escolha de uma sugestão) → “_Show it to the camera_”.
2. Plataforma → _edge_: `enrol(thing, camera)`.
3. _Edge_: durante cerca de 3 s, o Registo de objetos deteta o objeto nas imagens, guarda cerca de 8 recortes, calcula a assinatura visual e devolve uma fotografia.
4. Aplicação: mostra a fotografia, e o utilizador confirma-a ou repete o processo.

A assinatura visual fica guardada no _edge_, para os modelos locais, e na base de dados da plataforma, associada ao cliente. É apagada quando o objeto é eliminado.

## 5. Sensores e cenários

O modelo de linguagem, chamado pelo Serviço _ThingTracker_, compila numa regra cada sensor descrito por uma frase (ver a secção 5 do documento de arquitetura).

- As condições e ações sobre dispositivos (contacto da porta, cor da lâmpada, tomada) têm correspondência no modelo de cenários da plataforma, pelo que a regra aparece na lista de cenários (“_Scenarios_”) da aplicação.
- As condições sobre objetos e pessoas (“caneca na secretária há 10 min”) não têm equivalente nos acionadores de cenário atuais. Propõe-se, por isso, um novo tipo de acionador, `thingTracker`, avaliado pelo Motor de regras no _edge_. Quando a condição se verifica, o _edge_ envia o evento `sensor.fired` e a plataforma executa as ações de início do cenário.

O acionador proposto segue o formato dos atuais acionadores de dispositivo:
```json
{ "type": "thingTracker",
  "condition": { "thing": "mug", "in_place": "desk", "for": "10m", "home": "empty" } }
```

## 6. O que se pede à plataforma

| # | Necessidade | Motivo | Situação atual |
|---|---|---|---|
| 1 | Uma API de eventos ou de _push_, ou _webhooks_ | Os sensores têm de reagir à abertura da porta sem consultas periódicas | O MCP não tem notificações _push_ nem um fluxo geral de eventos (existe apenas o histórico do alarme, `get_home_security_alarm_history`), pelo que seria necessário consultá-lo periodicamente |
| 2 | Acesso RTSP local à câmara | O vídeo deve ficar na rede da casa | O _stream_ passa por um _relay_ na nuvem (_go2rtc_) |
| 3 | Capacidade de computação em casa (_edge_) | A perceção demora cerca de 0,5 s por imagem na GPU de um portátil; a câmara fica em repouso e os modelos de visão locais só correm quando há movimento ou som, a 1 a 2 imagens por segundo | A central LTE do kit não tem capacidade para correr modelos de visão |
| 4 | Uma forma de acrescentar ferramentas ao servidor MCP | Para as quatro ferramentas _Things_ | Por apurar |
| 5 | Eliminação de cenários | Os utilizadores têm de poder remover sensores | Não existe hoje nenhuma ferramenta para eliminar cenários |
| 6 | Notificações _push_ para a aplicação | Avisos | Não se sabe que serviço a aplicação utiliza |
| 7 | Contratos para o modelo de linguagem | Exclusão do uso dos dados para treino, acordo de tratamento de dados (DPA) e tratamento na UE | Não se sabe que fornecedores a Altice já utiliza |

## 7. Estado do protótipo

| Elemento da especificação | No protótipo (`prototype/`) |
|---|---|
| Ferramentas _Things_ | _Endpoints_ HTTP do servidor da equipa (`/api/state`, `/api/things`, `/api/ask`), com os mesmos dados e o mesmo comportamento |
| Sensores | Criados a partir de uma frase e guardados como regras; as ações sobre dispositivos passam pelo cliente MCP da equipa e funcionam em modo de simulação até serem ativadas |
| Registo de objetos | Implementado: 8 vistas do objeto na câmara do kit geram uma assinatura _DINOv2_, guardada no serviço local e na cópia da plataforma |
| Canal _edge_ ↔ plataforma | Um único servidor local desempenha os dois papéis |
