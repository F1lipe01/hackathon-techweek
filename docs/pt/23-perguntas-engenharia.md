# _ThingTracker_ · perguntas e respostas de engenharia

Este documento reúne as perguntas que um engenheiro do júri, ou da Altice Labs, provavelmente fará. Cada pergunta tem uma resposta de uma frase, para dizer em voz alta, o pormenor que a sustenta e o sítio onde se mostra: um diagrama em `docs/architecture/`, uma secção de [14-arquitetura.md](14-arquitetura.md) ou um ficheiro e uma linha em `prototype/`.

Dá-se primeiro a resposta curta, e o pormenor só se for pedido. Todas as respostas seguem duas regras:
1. Separar a solução proposta daquilo que o protótipo faz hoje.
2. Nunca afirmar um número que não esteja nos documentos.

Marcas de estado:
- [proposta]: a solução desenhada;
- [protótipo]: o que faz o código no portátil da demonstração;
- [a confirmar]: ainda em desenvolvimento a 19 de novembro, a verificar antes do _pitch_.

---

## A. Onde corre cada parte

### A1. O que corre onde?

Resposta curta: “Em casa vê-se, nos servidores da Altice decide-se, e o modelo de linguagem só escreve.”

- Em casa [proposta]: o equipamento que a Altice já instala (câmara ou _router_, sem processador de IA), onde correm:
  - o filtro de movimento;
  - as máscaras de privacidade;
  - o recorte apenas da região que mudou;
  - o reconhecimento facial, opcional;
  - a lista de telemóveis da família ligados ao Wi-Fi, que o _router_ conhece.
- Na Altice [proposta]:
  - servidores de visão, alimentados por filas (_OWLv2_ e _DINOv2_ em GPU NVIDIA _L4_);
  - o serviço _ThingTracker_, sem estado e atrás de um balanceador de carga, com o motor de presença e o motor de regras;
  - _PostgreSQL_ com _pgvector_, uma _cache_ em _Redis_ e armazenamento de objetos para as miniaturas;
  - um conjunto de servidores do modelo de linguagem, que recebe apenas texto;
  - o servidor MCP e as notificações que já existem.
- No telemóvel: a app da Altice, com o novo separador _Things_ e o botão do assistente.

Onde se mostra: `docs/architecture/implantacao.png`.

### A2. O que fez o _MacBook_ na demonstração?

Resposta curta: “Os três papéis ao mesmo tempo: a casa, os servidores da Altice e o modelo de linguagem.”

- [protótipo]:
  - o `edge.py` faz de agente da casa e de servidores de visão da Altice (_OWLv2_ e _DINOv2_ na GPU do _Mac_);
  - o `server.py` faz de serviço _ThingTracker_: app, API, motores de presença e de regras, com o _SQLite_ no lugar do _PostgreSQL_;
  - o `llm_local.py` faz de servidores do modelo de linguagem (_Qwen3-1.7B_).
- Na demonstração, o _stream_ da câmara do _kit_ chegou ao _Mac_ através do _relay_ na nuvem da organização. Isso deve-se à infraestrutura do _hackathon_, e não ao produto.

### A3. Porque não uma caixa em cada casa, com tudo local?

Resposta curta: “Porque exige um investimento inicial de 100 a 140 milhões de euros, para 500 000 casas.”

- Pormenor:
  - custos de operação de 6,55 a 8,64 € por casa e por mês (_Raspberry Pi 5_ com _AI HAT+_, ou _Jetson Orin Nano_);
  - cada atualização dos modelos tem de chegar a 500 000 caixas;
  - o modelo de linguagem precisaria de ainda mais memória.

Onde se mostra: [17-custos-operador.md](17-custos-operador.md) e o painel lateral de `docs/architecture/implantacao.png`.

### A4. Porque não enviar o vídeo para a nuvem?

Resposta curta: “Demasiado tráfego e demasiado risco para a privacidade, sem ganho nenhum.”

- Pormenor [estimativa do diagrama]:
  - o vídeo contínuo a 2 Mbps dá cerca de 657 GB por câmara e por mês;
  - as imagens completas durante o movimento custam ainda 2,41 € por casa e por mês nos servidores da própria Altice, e 3,93 a 4,26 € em GPU de _hyperscalers_.
- O caminho proposto envia apenas a região que mudou, cerca de uma vez por segundo enquanto há movimento: ≈ 0,49 € por casa e por mês com uma câmara, e 0,98 € com duas (documento 17).

