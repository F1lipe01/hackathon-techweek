# Casos de uso do _ThingTracker_

Versão 1, quarta-feira, 18 de novembro de 2026. Documento destinado ao júri, aos mentores da Altice Labs e à equipa. Responde a três perguntas: o que faz o _ThingTracker_ numa casa real, com que câmaras e dispositivos, e como cada caso responde aos critérios de avaliação do concurso.

## Como ler este documento

Cada caso parte de uma frase dita pelo cliente ou de uma proposta que a aplicação faz a partir do que a câmara aprende sobre a casa (há uma criança, um cão, um gato ou, se a família o indicar, uma pessoa idosa que vive só). O cliente aceita uma proposta com um toque.

Para cada caso, indica-se:
- a frase ou a proposta;
- o que a câmara procura (a pesquisa ao detetor _OWLv2_, em inglês, ou a _thing_ registada com 8 vistas e reconhecida pela assinatura visual do _DINOv2_) e o lugar;
- a forma da regra, que corre em casa;
- os dispositivos, marcados como “kit” (os do kit do desafio: câmara, sensor de contacto da porta, detetor de fumo, sensor de temperatura e humidade, tomada inteligente, central de segurança e lâmpada) ou “outro IoT” (dispositivos que o kit não tem);
- a ação;
- a viabilidade e os limites.

Três termos usados em todo o documento:
- Lugar: cada câmara é um lugar (“Cozinha 1”, “Sala 1”, “Jardim 1”). Dentro de um lugar não há zonas desenhadas; as superfícies (a bancada, o fogão) são encontradas pelo nome em cada imagem.
- Viabilidade: “hoje” significa que o protótipo já o faz; “pequena extensão” significa uma nova pesquisa ao detetor ou um novo tipo de regra, sem equipamento novo; “futuro” significa um modelo novo ou um dispositivo que a plataforma da Altice ainda teria de suportar.
- Ações: os avisos chegam ao telemóvel pelo serviço de notificações da aplicação, porque o servidor MCP não tem uma ferramenta de notificações (a confirmar com a Altice). As ações sobre os dispositivos (luz, tomada) seguem pelo MCP, com `update_device_capabilities`. A sirene segue a escolha da família para cada regra, feita ao criá-la: perguntar primeiro ou tocar logo; armar o alarme pede sempre um “sim”; no protótipo, nenhum dos dois está ligado, e as ações sobre a luz e a tomada são simuladas, salvo se forem ativadas.

## 1. Catálogo, por ordem de prioridade

Dentro de casa, primeiro a segurança, depois o cuidado e, por fim, a conveniência. Os casos no exterior (E1 a E9) têm uma secção própria, também ordenada por prioridade, e os dois casos da linha do tempo da casa (T1 e T2) vêm a seguir.

| # | Caso | Lugar | Dispositivos | Viabilidade |
|---|---|---|---|---|
| S1 | Faca na bancada com um gato, um cão ou uma criança por perto | Cozinha | Kit | Pequena extensão |
| S2 | Criança com uma faca, ou junto ao fogão ou ao forno | Cozinha | Kit; outro IoT opcional | Pequena extensão; “segurar” é futuro |
| S3 | Fogão ou forno ligado sem ninguém na cozinha | Cozinha | Kit (tomada, fumo) ou outro IoT (placa, forno) | Pequena extensão (tomada); futuro (placa) |
| S4 | Fumo: quem está em casa e onde | Todos | Kit | Pequena extensão |
| S5 | Medicamentos ou detergentes fora do sítio com uma criança em casa | Cozinha, sala | Kit | Pequena extensão |
| S6 | Janela aberta com uma criança na divisão | Sala | Kit; mais sensores são outro IoT | Pequena extensão |
| S7 | Pessoa desconhecida em casa | Entrada, sala | Kit e _router_ da casa | Em parte hoje |
| S8 | Porta ou janela aberta ao sair de casa ou à noite | Entrada | Kit; outro IoT opcional | Pequena extensão |
| S9 | Fuga de água | Cozinha | Outro IoT | Futuro |
| S10 | Fumo, chama ou água no chão vistos pela câmara | Cozinha | Kit; outro IoT opcional (válvula) | Futuro |
| C1 | Animal que não vai à taça da comida nem à da água | Cozinha | Kit | Hoje |
| C2 | Pessoa idosa: ninguém na cozinha até ao meio-dia | Cozinha | Kit | Hoje (hora fixa) |
| C3 | Caixa de medicamentos que não sai do lugar até à hora habitual | Cozinha, sala | Kit | Pequena extensão |
| C4 | Casa fria com uma pessoa na sala | Sala | Kit | Pequena extensão |
| C5 | Pessoa caída no chão | Cozinha, sala | Kit | Futuro |
| C6 | Uma criança chega a casa | Entrada | Kit | Hoje |
| C7 | Animal que sai quando a porta abre | Entrada | Kit | Pequena extensão |
| V1 | Sair de casa sem as chaves, a carteira ou o livro | Entrada | Kit | Hoje |
| V2 | “Onde está o livro?” | Todos | Kit | Hoje |
| V3 | Aparelho ligado numa divisão vazia | Sala | Kit | Hoje |
| V4 | Animal no sofá proibido | Sala | Kit | Hoje (aviso); pequena extensão (tomada) |
| V5 | Presença e postura: luz e aquecimento | Sala | Kit; outro IoT (termóstato) | Pequena extensão (presença); futuro (postura) |
| V6 | Gestos: luz, televisão, máquina do café | Sala, cozinha | Kit | Futuro |
| E1 | Intrusão: alguém força uma porta ou uma janela | Porta, traseiras | Outro IoT (câmara exterior); kit | Pequena extensão |
| E2 | Pessoa no jardim ou no portão à noite | Jardim, portão | Outro IoT (câmara exterior, holofotes, estores, coluna) | Pequena extensão |
| E3 | Portão aberto com o cão ou uma criança no jardim | Jardim, portão | Outro IoT | Pequena extensão |
| E4 | Furto: a bicicleta ou a encomenda deixam de ser vistas | Jardim, porta | Outro IoT; kit | Pequena extensão |
| E5 | Encomenda ou correio entregue | Porta | Outro IoT; lâmpada do kit | Pequena extensão |
| E6 | O carro chega a casa | Garagem | Outro IoT | Pequena extensão; a matrícula é futuro |
| E7 | Coisas deixadas lá fora: bicicleta, mangueira, caixote do lixo | Jardim | Outro IoT | Pequena extensão |
| E8 | Animais no jardim: rega durante 5 s | Jardim | Outro IoT | Pequena extensão |
| E9 | O cão à porta das traseiras: abrir a portinhola | Traseiras | Outro IoT | Futuro |
| T1 | Chegar tarde demais: o que esteve perto da criança, e quando | Cozinha | Kit | Pequena extensão; “comeu ou bebeu” é futuro |
| T2 | O que aconteceu às 4h? | Todos, exterior | Kit; outro IoT opcional (câmara exterior) | Pequena extensão; o latido e o “invulgar” são futuro |

Dos 34 casos, 24 funcionam só com dispositivos do kit, e os 9 do exterior precisam de uma câmara exterior (outro IoT). Sete já funcionam no protótipo, 22 exigem uma pequena extensão (S7 já funciona em parte) e 5 ficam para o futuro.

### Segurança

#### S1. Faca na bancada com um gato, um cão ou uma criança por perto

- Frase: “Avisa-me se o gato subir à bancada quando lá estiver uma faca.” Proposta da aplicação, quando a câmara vê um gato e uma faca na cozinha: “Avisar se o gato estiver perto de uma faca na bancada?”
- A câmara procura: `"a knife"`, `"a cat"` (ou `"a dog"`, `"a child"`) e a superfície `"a kitchen counter"`, na Cozinha 1.
- Regra: `near(faca, gato, Cozinha 1) durante 3 s`, em que “perto” quer dizer que as duas caixas estão sobre a mesma bancada ou a menos de uma distância fixa na imagem. Opcionalmente, só quando não há uma pessoa na cozinha, para não avisar enquanto alguém cozinha.
- Dispositivos: câmara (kit); lâmpada (kit).
- Ação: aviso com o recorte da bancada; luz vermelha; a sirene, só depois de o utilizador confirmar.
- Viabilidade: pequena extensão. O protótipo já deteta gatos, cães e crianças e encontra superfícies pelo nome; faltam a pesquisa `"a knife"`, a bancada no vocabulário de superfícies e o tipo de regra `near`. O vídeo mostra este caso como ilustração, e não como deteção real.
- Limites: a 3 m, uma faca ocupa poucas dezenas de píxeis na imagem que o detetor analisa (estimativa da equipa, não medida); uma lâmina vista de lado, tapada ou num cepo pode não ser detetada; “perto” na imagem não quer dizer “a tocar” nem “à mesma profundidade”, porque a câmara é uma só; cozinhar com o gato por perto gera avisos, se a regra não excluir a presença de uma pessoa.

#### S2. Criança com uma faca, ou junto ao fogão ou ao forno

- Frase: “Avisa-me se a criança se aproximar do fogão ou pegar numa faca.” Proposta (perfil criança): “Avisar se uma criança se aproximar do fogão ou de uma faca?”
- A câmara procura: `"a child"`, `"a knife"`, `"a stove"`, `"an oven"`, na Cozinha 1.
- Regras: `near(criança, fogão, Cozinha 1) durante 5 s`; `near(faca, criança, Cozinha 1) durante 2 s`.
- Dispositivos: câmara (kit); lâmpada (kit); uma placa ou um forno conectados (outro IoT), para avisar só quando estão ligados; uma coluna inteligente (outro IoT), para um aviso de voz na própria cozinha.
- Ação: aviso aos pais com o recorte; luz vermelha; aviso de voz, se houver coluna. A sirene não se recomenda aqui: assustar uma criança com uma faca na mão pode ser pior.
- Viabilidade: “perto” é uma pequena extensão, igual à do caso S1. Saber se a criança segura a faca exige um modelo de pose ou de mãos, que a arquitetura prevê para uma fase posterior: futuro.
- Limites: o detetor pode confundir uma criança com um adulto baixo e vice-versa; “perto” não é “segurar”; uma criança a ajudar a cozinhar ao lado de um adulto gera avisos, pelo que os pais escolhem os horários em que a regra está ativa.

#### S3. Fogão ou forno ligado sem ninguém na cozinha

- Frase: “Avisa-me se a placa ficar ligada sem ninguém na cozinha durante 15 minutos.” Proposta, quando a casa tem uma placa conectada ou um aparelho de cozinha ligado à tomada.
- A câmara procura: a ausência de `"a person"` na Cozinha 1, sem identificar ninguém.
- Regras: `on(placa) e nobody_for(Cozinha 1, 15 min)`; para aparelhos de bancada, `power(Tomada) > 500 W e nobody_for(Cozinha 1, 15 min)`; o detetor de fumo fica como última linha de defesa.
- Dispositivos: placa ou forno conectados (outro IoT); tomada com medição de consumo (kit), para uma fritadeira ou um forno elétrico de bancada, se a potência couber na tomada (a confirmar); detetor de fumo (kit).
- Ação: aviso; desligar a tomada pelo MCP, depois de confirmar ou automaticamente, se o cliente o escolher ao criar a regra; desligar a placa, se o fabricante e a plataforma o permitirem (a confirmar).
- Viabilidade: pela tomada, pequena extensão (o protótipo já lê os dispositivos pelo MCP e já tem `nobody_for` e o desligar da tomada; falta combiná-los). Pela placa ou pelo forno, futuro, porque dependem de a plataforma da Altice suportar esses aparelhos.
- Limites: um guisado em lume brando pode ser intencional, por isso a regra avisa por omissão e não corta; uma pessoa na sala de jantar, fora do campo da câmara, conta como “ninguém”; o limite de potência tem de ser escolhido para cada aparelho.

