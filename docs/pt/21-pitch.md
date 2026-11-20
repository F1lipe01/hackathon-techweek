# _Pitch_ do _ThingTracker_

Versão de 20 de novembro de 2026, de manhã, para as duas rondas de hoje, que substitui a de 19 de novembro. Serve de guião para os diapositivos, para os ensaios e para as perguntas do júri. O Filipe apresenta sozinho as duas versões e responde a todas as perguntas. O tom é positivo: o _pitch_ mostra como funciona, porque é bom, porque interessa à Altice e como se começa, e os limites e as ressalvas ficam para as perguntas, onde se tratam com franqueza (secções 10 a 12). Os números vêm dos documentos [14](14-arquitetura.md) (arquitetura), [16](16-viabilidade-negocio.md) (viabilidade do negócio) e [17](17-custos-operador.md) (custos do operador), e tudo o que se diz sobre os filmes segue o documento [24](../24-what-is-real.md), que classifica cada momento de cada filme; nenhum número ou afirmação entra no _pitch_ sem estar nesses documentos. As respostas às perguntas técnicas estão no documento [23](23-perguntas-engenharia.md) e a folha de apoio de uma página no documento [25](25-cola-pitch.md).

## 1. Formato e critérios

| Ronda | Quando | Formato | Critérios (peso) |
|---|---|---|---|
| Intermédia | Sexta, 20 nov, a partir das 16h00, perante os mentores e o júri do desafio; passam 3 finalistas por desafio | 3 min de _pitch_ + 2 min de perguntas | Enquadramento e resposta ao desafio (25 %), facilidade de adoção (25 %), viabilidade e sustentabilidade (25 %), apresentação da solução (25 %) |
| Final | Sexta, a partir das 18h00 | 5 min de _pitch_ + 3 min de perguntas | Enquadramento (20 %), adoção (20 %), viabilidade (20 %), possibilidade de replicação (20 %), apresentação (10 %), documentação (entregáveis) (10 %) |

Fonte: guia oficial dos participantes (Drive, lido a 20 de novembro), que prevalece sobre as normas resumidas em [01-event.md](../01-event.md). Dois quintos da nota final (40 %) vêm da adoção pela Altice e da replicação, pelo que o _pitch_ tem de mostrar que a Altice consegue lançar o produto com o que já tem e dizer em voz alta as palavras dos critérios (“adoção”, “viabilidade”, “replicação”). A documentação vale 10 % da final e é julgada pelo que se entrega às 17h30 (sumário executivo, apresentação e ligação ao repositório), daí o diapositivo do repositório no _pitch_ de 5 minutos. A apresentação entrega-se em PPT (aceita-se PDF), pelo Google Drive, até às 17h30, e tem de “incluir menção de que ferramentas foram utilizadas”, o que o diapositivo `modelos` cumpre.

O júri:
- Pedro Almeida, responsável da Altice pela plataforma que o _ThingTracker_ estende (_Head of Media Delivery and Smart Home Platforms_): é a ele que se dirige a mensagem de adoção, ou seja, tudo assenta na câmara, na app, no MCP e na plataforma que a equipa dele já tem, e começa-se com um piloto;
- Duarte Raposo, investigador do Instituto de Telecomunicações: a arquitetura, os modelos e o repositório;
- Vítor Santos, da Universidade de Aveiro;
- um vereador da Câmara Municipal de Aveiro: o benefício para as famílias, em palavras simples, como os casos da criança e do pai, no diapositivo `conceitos`.

## 2. A mensagem numa frase

O _ThingTracker_ põe a câmara que a Altice já vende a perceber o que vê, e a avisar a família quando é preciso.

A frase técnica, dita nas duas versões, é “os modelos veem, o código decide”; nas perguntas, acrescenta-se “e o modelo de linguagem só escreve”. Três provas sustentam a mensagem e são as três linhas do fecho: o reconhecimento já funciona nas imagens da câmara do _kit_ (o livro foi reconhecido em 68 de 68 fotogramas, com mediana 0,93, para um limiar de 0,62); a visão custa à Altice cerca de 0,49 € por casa e por mês; o produto usa a app e o MCP que a Altice já tem. O pedido é começar já com um piloto em casas de colaboradores da MEO, e a frase final, igual à da capa, é “A câmara da casa, atenta ao que importa.”

## 3. A abertura

A abertura segue a nova ordem do _deck_ (capa, `hoje`, `possivel`, `thingtracker`) e dura cerca de 43 s nas duas versões. As duas aberturas possíveis dizem-se no diapositivo `hoje`:
- Por omissão, “a cena”, que é a mais forte: abre pela segurança, como pediram os mentores, contrasta o que a câmara faz hoje com o que podia fazer e, no _pitch_ de 3 minutos, tem resposta no diapositivo `conceitos`.
- Em alternativa, “a pergunta”, que envolve o júri na primeira frase; com ela, em `possivel` diz-se “a criança em perigo” em vez de “onde ficaram as chaves”, para não repetir as chaves, e a abertura fica 1,5 s mais longa.

| Diapositivo | O que está no ecrã | O que se diz | Palavras |
|---|---|---|---|
| `capa` | Os nomes e a equipa | “Boa tarde. Somos a equipa IT-Porto, do Instituto de Telecomunicações.” | 10 |
| `hoje`, por omissão | “Hoje, a câmara de casa só grava”; a notificação “Movimento detetado”; “…e depois?” | “Hoje, a câmara de casa só grava. Uma criança pega numa cápsula de detergente, e o telemóvel diz apenas ‘movimento detetado’. E depois?” | 23 |
| `hoje`, em alternativa | O mesmo | “Onde deixaram as chaves esta manhã? A câmara de casa até as viu, mas só sabe gravar, e o telemóvel diz apenas ‘movimento detetado’. E depois?” | 26 |
| `possivel` | “Câmara + IA: a casa percebe o que vê”; seis casos de uso; “Cada família cria os seus, com uma frase.” | “Com IA, a câmara percebe o que vê: onde ficaram as chaves, quem entrou em casa, o que ficou ligado. Cada família cria os seus avisos, com uma frase.” | 29 |
| `thingtracker` | “Por isso criámos o _ThingTracker_”; Câmara → Imagens → IA → Aviso | “Por isso criámos o _ThingTracker_: a câmara que a Altice já vende capta as imagens, a IA percebe-as e a família recebe o aviso.” | 24 |