### A5. Onde ficam os balanceadores de carga, e porquê aí?

Resposta curta: “Na Altice, à frente do serviço sem estado e dos servidores de visão e de linguagem; em casa não há nada para distribuir.”

- Pormenor [proposta]:
  - cada casa mantém uma única ligação de saída, em mTLS, para um corretor de ligações (MQTT, um tópico por casa);
  - os balanceadores de carga repartem as ligações das casas e os pedidos HTTPS da app por N instâncias do serviço;
  - o estado de cada casa fica no _PostgreSQL_ e no _Redis_, pelo que qualquer instância pode servir qualquer casa;
  - a visão e o modelo de linguagem ficam atrás de filas: primeiro as verificações urgentes das regras, e tudo o resto em lote, nas horas calmas, para que as GPU não sejam dimensionadas para o pico do fim do dia.

Onde se mostra: `docs/architecture/implantacao.png`.

### A6. Como escala para 500 000 casas?

Resposta curta: “Na horizontal, e os custos já estão contabilizados.”

- Pormenor: o caso de negócio prevê 1 427 placas _L4_ (6,4 milhões de euros de _hardware_) para 500 000 casas com uma câmara, porque só o movimento desencadeia a análise e só se analisa a região que mudou (documento 17).

### A7. E se a internet falhar?

Resposta curta: “O agente da casa guarda os eventos numa fila e envia-os quando a ligação voltar; o alarme de segurança não depende de nós.”

- [proposta]:
  - o agente da casa guarda os eventos numa fila local (a “fila de saída” de `docs/architecture/implantacao.png`);
  - as regras que precisam de visão ficam em pausa;
  - o alarme e o sensor da porta continuam a funcionar através da central de segurança da Altice, como hoje.

### A8. Quanto demora um aviso?

Resposta curta: “O objetivo é menos de 3 segundos; no aviso da porta, o protótipo demora cerca de 10 segundos.”

- Pormenor:
  - o tempo divide-se em movimento, envio da região, fila urgente de visão, regra e notificação;
  - medido na GPU do _Mac_: _OWLv2_ 0,57 s por imagem e _DINOv2_ 22 ms por recorte (documento 14, §3);
  - os 10 s do protótipo resultam da consulta do sensor da porta pelo MCP a cada 4 s, somada à espera da regra (documento 19, §6.4).

## B. Perceção: o que os modelos fazem, e só isso

### B1. Como sabe que é o _seu_ livro, e não um livro qualquer?

Resposta curta: “Dois modelos: um encontra ‘um livro’ e o outro confirma que é o seu.”

- Pormenor:
  - o _OWLv2_ (vocabulário aberto) delimita numa caixa tudo o que se descreva por palavras, aqui `"a photo of a yellow book"`;
  - o _DINOv2_ transforma cada caixa numa assinatura visual (384 números) e compara-a, por semelhança de cosseno, com as 8 vistas guardadas;
  - a partir de 0,62, conta como seu;
  - no laboratório, na câmara do _kit_, o livro obteve 0,70 e uma garrafa 0,10;
  - `edge.py` (comparação por volta das linhas 195-208).
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
  - fotografias do telemóvel: o _OWLv2_ recorta o objeto em cada fotografia e o _DINOv2_ gera os vetores [a confirmar: implementado a 19 de novembro];
  - mostrando-o à câmara: o agente guarda 8 vistas, cada uma suficientemente diferente das outras (cosseno abaixo de 0,97) (`edge.py`, `enrol_step`);
  - a assinatura fica guardada, por cliente, na base de dados da plataforma.

### B3. Como sabe que alguém pegou no livro?

Resposta curta: “Não é um modelo que o decide: é uma regra sobre caixas.”

- [proposta; a confirmar no protótipo]:
  - quando a caixa do livro se sobrepõe à de uma pessoa, regista-se uma observação “na mão”, com o nome de quem o segura se o rosto estiver registado;
  - se, a seguir, o livro deixar de estar no seu lugar em 3 ou mais análises, regista-se “levado por…”;
  - se o livro for visto noutro sítio, regista-se “mudado para…”.

### B4. Como sabe que o livro ficou esquecido?

Resposta curta: “Quando a porta fecha depois de sair alguém da família, a câmara verifica se o livro continua lá.”

