# _Pitch_ do _ThingTracker_

Estado a 18 de novembro de 2026. Serve de guião para os diapositivos, para o ensaio e para as perguntas do júri. Os números vêm do relatório submetido, de [17-custos-operador.md](17-custos-operador.md) e de [18-casos-de-uso.md](18-casos-de-uso.md); nenhum número entra no _pitch_ sem fonte nesses documentos.

## 1. Formato e critérios

| Ronda | Quando | Formato | Critérios (peso) |
|---|---|---|---|
| Intermédia | Sexta, 20 nov, à tarde | 3 min de _pitch_ + 1 min de perguntas | Adequação ao desafio (25 %), facilidade de adoção pela Altice Labs (25 %), viabilidade e sustentabilidade (25 %), apresentação (25 %) |
| Final | Sexta, 18h00–19h30 | 5 min de _pitch_ + 3 min de perguntas | Adequação (20 %), adoção (20 %), viabilidade (20 %), replicação noutros territórios (20 %), apresentação (10 %), documentação (10 %) |

Fonte: normas do concurso, artigos 16.º e 18.º (resumidas em [01-event.md](../01-event.md)). Metade da nota final é adoção pela Altice e replicação: o _pitch_ tem de mostrar que a Altice consegue lançar isto com o que já tem.

## 2. A mensagem numa frase

A câmara que a Altice já vende passa a ser uma fonte de informação: percebe a casa, propõe o que vigiar e avisa a família quando é preciso, com a privacidade decidida em casa.

Três provas sustentam a frase: o reconhecimento real do livro na câmara do kit (0,70 para um limiar de 0,62), o custo para o operador (cerca de 0,49 € por casa e por mês) e a integração pelo MCP da plataforma.

## 3. Os diapositivos

O _deck_ ([ThingTracker · Pitch](https://claude.ai/artifact/HrCc8JBAhjvCy1fcKEkyXp), privado até ser partilhado) tem 17 diapositivos. As notas de cada um trazem o guião falado, o tempo e a versão em que entra.

| # | Diapositivo | 3 min | 5 min | Critério que ganha |
|---|---|---|---|---|
| 1 | Capa: a marca fecha-se sobre o nome | sim | sim | Apresentação |
| 2 | Hoje: “movimento detetado” contra o aviso do _ThingTracker_; o mercado | sim | sim | Adequação |
| 3 | A ideia em quatro verbos: ver, perceber, lembrar, agir | sim | sim | Adequação |
| 4 | A prova na câmara do kit (0,70), com o vídeo | sim (25 s) | sim (40 s) | Viabilidade, apresentação |
| 5 | Caso 1: a criança em perigo (conceito) | sim | sim | Adequação |
| 6 | Caso 2: o gato e a faca (conceito) | sim | sim | Adequação |
| 7 | Caso 3: a cozinha até ao meio-dia (funciona hoje) | sim | sim | Adequação, viabilidade |
| 8 | Caso 4: o que aconteceu às 4h (conceito) | sim | sim | Adequação |
| 9 | Caso 5: saíste sem o livro (ao vivo com o kit) | sim | sim | Viabilidade |
| 10 | A casa lembra-se: a linha do tempo (proposta) | opcional | sim | Adequação |
| 11 | Ninguém configura nada: a app propõe | sim | sim | Adoção |
| 12 | Arquitetura: encaixa no que a Altice já tem | sim | sim | Adoção, viabilidade |
| 13 | A privacidade decide-se em casa | não | sim | Adoção |
| 14 | Custos para a Altice: 49 cêntimos por casa e por mês | sim | sim | Viabilidade |
| 15 | Replicação noutros operadores e contextos | não | sim | Replicação |
| 16 | Lançamento em três passos | não | sim | Adoção, replicação |
| 17 | Fecho | sim | sim | Apresentação |

Na versão de 3 minutos, as cinco cenas passam a cerca de 6 s cada: o júri vê o caso e o aviso, e o orador diz uma frase.

## 4. Pontos de cada bloco

- Abertura e problema (1–2): “Há uma criança na cozinha e um armário aberto com detergente. A câmara da casa vê tudo, mas hoje só sabe dizer que houve movimento.” Depois, os números do mercado.
- Ideia e prova (3–4): regista-se uma _thing_, a câmara reconhece-a, a casa lembra-se e avisa. A prova: três fotografias do telemóvel bastaram para o livro ser reconhecido na câmara do kit com 0,70, acima do limiar de 0,62; uma garrafa ao lado fica em 0,10.
- Casos (5–9): dizer “junto a”, nunca “na boca”. A faca é conceito: nenhuma caixa de faca é real. A cozinha até ao meio-dia e o livro funcionam hoje.
- Memória e propostas (10–11): a mesma memória que encontra as coisas conta o que aconteceu; o cliente não escreve regras, aceita propostas com um toque.
- Adoção, privacidade, custos (12–14): câmara do kit, app com um separador novo, servidor MCP; só a zona que mudou sai de casa; cerca de 0,49 € por casa e por mês, para um serviço de 3,99 €.
- Replicação e lançamento (15–16): só precisa de uma câmara, da app e de uma interface como o MCP; piloto com colaboradores da MEO, clientes que aderem, _routers_ com IA. Ressalva: ainda nada demonstra que os _routers_ atuais tenham capacidade de IA.

## 5. Demonstração

- Preferência: vídeo, porque não falha. O exemplo real (vídeo 2) na ronda intermédia; o vídeo do produto (vídeo 1, cortado a 40 s) na final.
- Ao vivo, só se a sala o permitir e o teste de quinta correr bem: o livro na secretária, a porta abre e a luz fica vermelha. Com plano B: o vídeo do mesmo teste.
- Sem pessoas reconhecíveis em imagens do laboratório sem o acordo delas.

## 6. Perguntas prováveis do júri

| Pergunta | Resposta curta |
|---|---|
| Quanto custa à Altice? | Cerca de 0,49 € por casa e por mês na via híbrida (estimativa para 500 000 casas, 2 h de movimento por dia); 2,41 € se analisasse imagens completas. |
| E a privacidade? | A análise começa em casa, só com movimento; só a zona alterada sai; pessoas só com consentimento; o cliente escolhe as câmaras; o modelo de linguagem não vê imagens. |
| Funciona mesmo? | Sim, no protótipo: o livro reconhecido a 0,70 na câmara do kit, com um objeto de controlo a 0,10. A fiabilidade em produção mede-se num piloto. |
| E se houver falsos alarmes? | Cada aviso traz a fotografia do momento; ações fortes, como a sirene, pedem sempre um “sim”. |
| Porque não fazer tudo na nuvem? | Custa cerca de 4 € por casa e por mês com GPU alugadas a pedido e envia imagens para fora; a via híbrida é mais barata e mais privada. |
| Quantas câmaras por casa? | Duas ou três dentro (cozinha, sala, entrada) e uma exterior opcional. |
| O que muda na app da Altice? | Um quinto separador, _Things_, e um assistente em todos os separadores; o resto mantém-se. |
| Como se replica noutro país? | Precisa da câmara, da app e de uma interface de controlo como o MCP; nenhum dado é específico de Portugal. |

## 7. Lista para o dia

- Diapositivos em PDF e PPTX numa _pen_ e no Drive.
- Vídeos em ficheiro local (1080p), sem depender da rede.
- Ensaio cronometrado: 3 min e 5 min, em voz alta.
- Quem fala, quem responde a perguntas técnicas, quem a perguntas de negócio.