#### S4. Fumo: quem está em casa e onde

- Frase: “Se o detetor de fumo disparar, diz-me se está alguém na cozinha.” Proposta automática em qualquer casa com detetor de fumo e câmara.
- A câmara procura: `"a person"` em cada lugar, nos últimos minutos, sem identificar ninguém.
- Regra: `state(Detetor de fumo) = alarme`, acompanhado da presença registada em cada lugar.
- Dispositivos: detetor de fumo (kit), que já tem sirene própria; câmara (kit); lâmpada (kit).
- Ação: aviso do tipo “O detetor de fumo da cozinha disparou; a câmara da cozinha viu uma pessoa há 1 minuto”, sem fotografias de pessoas; luz vermelha; a sirene da central, só depois de confirmar.
- Viabilidade: pequena extensão. O protótipo já consulta a lista de dispositivos pelo MCP, só em leitura, para seguir a porta, e o estado do detetor de fumo vem na mesma resposta.
- Limites: os alertas de fumo já fazem parte da oferta da Altice; o _ThingTracker_ acrescenta contexto, e não deteta fogo. A câmara nunca substitui o detetor.

#### S5. Medicamentos ou detergentes fora do sítio com uma criança em casa

- Frase: “Avisa-me se a lixívia estiver fora do armário quando a criança estiver na cozinha.” Proposta (perfil criança): “Registar os produtos perigosos da casa?”
- A câmara procura: as _things_ registadas (a lixívia, a caixa de medicamentos) e `"a child"`, na Cozinha 1 ou na Sala 1.
- Regra: `seen_in(lixívia, Cozinha 1) e seen_in(criança, Cozinha 1)`. Se a lixívia vive num armário fechado, vê-la já significa que está fora do sítio.
- Dispositivos: câmara (kit).
- Ação: aviso com o recorte do objeto.
- Viabilidade: pequena extensão. `seen_in` com uma _thing_ já funciona no protótipo; falta a condição da criança.
- Limites: um objeto guardado numa prateleira aberta está sempre visível, e a regra tem de passar a ser “fora do sítio habitual”; frascos parecidos podem confundir a assinatura visual; a câmara só vê o que está no seu campo.

#### S6. Janela aberta com uma criança na divisão

- Frase: “Avisa-me se a janela da sala estiver aberta e a criança estiver na sala.”
- A câmara procura: `"a child"`, na Sala 1.
- Regra: `state(Sensor da janela) = aberto e seen_in(criança, Sala 1) durante 10 s`.
- Dispositivos: sensor de contacto (kit; o kit tem um, e cada janela a mais exige outra unidade, outro IoT); câmara (kit); coluna inteligente para um aviso de voz (outro IoT).
- Ação: aviso; luz vermelha; aviso de voz.
- Viabilidade: pequena extensão.
- Limites: o cliente tem de indicar a que lugar pertence cada sensor; a câmara pode não ver a janela; o detetor pode confundir uma criança com um adulto.

#### S7. Pessoa desconhecida em casa

- Frase: “Avisa-me se entrar alguém quando não estiver ninguém da família em casa.”
- A câmara procura: `"a person"`, na Entrada 1 ou na Sala 1. A presença da família vem dos telemóveis conhecidos ligados ao Wi-Fi da casa, como prevê a arquitetura.
- Regra: `someone_arrives(pessoa, Entrada 1) e nenhum telemóvel da família em casa`.
- Dispositivos: câmara (kit); central de segurança (kit); _router_ da casa.
- Ação: aviso com uma fotografia da pessoa; o utilizador pode armar o alarme, só depois de um “sim” explícito. A ferramenta MCP do alarme (`patch_home_security_status`) vem marcada como “só de leitura”, apesar de armar o alarme, pelo que a confirmação é sempre obrigatória.
- Viabilidade: em parte hoje (o protótipo avisa quando aparece uma pessoa numa divisão que estava vazia); os telemóveis da família são uma pequena extensão; o reconhecimento dos familiares é futuro, opcional e exige consentimento.
- Limites: uma visita ou uma empregada de limpeza com a família fora gera um aviso; um telemóvel esquecido em casa engana a regra; o reconhecimento de pessoas exige revisão jurídica (Regulamento da IA, artigo 9.º do RGPD).

#### S8. Porta ou janela aberta ao sair de casa ou à noite

- Frase: “Avisa-me se a porta da varanda ficar aberta depois das 23h” ou “quando eu sair de casa”.
- A câmara procura: `"a person"` na Entrada 1, para saber quando sai a última pessoa.
- Regra: `state(Sensor de contacto) = aberto durante 10 min e (hora > 23:00 ou nobody_for(casa, 10 min))`.
- Dispositivos: sensor de contacto (kit); lâmpada (kit), como lembrete junto à porta; fechadura inteligente (outro IoT).
- Ação: aviso; luz âmbar; trancar a porta, só depois de confirmar.
- Viabilidade: o protótipo já lê o sensor da porta em direto, pelo MCP. A versão noturna já se faz com os cenários da própria plataforma; a versão “quando sai a última pessoa” é uma pequena extensão.
- Limites: aqui a câmara acrescenta pouco a um cenário que a plataforma já permite; o kit tem um só sensor de contacto.

#### S9. Fuga de água

- Frase: “Se houver uma fuga de água junto à máquina da loiça, mostra-me a cozinha e desliga a máquina.”
- A câmara procura: nada de específico; envia o recorte mais recente do lugar, para o utilizador avaliar. Não se afirma que a câmara veja a água.
- Regra: `state(Sensor de inundação) = alarme`, com o recorte e a presença em casa.
- Dispositivos: sensor de inundação (outro IoT; a página do produto _Connected Home_ da Altice Labs refere alertas de fuga de água); tomada (kit), se a potência da máquina couber na tomada (a confirmar); eletroválvula (outro IoT).
- Ação: aviso; desligar a tomada ou fechar a válvula, depois de confirmar.
- Viabilidade: futuro, porque o kit não tem sensor de inundação; a regra, em si, é simples.
- Limites: a câmara acrescenta pouco; é um caso que a Altice já vende.

#### S10. Fumo, chama ou água no chão vistos pela câmara

- Frase: “Se a câmara vir chamas na cozinha vazia, desliga a fritadeira” ou “se vir água no chão, fecha a água”. É uma das ideias de IoT propostas na equipa.
- A câmara procura: `"smoke"`, `"fire"`, `"a puddle of water"`, na Cozinha 1; nos casos duvidosos, o modelo de linguagem verifica um único recorte.
- Regras: `seen_in(chama, Cozinha 1) durante 5 s e nobody_for(Cozinha 1, 5 min)`; `seen_in(água no chão, Cozinha 1) durante 30 s`.
- Dispositivos: câmara (kit); tomada (kit), com o aparelho; eletroválvula de corte da água (outro IoT); detetor de fumo (kit), que continua a ser o alarme de referência.
- Ação: aviso com o recorte; desligar a tomada ou fechar a válvula, depois de confirmar.
- Viabilidade: futuro. O _OWLv2_ aceita estas pesquisas, mas a fiabilidade não foi medida; um modelo treinado para fumo e chama seria mais seguro.
- Limites: o vapor de uma panela parece fumo; um reflexo no chão pode parecer água; a chama do fogão a gás também é uma chama, por isso a regra só vale com a cozinha vazia; a câmara nunca substitui o detetor de fumo nem o sensor de inundação.

### Cuidado

#### C1. Animal que não vai à taça da comida nem à da água

- Frase: “Avisa-me se o gato não for à taça da água em 12 horas.” Proposta (perfil gato ou cão), que o protótipo já faz: a comida até às 20h e a água em 12 horas.
- A câmara procura: `"a cat"` ou `"a dog"`, e as taças, registadas como _things_ ou encontradas pelo nome, na Cozinha 1.
- Regras: `not_by(gato, taça da comida, 20:00)`; `not_by(gato, taça da água, 12 h)`; para “não comeu num dia”, `not_by(gato, taça da comida, 24 h)`.
- Dispositivos: câmara (kit).
- Ação: aviso.
- Viabilidade: hoje, incluindo a proposta automática quando a câmara vê o animal.
- Limites: estar junto à taça não é comer nem beber; com três gatos, a regra vale para “um gato”, e distinguir cada um exigiria registá-lo como _thing_, o que ainda não foi testado; uma taça fora do campo da câmara não é vista.

#### C2. Pessoa idosa: ninguém na cozinha até ao meio-dia

- Frase: “Avisa a minha filha se ninguém passar na cozinha até ao meio-dia.” Proposta (perfil pessoa idosa que vive só): só aparece se a família indicar este perfil; nunca é deduzido pela câmara.
- A câmara procura: `"a person"`, na Cozinha 1, sem identificar ninguém.
- Regras: `nobody_by(Cozinha 1, 07:00–12:00)`; para “sem movimento à hora habitual”, `nobody_for(casa, 2 h)` dentro do horário que a casa costuma ter.
- Dispositivos: câmara (kit); sensores de presença sem imagem (outro IoT), para os quartos, onde não há câmaras; coluna inteligente (outro IoT), para perguntar “está tudo bem?”.
- Ação: aviso a um familiar.
- Viabilidade: hoje, com uma hora fixa. Aprender o horário habitual da casa é futuro.
- Limites: uma visita conta como “alguém”; a pessoa pode estar num quarto sem câmara, o que gera um aviso (preferível ao silêncio); nunca há sirene.

#### C3. Caixa de medicamentos que não sai do lugar até à hora habitual

- Frase: “Avisa-me se a caixa dos comprimidos não sair do lugar até às 10h.”
- A câmara procura: a caixa, registada como _thing_ com 8 vistas, na Cozinha 1 ou na Sala 1.
- Regra: `not_moved_by(caixa, 10:00)` (novo): a caixa foi vista no mesmo lugar desde manhã.
- Dispositivos: câmara (kit); coluna inteligente (outro IoT), para um lembrete de voz.
- Ação: lembrete à própria pessoa ou aviso a um familiar.
- Viabilidade: pequena extensão. O protótipo já regista cada mudança de lugar de uma _thing_; falta o tipo de regra.
- Limites: mexer na caixa não é tomar o medicamento; numa caixa semanal com compartimentos, a câmara não sabe qual foi aberto; a caixa tem de ficar onde a câmara a vê, e não no quarto.

#### C4. Casa fria com uma pessoa na sala

