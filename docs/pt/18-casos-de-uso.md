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
- Lugar: cada câmara é um lugar (“Cozinha 1”, “Sala 1”). Dentro de um lugar não há zonas desenhadas; as superfícies (a bancada, o fogão) são encontradas pelo nome em cada imagem.
- Viabilidade: “hoje” significa que o protótipo já o faz; “pequena extensão” significa uma nova pesquisa ao detetor ou um novo tipo de regra, sem equipamento novo; “futuro” significa um modelo novo ou um dispositivo que a plataforma da Altice ainda teria de suportar.
- Ações: os avisos chegam ao telemóvel pelo serviço de notificações da aplicação, porque o servidor MCP não tem uma ferramenta de notificações (a confirmar com a Altice). As ações sobre os dispositivos (luz, tomada) seguem pelo MCP, com `update_device_capabilities`. A sirene e o alarme só atuam depois de um “sim” do utilizador; no protótipo, nenhum dos dois está ligado, e as ações sobre a luz e a tomada são simuladas, salvo se forem ativadas.

## 1. Catálogo, por ordem de prioridade

Primeiro a segurança, depois o cuidado e, por fim, a conveniência.

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
| C1 | Animal que não vai à taça da comida nem à da água | Cozinha | Kit | Hoje |
| C2 | Pessoa idosa: ninguém na cozinha até ao meio-dia | Cozinha | Kit | Hoje (hora fixa) |
| C3 | Caixa de medicamentos que não sai do lugar até à hora habitual | Cozinha, sala | Kit | Pequena extensão |
| C4 | Casa fria com uma pessoa na sala | Sala | Kit | Pequena extensão |
| C5 | Pessoa caída no chão | Cozinha, sala | Kit | Futuro |
| C6 | Uma criança chega a casa | Entrada | Kit | Hoje |
| C7 | Animal que sai quando a porta abre | Entrada | Kit | Pequena extensão |
| V1 | Sair de casa sem as chaves, a carteira ou o livro | Entrada | Kit | Hoje |
| V2 | Encomenda ou correio entregue | Exterior, à porta | Outro IoT | Pequena extensão e equipamento novo |
| V3 | “Onde está o livro?” | Todos | Kit | Hoje |
| V4 | Aparelho ligado numa divisão vazia | Sala | Kit | Hoje |

Dos 20 casos, 18 funcionam só com dispositivos do kit; 6 já funcionam no protótipo, 12 exigem uma pequena extensão (S7 já funciona em parte) e 2 ficam para o futuro.

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

#### V2. Encomenda ou correio entregue

- Frase: “Avisa-me quando deixarem uma encomenda à porta” ou “quando chegar correio”.
- A câmara procura: `"a cardboard box"` ou `"a parcel"`, no lugar “Porta” (exterior).
- Regras: `appears(encomenda, Porta) e fica 1 min` (novo); para o correio, `state(Caixa do correio) = aberta`.
- Dispositivos: câmara exterior à porta (outro IoT; a câmara do kit tem proteção IP65 e poderia, em princípio, ficar numa entrada coberta, pressuposto a confirmar com a Altice); sensor na caixa do correio (outro IoT), ou o sensor de contacto do kit na tampa da caixa, se ficar ao alcance da central (a confirmar).
- Ação: aviso com o recorte da encomenda, e só da encomenda.
- Viabilidade: pequena extensão (detetar uma classe de objeto sem registo e um tipo de regra “aparece”), mais equipamento novo.
- Limites: o enquadramento tem de excluir a rua e os vizinhos; a noite, a chuva e o contraluz reduzem a deteção; não se afirma que o sistema detete o furto de encomendas.

#### V3. “Onde está o livro?”

- Pergunta: “Onde está o livro?”
- A câmara procura: o livro registado, em todos os lugares.
- Regra: nenhuma; a resposta vem da última observação (lugar, hora e fotografia).
- Dispositivos: câmara (kit).
- Ação: resposta na aplicação, com a fotografia.
- Viabilidade: hoje.
- Limites: só responde com o que uma câmara viu; “visto pela última vez” não quer dizer “está lá agora”.

#### V4. Aparelho ligado numa divisão vazia

