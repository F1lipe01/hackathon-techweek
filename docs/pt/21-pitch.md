# _Pitch_ do _ThingTracker_

Versão de 19 de novembro de 2026, à noite, para as duas rondas de sexta-feira, 20 de novembro, que substitui a de 18 de novembro. Serve de guião para os diapositivos, para os ensaios e para as perguntas do júri. Os números vêm dos documentos [14](14-arquitetura.md) (arquitetura), [16](16-viabilidade-negocio.md) (viabilidade do negócio) e [17](17-custos-operador.md) (custos do operador), e tudo o que se diz sobre os filmes segue o documento [24](../24-what-is-real.md), que classifica cada momento de cada filme; nenhum número ou afirmação entra no _pitch_ sem estar nesses documentos. As respostas às perguntas técnicas estão no documento [23](23-perguntas-engenharia.md) e a folha de apoio de uma página no documento [25](25-cola-pitch.md).

## 1. Formato e critérios

| Ronda | Quando | Formato | Critérios (peso) |
|---|---|---|---|
| Intermédia | Sexta, 20 nov, à tarde; finalistas escolhidos entre as 16h30 e as 17h30 | 3 min de _pitch_ + 1 min de perguntas | Adequação ao desafio (25 %), facilidade de adoção pela Altice Labs (25 %), viabilidade e sustentabilidade (25 %), apresentação (25 %) |
| Final | Sexta, 18h00–19h30 | 5 min de _pitch_ + 3 min de perguntas | Adequação (20 %), adoção (20 %), viabilidade (20 %), replicação noutros territórios (20 %), apresentação (10 %), documentação (10 %) |

Fonte: normas do concurso, artigos 16.º e 18.º (resumidas em [01-event.md](../01-event.md)). Dois quintos da nota final (40 %) vêm da adoção pela Altice e da replicação, pelo que o _pitch_ tem de mostrar que a Altice consegue lançar o produto com o que já tem e dizer em voz alta as palavras dos critérios (“adoção”, “viabilidade”, “replicação”). A documentação vale 10 % da final e é julgada pelo que se entrega às 17h30 (sumário executivo, apresentação e ligação ao repositório), daí o diapositivo do repositório no _pitch_ de 5 minutos.

## 2. A mensagem numa frase

O _ThingTracker_ põe a câmara que a Altice já vende a perceber o que vê, e a avisar a família quando é preciso.

A frase técnica, dita por B nas duas versões, é “os modelos veem, o código decide, o modelo de linguagem só escreve”. Três provas sustentam a mensagem e são as três linhas do fecho: o reconhecimento já funciona na câmara do _kit_ (num teste no laboratório, o livro obteve 0,70 para um limiar de 0,62 e uma garrafa 0,10); a visão custa à Altice cerca de 0,49 € por casa e por mês; o produto usa a app e o MCP que a Altice já tem. O pedido é um piloto em casas de colaboradores da MEO, e a frase final, igual à da capa, é “A câmara da casa, atenta ao que importa.”

## 3. Os diapositivos