- Frase: “Se a sala estiver abaixo de 18 °C e estiver alguém na sala, avisa-me.” O limite é escolhido pela família.
- A câmara procura: `"a person"`, na Sala 1.
- Regra: `temperatura(Sensor) < 18 °C e seen_in(pessoa, Sala 1) durante 15 min`.
- Dispositivos: sensor de temperatura e humidade (kit, lido em direto pelo MCP); tomada (kit), com um aquecedor, se a potência couber na tomada (a confirmar).
- Ação: aviso à família; ligar a tomada, só depois de confirmar.
- Viabilidade: pequena extensão. O MCP já dá a temperatura; o protótipo ainda não a combina com a presença.
- Limites: o sensor tem de estar na divisão da câmara; ligar um aquecedor à distância tem riscos, por isso só com alguém presente e depois de confirmar.
- Contexto: em Portugal, 22,2 % das pessoas com 65 ou mais anos não conseguem manter a casa adequadamente aquecida (Eurostat, `hlth_dhc140`, 2025).

#### C5. Pessoa caída no chão

- Proposta (perfil pessoa idosa): “Avisar se alguém ficar deitado no chão da cozinha ou da sala durante mais de 1 minuto?”
- A câmara procura: a postura da pessoa, com um modelo de pose que a arquitetura prevê para uma fase posterior.
- Regra: `lying(pessoa, Cozinha 1) durante 60 s`.
- Dispositivos: câmara (kit); coluna inteligente (outro IoT), para perguntar “está bem?”.
- Ação: aviso à família; nunca sirene.
- Viabilidade: futuro.
- Limites: alguém deitado no sofá ou a brincar no chão gera avisos; as quedas no quarto ou na casa de banho ficam de fora, porque aí não há câmaras.

#### C6. Uma criança chega a casa

- Frase: “Avisa-me quando a criança chegar a casa.” Proposta (perfil criança), que o protótipo já faz.
- A câmara procura: `"a child"`, na Entrada 1.
- Regra: `someone_arrives(criança, Entrada 1, 30 min)`: uma criança vista depois de 30 minutos sem nenhuma.
- Dispositivos: câmara (kit); sensor de contacto da porta (kit).
- Ação: aviso, sem fotografia.
- Viabilidade: hoje.
- Limites: qualquer criança conta, incluindo um amigo; não há identificação, salvo se a família a ativar.

#### C7. Animal que sai quando a porta abre

- Frase: “Avisa-me se o cão sair quando a porta abrir.” Proposta (perfil cão ou gato).
- A câmara procura: `"a dog"` ou `"a cat"`, em todos os lugares, sobretudo na Entrada 1.
- Regra: `leave_without(cão, 5 min)`: a porta abre e, nos 5 minutos seguintes, o cão não volta a ser visto em nenhum lugar.
- Dispositivos: sensor de contacto da porta (kit, lido em direto pelo MCP); câmara (kit).
- Ação: aviso com a hora a que a porta abriu e o último lugar onde o cão foi visto.
- Viabilidade: pequena extensão. O protótipo já tem `leave_without` para as _things_ e já deteta cães e gatos; falta aplicar a regra a um animal.
- Limites: um cão a dormir num quarto, sem câmara, deixa de ser visto sem ter saído; um passeio também gera um aviso, a menos que a regra ignore as saídas em que o cão e uma pessoa são vistos juntos à porta.

### Conveniência

#### V1. Sair de casa sem as chaves, a carteira ou o livro

- Frase: “Avisa-me se sair de casa sem o livro.” É o exemplo da demonstração.
- A câmara procura: o livro, registado com 8 vistas e reconhecido pela assinatura visual, em qualquer lugar.
- Regra: `leave_without(livro, 60 s)`: a porta abre e, 60 segundos depois, o livro continua visto em casa.
- Dispositivos: sensor de contacto da porta (kit, lido em direto pelo MCP); câmara (kit); lâmpada (kit), como lembrete; coluna inteligente junto à porta (outro IoT).
- Ação: aviso com a fotografia e o último lugar do livro; luz.
- Viabilidade: hoje, com o sensor real da porta ou com a porta simulada.
- Limites: a porta também abre quando alguém chega; um objeto que sai sem a câmara o ver continua a contar como “em casa”; objetos pequenos num bolso ou numa mala não se veem.

#### V2. “Onde está o livro?”

- Pergunta: “Onde está o livro?”
- A câmara procura: o livro registado, em todos os lugares.
- Regra: nenhuma; a resposta vem da última observação (lugar, hora e fotografia).
- Dispositivos: câmara (kit).
- Ação: resposta na aplicação, com a fotografia.
- Viabilidade: hoje.
- Limites: só responde com o que uma câmara viu; “visto pela última vez” não quer dizer “está lá agora”.

#### V3. Aparelho ligado numa divisão vazia

- Frase: “Se não estiver ninguém na sala há 30 minutos, desliga o aquecedor.”
- A câmara procura: a ausência de `"a person"`, na Sala 1.
- Regra: `nobody_for(Sala 1, 30 min) e power(Tomada) > 50 W`.
- Dispositivos: tomada com medição de consumo (kit); câmara (kit).
- Ação: desligar a tomada pelo MCP.
- Viabilidade: hoje (`nobody_for` e o desligar da tomada já existem; a condição de potência é uma pequena extensão).
- Limites: a gestão de energia já faz parte da oferta da Altice; ver, nos limites comuns, o caso das pessoas paradas.

#### V4. Animal no sofá proibido

- Frase: “Se o cão subir ao sofá, liga o dissuasor.” É uma das ideias de IoT propostas na equipa.
- A câmara procura: `"a dog"` ou `"a cat"` e a superfície `"a sofa"`, na Sala 1.
- Regra: `seen_in(cão, sofá) durante 5 s`.
- Dispositivos: câmara (kit); tomada (kit), com um dissuasor, por exemplo um aparelho que emite um som.
- Ação: aviso; ligar a tomada durante alguns segundos.
- Viabilidade: o aviso funciona hoje (o protótipo já associa cada animal à superfície onde está, e o sofá faz parte do vocabulário); ligar a tomada a partir de uma regra é uma pequena extensão.
- Limites: um cão deitado e quieto no sofá não gera movimento, e os modelos podem nem chegar a correr; o dissuasor deve ser suave, como um som, e nunca algo que possa magoar o animal.

#### V5. Presença e postura: luz e aquecimento

- Frases: “Quando entrar alguém na sala à noite, acende a luz em tom quente” e “se alguém adormecer no sofá, baixa o aquecimento”. É uma das ideias de IoT propostas na equipa.
- A câmara procura: `"a person"`, na Sala 1; para a postura (sentado, deitado), um modelo de pose.
- Regras: `someone_arrives(pessoa, Sala 1) depois do pôr do sol` → luz; `lying(pessoa, sofá) e imóvel durante 20 min` → termóstato.
- Dispositivos: lâmpada (kit); termóstato ou aquecimento conectado (outro IoT).
- Ação: acender a luz pelo MCP (ligar, brilho e temperatura de cor); baixar o termóstato.
- Viabilidade: a presença é uma pequena extensão (o protótipo já deteta a chegada de uma pessoa; falta a ação de acender a luz em branco); a postura é futuro, porque exige um modelo de pose.
- Limites: “a dormir” não se vê numa imagem, e o máximo que se mede é “deitado e imóvel”; uma pessoa imóvel não gera movimento, pelo que seria preciso analisar uma imagem a intervalos fixos; os sensores de movimento comuns já acendem luzes à passagem, o que reduz o valor deste caso.

#### V6. Gestos: luz, televisão, máquina do café

- Frase: “Quando eu levantar a mão aberta na sala, apaga a luz.” É uma das ideias de IoT propostas na equipa.
- A câmara procura: gestos das mãos, com um modelo de gestos.
- Regra: `gesture(mão aberta, Sala 1)` → ação.
- Dispositivos: lâmpada (kit); tomada (kit), com a máquina do café; televisão ou _set-top box_ (fora do kit; a página da Altice Labs refere a gestão de _set-top boxes_).
- Ação: ligar ou desligar pelo MCP.
- Viabilidade: futuro, porque exige um modelo de gestos.
- Limites: um gesto involuntário dispara uma ação; a voz ou um botão na aplicação fazem o mesmo com menos erros; arrisca parecer um truque, quando a Altice pediu, no arranque do desafio, algo que não seja “apenas um _gimmick_”.

### Exterior

Os casos seguintes precisam de uma câmara no exterior (outro IoT): à porta, no jardim, no portão ou na entrada da garagem. Também aqui a segurança vem primeiro. A todos se aplicam as regras da secção 2.6: a câmara só pode incidir sobre a propriedade e, no estritamente necessário, sobre os acessos ao imóvel. Limites próprios do exterior: à noite, a câmara usa a visão noturna e a deteção piora (não medido); a chuva, o vento nas árvores e os animais geram movimento e, portanto, análises; os objetos ficam mais longe da câmara.

#### E1. Intrusão: alguém força uma porta ou uma janela

- Frase: “Avisa-me se alguém mexer na janela das traseiras quando não estiver ninguém em casa.”
- A câmara procura: `"a person"`, nas Traseiras 1, sem identificar ninguém.
- Regra: `seen_in(pessoa, Traseiras 1) e nenhum telemóvel da família em casa`, reforçada por `state(Sensor da janela) = aberto`.
- Dispositivos: câmara exterior (outro IoT); sensor de contacto da janela (kit; mais unidades são outro IoT); central de segurança (kit); holofote (outro IoT).
- Ação: aviso com a fotografia da pessoa; holofote aceso; armar o alarme ou tocar a sirene, só depois de um “sim”.
- Viabilidade: pequena extensão (a regra junta `seen_in`, a presença dos telemóveis e o sensor de contacto).
- Limites: um jardineiro ou um vizinho conhecido gera um aviso; o sistema mostra o que viu e não prova uma intrusão; o alarme da Altice já deteta a abertura da janela, e o _ThingTracker_ acrescenta a fotografia e o contexto.

#### E2. Pessoa no jardim ou no portão à noite

- Frase: “Se estiver alguém no jardim depois da meia-noite, acende os holofotes.” A ideia proposta na equipa junta os holofotes, os estores e uma coluna que imita um cão a ladrar.
- A câmara procura: `"a person"`, no Jardim 1 ou no Portão 1, sem identificar ninguém.
- Regra: `seen_in(pessoa, Jardim 1) durante 30 s e hora entre 00:00 e 06:00`; o tempo mínimo evita avisos por quem só passa.
- Dispositivos: câmara exterior, holofotes, motor dos estores, coluna exterior (outro IoT); lâmpada (kit), acesa dentro de casa.
- Ação: holofotes acesos de imediato, porque não fazem barulho; aviso com o recorte; estores e latido na coluna, se o cliente os escolher ao criar a regra; sirene, só depois de um “sim”.
- Viabilidade: pequena extensão (`seen_in` com uma pessoa já existe; falta juntar a hora e o tempo mínimo).
- Limites: sem reconhecimento (opcional e com consentimento), o sistema não sabe se é um desconhecido, por isso a regra fala de “uma pessoa”; um familiar que chega tarde dispara o caso, salvo se o telemóvel dele já estiver na rede da casa; um latido às três da manhã incomoda os vizinhos.

#### E3. Portão aberto com o cão ou uma criança no jardim

