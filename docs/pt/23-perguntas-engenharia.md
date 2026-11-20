# _ThingTracker_ · perguntas e respostas de engenharia

Este documento reúne as perguntas que um engenheiro do júri, ou da Altice Labs, provavelmente fará. Cada pergunta tem uma resposta de uma frase, para dizer em voz alta, o pormenor que a sustenta e o sítio onde se mostra: um diagrama em `docs/architecture/`, uma secção de [14-arquitetura.md](14-arquitetura.md) ou um ficheiro e uma linha em `prototype/`.

Dá-se primeiro a resposta curta, e o pormenor só se for pedido. Todas as respostas seguem duas regras:
1. Separar a solução proposta daquilo que o protótipo faz hoje.
2. Nunca afirmar um número que não esteja nos documentos.

Marcas de estado:
- [proposta]: a solução desenhada;
- [protótipo]: o que faz o código no portátil da demonstração;
- [execução sem montagem]: o que se mostrou com as gravações dos próprios filmes, passadas de novo pelo sistema real na noite de 19 para 20 de novembro (`video/out/proof/`, [24-what-is-real.md](../24-what-is-real.md)).

## Solução final (20 de novembro): tudo local, com a privacidade em primeiro lugar

O equipamento da casa faz toda a perceção e toda a inferência; as imagens, o vídeo, as assinaturas visuais e os padrões faciais nunca saem de casa; a plataforma da Altice transporta apenas texto. A visão nos servidores da Altice, em GPU _L4_, foi uma alternativa avaliada e não escolhida ([14-arquitetura.md](14-arquitetura.md)).

---

## A. Onde corre cada parte

### A1. O que corre onde?

Resposta curta: “O equipamento da casa vê, lembra-se e decide; a plataforma da Altice só transporta texto; e o modelo de linguagem só escreve.”

- Em casa [proposta]: um único equipamento, que é o _router_, se tiver uma NPU, ou uma caixa dedicada, como um _Raspberry Pi 5_ com um acelerador de IA ou um _Jetson Orin Nano Super_. Nele correm:
  - a receção das imagens da câmara, na rede local;
  - o filtro de movimento;
  - a visão: deteção e reidentificação face à assinatura visual (_OWLv2_ e _DINOv2_ no protótipo; detetores mais leves, como o _YOLOv8n_, nos equipamentos pequenos);
  - o reconhecimento facial, opcional (_YuNet_ e _SFace_, com os padrões guardados no equipamento);
  - a memória local (onde e quando foi visto cada objeto);
  - o motor de regras;
  - o modelo de linguagem (_Qwen3-1.7B_ no protótipo), que transforma uma frase numa regra e uma pergunta numa resposta; nunca decide.
- Na Altice [proposta], só texto:
  - as contas, a identidade e as permissões da família;
  - o registo de referência dos metadados (objetos, pessoas, só com o nome, ligações de posse, cenários), que dá cópia de segurança, sincronização entre os telemóveis da família e reposição, se a caixa for substituída;
  - o registo de eventos em texto estruturado (por exemplo, “livro, secretária, 18:02”);
  - as notificações para a app;
  - um _relay_, para que a app chegue à casa quando a família está fora;
  - as ações nos dispositivos, através do MCP do _Connected Home_.
- Porque continua a ser precisa a nuvem: o telemóvel nem sempre está na rede da casa; as notificações e o controlo dos dispositivos são serviços da plataforma da Altice; e os metadados precisam de cópia de segurança e de sincronização entre vários utilizadores.
- No telemóvel: a app da Altice, com o novo separador _Things_ e o botão do assistente.

Onde se mostra: `docs/architecture/implantacao.png`.

### A2. O que fez o _MacBook_ na demonstração?

Resposta curta: “Os dois papéis ao mesmo tempo: o equipamento da casa e a plataforma da Altice.”

- [protótipo]:
  - o `edge.py` faz da parte de câmara do equipamento da casa: filtro de movimento, _OWLv2_ e _DINOv2_ na GPU do _Mac_, e rostos;
  - o `server.py` faz da memória e dos motores de presença e de regras do equipamento da casa, e da app e da API da plataforma, com o _SQLite_;
  - o `llm_local.py` faz do modelo de linguagem do equipamento da casa (_Qwen3-1.7B_);
  - o `judge.py`, opcional, faz de juiz de visão (_Qwen2-VL-2B_).
- Nas gravações do laboratório, o _stream_ da câmara do _kit_ chegou ao _Mac_ através do _relay_ na nuvem da organização. Isso deve-se à infraestrutura do _hackathon_, e não ao produto.

### A3. Porque não uma caixa em cada casa, com tudo local?

Resposta curta: “Tudo local é a solução escolhida. O equipamento compra-se uma vez, no _router_ com NPU ou como equipamento comprado pelo cliente; uma caixa paga pela Altice não compensa.”