Os três exemplos de `possivel` correspondem aos três filmes do _pitch_ de 5 minutos (as coisas, a segurança e a energia), e, no de 3 minutos, os conceitos acrescentam a criança e o pai.

## 4. Os diapositivos

O _deck_ ([ThingTracker · Pitch](https://claude.ai/artifact/HrCc8JBAhjvCy1fcKEkyXp), privado até ser partilhado) está a ser refeito pelo agente do _deck_ com esta ordem. Os filmes não passam dentro do _deck_: o diapositivo de cada filme é um cartão com o título, e o filme passa em ecrã inteiro a partir do ficheiro local (secção 9). As notas de todos os diapositivos têm um só orador, o Filipe, com os tempos e as frases das secções 6 e 7.

### 4.1 Lista e critérios

| Id | Diapositivo | 3 min | 5 min | Critério que ganha |
|---|---|---|---|---|
| `capa` | Os nomes e a equipa IT-Porto, do Instituto de Telecomunicações | 1 | 1 | Apresentação |
| `hoje` | “Hoje, a câmara de casa só grava”: “Movimento detetado”… e depois? | 2 | 2 | Enquadramento |
| `possivel` | “Câmara + IA: a casa percebe o que vê”: seis casos de uso; cada família cria os seus com uma frase | 3 | 3 | Enquadramento, replicação |
| `thingtracker` | “Por isso criámos o _ThingTracker_”: Câmara → Imagens → IA → Aviso | 4 | 4 | Enquadramento, adoção |
| `conceitos` | Dois conceitos: a criança em perigo e os comprimidos do pai | 5 | — | Enquadramento |
| `filme-livro` | As coisas: o livro esquecido (filme) | 6 | 5 | Enquadramento, viabilidade, apresentação |
| `filme-desconhecido` | A segurança: uma pessoa desconhecida (filme) | — | 6 | Enquadramento, apresentação |
| `filme-casa-vazia` | A energia: ninguém em casa (filme) | — | 7 | Enquadramento, viabilidade |
| `como-funciona` | No protótipo, um portátil faz de casa e de servidores da Altice; na proposta, o _router_ e os servidores da Altice; “os modelos veem, o código decide” | 7 | 8 | Adoção, viabilidade |
| `modelos` | Modelos e ferramentas (menção obrigatória) | — | 9 | Viabilidade, adoção, replicação, documentação |
| `custos` | Custos: 49 cêntimos por casa e por mês | 8 | 10 | Viabilidade |
| `replicacao` | Replicação noutros operadores e países | — | 11 | Replicação |
| `comecar` | Como se começa: o piloto | 9 | 12 | Adoção, viabilidade, replicação |
| `repositorio` | Está tudo no repositório | — | 13 | Documentação |
| `fecho` | Fecho: três pontos, o pedido e a frase final | 10 | 14 | Apresentação, adoção, viabilidade |

Ordem de cada versão:
- 3 minutos (10 diapositivos): `capa`, `hoje`, `possivel`, `thingtracker`, `conceitos`, `filme-livro`, `como-funciona`, `custos`, `comecar`, `fecho`.
- 5 minutos (14 diapositivos): `capa`, `hoje`, `possivel`, `thingtracker`, `filme-livro`, `filme-desconhecido`, `filme-casa-vazia`, `como-funciona`, `modelos`, `custos`, `replicacao`, `comecar`, `repositorio`, `fecho`.
- Reserva, depois do fecho e fora das duas versões: os diapositivos `anexo-*` e os antigos que ficaram de fora, como `privacidade`, `arquitetura` e `memoria`.

Saem das duas versões os antigos `cover`, `problema`, `ideia`, `equipa` (os nomes passam para a capa), `prototipo-proposta` (passa a `como-funciona`) e `lancamento` (passa a `comecar`). Para não saltar diapositivos em palco, sugere-se uma exportação por versão (PDF e PPTX). Aos créditos, o fecho acrescenta três linhas: “Filmes: laboratório da equipa, com momentos encenados”; as ferramentas (os modelos do diapositivo `modelos`, o servidor MCP da Altice e o _Claude Code_), para que também a exportação de 3 minutos as mencione; e, em letra pequena, o endereço do repositório. A apresentação entregue às 17h30 é a de 5 minutos, que inclui `modelos`.

### 4.2 O conteúdo dos diapositivos

`possivel`: seis casos de uso, se o _deck_ ainda não os tiver escolhido: onde ficaram as chaves, a criança em perigo, quem entrou em casa, o que ficou ligado, os comprimidos do pai e o gato na bancada. Por baixo: “Cada família cria os seus, com uma frase.”

`conceitos`: “Uma frase basta”, com a marca “Conceito” bem visível e dois conceitos lado a lado.
- À esquerda, a criança em perigo:
  - imagem: a fotografia da Figura 1 do relatório submetido, `deliverables/executive-summary/fotos/crianca2-cena.jpg` (há também `crianca2-cena-full.jpg`), com o rosto e os logótipos desfocados; o _deck_ usa uma cópia com a marca do forno também desfocada, sem mudar o ficheiro do relatório;
  - caixas, como na Figura 1: “Criança” e “Detergente” (coordenadas em `fotos/fotos.json`);
  - a regra, definida de antemão: “Avisa-me se a criança estiver em perigo”;
  - o aviso: “A criança pôs um detergente na boca. Cozinha · 16h30 · com fotografia”.
- À direita, os comprimidos do pai:
  - a regra: “Avisa-me se o pai não tomar os comprimidos até ao meio-dia”;
  - o aviso, às 12h00, para a filha: “O pai ainda não tomou os comprimidos.”;
  - como funcionaria, numa linha: a caixa dos comprimidos é registada como objeto, e os comprimidos contam como tomados quando a caixa aparece na mão do pai (o evento “na mão”, documento 14, §8.2);
  - imagem: reaproveitar a fotografia de `mae` (“um casal idoso ao pequeno-almoço, numa sala luminosa”), recortada no homem, se resultar; caso contrário, uma fotografia de arquivo com licença (Pexels, como o resto do _deck_) de um homem idoso à mesa da cozinha, de manhã, com uma caixa ou um organizador de comprimidos à vista, vista de um canto alto, como a de uma câmara de casa, e sem marcas. Só se desenham caixas se forem deteções reais do _OWLv2_ nessa imagem, como em `gato` e `mae`.
- Créditos: a fotografia da criança foi fornecida pela equipa, com o rosto e os logótipos desfocados (`fotos.json`). Os créditos do fecho têm de corresponder às imagens que ficarem no _deck_.

`filme-livro`: “As coisas: o livro esquecido”.
- Cartão escuro com o título e uma linha: “Filmado no nosso laboratório, com a câmara do _kit_ e o nosso protótipo; alguns momentos foram encenados.”
- Em letra pequena, os números do `exemplo` atualizado: “O livro reconhecido em 68 de 68 fotogramas, a 0,93 (limiar de 0,62).”
- Filme: no de 3 min, `ThingTracker - pitch - o livro (25 s).mp4`; no de 5 min, `ThingTracker - pitch - o livro (20 s).mp4`.

`filme-desconhecido`: “A segurança: uma pessoa desconhecida”, com a linha “Com a família fora, o sistema distingue quem é da família de um desconhecido.” Filme: `ThingTracker - pitch - pessoa desconhecida (20 s).mp4`, só no de 5 min.

`filme-casa-vazia`: “A energia: ninguém em casa”, com a linha “Quando sai a última pessoa, a app propõe desligar o que ficou ligado.” Filme: `ThingTracker - pitch - ninguém em casa (20 s).mp4`, só no de 5 min.

`modelos`: “Modelos e ferramentas”. O guia dos participantes exige que a apresentação mencione as ferramentas utilizadas; o diapositivo segue a secção “Ferramentas de IA” do sumário executivo e não nomeia os serviços de áudio ou de música usados nos filmes.

| Modelo | Licença | O que faz | Onde corre, na proposta |
|---|---|---|---|
| _OWLv2_ | Apache-2.0 | Encontra pessoas e coisas pelo nome | Servidores da Altice |
| _DINOv2_ | Apache-2.0 | Reconhece as coisas de cada família pela assinatura visual | Servidores da Altice |
| _YuNet_ e _SFace_ | MIT e Apache-2.0 | Encontram e comparam rostos, com consentimento | Em casa, no _router_ |
| _Qwen3-1.7B_ (local, no protótipo) | Apache-2.0 | Transforma frases em regras e escreve as mensagens | Servidores da Altice, ou um fornecedor sob contrato |
| _Qwen2-VL-2B_ (opcional) | Apache-2.0 | Confirma os casos duvidosos, que são raros | Servidores da Altice |

- Ferramentas, por baixo da tabela:
  - a plataforma: o servidor MCP do _Connected Home_ da Altice;
  - em produção, o modelo de linguagem: de pesos abertos e alojado pela Altice, ou sob contrato (_Claude_ ou equivalente), sem usar os dados para treino;
  - o desenvolvimento: _Claude Code_ (_Claude Opus 5.5_), na pesquisa, na programação e na redação.
- Rodapé: “Os modelos veem; quem decide é o código.”

`como-funciona`: “Os modelos veem, o código decide”.
- À esquerda, numa coluna estreita, “No protótipo”: “Um _MacBook_ faz de casa e de servidores da Altice: recebe o _stream_ real da câmara do _kit_, corre todos os modelos, guarda os dados e lê os dispositivos do _kit_ pelo servidor MCP da Altice.”
- À direita, numa coluna larga marcada “Proposta”, o diagrama de `arquitetura`, que já tem os rostos em casa e a presença:
  - em casa, no processador do _router_, sem _hardware_ novo: o movimento, a zona da imagem que mudou e, se a família quiser, os rostos, cujos padrões faciais nunca saem de casa;
  - na Altice: os servidores de visão (_OWLv2_ e _DINOv2_ em GPU _L4_), o serviço _ThingTracker_ atrás de um balanceador de carga, com os motores de presença e de regras, a base de dados _PostgreSQL_ e o modelo de linguagem, só para texto;
  - o que já existe: a app, o servidor MCP e as notificações.
- Faixa em baixo: “Presença: câmaras, sensor da porta e telemóveis no Wi-Fi” e “Cerca de 0,49 € por casa e por mês”.

`comecar`: “Como se começa”, com o piloto em destaque e os passos seguintes em pequeno.
- O piloto: casas de colaboradores da MEO, com a câmara do _kit_ e o MCP que já existem, e a app com o novo separador _Things_; GPU alugadas na nuvem, sem custo fixo.
- Depois, os clientes: 3,99 € por mês; servidores próprios quando a base de clientes crescer.
- Por fim, os _routers_ com IA: a visão passa para casa, a cerca de 0,36 € por casa e por mês.

`repositorio`: “Está tudo no repositório”.
- Seis blocos:
  - código: o protótipo (servidor, agente da casa, app e modelo de texto local);
  - arquitetura: o documento 14, com 12 diagramas, em português e em inglês;
  - custos: os documentos 16 e 17 e os respetivos modelos de cálculo;
  - testes: 107 testes dos cenários, todos a passar (`prototype/test_scenarios.py`);
  - filmes: o que é real em cada um (documento 24) e as fontes da montagem;
  - execuções sem montagem: a ferramenta `video/tools/proof_run.py`.
- O endereço `github.com/F1lipe01/hackathon-techweek`, o mesmo da entrega das 17h30.
- Os vídeos não estão no _git_ (AGENTS.md); se a equipa os puser no Drive, acrescenta-se a ligação.

### 4.3 A qualidade dos diapositivos

O líder da equipa quer diapositivos de grande qualidade. Para o agente do _deck_:
- uma ideia por diapositivo, que se perceba em 3 segundos, com poucas palavras no ecrã, porque o Filipe diz o resto;
- imagens reais e grandes, com as caixas dos modelos onde forem reais, e o mesmo estilo nos cartões dos filmes;
- a palavra do critério visível, em pequeno, no canto (“Adoção pela Altice”, “Viabilidade”, “Replicação”), como já acontece em `arquitetura` e `custos`;
- números grandes e com unidade (0,49 €, 68 de 68, 107 testes);
- nenhum diapositivo com avisos, limites ou “a confirmar”: esse conteúdo fica na reserva e no documento 23.

## 5. Quem apresenta

- O Filipe apresenta tudo, nas duas versões, e responde a todas as perguntas. Fala na primeira pessoa do plural (“filmámos”, “propomos”); nos filmes, em que aparece, pode dizer “saio de casa sem o livro”.
- Sugere-se que um colega controle o portátil e os filmes, para o Filipe falar sem se virar para o ecrã, e que o outro cronometre e mostre os pontos de controlo das secções 6 e 7.
- Sem passagens de palavra, o tempo que lhes cabia vai para o ritmo e para a folga.

## 6. _Pitch_ de 3 minutos

As contas fazem-se a 2 palavras por segundo, com os números contados como se dizem (“três e noventa e nove” são cinco palavras), e com 1 s para cada troca entre o _deck_ e o filme. O _pitch_ termina aos 2:43, ou aos 2:45 com a abertura alternativa, dentro do limite de 2:45 e com pelo menos 5 s de folga até aos 2:50. As contas são conservadoras: ao ritmo médio de fala (138 palavras por minuto), o texto encurta cerca de 15 s, mas não se conta com essa folga.

| Início | Fim | Diapositivo | Palavras | O que se diz |
|---|---|---|---|---|
| 0:00 | 0:05 | `capa` | 10 | “Boa tarde. Somos a equipa IT-Porto, do Instituto de Telecomunicações.” |
| 0:05 | 0:16 | `hoje` | 23 | “Hoje, a câmara de casa só grava. Uma criança pega numa cápsula de detergente, e o telemóvel diz apenas ‘movimento detetado’. E depois?” |
| 0:16 | 0:31 | `possivel` | 29 | “Com IA, a câmara percebe o que vê: onde ficaram as chaves, quem entrou em casa, o que ficou ligado. Cada família cria os seus avisos, com uma frase.” |
| 0:31 | 0:43 | `thingtracker` | 24 | “Por isso criámos o _ThingTracker_: a câmara que a Altice já vende capta as imagens, a IA percebe-as e a família recebe o aviso.” |
| 0:43 | 0:53 | `conceitos` | 21 | “Dois conceitos: ‘avisa-me se a criança estiver em perigo’ e ‘avisa-me se o pai não tomar os comprimidos até ao meio-dia’.” |
| 0:53 | 1:02 | `filme-livro` | 17 | “Filmámos no nosso laboratório, com a câmara do _kit_ e o nosso protótipo; alguns momentos foram encenados.” |
| 1:03 | 1:28 | Filme | — | `ThingTracker - pitch - o livro (25 s).mp4`, em ecrã inteiro |
| 1:29 | 1:47 | `como-funciona` | 37 | “No protótipo, este portátil faz de casa e de servidores da Altice. A adoção não exige _hardware_ novo: o _router_ deteta o movimento e os servidores da Altice tratam da visão. Os modelos veem, o código decide.” |
| 1:47 | 2:03 | `custos` | 31 | “Viabilidade: a visão custa uns 49 cêntimos por casa e por mês; num serviço de 3,99 €, ficam uns 1,25 € de margem.” |
| 2:03 | 2:16 | `comecar` | 27 | “Para começar: um piloto em casas de colaboradores da MEO, com a câmara, a app e o MCP que já existem, e GPU alugadas, sem custo fixo.” |
| 2:16 | 2:43 | `fecho` | 50 | A frase de fecho (secção 8), uma pausa e a frase final. |

Pontos de controlo: o filme começa até aos 1:04, os custos até aos 1:49 e o fecho até aos 2:18. Se aos 0:43 houver atraso, salta-se `conceitos`, o que poupa cerca de 10 s.

## 7. _Pitch_ de 5 minutos

As mesmas contas. O _pitch_ termina aos 4:32, ou aos 4:34 com a abertura alternativa, com pelo menos 6 s de folga até aos 4:40; ao ritmo médio de fala, o texto encurta cerca de 25 s, folga com que também não se conta. Os três filmes (20,5 s, 20,2 s e 19,5 s) substituem os casos e o exemplo real, e nunca se mostram juntos com eles.

| Início | Fim | Diapositivo | Palavras | O que se diz |
|---|---|---|---|---|
| 0:00 | 0:43 | `capa`, `hoje`, `possivel` e `thingtracker` | 86 | Igual ao _pitch_ de 3 minutos (secção 3). |
| 0:43 | 0:56 | `filme-livro` | 26 | “Filmámos no nosso laboratório, com a câmara do _kit_ e o nosso protótipo; alguns momentos foram encenados. No primeiro filme, saio de casa sem o livro.” |
| 0:57 | 1:17 | Filme | — | `ThingTracker - pitch - o livro (20 s).mp4` |
| 1:18 | 1:26 | `filme-desconhecido` | 16 | “Depois, a segurança: o sistema reconhece-me, com o meu consentimento, e avisa quando entra um desconhecido.” |
| 1:27 | 1:47 | Filme | — | `ThingTracker - pitch - pessoa desconhecida (20 s).mp4` |
| 1:48 | 1:58 | `filme-casa-vazia` | 19 | “Por fim, a energia: quando já não está ninguém em casa, a app propõe desligar o que ficou ligado.” |
| 1:59 | 2:18 | Filme | — | `ThingTracker - pitch - ninguém em casa (20 s).mp4` |
| 2:19 | 2:38 | `como-funciona` | 37 | Igual ao _pitch_ de 3 minutos. |
| 2:38 | 2:58 | `modelos` | 41 | “Os modelos são _open-source_ e permitem uso comercial: o _OWLv2_ encontra pessoas e coisas, o _DINOv2_ reconhece as coisas de cada família, o _YuNet_ e o _SFace_ tratam dos rostos e o _Qwen3_ escreve regras e mensagens.” |
| 2:58 | 3:14 | `custos` | 31 | Igual ao _pitch_ de 3 minutos. |
| 3:14 | 3:27 | `replicacao` | 26 | “Replicação: basta uma câmara, uma app e uma interface como o MCP; nada depende do mercado português. Serve outros operadores, lares de idosos e alojamento local.” |
| 3:27 | 3:54 | `comecar` | 54 | “Adoção em três passos. Primeiro, um piloto em casas de colaboradores da MEO, com a câmara, a app e o MCP que já existem, e GPU alugadas, sem custo fixo. Depois, os clientes, a 3,99 € por mês. Por fim, _routers_ com IA, e a visão passa a correr em casa.” |
| 3:54 | 4:06 | `repositorio` | 23 | “Está tudo no repositório: o código, a arquitetura com 12 diagramas, os custos e 107 testes dos cenários, todos a passar.” |
| 4:06 | 4:32 | `fecho` | 50 | A frase de fecho (secção 8), uma pausa e a frase final. |

Pontos de controlo: o primeiro filme começa até aos 0:58, o último acaba até aos 2:19 e os custos começam até aos 3:00. Se aos 2:19 houver atraso, dos modelos diz-se só “Os modelos são _open-source_ e permitem uso comercial.”, o que poupa cerca de 14 s.

## 8. Frases fixas

- A abertura: secção 3, com `hoje` por omissão ou em alternativa.
- Antes do primeiro filme, nas duas versões: “Filmámos no nosso laboratório, com a câmara do _kit_ e o nosso protótipo; alguns momentos foram encenados.”
- A frase técnica, nas duas versões: “Os modelos veem, o código decide.” Nas perguntas, acrescenta-se “e o modelo de linguagem só escreve”.
- O primeiro passo, nas duas versões: “Um piloto em casas de colaboradores da MEO, com a câmara, a app e o MCP que já existem, e GPU alugadas, sem custo fixo.”
- O fecho, nas duas versões: “O _ThingTracker_ já reconhece objetos nas imagens da câmara do _kit_, custa à Altice cerca de 49 cêntimos por casa e por mês, e usa a app e o MCP que a Altice já tem. Propomos começar já pelo piloto.” Pausa. Última frase, palavra por palavra: “A câmara da casa, atenta ao que importa.” Depois, silêncio; nunca “alguma pergunta?”.

O que não se diz no _pitch_, porque pertence às perguntas: “ainda não”, “não sabemos”, “a confirmar”, “simulado”, “em teste”, e qualquer referência ao que falta fazer.

## 9. Os filmes

As quatro versões estão em `video/out/pitch/`, a 1080p, com música baixa. Cada filme começa depois de uma frase dita com o cartão no ecrã e passa sem narração; o Filipe espera em silêncio até ao fim.

| Filme | Ficheiro | Duração | Onde passa | Frase antes | O que mostra | O que foi encenado (documento 24, para as perguntas) |
|---|---|---|---|---|---|---|
| O livro | `ThingTracker - pitch - o livro (25 s).mp4` | 25,0 s | 3 min, aos 1:03 | “Filmámos no nosso laboratório (…); alguns momentos foram encenados.” | As fotografias do livro; uma frase que se torna cenário; o Filipe sai sem o livro e o alarme toca; a notificação e o aviso no telemóvel; volta para o buscar; “Desta vez, o alarme não tocou.” | O som do alarme, a notificação e “Desligar o alarme”; a porta aberta ou fechada foi deduzida da imagem na montagem |
| O livro | `ThingTracker - pitch - o livro (20 s).mp4` | 20,5 s | 5 min, aos 0:57 | A mesma frase e “No primeiro filme, saio de casa sem o livro.” | O mesmo caso, mais curto | O mesmo |
| A pessoa desconhecida | `ThingTracker - pitch - pessoa desconhecida (20 s).mp4` | 20,2 s | 5 min, aos 1:27 | “Depois, a segurança: o sistema reconhece-me, com o meu consentimento, e avisa quando entra um desconhecido.” | Segundo o documento 24, o registo do Filipe na app, o cenário sugerido, a entrada do Filipe e a de um desconhecido, e o alarme com a sugestão de chamar a polícia | No filme, a comparação de rostos é ilustrativa e está marcada como tal; o alarme e a sugestão da polícia foram acrescentados na montagem |
| Ninguém em casa | `ThingTracker - pitch - ninguém em casa (20 s).mp4` | 19,5 s | 5 min, aos 1:59 | “Por fim, a energia: quando já não está ninguém em casa, a app propõe desligar o que ficou ligado.” | O cenário guardado; entram, acendem as luzes; sentados, a 4×, com o ar condicionado ligado; saem; o aviso com dois cartões e a sala a escurecer; a passagem ao ar condicionado; a porta fechada; “Ninguém em casa, nada ligado.” | As luzes e o ar condicionado foram desligados à mão; o contador de pessoas e a porta foram calculados na montagem; a caixa da tomada e a passagem a escuro foram feitas na montagem; o aviso foi disparado à mão, o desligar da tomada foi em simulação e o ar condicionado é simulado |

Como se passam (procedimento a ensaiar na sala):
- Os ficheiros ficam no portátil e numa _pen_, sem depender da rede.
- Antes de cada ronda, quem controla o portátil abre no _QuickTime_ os filmes dessa versão, cada um numa janela já em ecrã inteiro e parada em 0:00, pela ordem inversa à de passagem, para que o primeiro fique à frente. O _deck_ fica em ecrã inteiro no navegador.
- À última palavra da frase antes do filme, muda-se para o _QuickTime_ (Cmd-Tab) e carrega-se na barra de espaços; no fim, fecha-se a janela (Cmd-W), volta-se ao navegador (Cmd-Tab) e avança-se para o diapositivo seguinte. O rato não se mexe enquanto o filme passa, para os controlos não aparecerem.
- O volume da música acerta-se no ensaio da sala, baixo o bastante para não competir com a frase seguinte.

Se um filme não arrancar em 3 s, o cartão fica no ecrã e o Filipe conta o caso numa frase:
- o livro: “No filme, saio sem o livro; a porta fecha-se, a câmara confirma que o livro ficou na secretária e o telemóvel avisa-me.”
- a pessoa desconhecida: “No filme, com a família fora, entra uma pessoa que ninguém registou, e chega um aviso urgente, com a fotografia.”
- ninguém em casa: “No filme, sai a última pessoa e a app propõe desligar a luz e o ar condicionado, com um ‘Sim’ para cada um.”

## 10. “O vídeo é real?”

A resposta segue a decisão da equipa: um sistema real, com alguns momentos encenados, e a prova de que as decisões são do sistema. Nunca se diz que os filmes são inteiramente reais, nem que são falsos.

Resposta curta, na ronda intermédia: “É um sistema real, com alguns momentos encenados. A filmagem é da câmara do _kit_ e a app é o nosso protótipo; e, quando passamos a mesma gravação pelo sistema, sem montagem, é a regra que dispara o aviso do livro.”

Resposta completa, na final (cerca de 35 s): “É um sistema real, com alguns momentos encenados. A filmagem é da câmara do _kit_, no nosso laboratório; os ecrãs são o nosso protótipo, gravado a funcionar; as caixas vêm dos nossos modelos, aplicados à gravação. O alarme, as notificações e as luzes a apagarem-se foram encenados para o filme. Depois, passámos as mesmas gravações pelo sistema real, sem montagem: a regra dispara o aviso do livro, o sistema reconhece-me e trata a outra pessoa como desconhecida, e, com a casa vazia, propõe desligar os dois aparelhos.”

O pormenor, só se for pedido:

| Filme | Real | Resultado dos modelos, calculado depois da filmagem | Feito na montagem, à mão ou encenado | Na execução sem montagem (documento 24) |
|---|---|---|---|---|
| O livro | Os ecrãs da app (as 8 fotografias, o nome, Guardar, a frase que se torna cenário); a saída e o regresso, numa única gravação contínua da câmara do _kit_ | A caixa “pessoa” (_OWLv2_); a caixa “livro” com a pontuação (_OWLv2_ e _DINOv2_), encontrada em 68 de 68 fotogramas, com mediana 0,93, comparada com uma assinatura feita com vistas da própria câmara noutra gravação | A porta aberta ou fechada, deduzida da imagem; o som do alarme, a notificação e “Desligar o alarme” | A regra dispara “esquecido” (a porta, o telemóvel a sair e a verificação ativa da câmara, com o livro visto a 0,94 em 3 imagens); quando o Filipe sai com o livro, o resultado é “incerto”, sem aviso, e o juiz de visão concorda. O alarme continua simulado |
| A pessoa desconhecida | Os ecrãs da app (adicionar pessoa, o vídeo do rosto, “Filipe adicionado”, Família, o cenário sugerido, “Cenário guardado”); a entrada do Filipe e a do desconhecido | No registo do filme, o servidor cortou 8 quadrados fixos; hoje, o _YuNet_ encontra o rosto e o _SFace_ cria os padrões, em casa | A comparação de rostos, ilustrativa; o alarme e a sugestão da polícia | O Filipe é reconhecido (0,54 e 0,63, para um limiar de 0,40) e nada dispara enquanto está em casa; o outro é classificado como desconhecido (0,17 e 0,14). O alarme disparou pela regra em 2 de 4 repetições; nas outras 2, poucos rostos estavam nítidos o bastante e o sistema perguntou (“está alguém em casa, rosto não visto”) em vez de dar o alarme. O alarme é simulado e a app nunca liga para o 112 |
| Ninguém em casa | Duas frases que se tornam cenários (por padrões de palavras-chave); três pessoas entram, sentam-se e saem, com as luzes e o ar condicionado ligados | As caixas “pessoa” (_OWLv2_), ligadas em trajetos pela nossa ferramenta | Quatro gravações juntas, com o relógio reescrito com os dígitos da própria câmara e a parte sentada a 4×; o contador e a porta; as luzes e o ar condicionado desligados à mão; a caixa da tomada e a passagem a escuro; o aviso disparado à mão | O motor de presença conta as pessoas e decide “ninguém em casa” a partir dos telemóveis (simulados, nos momentos lidos da gravação), da porta e das câmaras; dispara um aviso pela regra, com os dois cartões e a faixa da porta; o “Sim” desliga a tomada (em simulação) e o ar condicionado (simulado) |

Perguntas que costumam seguir-se:
- “As fotografias do telemóvel chegam para reconhecer o livro?” Numa imagem do _kit_ à altura da secretária, chegam a 0,69; com a câmara no teto, só as vistas da própria câmara o reconhecem (0,91 a 0,94), e a app junta-as quando o utilizador confirma (documento 23, B1a e B2).
- “O _ThingTracker_ desligou mesmo as luzes?” No laboratório, as luzes e o ar condicionado não estão ligados a nenhum dispositivo do _kit_, por isso foram desligados à mão no momento do toque na app; numa casa, o comando segue pelo MCP para os aparelhos que a família tiver associado à app (documento 23, E3).
- “Há testes?” Os 107 testes dos cenários passam todos (`prototype/test_scenarios.py`).

## 11. Demonstração

Durante o _pitch_ não há demonstração ao vivo: os filmes fazem esse papel. As provas mostram-se nas perguntas da final, e só se o júri as pedir; na ronda intermédia, com 2 minutos de perguntas, apenas se oferecem.

### 11.1 As execuções sem montagem

Foram feitas na noite de 19 para 20 de novembro, com `video/tools/proof_run.py`. A gravação de cada filme faz de câmara e passa pelo sistema real (agente da casa, modelos, motor de presença e motor de regras), em tempo real e em resolução completa. Só a porta, os telemóveis e os dispositivos ligados à mão são reproduzidos, nos momentos em que aconteceram na gravação, e cada um aparece como “Replayed” na atividade; como os telemóveis não foram registados no laboratório, reproduzem-se nos momentos em que cada pessoa sai e entra, lidos da imagem. Tudo o resto é calculado no momento.

| Execução | Ficheiros | O que mostra (documento 24) |
|---|---|---|
| O livro | `video/out/proof/book.mp4` e `book.log.txt` | A porta fecha-se depois de o Filipe sair e o telemóvel dele sai do Wi-Fi; a verificação ativa vê o livro na secretária (0,94 em 3 imagens) e a regra dispara o aviso; quando sai com o livro, o resultado é “incerto”, sem aviso |
| A pessoa desconhecida | `video/out/proof/face.mp4` e `face.log.txt` | O Filipe é reconhecido e nada dispara; o outro é classificado como desconhecido; o alarme dispara pela regra em 2 de 4 repetições e, nas outras, o sistema pergunta |
| Ninguém em casa | `video/out/proof/nobody.mp4` e `nobody.log.txt` | A casa passa a VAZIA e chega um aviso com os dois cartões e a faixa da porta |

Como se mostra, em 30 s no máximo: o Filipe abre o vídeo no momento do aviso, ou o registo na linha do aviso, e diz “É a mesma gravação a passar pelo sistema, sem montagem: a porta e o telemóvel são reproduzidos a partir da gravação; a deteção, a presença e a decisão da regra são calculadas aqui, no momento.” Os vídeos das execuções mostram pessoas do laboratório: só se mostram com o acordo delas ou com os rostos desfocados (regra 6 do AGENTS.md); no vídeo dos rostos, um rosto já aparece desfocado.

### 11.2 Ao vivo, só com o _kit_ instalado

Faz-se apenas se o _kit_ estiver instalado na sala e o ensaio no local correr bem duas vezes seguidas; caso contrário, ficam as execuções sem montagem.
- Instalação: a câmara do _kit_ virada para uma mesa com o livro, nunca para o público (regra 6 do AGENTS.md); o sensor de contacto numa porta ou na tampa de uma caixa; a sessão MCP iniciada nesse dia (o _token_ dura cerca de 24 h); os três processos arrancados por ordem (`llm_local.py`, `server.py`, `edge.py`), sem a variável `TT_LIVE_ACTIONS` (ações em simulação).
- Guião, em 30 s: o cenário “avisa-me se sair sem o livro” já criado; abre-se o sensor, tira-se o telemóvel do Filipe do Wi-Fi na página (simulado, e diz-se) e fecha-se o sensor; o aviso chega à cópia da app em cerca de 10 s, porque o protótipo consulta a porta pelo MCP a cada 4 s (documento 23, A8).
- Se houver um telemóvel com a app da Altice, a app notifica a abertura da porta; é uma função que a Altice já tem, não do _ThingTracker_ (documento 23, E2).
- Nunca se liga ou desliga a tomada ou a lâmpada, nunca se toca no alarme e nunca se usam as ferramentas de escrita do MCP (regra 1 do AGENTS.md).
- A câmara chega ao portátil pelo _relay_ da organização, pelo que a demonstração depende da rede da sala.

## 12. Perguntas prováveis do júri

O Filipe responde a todas. Na ronda intermédia, os 2 minutos dão para duas ou três perguntas e, na final, os 3 minutos para quatro ou cinco. Cada resposta segue o mesmo padrão, em cerca de 25 s: uma frase de resposta, a prova, a limitação, dita com franqueza, e a ligação ao piloto. As respostas completas, com as fontes, estão no documento 23.

| Pergunta | Resposta |
|---|---|
| O vídeo é real? | A resposta da secção 10. |
| O que fez o portátil na demonstração? | Fez de casa, de servidores da Altice e de modelo de linguagem, tudo ao mesmo tempo. Na proposta, o movimento e os rostos ficam no _router_ e a visão corre na Altice (23, A2). |
| É o modelo de linguagem que decide? | Não. Os modelos só veem, e quem decide é um motor de regras determinista. O modelo de linguagem transforma a frase em regra e escreve as mensagens; a regra é validada e mostrada ao utilizador em palavras simples (23, C4 e C5). |
| Como sabe que saí sem o livro? | Quando a porta se fecha depois de sair alguém da família, a câmara verifica se o livro ainda lá está; se não o vê, o resultado é “incerto” e não há alarme. Na mesma gravação do filme, sem montagem, é a regra que dispara o aviso (23, B4 e B4a). |
| Quanto custa com 500 000 casas? Porque não a nuvem ou uma caixa em cada casa? | Cerca de 0,49 € por casa e por mês, porque só se analisa quando há movimento e só sai a zona que mudou. Com imagens completas seriam 2,41 € nos servidores da Altice e 3,93 a 4,26 € em GPU alugadas na nuvem; uma caixa em cada casa exigiria 100 a 140 milhões de euros de investimento inicial. É uma estimativa da equipa com preços públicos, e o piloto mede o custo real (23, A3, A4 e F1). |
| E a privacidade? E os rostos? | Na proposta, o vídeo não sai de casa: sai só a zona que mudou, enquanto há movimento. Reconhecer rostos é opcional e exige consentimento explícito, porque os rostos são dados biométricos (RGPD, artigo 9.º), e os padrões faciais nunca saem de casa. O modelo de linguagem só recebe texto (23, B5, D2 e D4). |
| O reconhecimento de rostos funciona? | Com a gravação do filme passada pelo sistema, sem montagem, o Filipe foi reconhecido e o desconhecido não; o alarme disparou em 2 de 4 repetições e, nas outras 2, com poucos rostos nítidos, o sistema perguntou em vez de dar o alarme (23, B5). |
| Falsos alarmes? | Limiares, confirmação em análises seguidas e a escolha da família, para cada perigo, entre perguntar primeiro e tocar logo o alarme; cada aviso traz a fotografia do momento. Em casas reais ainda não está medido, e é o piloto que o mede (23, B7 e G3). |
| Quanto trabalho dá integrar? | Um separador _Things_, um botão de assistente, quatro ferramentas MCP para as coisas, uma para a presença no Wi-Fi e o serviço. As ações usam as ferramentas que já existem (23, E1). |
| Como leram o sensor da porta sem acesso ao nosso _backend_? | Pelo servidor MCP que a Altice deu às equipas: o sensor é do nosso _kit_ de teste e lemos o estado a cada 4 s, sem nunca alterar nada (23, E1a). |
| Onde correm os modelos? E os _routers_? | No _router_, só o que é leve: o movimento, a zona que mudou e os rostos. A visão corre nos servidores da Altice. Se o _router_ tiver uma NPU capaz de correr um detetor, a visão passa para casa e o custo desce para cerca de 0,36 €; é a primeira pergunta para a Altice (14, §5.2). |
| Que licenças têm os modelos? | Todas abertas, e todas permitem uso comercial: _OWLv2_, _DINOv2_ e _Qwen3-1.7B_ com Apache-2.0, _YuNet_ com MIT e _SFace_ com Apache-2.0 (23, F2). |
| Replica-se noutros países? | Basta uma câmara, uma app e uma interface como o MCP; nada depende do mercado português. Em França, 39,01 % das pessoas usam dispositivos de casa conectada, contra 23,99 % em Portugal (Eurostat, 2024; documento 16). |
| Quem paga? | O cliente, 3,99 € por mês (proposta). A visão pode custar até 1,73 € sem dar prejuízo e custa cerca de 0,49 €; o preço testa-se no piloto (17, §9). |
| Quantas câmaras? Exterior? | Duas ou três dentro de casa e uma exterior opcional; cada câmara é um lugar e, com duas, a visão custa cerca de 0,98 € por casa e por mês (17, §8). |
| O que vos distingue? | Detetar “uma pessoa” não basta: o sistema reconhece as coisas desta família, e uma frase cria um sensor, tudo pela plataforma da Altice. Não se fazem afirmações sobre concorrentes sem fonte. |

## 13. Lista para o dia

O Filipe e os ensaios:
- Confirmar a abertura no primeiro ensaio (secção 3; por omissão, “a cena”).
- Três ensaios cronometrados de cada versão, em voz alta e com os filmes a passar, um deles filmado; uma ronda de perguntas difíceis feita por quem não conhece o projeto, com “o vídeo é real?” incluída.
- Um ensaio no equipamento da sala: projetor, som, resolução e a troca entre o _deck_ e o leitor de vídeo.
- Terminar até aos 2:50 no de 3 minutos e até aos 4:45 no de 5, porque a apresentação é interrompida no limite; o que não cabe corta-se no ensaio, não em palco.
- Decidir quem controla o portátil e quem cronometra.

Material:
- Os quatro filmes de `video/out/pitch/` no portátil e numa _pen_.
- O _deck_ em PDF e PPTX numa _pen_ e no Drive, se possível uma exportação por versão.
- As execuções sem montagem (`video/out/proof/`) abertas no portátil para as perguntas da final, mas só com o acordo das pessoas que nelas aparecem, ou com os rostos desfocados.
- Às 17h30, a entrega do sumário executivo, da apresentação (PPT) e da ligação ao repositório. Antes de entregar a ligação, confirmar que o júri tem acesso ao repositório e rever `sources/`, como pede o README (“Before sharing this repo”).
- Acordo de todas as pessoas que aparecem nos filmes, ou rostos desfocados (regra 6 do AGENTS.md).

Portátil:
- Bateria carregada, carregador e adaptador para a ligação ao projetor.
- Modo “Não incomodar”, notificações desligadas e outras aplicações fechadas, e nenhum terminal ou ficheiro `.env` à vista (regra 2 do AGENTS.md).
- Nenhum _render_ nem outro trabalho pesado durante as rondas (regra 5 do AGENTS.md).
- Se houver demonstração ao vivo, a instalação da secção 11.2.

Fontes do guia de _pitch_: Y Combinator, _Guide to Demo Day Pitches_ e _How to Pitch Your Company_; Paul Graham, _How to Convince Investors_; AngelHack, dicas para demonstrações em _hackathons_; Duarte, _The Glance Test_; Guy Kawasaki, regra 10/20/30; Wharton Communication Program, _Handling Q&A_; VirtualSpeech, ritmo médio de fala (138 palavras por minuto). Consultadas a 18 de novembro de 2026. Fontes internas: documentos 14, 16, 17, 23 e 24; `video/out/pitch/` (versões de 19 de novembro); os 107 testes, no registo da execução de `prototype/test_scenarios.py` (_commit_ f2351c2).