O _deck_ ([ThingTracker · Pitch](https://claude.ai/artifact/HrCc8JBAhjvCy1fcKEkyXp), privado até ser partilhado) tem hoje 18 diapositivos. Esta secção indica ao agente do _deck_ os que ficam, os que mudam, os que entram e a posição de cada um nas duas versões. Os filmes não passam dentro do _deck_: o diapositivo de cada filme é um cartão com o título e uma linha sobre o que foi encenado, e o filme passa em ecrã inteiro a partir do ficheiro local (secção 8). As notas de todos os diapositivos que ficam têm de ser atualizadas com os tempos e as frases das secções 5 e 6.

### 3.1 Lista e critérios

| Id | Diapositivo | Estado | 3 min | 5 min | Critério que ganha |
|---|---|---|---|---|---|
| `cover` | Capa: logótipo, Altice Labs, Instituto de Telecomunicações, equipa IT-Porto | Fica; notas atualizadas | 1 | 1 | Apresentação |
| `problema` | O problema: pequenas preocupações de todos os dias | Fica | 2 | 2 | Adequação |
| `ideia` | A ideia: ver, perceber, lembrar, agir | Fica | 3 | 3 | Adequação |
| `crianca` | Caso 1: a criança em perigo (conceito) | Fica só no de 3 min, com a marca “Conceito” visível, como a de `mae` | 4 | — | Adequação |
| `mae` | Caso 3: “A minha mãe já acordou?” (já funciona) | Fica só no de 3 min | 5 | — | Adequação, viabilidade |
| `filme-livro` | As coisas: o livro esquecido (filme) | Novo; substitui `exemplo` | 6 | 4 | Adequação, viabilidade, apresentação |
| `filme-desconhecido` | A segurança: uma pessoa desconhecida (filme) | Novo | — | 5 | Adequação, apresentação |
| `filme-casa-vazia` | A energia: ninguém em casa (filme) | Novo | — | 6 | Adequação, viabilidade |
| `modelos` | Modelos _open-source_ que permitem uso comercial | Novo | — | 7 | Viabilidade, adoção, replicação |
| `prototipo-proposta` | Os modelos veem, o código decide, o modelo de linguagem só escreve | Novo; substitui `arquitetura` e reaproveita o seu diagrama | 7 | 8 | Adoção, viabilidade |
| `custos` | Custos: 49 cêntimos por casa e por mês | Fica | 8 | 9 | Viabilidade |
| `replicacao` | Replicação noutros operadores e países | Fica | — | 10 | Replicação |
| `lancamento` | Lançamento em três passos, a terminar no pedido | Fica | — | 11 | Adoção, replicação |
| `repositorio` | Está tudo no repositório | Novo | — | 12 | Documentação |
| `equipa` | Equipa IT-Porto | Fica | — | 13 | Apresentação |
| `fecho` | Fecho: três pontos, o pedido e a frase final | Fica; créditos atualizados | 9 | 14 | Apresentação, adoção, viabilidade |
| `exemplo` | Exemplo real: o livro, com o vídeo 2 | Sai das duas versões | — | — | Substituído por `filme-livro` |
| `arquitetura` | Arquitetura: encaixa no que a Altice já tem | Sai das duas versões; reserva | — | — | O diagrama passa para `prototipo-proposta` |
| `privacidade` | A privacidade decide-se em casa | Sai do de 5 min; reserva | — | — | Resposta a perguntas sobre privacidade |
| `memoria` | A memória da casa: a linha do tempo (proposta), com o título mudado (antes “A casa lembra-se”) | Sai do de 5 min; reserva | — | — | Resposta a perguntas sobre a memória |
| `propoe` | Ninguém configura nada: a app propõe | Sai das duas versões; reserva | — | — | Resposta a perguntas sobre configuração |
| `gato` | Caso 2: o gato na bancada | Sai das duas versões; reserva | — | — | Resposta a perguntas sobre animais |
| `noite` | Caso 4: o que aconteceu esta noite (conceito) | Sai das duas versões | — | — | Sem lugar nas duas versões |
| `carteira` | Caso 5: a carteira esquecida | Sai das duas versões | — | — | Repete o filme do livro |

Ordem de cada versão:
- 3 minutos (9 diapositivos): `cover`, `problema`, `ideia`, `crianca`, `mae`, `filme-livro`, `prototipo-proposta`, `custos`, `fecho`.
- 5 minutos (14 diapositivos): `cover`, `problema`, `ideia`, `filme-livro`, `filme-desconhecido`, `filme-casa-vazia`, `modelos`, `prototipo-proposta`, `custos`, `replicacao`, `lancamento`, `repositorio`, `equipa`, `fecho`.
- Reserva, depois do fecho e fora das duas versões: `privacidade`, `arquitetura`, `memoria`, `propoe`, `gato`.

Para não saltar diapositivos em palco, sugere-se uma exportação por versão (PDF e PPTX). As alterações aos diapositivos que ficam são três. A capa recebe nas notas as novas versões e tempos. O fecho acrescenta aos créditos “Filmes: laboratório da equipa, com momentos encenados” e, em letra pequena, o endereço do repositório. Se a reserva `privacidade` for mostrada, o ponto dos 30 dias tem de aparecer como proposta.

### 3.2 Os diapositivos novos

`filme-livro`: “As coisas: o livro esquecido”.
- Cartão escuro com o título e uma linha: “Filmado no laboratório da equipa, com a câmara do _kit_ e o protótipo.”
- Em letra pequena, em baixo: “As caixas vêm dos nossos modelos, aplicados à gravação; o alarme e o aviso no telemóvel foram encenados.”
- Filme: no de 3 min, `ThingTracker - pitch - o livro (25 s).mp4`; no de 5 min, `ThingTracker - pitch - o livro (20 s).mp4`.
- Substitui `exemplo`, cuja frase “registado com 3 fotografias do telemóvel” já não corresponde ao filme: a caixa do livro resulta de uma assinatura visual feita com vistas da própria câmara, e as fotografias do telemóvel, sozinhas, dão apenas 0,23 com a câmara no teto (documento 24; documento 23, B1a).

`filme-desconhecido`: “A segurança: uma pessoa desconhecida”.
- Linha: “A família saiu de casa e entra uma pessoa que ninguém registou.”
- Em letra pequena: “Os rostos no registo e a comparação são ilustrativos; o alarme e a sugestão de ligar à polícia foram encenados.”
- Filme: `ThingTracker - pitch - pessoa desconhecida (20 s).mp4`, só no de 5 min.

`filme-casa-vazia`: “A energia: ninguém em casa”.
- Linha: “Quando sai a última pessoa, a app propõe desligar o que ficou ligado.”
- Em letra pequena: “As luzes e o ar condicionado foram desligados à mão; o contador de pessoas foi feito na montagem; a parte em que estão sentados passa a 4×.”
- Filme: `ThingTracker - pitch - ninguém em casa (20 s).mp4`, só no de 5 min.

`modelos`: “Modelos _open-source_ que permitem uso comercial”.

| Modelo | Licença | O que faz | Onde corre, na proposta |
|---|---|---|---|
| _OWLv2_ | Apache-2.0 | Encontra pessoas e coisas pelo nome | Servidores da Altice |
| _DINOv2_ | Apache-2.0 | Distingue a coisa da família pela assinatura visual | Servidores da Altice |
| _YuNet_ e _SFace_ | MIT e Apache-2.0 | Encontram e comparam rostos, só com consentimento | Em casa, no _router_ |
| _Qwen3-1.7B_ | Apache-2.0 | Transforma frases em regras e escreve as mensagens | Servidores da Altice |

- Uma linha a cinzento: “Opcional: um modelo de visão e linguagem, chamado raramente, para confirmar os casos duvidosos (modelo ainda por escolher).”
- Pé: “Os modelos veem; quem decide é o código.”

`prototipo-proposta`: “Os modelos veem, o código decide, o modelo de linguagem só escreve”.
- À esquerda, numa coluna estreita, “Na demonstração”: “Um _MacBook_ faz de casa e de servidores da Altice: recebe o _stream_ real da câmara do _kit_, corre todos os modelos, guarda os dados e lê os dispositivos do _kit_ pelo servidor MCP da Altice. Quem decide é código simples.”
- À direita, numa coluna larga marcada “Proposta”, o diagrama de `arquitetura`, atualizado:
  - em casa, no processador do _router_, sem _hardware_ novo: o movimento, a zona que mudou e os rostos, opcionais (os padrões faciais nunca saem de casa);
  - na Altice: os servidores de visão (_OWLv2_ e _DINOv2_ em GPU _L4_), o serviço _ThingTracker_ atrás de um balanceador de carga, com os motores de presença e de regras, a base de dados _PostgreSQL_ e o modelo de linguagem, só para texto;
  - o que já existe: a app, o servidor MCP e as notificações.
- Faixa em baixo: “Presença: câmaras, sensor da porta e telemóveis no Wi-Fi” e “Cerca de 0,49 € por casa e por mês”.

`repositorio`: “Está tudo no repositório”.
- Seis blocos:
  - código: o protótipo (servidor, agente da casa, app e modelo de texto local);
  - arquitetura: o documento 14, com 12 diagramas, em português e em inglês;
  - custos: os documentos 16 e 17 e os respetivos modelos de cálculo;
  - testes: os cenários de ponta a ponta (`prototype/test_scenarios.py`);
  - filmes: o que é real em cada um (documento 24) e as fontes da montagem;
  - execuções sem montagem: a ferramenta `video/tools/proof_run.py`.
- O endereço `github.com/F1lipe01/hackathon-techweek`, o mesmo da entrega das 17h30.
- Os vídeos não estão no _git_ (AGENTS.md); se a equipa os puser no Drive, acrescenta-se a ligação.

## 4. Quem fala

- A abre e fecha. No de 3 minutos diz a capa, o problema, a ideia e os dois casos; no de 5 minutos, a capa, o problema, a ideia, os três filmes, a equipa e o fecho. Escolhe-se pela clareza, não pela antiguidade.
- B explica como funciona e o que é real. No de 3 minutos apresenta o filme do livro, a passagem do protótipo à proposta e os custos; no de 5 minutos, os modelos e a passagem do protótipo à proposta. Responde às perguntas técnicas e à pergunta “o vídeo é real?”.
- C fala do negócio no de 5 minutos (custos, replicação, lançamento e repositório) e controla o portátil durante todo o de 3 minutos e, no de 5 minutos, enquanto A e B falam. Durante o bloco de C, o portátil fica com B.
- Cada passagem diz o nome de quem fala a seguir. Os marcadores [A], [B] e [C] são substituídos pelos nomes próprios (Filipe Peixoto, Simon Ranjith e Mushahid Hussain), numa atribuição que a equipa decide no primeiro ensaio de sexta. Memorizam-se as passagens e as frases fixas, não o texto todo.

## 5. _Pitch_ de 3 minutos

As contas fazem-se a 2 palavras por segundo, com os números contados como se dizem (“três e noventa e nove” são cinco palavras), e com 1 s para cada troca entre o _deck_ e o filme. O _pitch_ termina aos 2:45, com 5 s de folga até aos 2:50 e 15 s até ao corte. As contas são conservadoras: ao ritmo médio de fala (138 palavras por minuto), o texto encurta cerca de 15 s, mas não se conta com essa folga.

| Início | Fim | Diapositivo | Quem | Palavras | O que se diz |
|---|---|---|---|---|---|
| 0:00 | 0:11 | `cover` | A | 23 | “O _ThingTracker_ põe a câmara que a Altice já vende a perceber o que vê, e a avisar a família quando é preciso.” |
| 0:11 | 0:20 | `problema` | A | 18 | “Onde deixei as chaves? A criança está em segurança? A câmara que já está em casa pode responder.” |
| 0:20 | 0:31 | `ideia` | A | 21 | “Só analisa a imagem quando há movimento: reconhece a criança e o detergente, regista onde e quando e avisa os pais.” |
| 0:31 | 0:40 | `crianca` | A | 18 | “Um conceito: basta uma frase, ‘avisa-me se a criança estiver em perigo’. Perigo detetado, alarme acionado, pais avisados.” |
| 0:40 | 0:53 | `mae` | A | 26 | “A minha mãe já acordou? Sim. E se ninguém passar pela cozinha até ao meio-dia, a filha é avisada. O [B] mostra-vos o caso do livro.” |
| 0:53 | 1:07 | `filme-livro` | B | 28 | “Filmámos no laboratório, com a câmara do _kit_ e o nosso protótipo. As caixas vêm dos nossos modelos, aplicados à gravação; o alarme e o aviso foram encenados.” |
| 1:07 | 1:32 | Filme | — | — | `ThingTracker - pitch - o livro (25 s).mp4`, em ecrã inteiro |
| 1:33 | 1:58 | `prototipo-proposta` | B | 49 | “No protótipo, este portátil faz de casa e de servidores da Altice. Para a adoção, não é preciso _hardware_ novo: o _router_ trata do movimento e dos rostos, e a Altice trata da visão e das regras. Os modelos veem, o código decide, o modelo de linguagem só escreve.” |
| 1:58 | 2:15 | `custos` | B | 34 | “Viabilidade: cerca de 49 cêntimos por casa e por mês, para um serviço de 3,99 €. Uma caixa em cada casa custaria mais de 6 €. O [A] fecha.” |
| 2:15 | 2:45 | `fecho` | A | 56 | A frase de fecho (secção 7), uma pausa e a frase final. |

Pontos de controlo: o filme começa até aos 1:07, os custos até aos 2:00 e o fecho até aos 2:17. Se aos 0:40 houver atraso, A salta `mae` e diz logo “O [B] mostra-vos o caso do livro.”, o que poupa cerca de 10 s.

## 6. _Pitch_ de 5 minutos

As mesmas contas. O _pitch_ termina aos 4:40, com 5 s de folga até aos 4:45; ao ritmo médio de fala, o texto encurta cerca de 25 s, folga com que também não se conta. Os três filmes (20,5 s, 20,2 s e 19,5 s) substituem os cinco casos e o exemplo real; uns e outros nunca se mostram juntos.

| Início | Fim | Diapositivo | Quem | Palavras | O que se diz |
|---|---|---|---|---|---|
| 0:00 | 0:11 | `cover` | A | 23 | A frase de abertura, igual à do _pitch_ de 3 minutos. |
| 0:11 | 0:20 | `problema` | A | 18 | Igual ao _pitch_ de 3 minutos. |
| 0:20 | 0:31 | `ideia` | A | 21 | Igual ao _pitch_ de 3 minutos. |
| 0:31 | 0:59 | `filme-livro` | A | 55 | “Filmámos no nosso laboratório, com a câmara do _kit_ e o protótipo. As caixas das pessoas e do livro vêm dos nossos modelos, aplicados à gravação; alguns momentos, como o alarme e as luzes a apagarem-se, foram encenados. Se quiserem, mostramos-vos a gravação original a passar pelo sistema. Primeiro, o Filipe sai sem o livro.” |
| 0:59 | 1:20 | Filme | — | — | `ThingTracker - pitch - o livro (20 s).mp4` |
| 1:20 | 1:30 | `filme-desconhecido` | A | 19 | “Depois, a segurança: a família saiu e entra um desconhecido. O reconhecimento de rostos só se faz com consentimento.” |
| 1:30 | 1:51 | Filme | — | — | `ThingTracker - pitch - pessoa desconhecida (20 s).mp4` |
| 1:51 | 2:01 | `filme-casa-vazia` | A | 19 | “Por fim, a energia: quando já não está ninguém em casa, a app propõe desligar o que ficou ligado.” |
| 2:01 | 2:21 | Filme | — | — | `ThingTracker - pitch - ninguém em casa (20 s).mp4` |
| 2:22 | 2:25 | `filme-casa-vazia` | A | 5 | “O [B] explica como funciona.” |
| 2:25 | 2:45 | `modelos` | B | 40 | “Os modelos são _open-source_ e permitem uso comercial: o _OWLv2_ encontra pessoas e coisas, o _DINOv2_ reconhece as de cada família, o _YuNet_ e o _SFace_ tratam dos rostos e o _Qwen3_ escreve regras e mensagens.” |
| 2:45 | 3:12 | `prototipo-proposta` | B | 54 | A frase do _pitch_ de 3 minutos, mais “O [C] fala dos custos.” |
| 3:12 | 3:28 | `custos` | C | 31 | “Viabilidade: cerca de 49 cêntimos por casa e por mês, para um serviço de 3,99 €. Uma caixa em cada casa custaria mais de 6 €.” |
| 3:28 | 3:41 | `replicacao` | C | 26 | “Replicação: basta uma câmara, uma app e uma interface como o MCP; nada depende do mercado português. Serve outros operadores, residências de idosos e alojamento local.” |
| 3:41 | 3:54 | `lancamento` | C | 26 | “Adoção em três passos: um piloto com colaboradores da MEO, em GPU alugadas; depois, clientes a 3,99 €; por fim, _routers_ com IA.” |
| 3:54 | 4:05 | `repositorio` | C | 22 | “Está tudo no repositório: código, arquitetura com 12 diagramas, custos, testes e o que é real em cada filme. O [A] fecha.” |
| 4:05 | 4:10 | `equipa` | A | 9 | “Somos a equipa IT-Porto, do Instituto de Telecomunicações.” |
| 4:10 | 4:40 | `fecho` | A | 56 | A frase de fecho (secção 7), uma pausa e a frase final. |

Pontos de controlo: o primeiro filme começa até aos 1:00, o último acaba até aos 2:22 e os custos começam até aos 3:14. Se aos 2:25 houver atraso, B diz dos modelos só “Os modelos são _open-source_ e permitem uso comercial.” e A salta a equipa, o que poupa cerca de 15 s.

## 7. Frases fixas

- Abertura (A, nas duas versões): “O _ThingTracker_ põe a câmara que a Altice já vende a perceber o que vê, e a avisar a família quando é preciso.”
- Passagem de A para B no de 3 minutos, no fim de `mae`: “O [B] mostra-vos o caso do livro.”
- Antes do filme, no de 3 minutos (B): “Filmámos no laboratório, com a câmara do _kit_ e o nosso protótipo. As caixas vêm dos nossos modelos, aplicados à gravação; o alarme e o aviso foram encenados.”
- Antes dos filmes, no de 5 minutos (A): “Filmámos no nosso laboratório, com a câmara do _kit_ e o protótipo. As caixas das pessoas e do livro vêm dos nossos modelos, aplicados à gravação; alguns momentos, como o alarme e as luzes a apagarem-se, foram encenados. Se quiserem, mostramos-vos a gravação original a passar pelo sistema.”
- Passagem de A para B no de 5 minutos, depois do último filme: “O [B] explica como funciona.”
- A frase técnica (B, nas duas versões): “Os modelos veem, o código decide, o modelo de linguagem só escreve.”
- Passagem de B para A no de 3 minutos, no fim dos custos: “O [A] fecha.”
- Passagem de B para C no de 5 minutos: “O [C] fala dos custos.”
- C passa a A, no fim do repositório: “O [A] fecha.”
- A, na equipa: “Somos a equipa IT-Porto, do Instituto de Telecomunicações.”
- Fecho (A, nas duas versões): “O _ThingTracker_ já reconhece objetos nas imagens da câmara do _kit_, custa à Altice cerca de 49 cêntimos por casa e por mês, e usa a app e o MCP que a Altice já tem. Propomos começar com um piloto em casas de colaboradores da MEO.” Pausa. Última frase, palavra por palavra: “A câmara da casa, atenta ao que importa.” Depois, silêncio; nunca “alguma pergunta?”.

## 8. Os filmes

As quatro versões estão em `video/out/pitch/`, a 1080p, com música baixa. Cada filme começa depois de uma frase dita com o cartão no ecrã e passa sem narração; quem fala espera em silêncio até ao fim.

| Filme | Ficheiro | Duração | Onde passa | Frase antes | O que mostra | O que foi encenado (documento 24) |
|---|---|---|---|---|---|---|
| O livro | `ThingTracker - pitch - o livro (25 s).mp4` | 25,0 s | 3 min, aos 1:07 | A frase curta sobre o que foi encenado (secção 7) | As fotografias do livro; uma frase que se torna cenário; ele sai sem o livro e o alarme toca; a notificação e o aviso no telemóvel; volta para o buscar; “Desta vez, o alarme não tocou.” | O som do alarme, a notificação e “Desligar o alarme”; a porta aberta ou fechada foi deduzida da imagem na montagem |
| O livro | `ThingTracker - pitch - o livro (20 s).mp4` | 20,5 s | 5 min, aos 0:59 | A frase completa sobre o que foi encenado e “Primeiro, o Filipe sai sem o livro.” | O mesmo caso, mais curto | O mesmo |
| A pessoa desconhecida | `ThingTracker - pitch - pessoa desconhecida (20 s).mp4` | 20,2 s | 5 min, aos 1:30 | “Depois, a segurança: a família saiu e entra um desconhecido. O reconhecimento de rostos só se faz com consentimento.” | Segundo o documento 24, o registo do Filipe na app, o cenário sugerido, a entrada do Filipe e a de um desconhecido, e o alarme com a sugestão de chamar a polícia; a confirmar na versão de 20 s | A deteção do rosto no vídeo de registo não foi feita por um modelo; a comparação de rostos é ilustrativa e o filme di-lo; o alarme e a sugestão da polícia foram acrescentados na montagem |
| Ninguém em casa | `ThingTracker - pitch - ninguém em casa (20 s).mp4` | 19,5 s | 5 min, aos 2:01 | “Por fim, a energia: quando já não está ninguém em casa, a app propõe desligar o que ficou ligado.” | O cenário guardado; entram, acendem as luzes; sentados, a 4×, com o ar condicionado ligado; saem; o aviso com dois cartões e a sala a escurecer; a passagem ao ar condicionado; a porta fechada; “Ninguém em casa, nada ligado.” | As luzes e o ar condicionado foram desligados à mão; o contador de pessoas e a porta foram calculados na montagem; a caixa da tomada e a passagem a escuro foram feitas na montagem; o aviso foi disparado à mão, o desligar da tomada foi em simulação e o ar condicionado é simulado |

Como se passam (procedimento a ensaiar na sala):
- Os ficheiros ficam no portátil e numa _pen_, sem depender da rede.
- Antes de cada ronda, C abre no _QuickTime_ os filmes dessa versão, cada um numa janela já em ecrã inteiro e parada em 0:00, pela ordem inversa à de passagem, para que o primeiro fique à frente. O _deck_ fica em ecrã inteiro no navegador.
- À última palavra da frase antes do filme, C muda para o _QuickTime_ (Cmd-Tab) e carrega na barra de espaços; no fim, fecha a janela (Cmd-W), volta ao navegador (Cmd-Tab) e avança para o diapositivo seguinte. O rato não se mexe enquanto o filme passa, para os controlos não aparecerem.
- O volume da música acerta-se no ensaio da sala, baixo o bastante para não competir com a frase seguinte.

Se um filme não arrancar em 3 s, o cartão fica no ecrã e quem fala conta o caso numa frase:
- o livro: “No filme, o Filipe sai sem o livro; a porta fecha-se, a câmara confirma que o livro ficou na secretária e o telemóvel avisa-o.”
- a pessoa desconhecida: “No filme, com a família fora, entra uma pessoa que ninguém registou, e chega um aviso urgente, com a fotografia.”
- ninguém em casa: “No filme, sai a última pessoa e a app propõe desligar a luz e o ar condicionado, com um ‘Sim’ para cada um.”

## 9. “O vídeo é real?”

A resposta segue a decisão da equipa: um sistema real, com alguns momentos encenados. Nunca se diz que os filmes são inteiramente reais, nem que são falsos. Responde B.

Resposta curta, na ronda intermédia: “É um sistema real, com alguns momentos encenados: a filmagem é da câmara do _kit_, a app é o nosso protótipo e as caixas vêm dos nossos modelos, aplicados depois à gravação; o alarme e o aviso foram acrescentados para mostrar a experiência completa.”

Resposta completa, na final (cerca de 30 s): “É um sistema real, com alguns momentos encenados. A filmagem é da câmara do _kit_, no nosso laboratório; os ecrãs são o nosso protótipo, gravado a funcionar; as caixas das pessoas e do livro vêm dos nossos modelos, aplicados depois à gravação. O alarme, as notificações e as luzes a apagarem-se foram encenados; a comparação de rostos é ilustrativa, e a porta e o contador de pessoas foram calculados na montagem. Podemos mostrar-vos a mesma gravação a passar pelo sistema, sem montagem.”

O pormenor, só se for pedido:

| Filme | Real | Resultado dos modelos, calculado depois da filmagem | Feito na montagem, à mão ou encenado |
|---|---|---|---|
| O livro | Os ecrãs da app (as 8 fotografias, o nome, Guardar, a frase que se torna cenário); a saída e o regresso, numa única gravação contínua da câmara do _kit_ | A caixa “pessoa” (_OWLv2_); a caixa “livro” com a pontuação (_OWLv2_ e _DINOv2_), encontrada em 68 de 68 fotogramas, com mediana 0,93, comparada com uma assinatura feita com vistas da própria câmara noutra gravação | A porta aberta ou fechada, deduzida da imagem; o som do alarme, a notificação e “Desligar o alarme” |
| A pessoa desconhecida | Os ecrãs da app (adicionar pessoa, o vídeo do rosto, “Filipe adicionado”, Família, o cenário sugerido, “Cenário guardado”); a entrada do Filipe e a do desconhecido | Nenhum resultado de rostos: no registo, o servidor cortou 8 quadrados fixos | A comparação de rostos, ilustrativa; o alarme e a sugestão da polícia |
| Ninguém em casa | Duas frases que se tornam cenários (por padrões de palavras-chave); três pessoas entram, sentam-se e saem, com as luzes e o ar condicionado ligados | As caixas “pessoa” (_OWLv2_), ligadas em trajetos pela nossa ferramenta | Quatro gravações juntas, com o relógio reescrito com os dígitos da própria câmara e a parte sentada a 4×; o contador e a porta; as luzes e o ar condicionado desligados à mão; a caixa da tomada e a passagem a escuro; o aviso disparado à mão, a tomada em simulação e o ar condicionado simulado |

Perguntas que costumam seguir-se:
- “As fotografias do telemóvel chegam para reconhecer o livro?” Não, com a câmara no teto: dão uma primeira assinatura (0,23 na gravação do filme 1), e a app pergunta “é este o teu livro?” para juntar as vistas da própria câmara, até 8 (documento 23, B1a).
- “O sistema decide sozinho que o livro ficou?” Na arquitetura proposta, sim: a porta fecha-se depois de alguém sair e a câmara faz uma verificação ativa (documento 14, §8.1). No filme, o aviso foi disparado para a gravação; a mesma gravação, a passar pelo sistema, mostra a regra a decidir [a confirmar].
- “O _ThingTracker_ desligou mesmo as luzes?” No laboratório, as luzes e o ar condicionado não estão ligados a nenhum dispositivo do _kit_, por isso foram desligados à mão no momento do toque na app; numa casa, o comando segue pelo MCP para os aparelhos que a família tiver associado à app (documento 23, E3).
- “A comparação de rostos do filme é real?” Não: está marcada como ilustrativa; desde 19 de novembro, o agente da casa tem reconhecimento de rostos com _YuNet_ e _SFace_ (documento 14, §16), o que a mesma gravação, a passar pelo sistema, deve mostrar [a confirmar].

## 10. Demonstração

Durante o _pitch_ não há demonstração ao vivo: os filmes fazem esse papel. As provas mostram-se nas perguntas da final, e só se o júri as pedir; na ronda intermédia, com 1 minuto de perguntas, apenas se oferecem.

### 10.1 As execuções sem montagem

Estão a ser feitas na noite de 19 de novembro, com `video/tools/proof_run.py`. A gravação do laboratório faz de câmara e passa pelo sistema real (agente da casa, modelos, motor de presença e motor de regras), em tempo real e em resolução completa. Só a porta, os telemóveis e os dispositivos ligados à mão são reproduzidos, nos momentos em que aconteceram na gravação, e cada um aparece como “Replayed” na atividade; como os telemóveis não foram registados no laboratório, reproduzem-se nos momentos em que cada pessoa sai e entra. Tudo o resto é calculado no momento.

| Execução | Ficheiros | O que deve mostrar [a confirmar no registo antes do _pitch_] |
|---|---|---|
| O livro | `video/out/proof/book.mp4` e `book.log.txt` | A porta fecha-se depois de o Filipe sair e o telemóvel dele sai do Wi-Fi; a verificação ativa vê o livro na secretária e chega o aviso, com a prova (a porta, o telemóvel e a verificação da câmara); quando sai com o livro, o resultado é “incerto” e não há aviso |
| A pessoa desconhecida | `video/out/proof/face.mp4` e `face.log.txt` | O Filipe é reconhecido e não há alarme; um rosto desconhecido, visível em 3 análises seguidas com a família fora, dispara o aviso urgente com a sugestão do 112 |
| Ninguém em casa | `video/out/proof/nobody.mp4` e `nobody.log.txt` | A casa passa a VAZIA e chega um aviso com um cartão por dispositivo que ficou ligado |

Como se mostra, em 30 s no máximo: B abre o vídeo no momento do aviso, ou o registo na linha do aviso, e diz “É a mesma gravação a passar pelo sistema, sem montagem: a porta e o telemóvel são reproduzidos da gravação; a deteção, a presença e a regra são calculadas aqui.” O que cada execução mostrou fica registado na coluna “Tonight” do documento 24.

### 10.2 Ao vivo, só com o _kit_ instalado

Faz-se apenas se o _kit_ estiver instalado na sala e o ensaio no local correr bem duas vezes seguidas; caso contrário, ficam as execuções sem montagem.
- Instalação: a câmara do _kit_ virada para uma mesa com o livro, nunca para o público (regra 6 do AGENTS.md); o sensor de contacto numa porta ou na tampa de uma caixa; a sessão MCP iniciada nesse dia (o _token_ dura cerca de 24 h); os três processos arrancados por ordem (`llm_local.py`, `server.py`, `edge.py`), sem a variável `TT_LIVE_ACTIONS` (ações em simulação).
- Guião, em 30 s: o cenário “avisa-me se sair sem o livro” já criado; B abre o sensor, tira o telemóvel do Filipe do Wi-Fi na página (simulado, e diz-se) e fecha o sensor; o aviso chega à cópia da app em cerca de 10 s, porque o protótipo consulta a porta pelo MCP a cada 4 s (documento 23, A8).
- Se houver um telemóvel com a app da Altice, a app notifica a abertura da porta; é uma função que a Altice já tem, não do _ThingTracker_ (documento 23, E2).
- Nunca se liga ou desliga a tomada ou a lâmpada, nunca se toca no alarme e nunca se usam as ferramentas de escrita do MCP (regra 1 do AGENTS.md).
- A câmara chega ao portátil pelo _relay_ da organização, pelo que a demonstração depende da rede da sala.

## 11. Perguntas prováveis do júri

Cada resposta segue o mesmo padrão, em 25 s no máximo: uma frase de resposta, a prova, a limitação, dita com franqueza, e a ligação ao piloto. A passa as perguntas técnicas a B e as de negócio a C. As respostas completas, com as fontes, estão no documento 23.

| Pergunta | Quem | Resposta |
|---|---|---|
| O vídeo é real? | B | A resposta da secção 9. |
| O que fez o portátil na demonstração? | B | As três partes ao mesmo tempo: a casa, os servidores da Altice e o modelo de linguagem. Na proposta, o movimento e os rostos ficam no _router_ e a visão corre na Altice (23, A2). |
| É o modelo de linguagem que decide? | B | Não. Os modelos só veem, e quem decide é um motor de regras determinista. O modelo de linguagem transforma a frase em regra e escreve as mensagens; a regra é validada e mostrada ao utilizador em palavras simples (23, C4 e C5). |
| Como sabe que saí sem o livro? | B | Quando a porta se fecha depois de sair alguém da família, a câmara verifica se o livro ainda lá está; se não o vê, o resultado é “incerto” e não há alarme. O sinal de saída é o sensor da porta do _kit_, que só lemos, ou o telemóvel a sair do Wi-Fi (23, B4 e B4a). |
| Quanto custa com 500 000 casas? Porque não a nuvem ou uma caixa em cada casa? | C | Cerca de 0,49 € por casa e por mês, porque só se analisa quando há movimento e só sai a zona que mudou. Com imagens completas seriam 2,41 € nos servidores da Altice e 3,93 a 4,26 € em GPU alugadas na nuvem; uma caixa em cada casa exigiria 100 a 140 milhões de euros de investimento inicial. É uma estimativa da equipa com preços públicos, e o piloto mede o custo real (23, A3, A4 e F1). |
| E a privacidade? E os rostos? | B | Na proposta, o vídeo não sai de casa: sai só a zona que mudou, enquanto há movimento. Reconhecer rostos é opcional e exige consentimento explícito, porque são dados biométricos (RGPD, artigo 9.º), e os padrões faciais nunca saem de casa. O modelo de linguagem só recebe texto (23, B5, D2 e D4). |
| Falsos alarmes? | B | Limiares, confirmação em análises seguidas e a escolha da família, para cada perigo, entre perguntar primeiro e tocar logo; cada aviso traz a fotografia do momento. Em casas reais ainda não está medido, e é o piloto que o mede (23, B7 e G3). |
| Quanto trabalho dá integrar? | B | Um separador _Things_, um botão de assistente, quatro ferramentas MCP para as coisas, uma para a presença no Wi-Fi e o serviço. As ações usam as ferramentas que já existem (23, E1). |
| Como leram o sensor da porta sem acesso ao nosso _backend_? | B | Pelo servidor MCP que a Altice deu às equipas: o sensor é do nosso _kit_ de teste e lemos o estado a cada 4 s, sem nunca alterar nada. Nunca usámos as ferramentas de escrita (23, E1a). |
| Onde correm os modelos? E os _routers_? | B | No _router_, só o que é leve: o movimento, a zona que mudou e os rostos. A visão corre nos servidores da Altice. Se o _router_ tiver uma NPU capaz de correr um detetor, a visão passa para casa e o custo desce para cerca de 0,36 €; é a primeira pergunta para a Altice (14, §5.2). |
| Que licenças têm os modelos? | B | Todas abertas, e todas permitem uso comercial: _OWLv2_, _DINOv2_ e _Qwen3-1.7B_ com Apache-2.0, _YuNet_ com MIT e _SFace_ com Apache-2.0 (23, F2). |
| Replica-se noutros países? | C | Basta uma câmara, uma app e uma interface como o MCP; nada depende do mercado português. Em França, 39,01 % das pessoas usam dispositivos de casa conectada, contra 23,99 % em Portugal (Eurostat, 2024; documento 16). |
| Quem paga? | C | O cliente, 3,99 € por mês (proposta). A visão pode custar até 1,73 € sem dar prejuízo e custa cerca de 0,49 €; o preço testa-se no piloto (17, §9). |
| Quantas câmaras? Exterior? | B | Duas ou três dentro de casa e uma exterior opcional; cada câmara é um lugar e, com duas, a visão custa cerca de 0,98 € por casa e por mês (17, §8). |
| O que vos distingue? | A | Detetar “uma pessoa” não basta: o sistema reconhece as coisas desta família, e uma frase cria um sensor, tudo pela plataforma da Altice. Não se fazem afirmações sobre concorrentes sem fonte. |

## 12. Lista para o dia

Pessoas e ensaios:
- Atribuir A, B e C e pôr os nomes nas passagens.
- Três ensaios cronometrados de cada versão, em voz alta e com os filmes a passar, um deles filmado; uma ronda de perguntas difíceis feita por quem não conhece o projeto, com “o vídeo é real?” incluída.
- Um ensaio no equipamento da sala: projetor, som, resolução e a troca entre o _deck_ e o leitor de vídeo.
- Terminar até aos 2:50 no de 3 minutos e até aos 4:45 no de 5, porque o tempo é cortado; o que não cabe corta-se no ensaio, não em palco.
- Quem fala, quem controla o portátil, quem responde às perguntas técnicas (B) e quem responde às de negócio (C); A distribui.

Material:
- Os quatro filmes de `video/out/pitch/` no portátil e numa _pen_.
- O _deck_ em PDF e PPTX numa _pen_ e no Drive, se possível uma exportação por versão.
- As execuções sem montagem (`video/out/proof/`) abertas no portátil para as perguntas da final, com a coluna “Tonight” do documento 24 preenchida.
- Às 17h30, a entrega do sumário executivo, da apresentação (PPT) e da ligação ao repositório. Antes de entregar a ligação, confirmar que o júri lhe tem acesso e rever `sources/`, como pede o README (“Before sharing this repo”).
- Acordo de todas as pessoas que aparecem nos filmes, ou rostos desfocados (regra 6 do AGENTS.md).

Portátil:
- Bateria carregada, carregador e adaptador para a ligação ao projetor.
- Modo “Não incomodar”, notificações e outras aplicações fechadas, e nenhum terminal ou ficheiro `.env` à vista (regra 2 do AGENTS.md).
- Nenhum _render_ nem outro trabalho pesado durante as rondas (regra 5 do AGENTS.md).
- Se houver demonstração ao vivo, a instalação da secção 10.2.

Fontes do guia de _pitch_: Y Combinator, _Guide to Demo Day Pitches_ e _How to Pitch Your Company_; Paul Graham, _How to Convince Investors_; AngelHack, dicas para demonstrações em _hackathons_; Duarte, _The Glance Test_; Guy Kawasaki, regra 10/20/30; Wharton Communication Program, _Handling Q&A_; VirtualSpeech, ritmo médio de fala (138 palavras por minuto). Consultadas a 18 de novembro de 2026. Fontes internas: documentos 14, 16, 17, 23 e 24, e `video/out/pitch/` (versões de 19 de novembro).