- Pormenor (pesquisa de preços da equipa, 20 de novembro):
  - o equipamento compra-se uma vez: uma câmara de interior, ≈ 45 €; um _Raspberry Pi 5_, ≈ 200 €; um _Jetson Orin Nano Super_, ≈ 345 €; ou um _router_ com NPU, +15 € (uma estimativa);
  - a 5 anos, o equipamento custa 3,33 ou 5,75 € por mês;
  - com o serviço adicional a 3,99 €, uma caixa paga pela Altice deixa −4,81 a −6,90 € por casa e por mês (documento 17), e é por isso que a IA fica no _router_ ou em equipamento comprado pelo cliente;
  - cada atualização dos modelos tem de chegar aos equipamentos das casas.
- Análise anterior, mantida como contexto: com a Altice a comprar uma caixa para cada casa (um _Raspberry Pi 5_ com _AI HAT+_, ou um _Jetson Orin Nano Super_ ao preço de lançamento de 249 USD), paga em 36 meses, o investimento inicial seria de 100 a 140 milhões de euros para 500 000 casas, e a operação de 6,55 a 8,64 € por casa e por mês.

Onde se mostra: [17-custos-operador.md](17-custos-operador.md) e o painel lateral de `docs/architecture/implantacao.png`.

### A4. Porque não enviar o vídeo para a nuvem?

Resposta curta: “Demasiado tráfego e demasiado risco para a privacidade, sem ganho nenhum.”

- Pormenor [estimativa do diagrama]:
  - o vídeo contínuo a 2 Mbps dá cerca de 657 GB por câmara e por mês;
  - as imagens completas durante o movimento custam ainda 2,41 € por casa e por mês nos servidores da própria Altice, e 3,93 a 4,26 € em GPU de _hyperscalers_.
- O caminho proposto: nenhuma imagem sai de casa; o equipamento da casa analisa-a aí e envia à Altice apenas eventos em texto.
- Alternativa avaliada e não escolhida: enviar apenas a região que mudou para as GPU _L4_ da Altice, cerca de uma vez por segundo enquanto há movimento, ≈ 0,49 € por casa e por mês com uma câmara, e 0,98 € com duas (documento 17). As imagens sairiam de casa.

### A5. Onde ficam os balanceadores de carga, e porquê aí?

Resposta curta: “Na Altice, à frente dos serviços da plataforma, que só tratam texto; em casa não há nada para distribuir.”

- Pormenor [proposta]:
  - cada casa mantém uma única ligação de saída, em mTLS, para um corretor de ligações (MQTT, um tópico por casa);
  - os balanceadores de carga repartem as ligações das casas e os pedidos HTTPS da app por N instâncias do serviço;
  - os metadados de cada casa e o registo de eventos em texto ficam na base de dados da plataforma, pelo que qualquer instância pode servir qualquer casa;
  - nenhum modelo de visão ou de linguagem corre na Altice, pelo que não há filas de GPU; as filas da solução anterior pertencem à alternativa da visão nos servidores, que não foi escolhida.

Onde se mostra: `docs/architecture/implantacao.png`.

### A6. Como escala para 500 000 casas?

Resposta curta: “Cada casa traz a sua própria capacidade de cálculo; do lado da Altice, só passa texto.”

- Pormenor:
  - a perceção e a inferência crescem com as casas, um equipamento em cada uma;
  - a plataforma trata das contas, dos metadados, dos eventos em texto, das notificações e do _relay_, sem GPU para dimensionar;
  - a estimativa anterior de 1427 placas _L4_ (6,4 milhões de euros de _hardware_) para 500 000 casas pertence à alternativa da visão nos servidores, que não foi escolhida (documento 17).

### A7. E se a internet falhar?

Resposta curta: “O equipamento da casa continua a ver e a avaliar as regras, e guarda os eventos em texto numa fila até a ligação voltar; o alarme de segurança não depende de nós.”

- [proposta]:
  - o equipamento da casa guarda os eventos numa fila local (a “fila de saída” de `docs/architecture/implantacao.png`);
  - a visão, a memória e as regras correm no equipamento da casa, pelo que não precisam de ligação;
  - as notificações e as ações nos dispositivos passam pela plataforma da Altice, pelo que esperam pela ligação;
  - o alarme e o sensor da porta continuam a funcionar através da central de segurança da Altice, como hoje.

### A8. Quanto demora um aviso?

Resposta curta: “A meta é no máximo 3 segundos; no aviso da porta, o protótipo demora cerca de 10 segundos.”

- Pormenor:
  - a meta, do evento à ação, é a do documento [20](20-produto.md), §6.4, e confirma-se no piloto;
  - o tempo divide-se em movimento, visão no equipamento da casa, regra e notificação pela plataforma;
  - medido na GPU do _Mac_: _OWLv2_ 557 ms por imagem, com 10 objetos pedidos, e _DINOv2_ 22 ms por recorte (documento 14, §14); num _Raspberry Pi 5_ ou num _Jetson_, ainda não foi medido;
  - os 10 s do protótipo resultam da consulta do sensor da porta pelo MCP a cada 4 s, da espera da regra (5 s) e do motor de regras (2 s) (documento 19, secção 6).