- [proposta; a confirmar no protótipo]:
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
  - na solução proposta, um rosto conhecido obtém 0,363 ou mais, o valor recomendado pelo OpenCV; o protótipo usa 0,30, medido numa gravação do laboratório em que os rostos na câmara do _kit_ têm 40-86 px, e o valor tem de ser calibrado por câmara num piloto;
  - de casa só sai um rótulo: “Filipe”, “rosto desconhecido” ou “rosto não visível”;
  - os dados biométricos usados para identificar uma pessoa são uma categoria especial ao abrigo do RGPD (artigo 9.º), que exige consentimento explícito.
- Onde se mostra: `docs/architecture/seq-pessoa-desconhecida.png`.
- [protótipo antes de 19 de novembro]: não havia modelo de rostos, e qualquer pessoa desencadeava a regra. Em correção a 19 de novembro [a confirmar].

### B6. E quando entra alguém sem o rosto visível?

Resposta curta: “Pergunta, não dá o alarme.”

- Pormenor:
  - o alarme só soa perante um rosto desconhecido visível em várias análises seguidas (3, na solução proposta), e nunca para um membro da família;
  - uma pessoa sem o rosto visível, com a família fora, deixa a casa no estado INCERTA, e o serviço envia uma pergunta à família.

### B7. Falsas deteções, como um casaco confundido com uma pessoa?

Resposta curta: “Limiares, seguimento e respostas graduais, e é a família que escolhe o que é intrusivo.”

- Pormenor:
  - pontuações mínimas (uma pessoa a 0,2 no _OWLv2_);
  - uma deteção tem de se manter ao longo de várias análises antes de contar;
  - os alarmes exigem confirmações seguidas;
  - cada aviso traz a fotografia do momento;
  - para cada risco, a família escolhe, ao criar a regra, entre “perguntar primeiro” e “tocar logo o alarme”.
- A exatidão em casas reais ainda não foi medida; será medida no piloto.

### B8. E às escuras?

Resposta curta: “A câmara do _kit_ passa para a visão noturna por infravermelhos, e os modelos continuam a funcionar com essa imagem; na escuridão total, não se deteta nada, e não afirmamos o contrário.”

- Pormenor: nos filmes, a imagem da própria câmara fica negra durante uma fração de segundo e passa depois à visão noturna. Enquanto a imagem está demasiado escura, não aparecem caixas.

### B9. Ângulos mortos e oclusões?

Resposta curta: “Cada câmara é um lugar; o que nenhuma câmara vê fica a cargo dos telemóveis e do sensor da porta; não se adivinha.”

- Pormenor: uma pessoa escondida atrás de um monitor continua a ser seguida enquanto está parada. As zonas dentro de uma câmara ficam para uma fase posterior.

## C. Presença e regras: quem decide

### C1. Como se sabe que não está ninguém em casa?

Resposta curta: “Não só pela câmara: têm de concordar três sinais.”

- Pormenor [proposta]: uma máquina de estados por casa, no serviço _ThingTracker_, que junta:
  - os telemóveis da família no Wi-Fi (o _router_ sabe quais são; o acesso é por uma nova ferramenta MCP, proposta à Altice);
  - o sensor da porta (eventos de abertura e fecho, que a plataforma já recebe);
  - as pessoas que as câmaras veem, com o nome, se o rosto estiver registado.
- Estados:
  - OCUPADA: há um telemóvel em casa, ou alguém foi visto há pouco;
  - A SAIR: a porta abriu e fechou, e o serviço verifica quem saiu;
  - VAZIA: todos os telemóveis fora, a porta abriu e fechou, e ninguém foi visto durante um tempo definido;
  - INCERTA: os sinais não concordam.
- Tempos: valores em segundos na demonstração e em minutos em produção (por exemplo, “vazia” ao fim de 20 s na demonstração, e 3 min propostos para produção).

Onde se mostra: `docs/architecture/presenca-estados.png`.

### C2. Uma divisão sem câmara? Alguém parado?

Resposta curta: “Os telemóveis cobrem esses casos.”

- Pormenor: se o telemóvel do Filipe está no Wi-Fi, o Filipe está em casa, mesmo numa divisão sem câmara. Uma pessoa parada fica coberta pelos telemóveis e, enquanto a presença depender apenas de uma câmara, por uma análise periódica de atualização.

### C3. E se o telemóvel ficar em casa, ou uma visita não tiver telemóvel?

Resposta curta: “Nesse caso, os sinais não concordam, a casa fica ‘incerta’ e as regras perguntam em vez de agir.”

