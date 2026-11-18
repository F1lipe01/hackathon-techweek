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

## 3. _Pitch_ de 3 minutos (ronda intermédia)

Cerca de 330 palavras faladas, mais 25 s de vídeo. Uma pessoa fala; outra controla o vídeo.

| # | Diapositivo | Tempo | Critério que ganha |
|---|---|---|---|
| 1 | Abertura: “Onde está a criança agora?” | 0:00–0:15 | Apresentação |
| 2 | O problema: a câmara só deteta movimento | 0:15–0:35 | Adequação |
| 3 | A solução: ver, perceber, lembrar e agir | 0:35–1:05 | Adequação |
| 4 | Vídeo: o exemplo real (25 s) | 1:05–1:30 | Viabilidade, apresentação |
| 5 | A app propõe: 5 casos de segurança e cuidado | 1:30–2:05 | Adequação, adoção |
| 6 | Como encaixa na Altice: arquitetura e MCP | 2:05–2:30 | Adoção, viabilidade |
| 7 | Custo e negócio | 2:30–2:50 | Viabilidade |
| 8 | Fecho | 2:50–3:00 | Apresentação |

Guião falado:

1. “Há uma criança na cozinha e um armário aberto com detergente. A câmara da casa vê tudo, mas hoje só sabe dizer que houve movimento.”
2. “No kit do desafio, a câmara é o sensor mais versátil e o mais desaproveitado. Em Portugal, 24 % das pessoas usam casa conectada; na União Europeia, 33 %. Há espaço para crescer, e a MEO tem 40 % da banda larga fixa.”
3. “O _ThingTracker_ torna a câmara numa fonte de informação. Regista-se uma _thing_ (um livro, um animal, uma pessoa da família), a câmara reconhece-a, a casa lembra-se de onde a viu e age por frases simples: ‘avisa-me se a criança estiver em perigo’.”
4. Vídeo do exemplo real (25 s, sem narração). Depois: “Isto foi feito ontem, no laboratório, com a câmara do kit: três fotografias do livro bastaram para o reconhecer.”
5. “E o cliente não tem de configurar nada. A app percebe a casa e propõe: a criança com um detergente na boca, o gato junto a uma faca, o cão que não comeu, a avó que não passou pela cozinha até ao meio-dia, alguém no jardim às três da manhã. Um toque e fica ativo.”
6. “Encaixa no que a Altice já tem: a câmara do kit, a app com um novo separador e o servidor MCP. A deteção de movimento corre em casa e só a zona da imagem que mudou é analisada; nenhum vídeo sai de casa.”
7. “Para a Altice, custa cerca de 49 cêntimos por casa e por mês, para um serviço adicional de 3,99 €.”
8. “_ThingTracker_: a câmara que a casa já tem, agora a perceber o que importa.”

## 4. _Pitch_ de 5 minutos (final)

Cerca de 520 palavras faladas, mais 40 s de vídeo. Junta à versão de 3 minutos a replicação, a privacidade e o plano de lançamento.

| # | Diapositivo | Tempo | Critério |
|---|---|---|---|
| 1 | Abertura | 0:00–0:15 | Apresentação |
| 2 | O problema e o mercado | 0:15–0:40 | Adequação |
| 3 | A solução, com a Figura 1 do relatório | 0:40–1:15 | Adequação |
| 4 | Vídeo do produto (40 s) | 1:15–1:55 | Apresentação |
| 5 | A app propõe: os 5 casos | 1:55–2:35 | Adequação, adoção |
| 6 | O que já funciona: a prova real | 2:35–3:00 | Viabilidade |
| 7 | Arquitetura e privacidade | 3:00–3:35 | Adoção, viabilidade |
| 8 | Custos para o operador e negócio | 3:35–4:10 | Viabilidade |
| 9 | Replicação: outros territórios e contextos | 4:10–4:40 | Replicação |
| 10 | Lançamento em três passos e fecho | 4:40–5:00 | Adoção, apresentação |

Pontos de cada diapositivo novo:

- 6, o que já funciona: protótipo com _OWLv2_ e _DINOv2_ na câmara do kit; o livro reconhecido a 0,70 (garrafa de controlo a 0,10); assistente com modelo de linguagem local; regras que disparam ao abrir a porta; ligação ao MCP.
- 7, privacidade: o cliente escolhe onde ficam as câmaras (nunca quartos nem casas de banho); o reconhecimento de pessoas exige consentimento; só a zona alterada segue para a Altice; o modelo de linguagem só recebe texto.
- 9, replicação: o produto depende só de uma câmara, da app e de uma interface como o MCP, e não do mercado português; os modelos são _open-source_ e correm em casa ou num servidor do operador; serve outros operadores e outros contextos (residências de idosos, pequenos negócios, alojamento local). Dados de outros mercados só entram com fonte.
- 10, lançamento: piloto em casas de colaboradores da MEO, depois clientes que aderem, depois _routers_ com capacidade de IA.

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