## B. Perceção: o que os modelos fazem, e só isso

### B1. Como sabe que é o _seu_ livro, e não um livro qualquer?

Resposta curta: “Dois modelos: um encontra ‘um livro’ e o outro confirma que é o seu.”

- Pormenor:
  - o _OWLv2_ (vocabulário aberto) delimita numa caixa tudo o que se descreva por palavras, aqui `"a photo of a yellow book"`;
  - o _DINOv2_ transforma cada caixa numa assinatura visual (384 números) e compara-a, por semelhança de cosseno, com as 8 vistas guardadas;
  - a partir de 0,62, conta como seu;
  - no laboratório, na câmara do _kit_, o livro obteve 0,70 e uma garrafa 0,10;
  - `edge.py`, funções `analyse` e `best_match` (a comparação com o limiar `--match`, 0,62 por omissão).
- Medido na gravação do filme 1, com a câmara no teto:
  - na região da secretária em resolução completa, o _OWLv2_ encontrou o livro em 68 de 68 imagens;
  - face a uma assinatura registada a partir da mesma câmara, o livro obteve uma mediana de 0,93 (0,79-0,96), os outros objetos 0,23 (máximo 0,28), e depois de o livro ser levado não houve candidatos;
  - (`video/tools/book_region.py`).

### B1a. As fotografias do telemóvel bastam para reconhecer o objeto?

Resposta curta: “Com uma câmara no teto, não: dão uma primeira assinatura, mas são as vistas da própria câmara que a tornam fiável.”

- Pormenor:
  - a assinatura feita com as fotografias do telemóvel obteve 0,23 no livro visto do teto, porque os grandes planos são demasiado diferentes de um pequeno recorte visto de cima;
  - por isso, da primeira vez que a câmara vê um candidato, a app pergunta “é este o teu livro?” e junta à assinatura as vistas da própria câmara (até 8);
  - só a análise da região em resolução completa, e não de uma imagem reduzida, permite encontrar o livro (68 de 68 imagens, contra 7 de 69).

### B2. Como se regista um objeto?

Resposta curta: “Com fotografias do telemóvel, ou mostrando-o a uma câmara; o resultado são 8 vistas e uma assinatura.”

- Pormenor:
  - fotografias do telemóvel: seguem do telemóvel para o equipamento da casa, diretamente pelo Wi-Fi da casa ou por um _relay_ cifrado de ponta a ponta, que a Altice não consegue ler; no equipamento, o _OWLv2_ recorta o objeto em cada fotografia e o _DINOv2_ gera os vetores [protótipo: postos em fila para o agente, `server.py`, `edge.py`]. Chegam a 0,69 numa imagem do _kit_ tirada à altura da secretária, mas, com a câmara no teto, só as vistas da própria câmara reconhecem o livro (0,91-0,94), pelo que a app as acrescenta quando o utilizador confirma (B1a);
  - mostrando-o à câmara: o agente guarda 8 vistas, cada uma suficientemente diferente das outras (cosseno abaixo de 0,97) (`edge.py`, `enrol_step`);
  - a assinatura fica no equipamento da casa; a plataforma guarda apenas o nome do objeto e o dono, em texto.

### B3. Como sabe que alguém pegou no livro?

Resposta curta: “Não é um modelo que o decide: é uma regra sobre caixas.”

- [proposta; protótipo: no código, com testes de ponta a ponta, ainda não visto nas gravações do laboratório]:
  - quando a caixa do livro se sobrepõe à de uma pessoa, regista-se uma observação “na mão”, com o nome de quem o segura se o rosto estiver registado;
  - se, a seguir, o livro deixar de estar no seu lugar em 3 ou mais análises, regista-se “levado por…”;
  - se o livro for visto noutro sítio, regista-se “mudado para…”.

### B4. Como sabe que o livro ficou esquecido?

Resposta curta: “Quando a porta fecha depois de sair alguém da família, a câmara verifica se o livro continua lá.”

- [protótipo e execução sem montagem]: na gravação do filme 1, passada de novo pelo sistema real, a regra dispara “esquecido” (o livro visto a 0,94 em 3 imagens); quando a mesma pessoa sai com o livro, o resultado é “incerto”, sem aviso, e o juiz de visão concorda (`server.py`, `check_leave_without`).
  - gatilho: a porta fecha depois de abrir, e o motor de presença indica que saiu alguém da família (um telemóvel saiu do Wi-Fi, ou há menos pessoas);
  - segue-se uma verificação ativa, ou seja, uma análise forçada do lugar do livro em algumas imagens, mesmo sem movimento;
  - só há aviso se o livro for visto; se não estiver visível, o resultado é “incerto”, sem alarme;
  - as chegadas não o desencadeiam.
- Onde se mostra: `docs/architecture/seq-livro-esquecido.png`.
- [protótipo antes de 19 de novembro]: a porta a abrir e a última observação do livro. Era uma regra mais fraca, e foi por isso que mudou.