- Frase: “Se não estiver ninguém na sala há 30 minutos, desliga o aquecedor.”
- A câmara procura: a ausência de `"a person"`, na Sala 1.
- Regra: `nobody_for(Sala 1, 30 min) e power(Tomada) > 50 W`.
- Dispositivos: tomada com medição de consumo (kit); câmara (kit).
- Ação: desligar a tomada pelo MCP.
- Viabilidade: hoje (`nobody_for` e o desligar da tomada já existem; a condição de potência é uma pequena extensão).
- Limites: a gestão de energia já faz parte da oferta da Altice; ver a secção seguinte sobre pessoas paradas.

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

Preveem-se duas ou três câmaras por casa (pressuposto da equipa):
- uma na cozinha, onde se concentram 9 dos 20 casos (S1 a S5, C1, C2, C3 e C5);
- uma na sala ou na entrada, para a presença, os objetos e as saídas;
- opcionalmente, uma no exterior, à porta, para as encomendas.

Cada câmara é um lugar. Duas câmaras na mesma divisão são dois lugares (“Cozinha 1”, “Cozinha 2”).

Três factos condicionam o número de câmaras:
- O ciclo completo de perceção demora cerca de 0,65 s por imagem no portátil da equipa, ou seja, cerca de 1,5 imagens por segundo. Com três câmaras com movimento ao mesmo tempo, o equipamento local alterna entre elas; a cadência por câmara desce na mesma proporção (estimativa, não medida).
- Como os modelos só correm quando há movimento, o custo de eletricidade acompanha as horas de movimento, e não o número de câmaras.
- A câmara do kit só usa Wi-Fi de 2,4 GHz e envia vídeo H.265 em 2304 × 1296, a 20 imagens por segundo (verificado a 18 de novembro).

### 2.2 Interior e exterior

| | Interior | Exterior, à porta |
|---|---|---|
| Para que serve | Segurança na cozinha, cuidado, objetos, presença | Encomendas, visitas à porta |
| Casos | S1 a S9, C1 a C7, V1, V3, V4 | V2 e parte de S7 |
| Cuidados | Fora de quartos e casas de banho | Enquadrar só a entrada da própria casa; a rua e os vizinhos ficam de fora; a validação jurídica fica com a Altice |
| Equipamento | Câmara do kit | Câmara exterior (outro IoT), ou a do kit numa entrada coberta, se a Altice o confirmar |

### 2.3 Onde colocar

- Cozinha: num canto alto, com a bancada, o fogão e as taças dos animais no campo de visão; sem uma janela em contraluz; o mais perto possível da bancada (2 a 3 m, pressuposto a medir), para que uma faca continue visível.
- Entrada: virada para a porta, por dentro, com a mesa ou o prato onde ficam as chaves.
- Sala: com o sofá, a mesa e a janela que tem o sensor de contacto.
- Exterior: só o tapete da entrada, abrigada da chuva, sem a rua.

### 2.4 O que cada lugar permite

| Lugar | Casos | Dispositivos que acrescentam valor |
|---|---|---|
| Cozinha | S1, S2, S3, S4, S5, C1, C2, C3, C5 | Detetor de fumo e tomada (kit); placa ou forno conectados, sensor de inundação, coluna inteligente (outro IoT) |
| Sala | S5, S6, S7, C3, C4, C5, V3, V4 | Sensor de temperatura e tomada (kit); sensores de contacto nas janelas (outro IoT) |
| Entrada, por dentro | S7, S8, C6, C7, V1, V3 | Sensor de contacto da porta e lâmpada (kit); fechadura inteligente (outro IoT) |
| Exterior, à porta | V2 | Sensor na caixa do correio (outro IoT) |

### 2.5 Regras de privacidade

- O cliente escolhe onde ficam as câmaras. A solução não prevê câmaras em quartos nem em casas de banho; nessas divisões, os sensores de presença sem imagem (outro IoT) cobrem os casos de cuidado.
- Os modelos só correm quando há movimento ou som; no resto do tempo, a câmara fica em repouso.
- Opção de recorte em tempo real: tudo o que não é o objeto seguido é removido da imagem antes de qualquer análise. É uma opção proposta pela equipa; hoje, o protótipo já envia ao servidor apenas pequenos recortes, nunca imagens completas.
- As pessoas são detetadas como “uma pessoa” ou “uma criança”, sem identificação. O reconhecimento dos familiares é opcional, ativado pessoa a pessoa, com consentimento, e feito no equipamento de casa.
- O cliente pode marcar máscaras: zonas da imagem que nunca são analisadas.
- O _ThingTracker_ não grava vídeo; as observações ficam 30 dias no equipamento de casa.
- Só o caso da pessoa desconhecida (S7) envia a fotografia de uma pessoa. Os outros enviam o recorte de um objeto ou nenhuma imagem (C6, por exemplo, nunca envia fotografia).