- Frase: “Avisa-me se o portão ficar aberto com o cão no jardim.”
- A câmara procura: `"a dog"` ou `"a child"`, no Jardim 1. O estado do portão vem de um sensor de contacto ou, sem sensor, de uma verificação visual de um recorte do portão pelo modelo de linguagem.
- Regra: `state(Sensor do portão) = aberto e seen_in(cão, Jardim 1)`.
- Dispositivos: câmara exterior (outro IoT); sensor de contacto no portão (outro IoT, do tipo do kit, se ficar ao alcance da central, a confirmar); lâmpada (kit).
- Ação: aviso com o recorte do portão; luz âmbar dentro de casa.
- Viabilidade: pequena extensão.
- Limites: a verificação visual depende do ângulo e da luz; o sensor é mais fiável; uma criança no jardim com um adulto ao lado gera um aviso.

#### E4. Furto: a bicicleta ou a encomenda deixam de ser vistas

- Frase: “Avisa-me se a bicicleta sair do jardim quando não estiver ninguém em casa.”
- A câmara procura: a bicicleta, registada com 8 vistas, como o livro, no Jardim 1; e `"a person"`, nos minutos anteriores.
- Regras: `missing(bicicleta, Jardim 1) durante 2 min e nenhum telemóvel da família em casa` (novo); para a encomenda, `missing(encomenda, Porta 1) e a porta de casa não abriu`.
- Dispositivos: câmara exterior (outro IoT); sensor de contacto da porta (kit).
- Ação: aviso com o último recorte da bicicleta e, se houver, o da pessoa vista junto dela.
- Viabilidade: pequena extensão (o protótipo já guarda a última observação de cada _thing_; falta a regra “deixou de ser vista”).
- Limites: o aviso diz o que a câmara viu (“deixou de ser vista”), e não que houve um furto; um vizinho que guarda a encomenda gera um aviso; uma bicicleta tapada por um carro conta como desaparecida.

#### E5. Encomenda ou correio entregue

- Frase: “Avisa-me quando deixarem uma encomenda à porta” ou “quando chegar correio”. A ideia proposta na equipa acrescenta um anúncio numa coluna dentro de casa e a lâmpada a ficar azul.
- A câmara procura: `"a cardboard box"` ou `"a parcel"`, na Porta 1 (exterior).
- Regras: `appears(encomenda, Porta 1) e fica 1 min` (novo); para o correio, `state(Caixa do correio) = aberta`.
- Dispositivos: câmara exterior à porta (outro IoT; a câmara do kit tem proteção IP65 e poderia, em princípio, ficar numa entrada coberta, pressuposto a confirmar com a Altice); sensor na caixa do correio (outro IoT), ou o sensor de contacto do kit na tampa da caixa, se ficar ao alcance da central (a confirmar); lâmpada (kit); coluna inteligente dentro de casa (outro IoT).
- Ação: aviso com o recorte da encomenda, e só da encomenda; lâmpada azul (o protótipo já tem esta ação); anúncio na coluna: “Chegou uma encomenda à porta.”
- Viabilidade: pequena extensão (detetar uma classe de objeto sem registo e um tipo de regra “aparece”), mais equipamento novo.
- Limites: o enquadramento tem de excluir a rua e os vizinhos; a noite, a chuva e o contraluz reduzem a deteção; o desaparecimento da encomenda trata-se no caso E4.

#### E6. O carro chega a casa

- Frase: “Avisa-me quando o carro chegar.” A ideia proposta na equipa vai mais longe: reconhecer a matrícula e abrir o portão da garagem.
- A câmara procura: `"a car"`, na Garagem 1, isto é, na entrada da garagem, dentro da propriedade. Ler a matrícula exigiria um modelo próprio.
- Regras: `appears(carro, Garagem 1)` → aviso; `plate(matrícula registada, Garagem 1) e telemóvel do dono na rede da casa` → abrir o portão (futuro).
- Dispositivos: câmara exterior (outro IoT); motor do portão da garagem (outro IoT).
- Ação: aviso “O carro chegou”; abrir o portão, só se o cliente o ativar e, de preferência, depois de confirmar no telemóvel.
- Viabilidade: o carro é uma pequena extensão; a matrícula é futuro.
- Limites e questões jurídicas: uma matrícula é um dado pessoal (CEPD, Diretrizes 3/2019, n.º 8), e a câmara lê também as matrículas das visitas; por isso, a leitura só se faz por opção explícita do cliente, só na entrada da própria garagem e depois de uma avaliação jurídica (a verificar). Uma matrícula copia-se com facilidade: abrir a garagem só com ela seria inseguro, daí juntar a presença do telemóvel do dono.

#### E7. Coisas deixadas lá fora: a bicicleta, a mangueira, o caixote do lixo

- Frases: “Lembra-me às 22h se a bicicleta ficar no jardim”; “avisa-me se a mangueira ficar no relvado à noite”; “se o caixote do lixo continuar no sítio às 21h de terça, lembra-me de o pôr na rua”.
- A câmara procura: as _things_ registadas (a bicicleta, a mangueira, o caixote), no Jardim 1.
- Regras: `seen_in(bicicleta, Jardim 1) às 22:00`; `not_moved_by(caixote, terça 21:00)` (novo, o mesmo tipo do caso C3).
- Dispositivos: câmara exterior (outro IoT); coluna inteligente (outro IoT), para um lembrete de voz.
- Ação: lembrete no telemóvel ou na coluna.
- Viabilidade: pequena extensão (falta a condição de hora em `seen_in` e o tipo `not_moved_by`).
- Limites: o caixote vê-se no sítio onde é guardado, dentro da propriedade, e não na rua, que a câmara não deve filmar; uma mangueira no chão é fina e comprida, e a deteção à distância é incerta (não medida). O portão aberto é o caso E3.

#### E8. Animais no jardim: rega durante 5 s

- Frase: “Se entrar um gato no jardim, liga a rega durante 5 segundos.” É uma das ideias de IoT propostas na equipa.
- A câmara procura: `"a cat"`, `"a dog"` ou `"a bird"`, no Jardim 1; os animais da casa, registados como _things_, ficam de fora.
- Regra: `seen_in(gato, Jardim 1) e não é o gato da casa` → rega durante 5 s, no máximo uma vez em cada 10 minutos.
- Dispositivos: câmara exterior; eletroválvula ou programador de rega (outro IoT).
- Ação: abrir a rega durante 5 s.
- Viabilidade: pequena extensão (a regra) e equipamento novo; distinguir o animal da casa de outro parecido pela assinatura visual ainda não foi testado.
- Limites: se o reconhecimento falhar, a rega molha o próprio animal da casa, ou uma pessoa que esteja no jardim; cada disparo gasta água.

#### E9. O cão à porta das traseiras: abrir a portinhola

- Frase: “Quando o cão estiver à porta das traseiras, abre-lhe a portinhola.” É uma das ideias de IoT propostas na equipa.
- A câmara procura: o cão da casa, registado como _thing_ com 8 vistas, nas Traseiras 1.
- Regra: `seen_in(cão registado, Traseiras 1) durante 3 s` → destrancar a portinhola durante 30 s.
- Dispositivos: câmara exterior (outro IoT); portinhola com fecho elétrico (outro IoT).
- Ação: destrancar a portinhola, e só para o animal registado.
- Viabilidade: futuro. Reconhecer um animal concreto, e não “um cão”, pela assinatura visual não foi testado e teria de ser muito fiável, porque abre uma passagem para dentro de casa.
- Limites: outro cão parecido, ou um animal selvagem, poderia entrar; as portinholas com leitor de microchip já resolvem este problema sem câmara, e a câmara pode limitar-se a avisar (“o cão entrou às 15h”).

### Linha do tempo da casa

A memória que encontra as coisas (o lugar, a hora e o recorte de cada observação) também conta o que aconteceu. Os dois casos seguintes, propostos por uma pessoa da equipa, não disparam um aviso: respondem a uma pergunta feita depois, com uma lista de acontecimentos, cada um com o tipo, a hora, o lugar e uma imagem, guardados durante um prazo limitado e depois apagados (proposta na secção 2.5).

#### T1. Chegar tarde demais: o que esteve perto da criança, e quando

- Pergunta: “O que é que esteve perto da criança esta tarde?” ou, depois de um aviso do caso da criança em perigo: “Mostra-me o que aconteceu na cozinha entre as 16h e as 16h30.”
- A câmara procura: o mesmo que no caso da criança em perigo (S2 e S5): a criança perto de um detergente, de um medicamento, de comida ou de uma bebida, na Cozinha 1. Cada acontecimento guarda o tipo, a hora, o lugar e um recorte.
- Regra: nenhuma nova; uma consulta à linha do tempo, por exemplo `timeline(criança, Cozinha 1, 16:00–16:30)`, que o modelo de linguagem resume em linguagem corrente.
- Dispositivos: câmara (kit).
- Ação: a aplicação mostra a sequência com os recortes (“16h28, junto a um detergente; 16h29, junto a um copo”), para os pais decidirem o que contar ao médico.
- Viabilidade: pequena extensão. O protótipo já guarda, para cada _thing_, o lugar, a hora e um recorte, e guarda a presença da criança sem imagem; falta o acontecimento “perto de” com recorte, o mesmo de S2 e S5. Saber se a criança comeu ou bebeu exige um modelo de ações, que é futuro: a aplicação mostra o que esteve perto, e são os pais que avaliam.
- Limites: “perto” não é “comeu”; o que acontece fora do campo da câmara não aparece; guardar recortes de uma criança aumenta o risco de privacidade, por isso só com o consentimento dos pais e com o prazo da secção 2.5.

#### T2. O que aconteceu às 4h?

- Pergunta: “O que aconteceu esta noite entre as 3h e as 5h?”, depois de um alarme em casa ou de um assalto na vizinhança.
- A câmara procura: acontecimentos invulgares para aquela casa: o cão a ladrar a uma hora em que nunca ladra, uma pessoa junto a uma janela (`"a person"`, na câmara exterior), uma porta aberta (sensor de contacto). Cada acontecimento guarda o tipo, a hora, o lugar e uma imagem; do som, guarda-se só a etiqueta (“latido, 4h02”), nunca o áudio (proposta).
- Regra: uma consulta, por exemplo `timeline(casa, 03:00–05:00, só invulgares)`, em que “invulgar” se mede contra o padrão da própria casa.
- Dispositivos: câmara (kit), cujo microfone serve de gatilho; sensor de contacto (kit); central de segurança (kit), cujo histórico de alarmes o MCP já lê (`get_home_security_alarm_history`); câmara exterior (outro IoT), para a janela.
- Ação: a aplicação mostra a lista com as imagens; a família pode fixar acontecimentos, para os guardar mais tempo, e exportá-los.
- Viabilidade: a linha do tempo do protótipo já guarda pessoas e animais com o lugar e a hora, sem imagem; juntar imagens aos acontecimentos de segurança e a vista “só invulgares” são pequenas extensões. Reconhecer um latido pelo som exige um modelo de áudio, e saber o que é invulgar exige aprender o padrão da casa (como a hora habitual de C2): futuro. Hoje, o protótipo não trata som.
- Limites: o som levanta uma questão jurídica, porque o artigo 19.º, n.º 4, da Lei n.º 58/2019 proíbe a captação de som onde a videovigilância é admitida, salvo com as instalações encerradas ou com autorização prévia da CNPD; a aplicação a uma casa particular fica a verificar (secção 2.6). A câmara exterior segue as regras da secção 2.6. Entregar imagens a um vizinho ou às autoridades: a verificar. Num cão que ladra muito, quase tudo é invulgar, e a lista só ajuda se for curta.
- A história que deu origem ao caso: a vizinha de uma pessoa da equipa foi assaltada; o cão dessa pessoa ladrou às 4h, e foi essa hora que ajudou a vizinha a procurar nas gravações da sua própria câmara.