### B4a. Então o caso do livro precisa da porta como dispositivo?

Resposta curta: “Precisa de um sinal de que ‘alguém acabou de sair’. O melhor é o sensor da porta que a Altice já vende no _kit_, e que apenas lemos.”

- Pormenor:
  - o sensor de contacto da porta (MS-D3D, com a central MS-WES1AS) faz parte do _kit_ da Altice e já está ligado à plataforma;
  - o _ThingTracker_ lê os seus eventos de abertura e fecho pelo MCP, só em leitura e sem _hardware_ novo;
  - [protótipo]: o sensor da porta do laboratório é o do próprio _kit_, consultado pelo MCP a cada 4 s.
- Sem sensor na porta, há duas alternativas que desencadeiam a mesma verificação:
  - um telemóvel da família sai do Wi-Fi da casa. O _router_ dá por isso, mas é mais lento (em produção espera cerca de 10 min, para que uma breve falha do Wi-Fi não conte), pelo que o aviso chega tarde, como “deixaste o livro em casa”;
  - uma câmara que vê a porta de saída: basta ver uma pessoa a sair pela zona da porta.
- O mínimo é um sinal de que “alguém saiu” e a verificação ativa do objeto pela câmara. A família indica qual dos sensores de contacto é o da porta de entrada.

### B5. Como funciona o reconhecimento facial? Os rostos não são dados biométricos?

Resposta curta: “São. Por isso, o reconhecimento é opcional, exige consentimento e os padrões faciais nunca saem de casa.”

- Pormenor:
  - o _YuNet_ (MIT) encontra o rosto e o _SFace_ (Apache-2.0) compara-o; ambos são modelos pequenos, que correm num processador comum;
  - um rosto é de uma pessoa da família a partir de 0,40 de semelhança com um dos seus padrões, e é “desconhecido” abaixo de 0,25 face a todos; entre os dois valores, o sistema não decide e responde “rosto não visível”. O OpenCV recomenda 0,363 para rostos nítidos e de perto; os rostos da câmara do _kit_ têm 40 a 86 px, e os limiares calibram-se por câmara no piloto (`faces.py`, `THRESHOLD_NOTE`);
  - só se avalia um rosto que o _YuNet_ pontue a 0,8 ou mais, com pelo menos 40 px de largura e não demasiado virado; caso contrário, é “rosto não visível”, e nunca “desconhecido”;
  - de casa só sai um rótulo: o identificador da pessoa, “rosto desconhecido” ou “rosto não visível”;
  - os dados biométricos usados para identificar uma pessoa são uma categoria especial ao abrigo do RGPD (artigo 9.º), que exige consentimento explícito.
- Onde se mostra: `docs/architecture/seq-pessoa-desconhecida.png`.
- [protótipo e execução sem montagem]: na gravação do filme 2, um membro da equipa (Filipe), registado com consentimento, é reconhecido (0,54 e 0,63) e nada dispara; a outra pessoa é classificada como desconhecida (0,17 e 0,14). O alarme e a sugestão de chamar a polícia dispararam pela regra em 2 de 4 repetições; nas outras 2, poucos rostos do desconhecido estavam nítidos o bastante, e o sistema perguntou em vez de dar o alarme. O alarme é simulado.

### B6. E quando entra alguém sem o rosto visível?

Resposta curta: “Pergunta, não dá o alarme.”

- Pormenor:
  - o alarme só soa perante um rosto desconhecido visível em várias análises seguidas, e nunca para um membro da família: 3 na solução proposta e 2 no protótipo, porque aí um veredicto “desconhecido” já exige um rosto nítido abaixo de 0,25 face a todos os padrões (`presence.py`, `unknown_runs`);
  - uma pessoa sem o rosto visível, com a família fora, deixa a casa no estado INCERTA, e o serviço envia uma pergunta à família.

### B7. Deteções erradas, como um casaco confundido com uma pessoa?

Resposta curta: “Limiares, seguimento e respostas graduais, e é a família que escolhe o que é intrusivo.”

- Pormenor:
  - pontuações mínimas (uma pessoa a 0,2 no _OWLv2_);
  - uma deteção tem de se manter ao longo de várias análises antes de contar;
  - os alarmes exigem confirmações seguidas;
  - cada aviso traz a fotografia do momento;
  - para cada risco, a família escolhe, ao criar a regra, entre “perguntar primeiro” e “tocar logo o alarme”.
- A exatidão em casas reais ainda não foi medida; será medida no piloto.

### B8. E às escuras?

Resposta curta: “A câmara do _kit_ passa para a visão noturna por infravermelhos; a exatidão dos modelos com essa imagem ainda não foi medida, e mede-se no piloto. Na escuridão total, não se deteta nada.”

- Pormenor: nos filmes, a imagem da própria câmara fica negra durante uma fração de segundo e passa depois à visão noturna. Enquanto a imagem está demasiado escura, não aparecem caixas.