## 3. Casos de uso e critérios de avaliação

### 3.1 Os critérios

Critérios e ponderações dos artigos 16.º e 18.º das Normas de Participação (`sources/rules/normas-2026.pdf`).

| Critério | Intermédia | Final | Como o _ThingTracker_ responde | Onde está a prova |
|---|---|---|---|---|
| Enquadramento e resposta ao Desafio | 25 % | 20 % | A câmara passa a ser uma fonte de informação; uma frase torna-se um sensor, “para além dos comandos”; os casos combinam a câmara com os sensores do kit; o MCP está integrado (lê a porta e atua na tomada e na luz); os casos de segurança na cozinha respondem ao pedido dos mentores | Protótipo (`prototype/`); relatório (Figura 1 e lista de casos); vídeo (`video/`, em curso); este documento |
| Facilidade de adoção do Projeto por parte dos Desafiadores | 25 % | 20 % | Um quinto separador na aplicação existente; as ações seguem pelo MCP que a Altice já tem; as regras ficam guardadas como cenários da plataforma; 18 dos 20 casos usam só dispositivos do kit | Arquitetura (`docs/pt/14-arquitetura.md`, §3 e D5); especificação de integração (`docs/pt/15-especificacao-integracao.md`); réplica da aplicação no protótipo |
| Viabilidade de implementação e gestão futura (sustentabilidade) do Projeto | 25 % | 20 % | Modelos _open-source_ de uso comercial livre; visão só quando há movimento, no _router_ ou em servidores da Altice; o modelo de linguagem só é chamado ao criar uma regra ou responder a uma pergunta; cerca de 0,43 € por casa e por mês em modelo de linguagem e 0,49 € em visão (estimativa do relatório); 6 casos já funcionam e 12 são pequenas extensões | Relatório (“Ferramentas de IA”); arquitetura (§8); viabilidade de negócio (`docs/pt/16-viabilidade-negocio.md`) |
| Possibilidade de replicação em outros territórios e contextos | — | 20 % | Serviço de plataforma para qualquer operador; nenhum dado é específico de Portugal; o modelo de linguagem fala a língua do utilizador; a França é o segundo mercado analisado | Viabilidade de negócio (secção sobre França); arquitetura (requisito N5) |
| Apresentação da solução | 25 % | 10 % | Demonstração ao vivo com a câmara do kit e o livro; vídeo com o caso da faca e do gato (ilustração); casos explicados numa frase | Vídeo; protótipo; _pitch_ |
| Documentação (Entregáveis) da solução | — | 10 % | Relatório de duas páginas; arquitetura, especificação de integração, viabilidade de negócio e casos de uso, em português e em inglês | `deliverables/`, `docs/pt/`, `docs/` |

### 3.2 Matriz

Autoavaliação da equipa, para discussão. Escala de cada critério:
- Enquadramento: forte se a câmara for uma fonte de informação combinada com outro sensor ou uma ação, num caso pedido pelos mentores ou fora da oferta atual da Altice; médio se a câmara só acrescentar contexto a um alerta que já existe.
- Adoção: forte se bastar o kit; médio se exigir mais unidades do kit ou um dispositivo que a Altice já refere na sua oferta; fraco se exigir um tipo de dispositivo novo na plataforma.
- Viabilidade: forte se já funcionar no protótipo; médio se for uma pequena extensão; fraco se for futuro.
- Replicação: forte se não depender do país nem da casa; médio se depender de regras locais ou de um dispositivo de terceiros.
- Apresentação: forte se puder ser mostrado ao vivo ou no vídeo; médio se só for descrito.
- Documentação: forte se constar também do relatório ou da arquitetura; médio se constar só deste documento.

