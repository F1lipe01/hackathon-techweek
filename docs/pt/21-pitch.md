# _Pitch_ do _ThingTracker_

Versão de 20 de novembro de 2026, à tarde, para as duas rondas de hoje, com a nova abertura: primeiro a motivação, e o _ThingTracker_ só a meio. Substitui a versão da manhã. Serve de guião para os diapositivos, para os ensaios e para as perguntas do júri. O Filipe apresenta sozinho as duas versões e responde a todas as perguntas. O tom é positivo: o _pitch_ mostra como funciona, porque é bom, porque interessa à Altice e como se começa, e os limites e as ressalvas ficam para as perguntas, onde se tratam com franqueza (secções 10 a 12). Os números vêm dos documentos [14](14-arquitetura.md) (arquitetura), [16](16-viabilidade-negocio.md) (viabilidade do negócio) e [17](17-custos-operador.md) (custos do operador), e tudo o que se diz sobre os filmes segue o documento [24](../24-what-is-real.md), que classifica cada momento de cada filme; nenhum número ou afirmação entra no _pitch_ sem estar nesses documentos. As respostas às perguntas técnicas estão no documento [23](23-perguntas-engenharia.md) e a folha de apoio de uma página no documento [25](25-cola-pitch.md).

## 1. Formato e critérios

| Ronda | Quando | Formato | Critérios (peso) |
|---|---|---|---|
| Intermédia | Sexta, 20 nov, a partir das 16h00, perante os mentores e o júri do desafio; passam 3 finalistas por desafio | 3 min de _pitch_ + 2 min de perguntas | Enquadramento e resposta ao desafio (25 %), facilidade de adoção (25 %), viabilidade e sustentabilidade (25 %), apresentação da solução (25 %) |
| Final | Sexta, a partir das 18h00 | 5 min de _pitch_ + 3 min de perguntas | Enquadramento (20 %), adoção (20 %), viabilidade (20 %), possibilidade de replicação (20 %), apresentação (10 %), documentação (entregáveis) (10 %) |

Fonte: guia oficial dos participantes (Drive, lido a 20 de novembro), que prevalece sobre as normas resumidas em [01-event.md](../01-event.md). Dois quintos da nota final (40 %) vêm da adoção pela Altice e da replicação, pelo que o _pitch_ tem de mostrar que a Altice consegue lançar o produto com o que já tem e dizer em voz alta as palavras dos critérios (“adoção”, “viabilidade”, “replicação”). A documentação vale 10 % da final e é julgada pelo que se entrega às 17h30 (sumário executivo, apresentação e ligação ao repositório), daí o repositório no diapositivo `comecar` do _pitch_ de 5 minutos. A apresentação entrega-se em PPT (aceita-se PDF), pelo Google Drive, até às 17h30, e tem de “incluir menção de que ferramentas foram utilizadas”, o que o diapositivo `como-funciona` cumpre.

O júri:
- Pedro Almeida, responsável da Altice pela plataforma que o _ThingTracker_ estende (_Head of Media Delivery and Smart Home Platforms_): é a ele que se dirige a mensagem de adoção, ou seja, tudo assenta na câmara, na app, no MCP e na plataforma que a equipa dele já tem, e começa-se com um piloto;
- Duarte Raposo, investigador do Instituto de Telecomunicações: a arquitetura, os modelos e o repositório;
- Vítor Santos, da Universidade de Aveiro;
- um vereador da Câmara Municipal de Aveiro: o benefício para as famílias, em palavras simples, como a criança do diapositivo `basta`.

## 2. A mensagem numa frase

O _ThingTracker_ põe a câmara que a Altice já vende a perceber o que vê, e a avisar a família quando é preciso.

A frase técnica, dita nas duas versões, é “os modelos veem, o código decide”; nas perguntas, acrescenta-se “e o modelo de linguagem só escreve”. Três provas sustentam a mensagem e são as três linhas do fecho: o reconhecimento já funciona nas imagens da câmara do _kit_ (o livro foi reconhecido em 68 de 68 fotogramas, com mediana 0,93, para um limiar de 0,62); a visão custa à Altice cerca de 0,49 € por casa e por mês; o produto usa a app e o MCP que a Altice já tem. O pedido é começar já com um piloto em casas de colaboradores da MEO, e a frase final é “A câmara da casa, atenta ao que importa.”