### B9. Ângulos mortos e oclusões?

Resposta curta: “Cada câmara é um lugar; o que nenhuma câmara vê fica a cargo dos telemóveis e do sensor da porta; não se adivinha.”

- Pormenor: uma pessoa parada não gera movimento; enquanto a presença depender só das câmaras, o serviço pede ao agente da casa, a cada 30 s, uma análise das zonas onde as pessoas foram vistas pela última vez, mesmo sem movimento (documento 14, §7; `presence.py`, `refresh_s`). As zonas dentro de uma câmara ficam para uma fase posterior.

## C. Presença e regras: quem decide

### C1. Como se sabe que não está ninguém em casa?

Resposta curta: “Não só pela câmara: têm de concordar três sinais.”

- Pormenor [proposta]: uma máquina de estados por casa, no equipamento da casa, que junta:
  - os telemóveis da família no Wi-Fi (o _router_ sabe quais são; o acesso é por uma nova ferramenta MCP, proposta à Altice);
  - o sensor da porta (eventos de abertura e fecho, que a plataforma já recebe);
  - as pessoas que as câmaras veem, com o nome, se o rosto estiver registado.
- Estados:
  - OCUPADA: há um telemóvel em casa, ou alguém foi visto há pouco;
  - A SAIR: a porta abriu e fechou, e o equipamento verifica quem saiu;
  - VAZIA: todos os telemóveis fora, a porta abriu e fechou, e ninguém foi visto durante um tempo definido;
  - INCERTA: os sinais não concordam.
- Tempos: valores em segundos na demonstração e em minutos em produção, estes propostos para afinar no piloto. Por exemplo, a fase A SAIR dura 10 s na demonstração e 5 min em produção, e uma pessoa vista conta como presente durante 15 s e 2 min, respetivamente (documento 14, §7; `presence.py`, `TIMINGS`).

Onde se mostra: `docs/architecture/presenca-estados.png`.

### C2. Uma divisão sem câmara? Alguém parado?

Resposta curta: “Os telemóveis cobrem esses casos.”

- Pormenor: se o telemóvel de um membro da família está no Wi-Fi, essa pessoa conta como estando em casa, mesmo numa divisão sem câmara. Uma pessoa parada fica coberta pelos telemóveis e, enquanto a presença depender apenas das câmaras, por uma análise de atualização a cada 30 s (B9).

### C3. E se o telemóvel ficar em casa, ou uma visita não tiver telemóvel?

Resposta curta: “Nesse caso, os sinais não concordam, a casa fica ‘incerta’ e as regras perguntam em vez de agir.”

- Pormenor:
  - um telemóvel em casa, sem nenhuma observação nem uso da porta durante muito tempo (4 h propostas para produção, 15 min na demonstração), indica um telemóvel esquecido, e a casa passa a INCERTA;
  - uma pessoa vista quando não há nenhum telemóvel em casa é alguém sem telemóvel registado: uma visita, uma criança ou um desconhecido;
  - o rosto decide qual, se estiver registado; caso contrário, pergunta-se à família.

### C4. É o modelo de linguagem que decide?

Resposta curta: “Não. Os modelos só veem; quem decide é um motor de regras determinista.”

- Pormenor:
  - o _OWLv2_ devolve caixas com pontuações, o _DINOv2_ indica quão próximo um recorte está de uma assinatura e o _SFace_ diz de quem é o rosto;
  - todas as conclusões (“esquecido”, “ninguém em casa”, “pessoa desconhecida”) são decididas por código nos motores de regras e de presença, e reavaliadas a cada evento e a cada temporizador;
  - o modelo de linguagem só escreve texto: transforma uma frase numa regra e redige as respostas e as mensagens;
  - o juiz de visão (_Qwen2-VL-2B_, opcional) é um modelo à parte: só é chamado quando uma verificação ativa não encontra o objeto, recebe um único recorte apertado do lugar e, no protótipo, o seu “sim” ou “incerto” torna-se uma pergunta à família; nunca aciona um dispositivo;
  - [protótipo]: `server.py`, `rules_engine`; o modelo de linguagem em `brain.py`; o juiz em `judge.py`.

### C5. E se o modelo de linguagem se enganar?

Resposta curta: “Não pode agir sozinho: a regra que escreve é validada e mostrada ao utilizador em palavras simples, e o código confere as respostas com a memória.”

- [protótipo]:
  - uma regra inválida é substituída pelos padrões de palavras-chave;
  - uma resposta que contradiga a memória é substituída por uma frase simples construída a partir da memória (`brain.py`; ver o [AGENTS.md](../../AGENTS.md)).

### C6. Como se executam as ações?

Resposta curta: “Através do servidor MCP da Altice; a sirene segue a escolha da família para cada risco, e armar o alarme de segurança exige sempre confirmação.”

- [protótipo]: todas as ações correm em simulação, salvo com `TT_LIVE_ACTIONS=1`, que a equipa nunca ativa, pelo que a casa real nunca é alterada; o alarme é sempre simulado, e o alarme da Altice nunca é chamado (`actions.py`).