- Pormenor:
  - um telemóvel em casa, sem nenhuma observação nem uso da porta durante muito tempo (3 h propostas), indica um telemóvel esquecido;
  - uma pessoa vista quando não há nenhum telemóvel em casa é alguém sem telemóvel registado: uma visita, uma criança ou um desconhecido;
  - o rosto decide qual, se estiver registado; caso contrário, pergunta-se à família.

### C4. É o modelo de linguagem que decide?

Resposta curta: “Não. Os modelos só veem; quem decide é um motor de regras determinista.”

- Pormenor:
  - o _OWLv2_ devolve caixas com pontuações, o _DINOv2_ indica quão próximo um recorte está de uma assinatura e o _SFace_ diz de quem é o rosto;
  - todas as conclusões (“esquecido”, “ninguém em casa”, “pessoa desconhecida”) são decididas por código nos motores de regras e de presença, e reavaliadas a cada evento e a cada temporizador;
  - o modelo de linguagem faz apenas três coisas: transformar uma frase numa regra, redigir respostas e mensagens e, raramente, avaliar um recorte duvidoso;
  - [protótipo]: `server.py`, `rules_engine`; o modelo de linguagem em `brain.py`.

### C5. E se o modelo de linguagem se enganar?

Resposta curta: “Não pode agir sozinho: a regra que escreve é validada e mostrada ao utilizador em palavras simples, e o código confere as respostas com a memória.”

- [protótipo]:
  - uma regra inválida é substituída pelos padrões de palavras-chave;
  - uma resposta que contradiga a memória é substituída por uma frase simples construída a partir da memória (`brain.py`; ver o [AGENTS.md](../../AGENTS.md)).

### C6. Como se executam as ações?

Resposta curta: “Através do servidor MCP da Altice; é a escolha da família que define o que é intrusivo, e ativar o alarme exige sempre confirmação.”

- [protótipo]: todas as ações correm em simulação, salvo com `TT_LIVE_ACTIONS=1`, que a equipa nunca ativa, pelo que a casa real nunca é alterada (`actions.py`).

## D. Dados, segurança e privacidade

### D1. Que base de dados?

Resposta curta: “_SQLite_ no protótipo; em produção, _PostgreSQL_ com _pgvector_ na Altice, e um pequeno armazenamento local em casa.”

- Pormenor:
  - na Altice, por cliente: objetos, assinaturas, regras, eventos, observações e presença, com _Redis_ para o estado em tempo real e armazenamento de objetos para as miniaturas (30 dias, valor proposto);
  - em casa: os padrões faciais, cifrados, e a fila de saída dos eventos;
  - [protótipo]: `store.py` (_SQLite_). O protótipo não tem _PostgreSQL_.

### D2. O vídeo é gravado ou enviado?

Resposta curta: “Não. Só se envia a região que mudou, enquanto há movimento, e apaga-se depois da análise, exceto a miniatura de uma observação.”

- As gravações do laboratório usadas nos filmes foram feitas para os filmes, localmente, com o acordo das pessoas ou com desfocagem.

### D3. Segurança?

Resposta curta: “Uma única ligação de saída por casa, com autenticação mútua; nenhuma porta de rede aberta em casa.”

- Pormenor: mTLS do agente da casa até ao corretor, um tópico MQTT por casa, HTTPS para a app e padrões faciais cifrados em repouso, em casa.

Onde se mostra: o diagrama de fluxo de dados com fronteiras de confiança.

### D4. RGPD?

Resposta curta: “Minimização desde a conceção: nenhum vídeo sai de casa, os rostos só com consentimento explícito e guardados em casa, e prazos de conservação limitados.”

- O fornecedor do modelo de linguagem tem de garantir que não treina com os nossos dados, assinar um acordo de tratamento de dados (DPA) e tratar os dados na UE (documento 14, §3).

## E. Integração com a Altice

### E1. O que tem a Altice de acrescentar?

Resposta curta: “Um separador _Things_, um botão de assistente, quatro ferramentas MCP para os objetos, uma para a presença no Wi-Fi, e o serviço.”

- As ferramentas: `list_things`, `create_thing`, `get_thing_last_seen` e `get_thing_timeline`, mais a ferramenta proposta para a presença no Wi-Fi. As ações usam as 18 ferramentas que já existem (documento 14, §3, e documento 15).

### E1a. Como ligaram a porta à vossa app sem acesso ao nosso _backend_, à app ou à base de dados?