## 3. A abertura

A abertura parte da motivação e só revela o _ThingTracker_ a meio. Depois da capa e da introdução, ocupa quatro diapositivos, de `casa` a `basta`, iguais nas duas versões; no de 5 minutos, acrescenta-se `ilusao`. A capa é a do modelo, tal como foi entregue, e passa-se logo; a introdução apresenta a equipa e deixa de nomear o _ThingTracker_ (os colegas estão a refazê-la). As frases e os avisos são os das notas do _deck_ (`PITCH_NOTES`, em `deliverables/deck/pptx/build_pptx.py`).

| Diapositivo | O que está no ecrã | O que se diz | Palavras |
|---|---|---|---|
| `capa` | A capa do modelo, sem texto da equipa | Nada: passa-se logo para a introdução. | 0 |
| `intro` | A equipa IT-Porto e os nomes, sem o nome do _ThingTracker_ | “Boa tarde. Somos a equipa IT-Porto, do Instituto de Telecomunicações.” | 10 |
| `casa` | “A casa já está toda ligada”: seis imagens (a porta, o frigorífico, a taça do cão, a luz, o ar condicionado e a câmara, a peça que falta, contornada a verde) | “Hoje, quase tudo em casa está ligado à internet: a fechadura da porta, o frigorífico, até a taça do cão. E isso já permite coisas muito úteis. Mas ainda falta uma peça. De todos estes aparelhos, há um que pode abrir uma realidade nova na casa inteligente. E é tão simples como uma câmara.” | 54 |
| `vigiar` | “Até hoje, a câmara serviu para vigiar”: à esquerda, uma vista de videovigilância, com “Movimento”, “Intrusão” e “Ver em direto”; à direita, um olho humano e “A visão é o sentido com que percebemos o mundo.” | “Há anos que a câmara serve sobretudo para segurança. Deteta movimento, as mais avançadas avisam de uma intrusão, e deixa-nos ver a casa à distância. Mas a visão vale muito mais. É o principal sentido do corpo humano: é com ela que percebemos o mundo. E foi por isso que criámos…” | 51 |
| `reveal` | Em fundo branco, o logótipo e “Uma câmara que percebe o que vê, ligada a toda a casa pelo MCP da Altice.”; a câmara do _kit_ no centro dos aparelhos do _kit_, ligados pelo MCP da Altice; em baixo, “A seguir”: ar condicionado, monitor de saúde, frigorífico, máquina de lavar e computador | “…o _ThingTracker_. Uma câmara, ligada a todos os aparelhos da casa através do MCP da Altice. Funciona com os aparelhos do _kit_ que recebemos, e com todos os que vierem: o ar condicionado, os monitores de saúde, o frigorífico, qualquer máquina, o computador.” | 43 |
| `basta` | “Basta uma imagem para perceber”: quatro imagens, “Criança em perigo” (a fotografia da equipa, com o rosto desfocado), “Faca à porta, às 4h”, “Comprimidos por tomar” e “Carteira esquecida” | “Com uma única imagem, o nosso cérebro percebe logo o que se passa: uma criança com uma cápsula de detergente na boca; alguém de faca na mão à porta, às quatro da manhã; o meu avô, que hoje ainda não tomou os comprimidos; a carteira que ficou em casa. A IA já faz o mesmo. E em certas situações faz melhor: não se cansa, não se distrai, e está atenta às quatro da manhã. Nós mostramos um destes casos, com modelos abertos, a correr num portátil.” | 86 |
| `ilusao` (só 5 min) | “Os olhos também se enganam”: uma imagem parada que os olhos veem a mexer, e “A câmara não se cansa, não se distrai e está atenta às 4 da manhã.” | “Um professor de visão por computador mostrou-nos imagens paradas que os nossos olhos veem a mexer. Os olhos humanos também se enganam. Uma câmara não se cansa e não se distrai.” | 31 |

Os avisos das notas:
- `vigiar`: cuidado, o júri inclui a Altice. Dizer “até hoje a câmara serviu sobretudo para segurança”, nunca “a câmara da Altice só deteta movimento”.
- `basta`: não dizer uma percentagem dos casos, porque não há fonte. Dizer “quase todos estes casos já são possíveis hoje”.
- `ilusao`: cuidado, há redes neuronais que também “veem” esta ilusão (Watanabe et al., _Frontiers in Psychology_, 2018). Não dizer que a máquina nunca se engana.