## D. Dados, segurança e privacidade

### D1. Que base de dados?

Resposta curta: “_SQLite_ no protótipo; em produção, um armazenamento local no equipamento da casa para tudo o que é visual e para a memória, e a base de dados da plataforma, na Altice, para os metadados, em texto.”

- Pormenor:
  - em casa: as assinaturas visuais, os padrões faciais (cifrados), a memória das observações, as regras e a fila de saída dos eventos;
  - na Altice, por cliente, só texto: objetos, pessoas (só o nome), ligações de posse, cenários e o registo de eventos, para cópia de segurança, sincronização entre os telemóveis da família e reposição, se a caixa for substituída;
  - [protótipo]: `store.py` (_SQLite_). O protótipo não tem _PostgreSQL_.

### D2. O vídeo é gravado ou enviado?

Resposta curta: “Não. As imagens, o vídeo, as assinaturas visuais e os padrões faciais nunca saem de casa: o equipamento da casa analisa a imagem aí, e só chegam à Altice eventos em texto.”

- As gravações do laboratório usadas nos filmes foram feitas para os filmes, localmente, com o acordo das pessoas ou com desfocagem.

### D3. Segurança?

Resposta curta: “Uma única ligação de saída por casa, com autenticação mútua; nenhuma porta de rede aberta em casa.”

- Pormenor: mTLS do agente da casa até ao corretor, um tópico MQTT por casa, HTTPS para a app e padrões faciais cifrados em repouso, em casa.

Onde se mostra: o diagrama de fluxo de dados com fronteiras de confiança.

### D4. RGPD?

Resposta curta: “Minimização desde a conceção: nenhuma imagem, vídeo, assinatura ou padrão facial sai de casa, os rostos só com consentimento explícito, e prazos de conservação limitados.”

- O modelo de linguagem corre no equipamento da casa, pelo que nenhum fornecedor recebe o texto da família. Um modelo externo (por exemplo, o _ChatGPT_ ou o _Claude_ do próprio utilizador) é uma opção futura possível, por escolha do utilizador e só com texto; não agora.

## E. Integração com a Altice

### E1. O que tem a Altice de acrescentar?

Resposta curta: “Um separador _Things_, um botão de assistente, quatro ferramentas MCP para os objetos, uma para a presença no Wi-Fi, e o serviço.”

- As ferramentas: `list_things`, `create_thing`, `get_thing_last_seen` e `get_thing_timeline`, mais a ferramenta proposta para a presença no Wi-Fi. As ações usam as 18 ferramentas que já existem (documento [15](15-especificacao-integracao.md), §2 e §5).

### E1a. Como ligaram a porta à vossa app sem acesso ao nosso _backend_, à app ou à base de dados?

Resposta curta: “Não precisámos do vosso _backend_. Deram às equipas o servidor MCP do _Connected Home_, a interface oficial da plataforma. O sensor da porta pertence à nossa casa de testes na vossa plataforma, como o dispositivo de qualquer cliente, e lemo-lo através dessa interface.”

- Pormenor:
  - o sensor: o sensor de contacto do _kit_ (MS-D3D) na nossa casa de testes (“Hack 3”). A Altice configurou os sete dispositivos do _kit_ e associou-os à conta da equipa; não acrescentámos nenhum dispositivo ([04-kit-and-access.md](../04-kit-and-access.md)). Colámos o sensor e o íman na porta do laboratório ([19-teste-real.md](../19-teste-real.md));
  - o acesso: o nosso cliente MCP (`mcp/client/chmcp.py`) inicia sessão com a conta da equipa através do _Keycloak_ da Altice (OAuth) e envia a chave da API em cada pedido (`chmcp.py:170-171`), com a versão 2025-06-18 do protocolo MCP;
  - a leitura da porta: a cada 4 s, o servidor chama a ferramenta de leitura `get_home_devices`, encontra o `contactSensor` e lê o `sensorState`, em que `"alarm"` significa aberta (`server.py`, `device_poller`). A base de dados do protótipo tem eventos reais da porta desde 19 de novembro;
  - nunca tocámos no _backend_, na app nem na base de dados da Altice. A app dos filmes é a nossa cópia dos ecrãs da app da Altice, a correr o nosso protótipo; em produção, a Altice acrescenta o separador _Things_ à sua própria app.
- A limitação, dita com franqueza, e o pedido: o servidor MCP não envia eventos, pelo que fazemos consultas periódicas, o que explica parte dos cerca de 10 s do aviso da porta no protótipo. Em produção, a parte do _ThingTracker_ que fica na plataforma corre dentro da plataforma da Altice, recebe os eventos dos sensores diretamente, ou por uma subscrição de eventos, e passa-os em texto ao equipamento da casa. Nunca chamamos as ferramentas de escrita: as ações correm em simulação, por regra da própria equipa.

### E1b. Como funciona o sensor da porta, e acrescentaram dispositivos?