### Ideias de IoT propostas na equipa: onde ficam

Nove ideias propostas na equipa juntam a câmara a outros dispositivos. A tabela indica o caso do catálogo onde cada uma fica, o que a arquitetura já tem e o que falta. Três exigem modelos além do _OWLv2_ e do _DINOv2_ (pose, matrículas e gestos) e ficam como futuro; o fumo e a chama também, até haver um modelo treinado e medido.

| Ideia | Caso | O que já existe | O que falta | Viabilidade |
|---|---|---|---|---|
| Encomenda detetada: anúncio numa coluna dentro de casa e lâmpada azul | E5 | Deteção pelo nome (_OWLv2_); a ação “luz azul” pelo MCP | Câmara exterior; coluna na plataforma; regra “aparece” | Pequena extensão e equipamento |
| Carro ou matrícula reconhecidos: portão da garagem | E6 | Deteção de `"a car"` | Modelo de matrículas; motor do portão na plataforma; opção explícita e avaliação jurídica | Carro: pequena extensão; matrícula: futuro |
| Pessoa a rondar à noite: holofotes, estores, latido na coluna | E2 | Deteção de pessoas; regra `seen_in`; presença dos telemóveis (arquitetura) | Câmara exterior; holofotes, estores e coluna na plataforma; hora e tempo mínimo na regra | Pequena extensão e equipamento |
| O cão à porta das traseiras: portinhola só para o animal registado | E9 | Assinatura visual (_DINOv2_) | Fiabilidade para um animal concreto, por medir; portinhola na plataforma | Futuro |
| Animais no jardim: rega durante 5 s | E8 | Deteção de animais | Rega na plataforma; excluir os animais da casa | Pequena extensão e equipamento |
| Animal no sofá proibido: dissuasor ligado à tomada | V4 | Animais associados às superfícies, sofá incluído; tomada pelo MCP | Ligar a tomada a partir de uma regra | Hoje (aviso); pequena extensão (tomada) |
| Presença ou postura (sentado, a dormir): luz e termóstato | V5 | Deteção de pessoas; lâmpada pelo MCP | Modelo de pose; termóstato na plataforma | Presença: pequena extensão; postura: futuro |
| Fumo, chama ou água no chão vistos: tomada ou válvula de corte | S10 | Pesquisa pelo nome; verificação visual de um recorte | Modelo de fumo e chama, com fiabilidade medida; válvula na plataforma | Futuro |
| Gestos: televisão, luz, máquina do café | V6 | Lâmpada e tomada pelo MCP | Modelo de gestos | Futuro |

Todos estes dispositivos teriam de existir na plataforma da Altice. A ferramenta de escrita do MCP aceita hoje ligar e desligar, brilho, temperatura de cor e cor: chegaria para uma válvula, uma rega ou um holofote vistos como interruptores, mas não para estores ou portões com posição (a confirmar com a Altice).

### Limites comuns a todos os casos

- Os modelos só correm quando há movimento ou som. As regras de ausência (`nobody_for`, `nobody_by`, `not_by`) medem “não se viu movimento”, e não “não está ninguém”: uma pessoa a ler, imóvel, pode contar como ausente.
- Objetos pequenos à distância (uma faca, uma caixa de comprimidos, as chaves) ocupam poucas dezenas de píxeis; a câmara tem de ficar perto do sítio que importa.
- “Perto” mede-se na imagem, a duas dimensões. O modelo de profundidade previsto na arquitetura reduz este erro, mas não o elimina.
- No protótipo, o vocabulário de superfícies é secretária, mesa, prateleira, sofá e bancada de trabalho; acrescentar bancada de cozinha, fogão e forno é uma pequena extensão.
- Cada regra tem um tempo de espera entre avisos, para não repetir o mesmo aviso; os casos duvidosos podem ser verificados pelo modelo de linguagem a partir de um único recorte.
- Do evento à ação passam cerca de 2 a 3 s, medidos no portátil da equipa.
- O servidor MCP não tem notificações _push_ nem um fluxo de eventos; o protótipo consulta os sensores periodicamente.
- Um dispositivo que não está no kit só serve se a plataforma da Altice o suportar e o puder instalar, o que a Altice não garante.

## 2. Câmaras: quantas, onde e com que regras

### 2.1 Quantas

Preveem-se duas ou três câmaras dentro de casa e, numa moradia, uma ou duas no exterior (pressuposto da equipa):
- uma na cozinha, onde se concentram 11 dos 34 casos (S1 a S5, S10, C1, C2, C3, C5 e T1);
- uma na sala ou na entrada, para a presença, os objetos e as saídas;
- numa moradia, uma à porta ou no portão (encomendas, carro, intrusão) e, havendo jardim, uma no jardim ou nas traseiras;
- num apartamento, nenhuma no exterior: a porta dá para o patamar, que é parte comum do prédio e não do domínio exclusivo do cliente (secção 2.6).

Cada câmara é um lugar. Duas câmaras na mesma divisão são dois lugares (“Cozinha 1”, “Cozinha 2”).

Três factos condicionam o número de câmaras:
- O ciclo completo de perceção demora cerca de 0,65 s por imagem no portátil da equipa, ou seja, cerca de 1,5 imagens por segundo. Com três câmaras com movimento ao mesmo tempo, o equipamento local alterna entre elas; a cadência por câmara desce na mesma proporção (estimativa, não medida).
- Como os modelos só correm quando há movimento, o custo de eletricidade acompanha as horas de movimento, e não o número de câmaras.
- A câmara do kit só usa Wi-Fi de 2,4 GHz e envia vídeo H.265 em 2304 × 1296, a 20 imagens por segundo (verificado a 18 de novembro).

### 2.2 Interior e exterior

| Aspeto | Interior | Exterior, à porta |
|---|---|---|
| Para que serve | Segurança na cozinha, cuidado, objetos, presença | Intrusão, pessoas à noite, encomendas, o carro, o que fica lá fora |
| Casos | S1 a S10, C1 a C7, V1 a V6, T1, T2 | E1 a E9, parte de T2 |
| Cuidados | Fora de quartos e casas de banho | Só a propriedade e, no estritamente necessário, os acessos ao imóvel; nem a rua nem os vizinhos; aviso afixado (a verificar); só o movimento como gatilho, sem som (secção 2.6) |
| Equipamento | Câmara do kit | Câmara exterior (outro IoT), ou a do kit numa entrada coberta, se a Altice o confirmar |

### 2.3 Onde colocar

- Cozinha: num canto alto, com a bancada, o fogão e as taças dos animais no campo de visão; sem uma janela em contraluz; o mais perto possível da bancada (2 a 3 m, pressuposto a medir), para que uma faca continue visível.
- Entrada: virada para a porta, por dentro, com a mesa ou o prato onde ficam as chaves.
- Sala: com o sofá, a mesa e a janela que tem o sensor de contacto.
- Exterior: à porta, só o tapete e a própria porta; no jardim, virada para dentro da propriedade, e não para a rua nem para o vizinho; abrigada da chuva; com visão noturna ou um holofote.

### 2.4 O que cada lugar permite

| Lugar | Casos | Dispositivos que acrescentam valor |
|---|---|---|
| Cozinha | S1, S2, S3, S4, S5, S10, C1, C2, C3, C5, V6, T1 | Detetor de fumo e tomada (kit); placa ou forno conectados, sensor de inundação, eletroválvula, coluna inteligente (outro IoT) |
| Sala | S5, S6, S7, C3, C4, C5, V2, V3, V4, V5, V6 | Sensor de temperatura, tomada e lâmpada (kit); sensores de contacto nas janelas, termóstato (outro IoT) |
| Entrada, por dentro | S7, S8, C6, C7, V1, V2 | Sensor de contacto da porta e lâmpada (kit); fechadura inteligente (outro IoT) |
| Exterior, à porta | E1, E4, E5 | Lâmpada (kit); sensor na caixa do correio, coluna dentro de casa (outro IoT) |
| Jardim e portão | E2, E3, E4, E7, E8 | Holofotes, estores, coluna exterior, sensor no portão, rega (outro IoT) |
| Entrada da garagem | E6 | Motor do portão da garagem (outro IoT) |
| Traseiras | E1, E9, T2 | Sensor de contacto (kit); portinhola com fecho elétrico (outro IoT) |

### 2.5 Regras de privacidade

- O cliente escolhe onde ficam as câmaras. A solução não prevê câmaras em quartos nem em casas de banho; nessas divisões, os sensores de presença sem imagem (outro IoT) cobrem os casos de cuidado.
- Os modelos só correm quando há movimento ou som; no resto do tempo, a câmara fica em repouso.
- Opção de recorte em tempo real: tudo o que não é o objeto seguido é removido da imagem antes de qualquer análise. É uma opção proposta pela equipa; hoje, o protótipo já envia ao servidor apenas pequenos recortes, nunca imagens completas.
- As pessoas são detetadas como “uma pessoa” ou “uma criança”, sem identificação. O reconhecimento dos familiares é opcional, ativado pessoa a pessoa, com consentimento, e feito no equipamento de casa.
- O cliente pode marcar máscaras: zonas da imagem que nunca são analisadas.
- O _ThingTracker_ não grava vídeo; as observações ficam 30 dias no equipamento de casa.
- Prazo de conservação dos acontecimentos da linha do tempo (proposta): 30 dias por omissão, e depois são apagados; os que a família fixar, por exemplo os de um alarme, ficam mais tempo, até a família os apagar ou até um prazo máximo por definir. Do som, guarda-se só a etiqueta (“latido, 4h02”), nunca o áudio. O registo das ações executadas na casa, previsto na arquitetura, fica 90 dias.
- Só os casos de segurança com pessoas (S7, E1, E2 e E4) enviam a fotografia de uma pessoa. Os outros enviam o recorte de um objeto ou nenhuma imagem (C6, por exemplo, nunca envia fotografia).

### 2.6 Câmaras exteriores em Portugal: privacidade e lei

Esta secção não é um parecer jurídico: resume as fontes primárias verificadas pela equipa a 18 de novembro de 2026 e assinala o que falta verificar.