| Caso | Enquadramento | Adoção | Viabilidade | Replicação | Apresentação | Documentação |
|---|---|---|---|---|---|---|
| S1 Faca e animal ou criança | forte | forte | médio | forte | forte | forte |
| S2 Criança, faca, fogão | forte | forte | médio | forte | forte | médio |
| S3 Fogão sem ninguém | forte | médio | médio | médio | médio | forte |
| S4 Fumo: quem está | médio | forte | médio | forte | médio | médio |
| S5 Produtos perigosos | forte | forte | médio | forte | médio | médio |
| S6 Janela e criança | forte | médio | médio | forte | médio | médio |
| S7 Pessoa desconhecida | forte | forte | médio | médio | médio | forte |
| S8 Porta aberta | médio | forte | médio | forte | médio | médio |
| S9 Fuga de água | médio | médio | fraco | forte | médio | médio |
| C1 Taças do animal | forte | forte | forte | forte | forte | forte |
| C2 Pessoa idosa | forte | forte | forte | forte | médio | forte |
| C3 Medicamentos | forte | forte | médio | forte | médio | médio |
| C4 Casa fria | forte | forte | médio | forte | médio | médio |
| C5 Queda | forte | forte | fraco | forte | médio | médio |
| C6 Criança chega | médio | forte | forte | forte | médio | médio |
| C7 Animal sai pela porta | forte | forte | médio | forte | médio | forte |
| V1 Sair sem o livro | forte | forte | forte | forte | forte | forte |
| V2 Encomendas | forte | médio | médio | médio | médio | forte |
| V3 “Onde está?” | forte | forte | forte | forte | forte | forte |
| V4 Energia | médio | forte | forte | forte | médio | médio |

As marcas “forte” na Documentação de S1, S3, C7 e V2 pressupõem que o relatório adota a nova lista de casos.

## 4. Proposta de valor

- Para a família: a câmara que já existe em casa passa a avisar dos perigos que ninguém está a ver (a faca ao alcance do gato, o fogão esquecido, a avó que não veio à cozinha) e a responder a “onde está?”.
- Para a família: cada aviso nasce de uma frase ou de uma proposta aceite com um toque; a sirene nunca toca sem um “sim”, e nenhuma imagem completa sai de casa para análise.
- Para a Altice e a MEO, diferenciação: as câmaras e os sensores que já vendem passam a ser um serviço novo, dentro da aplicação e do MCP que já existem.
- Para a Altice e a MEO, receita: uma mensalidade adicional de 3,99 €, de que restam cerca de 1,74 € por casa, e cerca de 19 000 casas MEO no cenário esperado (pressupostos da viabilidade de negócio).
- Para a Altice Labs: um serviço de plataforma para qualquer operador, que dá razões para vender mais sensores (placa conectada, inundação, fechadura).

## 5. Pressupostos e questões em aberto

1. Duas ou três câmaras por casa é um pressuposto da equipa, por validar com clientes.
2. Serviço de notificações: o MCP não tem uma ferramenta para avisos; falta saber que serviço a aplicação usa.
3. Sirene: a ferramenta de escrita do MCP aceita ligar e desligar, brilho, temperatura de cor e cor; falta confirmar como se aciona a sirene da câmara ou da central. Em qualquer caso, só depois de um “sim”.
4. Outros dispositivos (placa ou forno conectados, sensor de inundação, fechadura, sensor da caixa do correio, coluna inteligente, sensores de presença): falta saber quais a plataforma suporta.
5. Câmara do kit no exterior (proteção IP65): falta confirmar com a Altice.
6. Potência máxima da tomada do kit: desconhecida.
7. Fiabilidade da deteção de facas, encomendas e caixas de medicamentos à distância: por medir.
8. Revisão jurídica: enquadramento da câmara exterior e reconhecimento de familiares.

Fontes: Normas de Participação do Aveiro Tech City Hackathon 2026, artigos 16.º e 18.º; Eurostat, `hlth_dhc140` (2025, consultado a 18 de novembro de 2026, ver `docs/12-market-research.md`); página do produto _Connected Home_ da Altice Labs (ver `docs/02-challenge.md`); viabilidade de negócio (`docs/pt/16-viabilidade-negocio.md`); medições da equipa, 18 de novembro de 2026.