Resposta curta: “É o sensor de contacto magnético do _kit_, que comunica por rádio com a central de segurança do _kit_. Não acrescentámos nenhum dispositivo: a Altice configurou o _kit_, e uma família acrescenta dispositivos da forma habitual, na app da Altice.”

- O sensor:
  - tem duas peças, o corpo do sensor no aro e um íman na porta; ao abrir a porta, o íman afasta-se e o estado passa a “aberto”;
  - envia essa informação por _Zigbee_ ou 868 MHz para a central de segurança (MS-WES1AS), que chega à nuvem da Altice por _ethernet_ ou LTE;
  - a app mostra “Sensor de contacto: Aberto / Fechado”; o MCP devolve `sensorState` `"normal"` ou `"alarm"`.
- O _kit_: central de segurança, sensor de contacto, sensor de fumo, sensor de temperatura, câmara, tomada inteligente e lâmpada. Não tem sensor de movimento. A câmara, a tomada e a lâmpada usam o Wi-Fi de um ponto de acesso montado pela equipa; os sensores usam o rádio da central ([04-kit-and-access.md](../04-kit-and-access.md)).
- Acrescentar um dispositivo, em produção: no fluxo “Adicionar dispositivo” da app da Altice:
  - os sensores por rádio emparelham com a central;
  - os dispositivos Wi-Fi ligam-se ao Wi-Fi da casa e registam-se através da app.
- O limite: o servidor MCP não acrescenta dispositivos. Lê-os e controla-os, e trata de cenários, temporizadores e segurança. Não experimentámos acrescentar um dispositivo.
- Sobre o filme 3, dizer com franqueza:
  - o ar condicionado não é um dispositivo real: existe apenas no protótipo, em simulação, e a ligação “diretamente à app” é uma proposta;
  - a tomada é um dispositivo real do _kit_, mas “a tomada alimenta as luzes” é informação do próprio _ThingTracker_, e a ordem para a desligar correu em simulação.

### E2. Notificações? Porque é que o aviso não chegou à app real da Altice?

Resposta curta: “A vossa app já notifica o telemóvel quando a porta abre. O _ThingTracker_ transforma isso em ‘deixaste o livro’, através do mesmo serviço de notificações. O MCP ainda não expõe notificações, pelo que, na nossa demonstração, o aviso aparece na nossa cópia da vossa app.”

- Pormenor:
  - a plataforma da Altice já notifica a app da Altice para os eventos dos dispositivos (sensor de contacto aberto ou fechado, movimento, fumo, estado do alarme), configurados por dispositivo na secção “Notificações” da app ([09-platform-capabilities.md](../09-platform-capabilities.md), [08-app-and-apk.md](../08-app-and-apk.md));
  - só a Altice pode enviar notificações para a app da Altice;
  - o servidor MCP não tem nenhuma ferramenta de notificações ([10-mcp-in-practice.md](../10-mcp-in-practice.md));
  - em produção, a parte do _ThingTracker_ que fica na plataforma corre dentro da plataforma da Altice e usa diretamente esse serviço de notificações. É uma das poucas coisas que pediríamos à Altice para acrescentar.
- [protótipo]: os avisos são disparados pelas regras e aparecem na nossa cópia da app; o “Sim” e “Desligar o alarme” chamam as ações (em simulação). A notificação no telemóvel, nos filmes, foi composta na montagem.
- Se o _kit_ estiver montado para a demonstração: abre-se a porta e a app real da Altice notifica o telemóvel. Essa parte é uma funcionalidade que a Altice já tem.

### E3. O _ThingTracker_ desligou mesmo as luzes e o ar condicionado no filme 3? Porque não dizer que uma tomada inteligente cortou a corrente do laboratório?

Resposta curta: “No laboratório, as luzes e o ar condicionado não estão ligados a nenhum dispositivo do _kit_, por isso desligámo-los à mão no momento do toque na app, para mostrar o efeito. O _ThingTracker_ tomou a decisão e enviou o comando; numa casa, esse comando vai para o que a família tiver ligado.”

- Porque não “uma tomada inteligente cortou a corrente”:
  - uma tomada inteligente ocupa uma única tomada e só alimenta o que lá estiver ligado, um aparelho até cerca de 3 600 W;
  - as luzes e o ar condicionado do laboratório estão ligados aos circuitos do edifício, e não a uma tomada;
  - cortar o circuito de uma sala exige um relé ou disjuntor inteligente no quadro elétrico, que não faz parte do _kit_ e não foi o que se fez.
- Numa casa:
  - as luzes, através da lâmpada inteligente do _kit_ ou de um candeeiro ligado à tomada inteligente;
  - o ar condicionado, através da sua própria app Wi-Fi ou de uma central de infravermelhos;
  - em qualquer dos casos, o _ThingTracker_ envia o comando através da plataforma.
- [protótipo]: o comando para desligar a tomada corre em simulação (um dispositivo real do _kit_, que nunca é acionado sem a aprovação da equipa). O ar condicionado é simulado.