- O que a câmara pode filmar. A Lei n.º 58/2019, que executa o RGPD em Portugal, diz no artigo 19.º, n.º 2, alínea a), que as câmaras não podem incidir sobre “vias públicas, propriedades limítrofes ou outros locais que não sejam do domínio exclusivo do responsável, exceto no que seja estritamente necessário para cobrir os acessos ao imóvel” (Diário da República, 1.ª série, n.º 151, de 8 de agosto de 2019).
- Quando se aplica o RGPD. Uma câmara que filma só o jardim vedado da própria casa fica, em princípio, abrangida pela isenção doméstica do artigo 2.º, n.º 2, alínea c), do RGPD; deixa de ficar se se estender, ainda que em parte, ao espaço público ou à propriedade do vizinho (Comité Europeu para a Proteção de Dados, Diretrizes 3/2019, versão 2.0, n.os 12 e 13; Tribunal de Justiça da UE, acórdão Ryneš, C-212/13, de 11 de dezembro de 2014).
- Som. O mesmo artigo 19.º, no n.º 4, proíbe a captação de som onde a videovigilância é admitida, salvo com as instalações encerradas ou com autorização prévia da CNPD. Como a solução usa o som como gatilho da análise, as câmaras exteriores passam a usar só o movimento; falta verificar se a regra se aplica a uma casa particular. Pela mesma razão, o caso T2 guarda só a etiqueta do som, e nunca o áudio.
- Aviso. O artigo 19.º, n.º 1, remete para os requisitos do artigo 31.º da Lei n.º 34/2013, que, segundo fontes secundárias, incluem um aviso afixado em local visível; a redação atual desse artigo e a sua aplicação a uma casa particular estão por verificar. Quando o RGPD se aplica, as Diretrizes 3/2019 (secção 7.1) põem o sinal de aviso como primeiro nível de informação.
- Matrículas e rostos. Uma matrícula é um dado pessoal (Diretrizes 3/2019, n.º 8). Ler matrículas ou reconhecer rostos só por opção explícita do cliente, depois de uma avaliação jurídica e de uma avaliação de impacto (AIPD).
- Orientação da CNPD para câmaras domésticas: a verificar.

O que o produto faria (propostas da equipa):
- Ao instalar uma câmara exterior, a aplicação pede ao cliente que tire a rua e a casa do vizinho da imagem e lembra o aviso.
- As máscaras do _ThingTracker_ impedem a análise do que sobrar, mas não mudam o que a câmara capta; o enquadramento correto vem primeiro.
- Nenhuma fotografia de pessoas sai de casa, exceto nos casos de segurança E1, E2 e E4, e nenhuma pessoa é identificada sem consentimento.

## 3. Casos de uso e critérios de avaliação

### 3.1 Os critérios

Critérios e ponderações dos artigos 16.º e 18.º das Normas de Participação (`sources/rules/normas-2026.pdf`).

| Critério | Intermédia | Final | Como o _ThingTracker_ responde | Onde está a prova |
|---|---|---|---|---|
| Enquadramento e resposta ao Desafio | 25 % | 20 % | A câmara passa a ser uma fonte de informação; uma frase torna-se um sensor, “para além dos comandos”; os casos combinam a câmara com os sensores do kit; o MCP está integrado (lê a porta e atua na tomada e na luz); os casos de segurança na cozinha respondem ao pedido dos mentores | Protótipo (`prototype/`); relatório (Figura 1 e lista de casos); vídeo (`video/`, em curso); este documento |
| Facilidade de adoção do Projeto por parte dos Desafiadores | 25 % | 20 % | Um quinto separador na aplicação existente; as ações seguem pelo MCP que a Altice já tem; as regras ficam guardadas como cenários da plataforma; 24 dos 34 casos usam só dispositivos do kit, e os 9 do exterior acrescentam uma câmara exterior | Arquitetura (`docs/pt/14-arquitetura.md`, §3 e D5); especificação de integração (`docs/pt/15-especificacao-integracao.md`); réplica da aplicação no protótipo |
| Viabilidade de implementação e gestão futura (sustentabilidade) do Projeto | 25 % | 20 % | Modelos _open-source_ de uso comercial livre; visão só quando há movimento, no _router_ ou em servidores da Altice; o modelo de linguagem só é chamado ao criar uma regra ou responder a uma pergunta; cerca de 0,43 € por casa e por mês em modelo de linguagem e 0,49 € em visão (estimativa do relatório); 7 casos já funcionam e 22 são pequenas extensões | Relatório (“Ferramentas de IA”); arquitetura (§8); viabilidade de negócio (`docs/pt/16-viabilidade-negocio.md`) |
| Possibilidade de replicação em outros territórios e contextos | — (não avaliado nesta fase) | 20 % | Serviço de plataforma para qualquer operador; nenhum dado é específico de Portugal; o modelo de linguagem fala a língua do utilizador; a França é o segundo mercado analisado; as regras das câmaras exteriores mudam de país para país e teriam de ser revistas em cada um | Viabilidade de negócio (secção sobre França); arquitetura (requisito N5) |
| Apresentação da solução | 25 % | 10 % | Demonstração ao vivo com a câmara do kit e o livro; vídeo com o caso da faca e do gato (ilustração); casos explicados numa frase; cinco casos para o _pitch_ e o vídeo, um deles ao vivo (secção 5) | Vídeo; protótipo; _pitch_ |
| Documentação (Entregáveis) da solução | — (não avaliado nesta fase) | 10 % | Relatório de duas páginas; arquitetura, especificação de integração, viabilidade de negócio e casos de uso, em português e em inglês | `deliverables/`, `docs/pt/`, `docs/` |

### 3.2 Matriz

Autoavaliação da equipa, para discussão. Escala de cada critério:
- Enquadramento: forte se a câmara for uma fonte de informação combinada com outro sensor ou uma ação, num caso pedido pelos mentores ou fora da oferta atual da Altice; médio se a câmara só acrescentar contexto a um alerta que já existe.
- Adoção: forte se bastar o kit; médio se exigir mais unidades do kit ou um dispositivo que a Altice já refere na sua oferta; fraco se exigir um tipo de dispositivo novo na plataforma.
- Viabilidade: forte se já funcionar no protótipo; médio se for uma pequena extensão; fraco se for futuro.
- Replicação: forte se não depender do país nem da casa; médio se depender de regras locais ou de um dispositivo de terceiros.
- Apresentação: forte se puder ser mostrado ao vivo ou no vídeo, ou se fizer parte dos casos para a apresentação (secções 4 e 5); médio se só for descrito.
- Documentação: forte se constar também do relatório ou da arquitetura; médio se constar só deste documento.

| Caso | Enquadramento | Adoção | Viabilidade | Replicação | Apresentação | Documentação |
|---|---|---|---|---|---|---|
| S1 Faca e animal ou criança | forte | forte | médio | forte | forte | forte |
| S2 Criança, faca, fogão | forte | forte | médio | forte | forte | médio |
| S3 Fogão sem ninguém | forte | médio | médio | médio | forte | forte |
| S4 Fumo: quem está | médio | forte | médio | forte | médio | médio |
| S5 Produtos perigosos | forte | forte | médio | forte | médio | médio |
| S6 Janela e criança | forte | médio | médio | forte | médio | médio |
| S7 Pessoa desconhecida | forte | forte | médio | médio | médio | forte |
| S8 Porta aberta | médio | forte | médio | forte | médio | médio |
| S9 Fuga de água | médio | médio | fraco | forte | médio | médio |
| S10 Fumo, chama, água vistos | forte | forte | fraco | forte | médio | médio |
| C1 Taças do animal | forte | forte | forte | forte | forte | forte |
| C2 Pessoa idosa | forte | forte | forte | forte | forte | forte |
| C3 Medicamentos | forte | forte | médio | forte | médio | médio |
| C4 Casa fria | forte | forte | médio | forte | médio | médio |
| C5 Queda | forte | forte | fraco | forte | médio | médio |
| C6 Criança chega | médio | forte | forte | forte | médio | forte |
| C7 Animal sai pela porta | forte | forte | médio | forte | médio | forte |
| V1 Sair sem o livro | forte | forte | forte | forte | forte | forte |
| V2 “Onde está?” | forte | forte | forte | forte | forte | forte |
| V3 Energia | médio | forte | forte | forte | médio | médio |
| V4 Animal no sofá | forte | forte | forte | forte | médio | médio |
| V5 Presença e postura | médio | médio | médio | forte | médio | médio |
| V6 Gestos | médio | forte | fraco | forte | médio | médio |
| E1 Intrusão | forte | médio | médio | médio | médio | médio |
| E2 Pessoa à noite | forte | médio | médio | médio | forte | médio |
| E3 Portão aberto | forte | médio | médio | médio | forte | médio |
| E4 Furto no exterior | forte | médio | médio | médio | forte | médio |
| E5 Encomendas | forte | médio | médio | médio | forte | forte |
| E6 Carro e matrícula | médio | fraco | médio | médio | médio | médio |
| E7 Coisas lá fora | forte | médio | médio | médio | médio | médio |
| E8 Rega no jardim | médio | fraco | médio | médio | médio | médio |
| E9 Portinhola | médio | fraco | fraco | médio | médio | médio |
| T1 Chegar tarde demais | forte | forte | médio | forte | forte | médio |
| T2 O que aconteceu às 4h | forte | forte | médio | médio | forte | médio |

Na Documentação, “forte” segue o relatório submetido a 18 de novembro, cujo exemplo principal é a criança em perigo (S2 + S5) e que refere também S3, C1, C2, V1 e E5, e a arquitetura.

## 4. Os 8 casos para a apresentação

Os oito casos mais fortes para os diapositivos e para o vídeo: a segurança primeiro, quatro dentro de casa e quatro no exterior. Só C2 e V1 funcionam hoje no protótipo; os outros mostram-se como conceito, e o vídeo deve dizê-lo, por exemplo com a legenda “conceito”. A secção 5 reduz a escolha a 10 finalistas e aos 5 do _pitch_; as cenas desta secção ficam como reserva.

| # | Gancho | Caso | Onde |
|---|---|---|---|
| 1 | Uma faca na bancada. O gato salta. | S1 | Interior |
| 2 | Alguém no jardim às três da manhã. | E2 | Exterior |
| 3 | A placa ligada e ninguém na cozinha. | S3 | Interior |
| 4 | Portão aberto, cão no jardim. | E3 | Exterior |
| 5 | A bicicleta já não está no jardim. | E4 | Exterior |
| 6 | Meio-dia, e a avó não veio à cozinha. | C2 | Interior |
| 7 | A encomenda chegou; a luz fica azul. | E5 | Exterior |
| 8 | Ia sair sem o livro. | V1 | Interior |

### 4.1 Uma faca na bancada. O gato salta. (S1)

- Cena: a câmara da cozinha, do alto, vê uma faca na bancada (caixa “faca”). O gato salta para a bancada (caixa “gato”); ao fim de 3 segundos, as duas caixas ficam vermelhas e a lâmpada da cozinha também. Variante: uma criança em vez do gato.
- Aviso no telemóvel: “Há uma faca na bancada e o gato está perto.”, com o recorte e os botões “Tocar a sirene” e “Ignorar”.
- Dispositivos: câmara e lâmpada (kit).
- Estado: pequena extensão; no vídeo, ilustração.

### 4.2 Alguém no jardim às três da manhã. (E2)