Resposta curta: “Não precisámos do vosso _backend_. Deram às equipas o servidor MCP do _Connected Home_, a interface oficial da plataforma. O sensor da porta pertence à nossa casa de testes na vossa plataforma, como o dispositivo de qualquer cliente, e lemo-lo através dessa interface.”

- Pormenor:
  - o sensor: o sensor de contacto do _kit_ (MS-D3D) na nossa casa de testes (“Hack 3”). A Altice configurou os sete dispositivos do _kit_ e associou-os à conta da equipa; não acrescentámos nenhum dispositivo ([04-kit-and-access.md](../04-kit-and-access.md)). Colámos o sensor e o íman na porta do laboratório ([19-teste-real.md](../19-teste-real.md));
  - o acesso: o nosso cliente MCP (`mcp/client/chmcp.py`) inicia sessão com a conta da equipa através do _Keycloak_ da Altice (OAuth) e envia a chave da API em cada pedido (`chmcp.py:170-171`), com a versão 2025-06-18 do protocolo MCP;
  - a leitura da porta: a cada 4 s, o servidor chama a ferramenta de leitura `get_home_devices`, encontra o `contactSensor` e lê o `sensorState`, em que `"alarm"` significa aberta (`server.py:894-921`). A base de dados do protótipo tem eventos reais da porta desde 19 de novembro;
  - nunca tocámos no _backend_, na app nem na base de dados da Altice. A app dos filmes é a nossa cópia dos ecrãs da app da Altice, a correr o nosso protótipo; em produção, a Altice acrescenta o separador _Things_ à sua própria app.
- A limitação, dita com franqueza, e o pedido: o servidor MCP não envia eventos, pelo que fazemos consultas periódicas, o que explica parte dos cerca de 10 s do aviso da porta no protótipo. Em produção, o _ThingTracker_ corre dentro da plataforma da Altice e recebe os eventos dos sensores diretamente, ou por uma subscrição de eventos. Nunca chamamos as ferramentas de escrita: as ações correm em simulação, por regra da própria equipa.

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
  - em produção, o _ThingTracker_ corre dentro da plataforma da Altice e usa diretamente esse serviço de notificações. É uma das poucas coisas que pediríamos à Altice para acrescentar.
- [protótipo]: os avisos aparecem na nossa cópia da app [a confirmar: disparados pelas regras, e não injetados]. A notificação no telemóvel, nos filmes, foi composta na montagem.
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

Resposta curta: “Cerca de 0,49 € por mês para a visão, com uma câmara, e cerca de 0,43 € para o modelo de linguagem.”

- São estimativas da equipa feitas com preços públicos (documentos [16](16-viabilidade-negocio.md) e [17](17-custos-operador.md)), a medir no piloto.

### F2. Licenças?

Resposta curta: “Todas abertas, e todas permitem uso comercial.”

- Pormenor: _OWLv2_ e _DINOv2_, Apache-2.0; _Qwen3-1.7B_, Apache-2.0; _YuNet_, MIT; _SFace_, Apache-2.0 (verificadas nos ficheiros dos modelos; as somas de verificação estão no [AGENTS.md](../../AGENTS.md)).

## G. Os filmes e a demonstração

### G1. O que os filmes mostram é real?

Resposta curta: “As imagens são do laboratório real e da câmara do _kit_, a app é o nosso protótipo e as caixas vêm dos nossos modelos, aplicados a essas imagens; alguns momentos foram encurtados, e os filmes indicam-no.”

- Pormenor, a dizer com franqueza se for pedido:
  - os avisos foram disparados para a gravação [a confirmar: desde 19 de novembro, são as mesmas regras que os disparam no protótipo];
  - o trecho em que as pessoas estão sentadas aparece a 4×;
  - um corte elimina o tempo em que a sala está vazia;
  - o ecrã negro da câmara, quando as luzes se apagaram, foi reconstruído a partir do comportamento da própria câmara;
  - a caixa de deteção da tomada inteligente foi colocada numa tomada escolhida, porque o _kit_ já tinha sido arrumado.

### G2. O que podem mostrar ao vivo?

- [a confirmar depois do trabalho no código] as regras a disparar a partir de uma porta simulada e de telemóveis simulados, o estado de presença a mudar e um rosto reconhecido ou não.

### G3. O que está medido, e o que não está?

- Medido no laboratório, na câmara do _kit_: o livro a 0,70 para um limiar de 0,62; uma garrafa a 0,10.
- Não medido: a exatidão e os falsos alarmes em casas reais. Isso será medido no piloto.