No de 5 minutos passam três filmes, mas `basta` diz “Nós mostramos um destes casos”; cabe à equipa decidir se ajusta a frase nessa versão.

## 4. Os diapositivos

O _deck_ ([ThingTracker · Pitch](https://claude.ai/artifact/HrCc8JBAhjvCy1fcKEkyXp), privado até ser partilhado) tem duas versões curtas, de 9 e de 12 diapositivos, e o anexo de diagramas fica num ficheiro à parte, só para as perguntas. Os filmes não passam dentro do _deck_: o diapositivo de cada filme é um cartão, e os filmes passam em ecrã inteiro a partir dos ficheiros locais (secção 9). As notas de todos os diapositivos têm um só orador, o Filipe, com as frases das secções 3, 6 e 7. As notas de `livro`, `altice`, `exemplos`, `como-funciona`, `viabilidade`, `comecar` e `fecho` ainda trazem os tempos do plano anterior (e, em `livro`, o filme de 25 s); valem os tempos das secções 6 e 7.

### 4.1 Lista e critérios

| Id | Diapositivo | 3 min | 5 min | Critério que ganha |
|---|---|---|---|---|
| `capa` | A capa do modelo, tal como foi entregue | 1 | 1 | Apresentação |
| `intro` | A equipa IT-Porto, do Instituto de Telecomunicações, e os nomes | 2 | 2 | Apresentação |
| `casa` (A) | “A casa já está toda ligada” | 3 | 3 | Enquadramento |
| `vigiar` (B) | “Até hoje, a câmara serviu para vigiar” | 4 | 4 | Enquadramento |
| `reveal` (C) | O _ThingTracker_: a câmara do _kit_ ligada aos aparelhos pelo MCP da Altice | 5 | 5 | Enquadramento, adoção |
| `basta` (D) | “Basta uma imagem para perceber” | 6 | 6 | Enquadramento |
| `ilusao` (E) | “Os olhos também se enganam” | — | 7 | Enquadramento |
| `livro` | O filme do livro, 20 s | 7 | — | Enquadramento, viabilidade, apresentação |
| `altice` | “Encaixa no que a Altice já tem” · “≈ 0,49 € por casa e por mês” · “Começa com um piloto” | 8 | — | Adoção, viabilidade |
| `exemplos` | Os três filmes de 20 s, seguidos: as coisas, a segurança e a energia | — | 8 | Enquadramento, viabilidade, apresentação |
| `como-funciona` | O protótipo e a proposta, mais “Modelos e ferramentas” (menção obrigatória) | — | 9 | Adoção, viabilidade, documentação |
| `viabilidade` | ≈ 0,49 € por casa e por mês, e a replicação | — | 10 | Viabilidade, replicação |
| `comecar` | O piloto e o repositório | — | 11 | Adoção, documentação |
| `fecho` | Três pontos, o pedido e a frase final | 9 | 12 | Apresentação, adoção, viabilidade |

Ordem de cada versão:
- 3 minutos (9 diapositivos): `capa`, `intro`, `casa`, `vigiar`, `reveal`, `basta`, `livro`, `altice`, `fecho`.
- 5 minutos (12 diapositivos): `capa`, `intro`, `casa`, `vigiar`, `reveal`, `basta`, `ilusao`, `exemplos`, `como-funciona`, `viabilidade`, `comecar`, `fecho`.
- O anexo de diagramas, num ficheiro à parte, só para as perguntas.

A apresentação entregue às 17h30 é a de 5 minutos, em que `como-funciona` menciona as ferramentas. Aos créditos, o fecho acrescenta três linhas: “Filmes: laboratório da equipa, com momentos encenados”; as ferramentas (os modelos, o servidor MCP da Altice e o _Claude Code_), para que também a versão de 3 minutos as mencione; e, em letra pequena, o endereço do repositório.

### 4.2 O conteúdo dos diapositivos

`casa` (A): o título e seis imagens em duas filas de três, cada uma com o nome numa etiqueta: a porta (uma fechadura inteligente), o frigorífico com ecrã, a taça do cão (um comedouro automático), a luz, o ar condicionado e a câmara, a peça que falta, contornada a verde. A equipa escolhe as fotografias.

`vigiar` (B): à esquerda, em 60 % da largura, uma vista de videovigilância (uma grelha de câmaras num monitor ou num telemóvel), com as etiquetas “Movimento”, “Intrusão” e “Ver em direto”; à direita, um olho humano em grande plano, com a legenda “A visão é o sentido com que percebemos o mundo.”

`reveal` (C), em fundo branco:
- à esquerda, o logótipo do _ThingTracker_ e “Uma câmara que percebe o que vê, ligada a toda a casa pelo MCP da Altice.”;
- à direita, “Hoje · _kit_ Altice”: a câmara do _kit_ ao centro, ligada aos aparelhos reais do _kit_ (temperatura, tomada, lâmpada, sensor da porta, central e fumo), com a etiqueta “MCP da Altice”;
- em baixo, “A seguir”: ar condicionado, monitor de saúde, frigorífico, máquina de lavar e computador.

`basta` (D): quatro imagens lado a lado, com legenda: “Criança em perigo” (a fotografia da equipa, com o rosto desfocado), “Faca à porta, às 4h”, “Comprimidos por tomar” e “Carteira esquecida”.

`ilusao` (E, só 5 min): à esquerda, uma imagem parada que os olhos veem a mexer, de domínio público, da Wikimedia Commons (as “Rotating Snakes” de Kitaoka precisam de autorização); à direita, em grande, “A câmara não se cansa, não se distrai e está atenta às 4 da manhã.”

`livro` (3 min): cartão com o título “As coisas: o livro esquecido”, a linha “Filmado no nosso laboratório, com a câmara do _kit_ e o nosso protótipo; alguns momentos foram encenados.” e, em letra pequena, “O livro reconhecido em 68 de 68 fotogramas, a 0,93 (limiar de 0,62).” Filme: `ThingTracker - pitch - o livro (20 s).mp4`.

`altice` (3 min): três blocos grandes.
- “Encaixa no que a Altice já tem”: a câmara, a app com o novo separador _Things_ e o MCP; o _router_ deteta o movimento e os servidores da Altice tratam da visão.
- “≈ 0,49 € por casa e por mês”: num serviço de 3,99 €, cerca de 1,25 € de margem.
- “Começa com um piloto”: casas de colaboradores da MEO, GPU alugadas, sem custo fixo.

`exemplos` (5 min): cartão com três títulos lado a lado (“As coisas”, “A segurança”, “A energia”) e a linha “Filmado no nosso laboratório, com a câmara do _kit_ e o nosso protótipo; alguns momentos foram encenados.” Filmes, seguidos: `ThingTracker - pitch - o livro (20 s).mp4`, `ThingTracker - pitch - pessoa desconhecida (20 s).mp4` e `ThingTracker - pitch - ninguém em casa (20 s).mp4`.

`como-funciona` (5 min): “Os modelos veem, o código decide”.
- À esquerda, “No protótipo”: “Um _MacBook_ faz de casa e de servidores da Altice: recebe o _stream_ real da câmara do _kit_, corre todos os modelos, guarda os dados e lê os dispositivos do _kit_ pelo servidor MCP da Altice.”
- Ao centro, “Proposta”: em casa, no processador do _router_, sem _hardware_ novo, o movimento, a zona da imagem que mudou e, se a família quiser, os rostos, cujos padrões faciais nunca saem de casa; na Altice, os servidores de visão (_OWLv2_ e _DINOv2_ em GPU _L4_), o serviço _ThingTracker_ com os motores de presença e de regras, e o modelo de linguagem, só para texto.
- À direita ou em baixo, “Modelos e ferramentas”, que o guia dos participantes exige; segue a secção “Ferramentas de IA” do sumário executivo e não nomeia os serviços de áudio ou de música usados nos filmes:

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

`viabilidade` (5 min): “≈ 0,49 € por casa e por mês”, em grande, com “num serviço de 3,99 €, cerca de 1,25 € de margem”; por baixo, a replicação: uma câmara, uma app e uma interface como o MCP, para outros operadores, outros países, lares de idosos e alojamento local.

`comecar` (5 min): “Começa com um piloto”: casas de colaboradores da MEO, com a câmara do _kit_ e o MCP que já existem, e a app com o novo separador _Things_; GPU alugadas, sem custo fixo; depois, os clientes, a 3,99 € por mês. Por baixo, “Está tudo no repositório”: o código, 12 diagramas de arquitetura, os custos e 107 testes, todos a passar; o endereço `github.com/F1lipe01/hackathon-techweek`, o mesmo da entrega das 17h30.

### 4.3 A qualidade dos diapositivos

O líder da equipa quer diapositivos de grande qualidade. Para o agente do _deck_:
- uma ideia por diapositivo, que se perceba em 3 segundos, com poucas palavras no ecrã, porque o Filipe diz o resto;
- imagens reais e grandes, com as caixas dos modelos onde forem reais, e o mesmo estilo nos cartões dos filmes;
- a palavra do critério visível, em pequeno, no canto (“Adoção pela Altice”, “Viabilidade”, “Replicação”);
- números grandes e com unidade (0,49 €, 68 de 68, 107 testes);
- nenhum diapositivo com avisos, limites ou “a confirmar”: esse conteúdo fica na reserva e no documento 23.

## 5. Quem apresenta

- O Filipe apresenta tudo, nas duas versões, e responde a todas as perguntas. Fala na primeira pessoa do plural (“filmámos”, “propomos”).
- Sugere-se que um colega controle o portátil e os filmes, para o Filipe falar sem se virar para o ecrã, e que o outro cronometre e mostre os pontos de controlo das secções 6 e 7.

## 6. _Pitch_ de 3 minutos

As contas fazem-se a 2 palavras por segundo, com os números contados como se dizem (“três e noventa e nove” são cinco palavras), e com 1 s para cada troca entre o _deck_ e o filme. A coluna “Alvo” tem os tempos pedidos para terminar por volta dos 2:40, com folga até aos 2:45; a coluna seguinte, os tempos que as frases atuais dão a esse ritmo.

| Diapositivo | Alvo | A 2 palavras por segundo | Palavras | O que se diz |
|---|---|---|---|---|
| `capa` e `intro` | 0:00–0:08 | 0:00–0:08 | 10 | “Boa tarde. Somos a equipa IT-Porto, do Instituto de Telecomunicações.” |
| `casa` | 0:08–0:28 | 0:08–0:35 | 54 | A frase da secção 3. |
| `vigiar` | 0:28–0:48 | 0:35–1:01 | 51 | A frase da secção 3. |
| `reveal` | 0:48–1:05 | 1:01–1:22 | 43 | A frase da secção 3. |
| `basta` | 1:05–1:25 | 1:22–2:05 | 86 | A frase da secção 3. |
| `livro` | 1:25–1:50, com o filme | 2:05–2:14 | 17 | “Filmámos no nosso laboratório, com a câmara do _kit_ e o nosso protótipo; alguns momentos foram encenados.” |
| Filme | | 2:15–2:35 | — | `ThingTracker - pitch - o livro (20 s).mp4`, em ecrã inteiro |
| `altice` | 1:50–2:20 | 2:36–3:17 | 84 | “Encaixa no que a Altice já tem: a câmara, a app e o MCP. A adoção não exige _hardware_ novo: o _router_ deteta o movimento e os servidores da Altice tratam da visão. Os modelos veem, o código decide. Viabilidade: uns 49 cêntimos por casa e por mês; num serviço de 3,99 €, ficam uns 1,25 € de margem. E começa com um piloto em casas de colaboradores da MEO, em GPU alugadas, sem custo fixo.” |
| `fecho` | 2:20–2:40 | 3:17–3:44 | 50 | A frase de fecho (secção 8), uma pausa e a frase final. |

Atenção: com as frases atuais, o _pitch_ de 3 minutos acaba por volta dos 3:44, 64 s depois do alvo e 44 s depois do limite, onde a apresentação é interrompida. Só de `casa` a `basta` são 234 palavras, cerca de 1:57, contra 1:17 no alvo, o que obrigaria a falar a cerca de 3 palavras por segundo; e o segmento `livro`, com a frase, as duas trocas e o filme de 20,5 s, ocupa 31 s, contra 25 s no alvo. Para chegar aos 2:40, é preciso cortar cerca de 130 palavras; os cortes são uma decisão da equipa, a tomar antes do primeiro ensaio.

Pontos de controlo, segundo o alvo: `livro` começa até aos 1:25, `altice` até aos 1:50 e o fecho até aos 2:20.

## 7. _Pitch_ de 5 minutos

As mesmas contas. A nova abertura, de `capa` a `ilusao`, dura 2:21, contra 0:43 na anterior, e o resto do _pitch_ passa 1:38 para a frente.

| Início | Fim | Diapositivo | Palavras | O que se diz |
|---|---|---|---|---|
| 0:00 | 0:08 | `capa` e `intro` | 10 | “Boa tarde. Somos a equipa IT-Porto, do Instituto de Telecomunicações.” |
| 0:08 | 0:35 | `casa` | 54 | A frase da secção 3. |
| 0:35 | 1:01 | `vigiar` | 51 | A frase da secção 3. |
| 1:01 | 1:22 | `reveal` | 43 | A frase da secção 3. |
| 1:22 | 2:05 | `basta` | 86 | A frase da secção 3. |
| 2:05 | 2:21 | `ilusao` | 31 | A frase da secção 3. |
| 2:21 | 2:34 | `exemplos` | 26 | “Filmámos no nosso laboratório, com a câmara do _kit_ e o nosso protótipo; alguns momentos foram encenados. Três exemplos: as coisas, a segurança e a energia.” |
| 2:35 | 3:38 | Filmes | — | Os três filmes seguidos (20,5 s, 20,2 s e 19,5 s), sem nada dito entre eles |
| 3:38 | 4:16 | `como-funciona` | 77 | “No protótipo, este portátil faz de casa e de servidores da Altice. A adoção não exige _hardware_ novo: o _router_ deteta o movimento e os servidores da Altice tratam da visão, com modelos _open-source_ que permitem uso comercial. O _OWLv2_ encontra pessoas e coisas, o _DINOv2_ reconhece as coisas de cada família, o _YuNet_ e o _SFace_ tratam dos rostos e o _Qwen3_ escreve regras e mensagens. Os modelos veem, o código decide.” |
| 4:16 | 4:43 | `viabilidade` | 53 | “Viabilidade: uns 49 cêntimos por casa e por mês; num serviço de 3,99 €, ficam uns 1,25 € de margem. Para a replicação, basta uma câmara, uma app e uma interface como o MCP: serve outros operadores, outros países, lares de idosos e alojamento local.” |
| 4:43 | 5:11 | `comecar` | 57 | “Para começar: um piloto em casas de colaboradores da MEO, com a câmara, a app e o MCP que já existem, e GPU alugadas, sem custo fixo. Depois, os clientes, a 3,99 € por mês. E está tudo no repositório: o código, 12 diagramas de arquitetura e 107 testes, todos a passar.” |
| 5:11 | 5:38 | `fecho` | 50 | A frase de fecho (secção 8), uma pausa e a frase final. |

Atenção: com as frases atuais, o _pitch_ de 5 minutos acaba por volta dos 5:38, depois do limite dos 5:00, onde a apresentação é interrompida, e longe do alvo, por volta dos 4:15. Para ficar abaixo dos 4:30, é preciso cortar cerca de 70 s (umas 140 palavras); para chegar aos 4:15, cerca de 85 s. Os cortes são uma decisão da equipa, a tomar antes do primeiro ensaio.

Pontos de controlo, com as frases atuais: os filmes começam até aos 2:37 e `como-funciona` até aos 3:40; os seguintes dependem dos cortes.

## 8. Frases fixas

- A abertura: secção 3, de `casa` a `basta` nas duas versões e `ilusao` só no de 5 minutos; o _ThingTracker_ só é nomeado a partir de `reveal`.
- Antes dos filmes, nas duas versões: “Filmámos no nosso laboratório, com a câmara do _kit_ e o nosso protótipo; alguns momentos foram encenados.”
- A frase técnica, nas duas versões: “Os modelos veem, o código decide.” Nas perguntas, acrescenta-se “e o modelo de linguagem só escreve”.
- O primeiro passo: “um piloto em casas de colaboradores da MEO, (…) em GPU alugadas, sem custo fixo.”
- O fecho, nas duas versões: “O _ThingTracker_ já reconhece objetos nas imagens da câmara do _kit_, custa à Altice cerca de 49 cêntimos por casa e por mês, e usa a app e o MCP que a Altice já tem. Propomos começar já pelo piloto.” Pausa. Última frase, palavra por palavra: “A câmara da casa, atenta ao que importa.” Depois, silêncio; nunca “alguma pergunta?”.

O que não se diz no _pitch_, porque pertence às perguntas: “ainda não”, “não sabemos”, “a confirmar”, “simulado”, “em teste”, e qualquer referência ao que falta fazer.

## 9. Os filmes

As quatro versões estão em `video/out/pitch/`, a 1080p, com música baixa. No de 3 minutos passa só o filme do livro, na versão de 20 s, no diapositivo `livro`; no de 5 minutos passam os três filmes de 20 s, seguidos, no diapositivo `exemplos`. Os filmes passam sem narração, e o Filipe espera em silêncio até ao fim.

| Filme | Ficheiro | Duração | Onde passa | Frase antes | O que mostra | O que foi encenado (documento 24, para as perguntas) |
|---|---|---|---|---|---|---|
| O livro | `ThingTracker - pitch - o livro (25 s).mp4` | 25,0 s | Já não passa: fica de reserva | “Filmámos no nosso laboratório (…); alguns momentos foram encenados.” | As fotografias do livro; uma frase que se torna cenário; o Filipe sai sem o livro e o alarme toca; a notificação e o aviso no telemóvel; volta para o buscar; “Desta vez, o alarme não tocou.” | O som do alarme, a notificação e “Desligar o alarme”; a porta aberta ou fechada foi deduzida da imagem na montagem |
| O livro | `ThingTracker - pitch - o livro (20 s).mp4` | 20,5 s | 3 min, `livro` (no alvo, entre 1:25 e 1:50; aos 2:15 com as frases atuais); 5 min, `exemplos`, o primeiro, aos 2:35 | A mesma frase; no de 5 minutos, também “Três exemplos: as coisas, a segurança e a energia.” | O mesmo caso, mais curto | O mesmo |
| A pessoa desconhecida | `ThingTracker - pitch - pessoa desconhecida (20 s).mp4` | 20,2 s | 5 min, `exemplos`, o segundo, aos 2:56 | Nenhuma: passa logo a seguir ao primeiro | Segundo o documento 24, o registo do Filipe na app, o cenário sugerido, a entrada do Filipe e a de um desconhecido, e o alarme com a sugestão de chamar a polícia | No filme, a comparação de rostos é ilustrativa e está marcada como tal; o alarme e a sugestão da polícia foram acrescentados na montagem |
| Ninguém em casa | `ThingTracker - pitch - ninguém em casa (20 s).mp4` | 19,5 s | 5 min, `exemplos`, o terceiro, aos 3:17 | Nenhuma: passa logo a seguir ao segundo | O cenário guardado; entram, acendem as luzes; sentados, a 4×, com o ar condicionado ligado; saem; o aviso com dois cartões e a sala a escurecer; a passagem ao ar condicionado; a porta fechada; “Ninguém em casa, nada ligado.” | As luzes e o ar condicionado foram desligados à mão; o contador de pessoas e a porta foram calculados na montagem; a caixa da tomada e a passagem a escuro foram feitas na montagem; o aviso foi disparado à mão, o desligar da tomada foi em simulação e o ar condicionado é simulado |

Como se passam (procedimento a ensaiar na sala):
- Os ficheiros ficam no portátil e numa _pen_, sem depender da rede. Se houver um ficheiro com os três filmes de 20 s seguidos, usa-se esse no de 5 minutos.
- Antes de cada ronda, quem controla o portátil abre no _QuickTime_ os filmes dessa versão, cada um numa janela já em ecrã inteiro e parada em 0:00, pela ordem inversa à de passagem, para que o primeiro fique à frente. O _deck_ fica em ecrã inteiro no navegador.
- À última palavra da frase antes dos filmes, muda-se para o _QuickTime_ (Cmd-Tab) e carrega-se na barra de espaços. No fim de cada filme, fecha-se a janela (Cmd-W); no de 5 minutos, aparece logo o filme seguinte, e carrega-se outra vez na barra de espaços. Depois do último, volta-se ao navegador (Cmd-Tab) e avança-se para o diapositivo seguinte. O rato não se mexe enquanto os filmes passam, para os controlos não aparecerem.
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
- Antes do primeiro ensaio, decidir os cortes que fazem caber as duas versões (secções 6 e 7) e confirmar a nova abertura (secção 3).
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