- Cena: imagem noturna, a preto e branco, do jardim; uma pessoa (caixa “pessoa”) junto ao portão lateral; um contador chega aos 30 segundos; os holofotes acendem-se e os estores descem.
- Aviso no telemóvel: “Está uma pessoa no jardim há 30 segundos e não está ninguém da família em casa.”, com o recorte e os botões “Tocar a sirene”, “Ladrar na coluna” e “Ignorar”.
- Dispositivos: câmara exterior, holofotes, estores e coluna (outro IoT); central de segurança (kit).
- Estado: pequena extensão e equipamento novo; conceito.

### 4.3 A placa ligada e ninguém na cozinha. (S3)

- Cena: um tacho na placa; a última pessoa sai da cozinha e a caixa “pessoa” desaparece; um contador sobe até 15 minutos.
- Aviso no telemóvel: “A placa está ligada e não está ninguém na cozinha há 15 minutos.”, com o botão “Desligar”.
- Dispositivos: câmara, tomada e detetor de fumo (kit); placa conectada (outro IoT).
- Estado: pequena extensão; conceito.

### 4.4 Portão aberto, cão no jardim. (E3)

- Cena: o jardim de dia; o portão entreaberto (caixa “portão aberto”) e o cão no relvado (caixa “cão”).
- Aviso no telemóvel: “O portão ficou aberto e o cão está no jardim.”, com o recorte do portão; dentro de casa, a lâmpada fica âmbar.
- Dispositivos: câmara exterior e sensor de contacto no portão (outro IoT); lâmpada (kit).
- Estado: pequena extensão; conceito.

### 4.5 A bicicleta já não está no jardim. (E4)

- Cena: a bicicleta registada (caixa “bicicleta”, com a marca de objeto registado) encostada à parede; uma pessoa aproxima-se (caixa “pessoa”); pouco depois, a caixa da bicicleta desaparece.
- Aviso no telemóvel: “A bicicleta deixou de ser vista às 14h05 e não está ninguém da família em casa.”, com o último recorte da bicicleta e o da pessoa vista junto dela.
- Dispositivos: câmara exterior (outro IoT).
- Estado: pequena extensão; conceito.

### 4.6 Meio-dia, e a avó não veio à cozinha. (C2)

- Cena: a cozinha vazia; uma linha do tempo das 7h às 12h sem nenhuma caixa “pessoa”; às 12h, o relógio fica vermelho.
- Aviso no telemóvel da filha: “Ninguém passou na cozinha desde as 7h.”
- Dispositivos: câmara (kit).
- Estado: funciona hoje no protótipo.

### 4.7 A encomenda chegou; a luz fica azul. (E5)

- Cena: a câmara da porta vê uma caixa de cartão no tapete (caixa “encomenda”); dentro de casa, a lâmpada fica azul e a coluna diz “Chegou uma encomenda à porta.”
- Aviso no telemóvel: “Deixaram uma encomenda à porta às 11h20.”, com o recorte da encomenda, e só da encomenda.
- Dispositivos: câmara exterior e coluna (outro IoT); lâmpada (kit).
- Estado: pequena extensão e equipamento novo; conceito (a luz azul já existe no protótipo).

### 4.8 Ia sair sem o livro. (V1)

- Cena: imagem real da câmara do kit; o livro na mesa (caixa “livro”, reconhecido pela assinatura visual); a porta abre (sensor de contacto) e, 60 segundos depois, o livro continua em casa.
- Aviso no telemóvel: “Saíste sem o livro. Está na mesa.”, com a fotografia e o último lugar.
- Dispositivos: sensor de contacto da porta, câmara e lâmpada (kit).
- Estado: funciona hoje no protótipo; é o exemplo real do vídeo.

## 5. Os 10 finalistas e os 5 para o _pitch_

A equipa quer, no máximo, 10 casos fortes e, destes, 5 para o _pitch_ e para o vídeo. A escolha parte do catálogo (secção 1) e do caso que o relatório entregue a 18 de novembro usa: a criança em perigo na cozinha, com a regra “avisa-me se a criança estiver em perigo”, em que o modelo de linguagem define o perigo (um detergente, uma faca, o fogão). No catálogo, esse caso junta S2 e S5.

### 5.1 Como se pontua

Cada critério vai de 1 a 5:
- Impacto: o que a família ganha ou evita.
- Novidade: quanto surpreende; usar a câmara como fonte de informação conta a favor.
- Viabilidade: com o kit e, no máximo, um dispositivo a mais; 5 se já funciona no protótipo.
- Demonstração: 5 se funciona ao vivo com o kit; 4 se se filma com facilidade; 3 se exige encenação ou tempo de espera.
- Critérios: adequação aos critérios dos artigos 16.º e 18.º das Normas (enquadramento, adoção, viabilidade, replicação).
- Privacidade: o risco, de 1 (baixo) a 5 (alto). Entra no total invertido, como 6 menos o risco.

O total máximo é 30. É uma autoavaliação da equipa, para discussão.

### 5.2 Os 10 finalistas

Escolhidos para cobrir a criança em risco, os animais, a pessoa idosa, a segurança, os perdidos e achados e os casos que mostram a câmara como fonte de informação (C3, V2, T1 e T2). Os dois casos da linha do tempo da casa, T1 (24 pontos) e T2 (22), entraram para o lugar da encomenda à porta (E5, 19) e da pessoa no jardim à noite (E2, 18). O exterior e a segurança ficam representados por T2.

| # | Caso | Cat. | Imp. | Nov. | Viab. | Demo | Crit. | Priv. | Total |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Sair sem o livro, a carteira ou as chaves | V1 | 3 | 4 | 5 | 5 | 5 | 1 | 27 |
| 2 | Faca na bancada e o gato por perto | S1 | 4 | 4 | 4 | 4 | 5 | 1 | 26 |
| 3 | Ninguém na cozinha até ao meio-dia | C2 | 5 | 4 | 5 | 3 | 5 | 2 | 26 |
| 4 | A caixa dos comprimidos não saiu do lugar | C3 | 4 | 5 | 4 | 4 | 4 | 1 | 26 |
| 5 | “Onde está a carteira?” | V2 | 3 | 4 | 5 | 5 | 5 | 2 | 26 |
| 6 | A criança em perigo: detergente, faca, fogão | S2 + S5 | 5 | 5 | 3 | 4 | 5 | 4 | 24 |
| 7 | A placa ligada e ninguém na cozinha | S3 | 5 | 3 | 4 | 3 | 5 | 2 | 24 |
| 8 | Chegar tarde demais: o que esteve perto da criança | T1 | 4 | 5 | 4 | 4 | 5 | 4 | 24 |
| 9 | O gato não foi à taça | C1 | 3 | 3 | 5 | 3 | 4 | 1 | 23 |
| 10 | O que aconteceu às 4h? | T2 | 4 | 5 | 3 | 4 | 4 | 4 | 22 |

Cat.: caso no catálogo; Imp.: impacto; Nov.: novidade; Viab.: viabilidade; Demo: demonstração; Crit.: critérios; Priv.: privacidade (risco, de 1 a 5, que entra no total como 6 menos o risco).

### 5.3 A razão de cada nota

#### V1. Sair sem o livro, a carteira ou as chaves – 27

- Impacto 3: poupa um esquecimento diário, mas não evita um perigo.
- Novidade 4: a câmara lembra-se do objeto e o sensor da porta fecha o ciclo.
- Viabilidade 5: funciona hoje, só com o kit.
- Demonstração 5: ao vivo, com o livro amarelo, a porta e a lâmpada do kit.
- Critérios 5: mostra o MCP a ler um sensor e a agir; é o exemplo real dos entregáveis.
- Privacidade (risco) 1: segue um objeto; ninguém é identificado.

#### S1. Faca na bancada e o gato por perto – 26

- Impacto 4: evita que um animal se corte; é o caso que os mentores deram.
- Novidade 4: a câmara relaciona duas coisas, a faca e o gato, e não só movimento.
- Viabilidade 4: só o kit; faltam a pesquisa “faca” e a regra “perto”.
- Demonstração 4: filma-se bem; ao vivo, exigiria um gato no local.
- Critérios 5: segurança pedida pelos mentores, a câmara como fonte de informação, só o kit.
- Privacidade (risco) 1: nenhuma pessoa na imagem do aviso.

#### C2. Ninguém na cozinha até ao meio-dia – 26

- Impacto 5: dá o alerta horas mais cedo a quem tem um pai ou uma mãe a viver só; em 2021 viviam sós 517 146 pessoas com 65 ou mais anos.
- Novidade 4: a rotina da casa passa a ser um sinal, sem câmara no quarto e sem identificar ninguém.
- Viabilidade 5: funciona hoje, só com o kit.
- Demonstração 3: a ausência mostra-se com uma linha do tempo, e não ao vivo.
- Critérios 5: encaixa na linha “envelhecer em casa” da Altice e replica-se em qualquer país.
- Privacidade (risco) 2: deteta “uma pessoa”, sem fotografias; pede o acordo da própria pessoa.

#### C3. A caixa dos comprimidos não saiu do lugar – 26

- Impacto 4: um medicamento esquecido pode ter consequências sérias.
- Novidade 5: a câmara transforma um objeto parado em informação; é o exemplo mais claro da ideia.
- Viabilidade 4: só o kit; falta a regra “não saiu do lugar”.
- Demonstração 4: encena-se numa mesa com a câmara do kit; o registo da caixa já funciona.
- Critérios 4: cuidado e envelhecimento em casa; mexer na caixa não prova a toma.
- Privacidade (risco) 1: segue um objeto.

#### V2. “Onde está a carteira?” – 26

- Impacto 3: poupa tempo todos os dias.
- Novidade 4: a resposta traz o lugar, a hora e a fotografia: a câmara como memória da casa.
- Viabilidade 5: funciona hoje.
- Demonstração 5: ao vivo, logo a seguir ao V1.
- Critérios 5: é o núcleo do _ThingTracker_ e usa o modelo de linguagem para além dos comandos.
- Privacidade (risco) 2: guarda 30 dias de observações de objetos, que revelam rotinas.

#### S2 + S5. A criança em perigo: detergente, faca, fogão – 24

- Impacto 5: detergentes, facas e o fogão são perigos reais para uma criança pequena.
- Novidade 5: uma frase vaga torna-se várias regras concretas, escritas pelo modelo de linguagem.
- Viabilidade 3: só o kit; “perto” é uma pequena extensão, mas “na mão” ou “na boca” exige um modelo de pose (futuro); uma cápsula é pequena à distância.
- Demonstração 4: filma-se encenado ou ilustrado; filmar uma criança real exige o acordo dos pais.
- Critérios 5: é o caso do relatório entregue: segurança, perceção e ação numa só história.
- Privacidade (risco) 4: guarda a assinatura visual de uma criança e envia a fotografia dela no aviso; só com o consentimento dos pais.

#### S3. A placa ligada e ninguém na cozinha – 24

- Impacto 5: um fogão esquecido pode causar um incêndio.
- Novidade 3: o aviso de fogão esquecido não é novo; a novidade é a câmara saber que a cozinha está vazia.
- Viabilidade 4: a tomada do kit serve os aparelhos de bancada; uma placa conectada seria o único dispositivo a mais.
- Demonstração 3: precisa de um aparelho ligado e de 15 minutos de espera, acelerados no vídeo.
- Critérios 5: mostra uma ação real pelo MCP: desligar a tomada, a única escrita já testada.
- Privacidade (risco) 2: deteta “uma pessoa”, sem fotografias.