## F. Custos e modelos

### F1. Custo por casa?

Resposta curta: “O equipamento compra-se uma vez, 3,33 ou 5,75 € por mês a 5 anos, e a energia dos modelos custa cêntimos por mês.”

- Pormenor (pesquisa de preços da equipa, 20 de novembro; documentos [16](16-viabilidade-negocio.md) e [17](17-custos-operador.md)):
  - uma câmara de interior, ≈ 45 € (a média de 3 modelos à venda em Portugal); um _Raspberry Pi 5_, ≈ 200 €; um _Jetson Orin Nano Super_, ≈ 345 €; ou um _router_ com NPU, +15 € (uma estimativa);
  - energia: o _YOLOv8n_ fica abaixo de 0,01 € por mês, e o _OWLv2_ chega a 0,72 € com 12 h de movimento por dia (estimativa da equipa num _Jetson Orin Nano_);
  - o modelo de linguagem corre no equipamento, sem custo por pedido;
  - uma caixa paga pela Altice não compensa com o serviço adicional a 3,99 € por mês (−4,81 a −6,90 € por casa e por mês, documento 17), pelo que a IA fica no _router_ ou em equipamento comprado pelo cliente.
- Alternativa avaliada e não escolhida: a visão nos servidores _L4_ da Altice, ≈ 0,49 € por casa e por mês com uma câmara, mais ≈ 0,43 € para um modelo de linguagem na nuvem. As imagens sairiam de casa.

### F2. Licenças?

Resposta curta: “Todas abertas, e todas permitem uso comercial.”

- Pormenor: _OWLv2_ e _DINOv2_, Apache-2.0; _Qwen3-1.7B_, Apache-2.0; _Qwen2-VL-2B_ (o juiz opcional), Apache-2.0; _YuNet_, MIT; _SFace_, Apache-2.0. As licenças foram verificadas nos ficheiros dos modelos; as somas de verificação dos modelos de rostos estão no [AGENTS.md](../../AGENTS.md). O _Qwen2.5-VL-3B_ foi excluído por causa da sua licença, a _Qwen Research License_, que restringe o uso comercial.

## G. Os filmes e a demonstração

### G1. O que os filmes mostram é real?

Resposta curta: “As imagens são do laboratório real e da câmara do _kit_, a app é o nosso protótipo e as caixas vêm dos nossos modelos, aplicados a essas imagens; alguns momentos foram encenados para mostrar a experiência completa, e podemos mostrar-vos as mesmas imagens a passar pelo sistema, sem edição.”

- Pormenor, a dizer com franqueza se for pedido:
  - os avisos dos filmes foram disparados para a gravação; desde a noite de 19 para 20 de novembro, são as mesmas regras que os disparam no protótipo, como mostram as execuções sem montagem com as mesmas gravações;
  - o trecho em que as pessoas estão sentadas aparece a 4×;
  - um corte elimina o tempo em que a sala está vazia;
  - o ecrã negro da câmara, quando as luzes se apagaram, foi reconstruído a partir do comportamento da própria câmara;
  - a caixa de deteção da tomada inteligente foi colocada numa tomada escolhida, porque o _kit_ já tinha sido arrumado.

### G2. O que podem mostrar ao vivo?

Resposta curta: “As mesmas gravações dos filmes a passar pelo sistema real, sem montagem; os modelos a correr na _webcam_ do portátil; e, se o _kit_ estiver instalado, a porta lida pelo MCP e um aviso disparado por uma regra.”

- as execuções sem montagem: a gravação de cada filme passada de novo pelo sistema real, com as regras a disparar, o estado de presença a mudar e os rostos avaliados (um rosto aparece desfocado, por privacidade);
- ao vivo, com a _webcam_ do portátil e a app no telemóvel do apresentador: o _OWLv2_ e o _DINOv2_ a correr sobre a imagem da câmara, numa casa de demonstração própria (`prototype/site.py`), sem gravar nada;
- com o _kit_ instalado: o sensor da porta lido pelo MCP, a presença a mudar e um aviso disparado por uma regra.

### G3. O que está medido, e o que não está?

Resposta curta: “Está medido no laboratório, na câmara do _kit_; a exatidão em casas reais mede-se no piloto.”

- Medido no laboratório, na câmara do _kit_:
  - o livro a 0,70 para um limiar de 0,62, e uma garrafa a 0,10;
  - na gravação do filme 1, o livro encontrado em 68 de 68 imagens, com mediana 0,93 (B1);
  - na gravação do filme 2, o membro da equipa registado reconhecido a 0,54 e 0,63, para um limiar de 0,40, e o desconhecido a 0,17 e 0,14 (B5);
  - os tempos do _OWLv2_ e do _DINOv2_ na GPU do _Mac_ (A8).
- Estimado, e não medido: os custos por casa (F1).
- Não medido: a exatidão e os falsos alarmes em casas reais, a visão noturna (B8) e o tempo de aviso em produção (A8). Mede-se tudo no piloto.