#### T1. Chegar tarde demais: o que esteve perto da criança – 24

- Impacto 4: numa urgência, saber o quê e a que horas ajuda o médico; felizmente, é raro.
- Novidade 5: a memória da casa responde a “o que aconteceu?” com imagens, e não só com avisos.
- Viabilidade 4: só o kit; a linha do tempo existe; falta juntar a criança e o objeto num acontecimento com recorte.
- Demonstração 4: filma-se como epílogo da cena da criança em perigo.
- Critérios 5: completa o caso do relatório e usa o modelo de linguagem para responder a uma pergunta.
- Privacidade (risco) 4: guarda recortes de uma criança durante dias; só com o consentimento dos pais e com prazo.

#### C1. O gato não foi à taça – 23

- Impacto 3: um animal que deixa de comer ou de beber pode estar doente, e o aviso chega no próprio dia.
- Novidade 3: a proposta automática surpreende; o resto é simples.
- Viabilidade 5: funciona hoje, incluindo a proposta quando a câmara vê o gato.
- Demonstração 3: exige um gato e horas de espera; mostra-se sobretudo a proposta no telemóvel.
- Critérios 4: pedido dos mentores; só o kit.
- Privacidade (risco) 1: nenhuma pessoa.

#### T2. O que aconteceu às 4h? – 22

- Impacto 4: depois de um assalto, a família e os vizinhos sabem onde procurar.
- Novidade 5: o invulgar (o cão a ladrar às 4h) passa a ser informação; nasce de uma história real.
- Viabilidade 3: a linha do tempo existe; o latido e o “invulgar” exigem modelos novos (futuro), e a janela, a câmara exterior.
- Demonstração 4: uma linha do tempo noturna filma-se bem, e a história real conta-se depressa.
- Critérios 4: a segurança já está na oferta da Altice, mas a linha do tempo é nova; o som tem uma questão jurídica.
- Privacidade (risco) 4: som, câmara exterior e imagens de pessoas; do som guarda-se só a etiqueta.

### 5.4 Os 5 para o _pitch_ e o vídeo

| Ordem | Caso | Papel na história |
|---|---|---|
| 1 | A criança em perigo (S2 + S5), com o epílogo “chegar tarde demais” (T1) | Abre com o medo e com a ideia nova, uma frase vaga que o modelo de linguagem transforma em regras; o epílogo mostra a memória da casa |
| 2 | Faca na bancada e o gato (S1) | Os animais; o caso que os mentores deram |
| 3 | Ninguém na cozinha até ao meio-dia (C2) | O cuidado com quem vive só; funciona hoje |
| 4 | O que aconteceu às 4h? (T2) | A noite e a segurança, contadas com uma história verdadeira |
| 5 | Ao vivo: sair sem o livro e “onde está o livro?” (V1 e V2) | A prova: o livro amarelo, o sensor da porta do kit e a lâmpada a ficar vermelha |

Porque contam, juntos, a melhor história:
- Variedade: uma criança, um animal, uma pessoa idosa, a segurança à noite e os objetos do dia a dia; os avisos no momento e a memória da casa depois.
- Arco emocional: começa no medo (a criança), passa pela ternura (o gato, a avó), pela inquietação da noite (o cão que ladrou às 4h) e acaba na prova de que funciona.
- Um só fio: em todas, a câmara vê uma coisa e a casa percebe o que ela significa e lembra-se dela; quatro das cinco cenas só precisam do kit (T2 usa a câmara exterior para a janela), e duas já funcionam no protótipo (C2 e V1).
- A demonstração ao vivo fecha: depois de quatro casos em vídeo, o júri vê o kit real a funcionar.
- Ficam de fora casos com boa nota que repetiriam um tema: C3 (comprimidos) repete a pessoa idosa e S3 (placa) repete a cozinha; T1 e V2 entram como epílogos. A encomenda à porta (E5), que saiu dos 10, pode voltar como momento leve, se a equipa preferir terminar a parte em vídeo com uma boa notícia.

Uma linha de guião por cena:
1. Criança em perigo: primeiro, a frase “avisa-me se a criança estiver em perigo” e as três regras que o modelo escreveu (detergente, faca, fogão); depois, na cozinha, a criança (caixa “criança”) estende a mão para uma cápsula de detergente (caixa “detergente”) e as caixas ficam vermelhas; no telemóvel: “A criança está junto a um detergente. Cozinha, 16h30.”, com a fotografia e os botões “Ligar alarme” e “Tudo bem”. Epílogo (T1): a mãe pergunta “o que esteve perto dela esta tarde?” e vê a sequência, cada passo com o recorte: “16h28, junto a um detergente; 16h29, junto a um copo”.
2. Faca e gato: a câmara da cozinha, do alto, vê uma faca na bancada (caixa “faca”); o gato salta (caixa “gato”) e, 3 segundos depois, as caixas e a lâmpada ficam vermelhas; no telemóvel: “Há uma faca na bancada e o gato está perto.”
3. Avó: a cozinha vazia e uma linha do tempo das 7h às 12h sem nenhuma caixa “pessoa”; ao meio-dia, o relógio fica vermelho; no telemóvel da filha: “Ninguém passou na cozinha desde as 7h.”
4. O que aconteceu às 4h: de noite, a família pergunta “o que aconteceu esta noite?”; a linha do tempo mostra dois acontecimentos invulgares, “4h02, sala: o cão ladrou, o que nunca faz a esta hora” (só a etiqueta, sem som gravado) e “4h05, traseiras: uma pessoa junto à janela” (caixa “pessoa”, com o recorte); a família fixa os dois para os guardar.
5. Ao vivo, com a câmara do kit: o livro amarelo na mesa (caixa “livro”, reconhecido com uma semelhança de 0,70); a porta abre (sensor do kit) e a lâmpada fica vermelha; no telemóvel: “Saíste sem o livro. Está na mesa.”; por fim, a pergunta “onde está o livro?” e a resposta com a fotografia.

Antes de filmar:
- A Figura 1 do relatório mostra o aviso “A criança pôs um detergente na boca.” Hoje, a câmara só consegue dizer “junto a”; “na mão” ou “na boca” exige um modelo de pose (futuro). Para o vídeo, propõe-se “junto a um detergente”, ou a legenda “conceito”.
- A criança aparece em ilustração, ou numa encenação com o acordo dos pais.
- Em T2, reconhecer o latido e o “invulgar” é futuro: no vídeo, a cena é conceito. A história verdadeira conta-se sem nomes.
- A lâmpada a ficar vermelha ao vivo exige ligar as ações reais do protótipo, com a aprovação da equipa, e a lâmpada a comunicar com a plataforma (a 16 de novembro não comunicava desde 4 de novembro; a confirmar). Sem isso, a aplicação mostra a chamada MCP simulada.
- O protótipo espera 60 segundos depois de a porta abrir; numa demonstração de 3 minutos, convém encurtar esse tempo, que é um parâmetro da regra.

## 6. Proposta de valor

- Para a família: a câmara que já existe em casa passa a avisar dos perigos que ninguém está a ver (a faca ao alcance do gato, o fogão esquecido, a avó que não veio à cozinha, alguém no jardim de noite) e a responder a “onde está?”.
- Para a família: cada aviso nasce de uma frase ou de uma proposta aceite com um toque; a sirene só toca logo onde a família o escolheu, e nos outros casos depois de um “sim”; e nenhuma imagem completa sai de casa para análise.
- Para a Altice e a MEO, diferenciação: as câmaras e os sensores que já vendem passam a ser um serviço novo, dentro da aplicação e do MCP que já existem.
- Para a Altice e a MEO, receita: uma mensalidade adicional de 3,99 €, de que restam cerca de 1,74 € por casa, e cerca de 19 000 casas MEO no cenário esperado (pressupostos da viabilidade de negócio).
- Para a Altice Labs: um serviço de plataforma para qualquer operador, que dá razões para vender mais sensores (câmaras exteriores, holofotes, placa conectada, inundação, fechadura).

## 7. Pressupostos e questões em aberto

1. Duas ou três câmaras por casa é um pressuposto da equipa, por validar com clientes.
2. Serviço de notificações: o MCP não tem uma ferramenta para avisos; falta saber que serviço a aplicação usa.
3. Sirene: a ferramenta de escrita do MCP aceita ligar e desligar, brilho, temperatura de cor e cor; falta confirmar como se aciona a sirene da câmara ou da central. Segue a escolha da família para cada regra: perguntar primeiro ou tocar logo.
4. Outros dispositivos (placa ou forno conectados, sensor de inundação, fechadura, sensor da caixa do correio, coluna inteligente, sensores de presença): falta saber quais a plataforma suporta.
5. Câmara do kit no exterior (proteção IP65): falta confirmar com a Altice.
6. Potência máxima da tomada do kit: desconhecida.
7. Fiabilidade da deteção de facas, encomendas e caixas de medicamentos à distância: por medir.
8. Revisão jurídica: enquadramento da câmara exterior e reconhecimento de familiares.
9. Aviso das câmaras exteriores: a redação atual do artigo 31.º da Lei n.º 34/2013 e a sua aplicação a uma casa particular estão por verificar.
10. Som no exterior: falta verificar se a proibição do artigo 19.º, n.º 4, da Lei n.º 58/2019 se aplica a uma casa; até lá, as câmaras exteriores usam só o movimento como gatilho.
11. Matrículas: opção explícita do cliente, avaliação de impacto (AIPD) e parecer jurídico antes de qualquer piloto.
12. Dispositivos das ideias propostas na equipa (holofotes, estores, rega, portinhola, motor do portão, termóstato, coluna exterior): falta saber quais a plataforma suporta e se a ferramenta de escrita do MCP chega para os comandar.
13. Prazo de conservação da linha do tempo: 30 dias por omissão e mais tempo para os acontecimentos fixados é uma proposta, e o prazo máximo está por definir.
14. Partilha de imagens da linha do tempo com vizinhos ou com as autoridades: a verificar.

Fontes: Normas de Participação do Aveiro Tech City Hackathon 2026, artigos 16.º e 18.º; Lei n.º 58/2019, artigo 19.º (Diário da República, 1.ª série, n.º 151, 8 de agosto de 2019); Regulamento (UE) 2016/679 (RGPD), artigo 2.º, n.º 2, alínea c); Tribunal de Justiça da UE, acórdão Ryneš, C-212/13, 11 de dezembro de 2014; Comité Europeu para a Proteção de Dados, Diretrizes 3/2019 sobre o tratamento de dados pessoais através de dispositivos de vídeo, versão 2.0, 29 de janeiro de 2020 (n.os 8, 12 e 13, secção 7.1); as fontes jurídicas foram consultadas a 18 de novembro de 2026; INE, Censos 2021, quadro Q1.04 (soma das faixas etárias feita pela equipa, ver `docs/12-market-research.md`); Eurostat, `hlth_dhc140` (2025, consultado a 18 de novembro de 2026, ver `docs/12-market-research.md`); página do produto _Connected Home_ da Altice Labs (ver `docs/02-challenge.md`); viabilidade de negócio (`docs/pt/16-viabilidade-negocio.md`); medições da equipa, 18 de novembro de 2026.
