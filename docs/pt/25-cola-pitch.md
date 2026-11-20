# Folha de apoio do _pitch_

Folha de uma página para o apresentador, para as rondas de 20 de novembro de 2026. O guião completo está no documento [21](21-pitch.md) e as respostas longas no documento [23](23-perguntas-engenharia.md). Ronda intermédia, a partir das 16h00: 3 min de _pitch_ e 2 min de perguntas (duas ou três). Final, a partir das 18h00: 5 min e 3 min. A mensagem de adoção dirige-se ao responsável da Altice pela plataforma que o _ThingTracker_ estende.

## Ordem e tempos

- 3 minutos, 9 diapositivos, alvo aos 2:40: capa · introdução · a casa ligada (`casa`) · vigiar (`vigiar`) · _ThingTracker_ (`reveal`) · basta uma imagem (`basta`) · o livro (filme de 20 s) · Altice (encaixa, 0,49 €, piloto) · fecho.
  - Alvo: `casa` aos 0:08, `vigiar` aos 0:28, `reveal` aos 0:48, `basta` aos 1:05, `livro` aos 1:25, `altice` aos 1:50, fecho aos 2:20.
- 5 minutos, 12 diapositivos: capa · introdução · `casa` · `vigiar` · `reveal` · `basta` · os olhos também se enganam (`ilusao`) · exemplos (os três filmes de 20 s, seguidos) · como funciona (com os modelos e as ferramentas) · viabilidade e replicação · começar (o piloto e o repositório) · fecho.
  - Alvo: acabar por volta dos 4:15, e nunca depois dos 4:45.
- Regra de corte (guião, secção 6): a frase antes dos filmes, os números e o fecho dizem-se palavra por palavra; o que não couber no alvo corta-se primeiro nas enumerações da abertura (`casa`, `reveal` e `basta`).
- O anexo de diagramas é um ficheiro à parte, só para as perguntas.

## Abertura e fecho

- Capa: passa-se logo, sem dizer nada.
- Introdução: “Boa tarde. Somos a equipa IT-Porto, do Instituto de Telecomunicações.”
- `casa`, logo a seguir à introdução: “Hoje, quase tudo em casa está ligado à internet: a fechadura da porta, o frigorífico, até a taça do cão. E isso já permite coisas muito úteis. Mas ainda falta uma peça. De todos estes aparelhos, há um que pode abrir uma realidade nova na casa inteligente. E é tão simples como uma câmara.”
- `vigiar`: “Há anos que a câmara serve sobretudo para segurança. Deteta movimento, as mais avançadas avisam de uma intrusão, e deixa-nos ver a casa à distância. Mas a visão vale muito mais. É o principal sentido do corpo humano: é com ela que percebemos o mundo. E foi por isso que criámos…” Cuidado, o júri inclui a Altice: dizer “até hoje a câmara serviu sobretudo para segurança”, nunca “a câmara da Altice só deteta movimento”.
- `reveal`: “…o _ThingTracker_. Uma câmara, ligada a todos os aparelhos da casa através do MCP da Altice. Funciona com os aparelhos do _kit_ que recebemos, e com todos os que vierem: o ar condicionado, os monitores de saúde, o frigorífico, qualquer máquina, o computador.”
- `basta`: “Com uma única imagem, o nosso cérebro percebe logo o que se passa: uma criança com uma cápsula de detergente na boca; alguém de faca na mão à porta, às quatro da manhã; o meu avô, que hoje ainda não tomou os comprimidos; a carteira que ficou em casa. A IA já faz o mesmo. E em certas situações faz melhor: não se cansa, não se distrai, e está atenta às quatro da manhã. Nós mostramos um destes casos, com modelos abertos, a correr num portátil.” Não dizer uma percentagem dos casos, porque não há fonte; dizer “quase todos estes casos já são possíveis hoje”.
- `ilusao`, só no de 5 minutos: “Um professor de visão por computador mostrou-nos imagens paradas que os nossos olhos veem a mexer. Os olhos humanos também se enganam. Uma câmara não se cansa e não se distrai.” Cuidado: há redes neuronais que também “veem” esta ilusão (Watanabe et al., _Frontiers in Psychology_, 2018); não dizer que a máquina nunca se engana.
- Fecho: “O _ThingTracker_ já reconhece objetos nas imagens da câmara do _kit_, custa à Altice cerca de 49 cêntimos por casa e por mês, e usa a app e o MCP que a Altice já tem. Propomos começar já pelo piloto.” Pausa. “A câmara da casa, atenta ao que importa.” Silêncio.

## Antes dos filmes

“Filmámos no nosso laboratório, com a câmara do _kit_ e o nosso protótipo; alguns momentos foram encenados.”

## Como se começa

“Um piloto em casas de colaboradores da MEO, com a câmara, a app e o MCP que já existem, e GPU alugadas, sem custo fixo.”

## A arquitetura em três frases

1. Na demonstração, um _MacBook_ faz de casa e de servidores da Altice: recebe o _stream_ real da câmara do _kit_, corre todos os modelos e lê os dispositivos do _kit_ pelo servidor MCP da Altice.
2. Na proposta, sem _hardware_ novo, o processador do _router_ trata do movimento, da zona que mudou e dos rostos, que são opcionais e cujos padrões nunca saem de casa; os servidores da Altice correm os modelos de visão (_OWLv2_ e _DINOv2_ em GPU _L4_), os motores de presença e de regras e o modelo de linguagem, só para texto.
3. Os modelos veem, o código decide (no _pitch_), e o modelo de linguagem só escreve (nas perguntas); quem está em casa sabe-se por três sinais: as câmaras, o sensor da porta e os telemóveis ligados ao Wi-Fi.

## Cinco números

| Número | O que é | Fonte |
|---|---|---|
| 0,49 € | Custo da visão por casa e por mês, com uma câmara, nos servidores da Altice, para 500 000 casas (estimativa) | Documento 17, §8 |
| 1,25 € | O que sobra por casa e por mês, num serviço de 3,99 €, depois de todos os custos | Documento 17, §9 |
| 68 de 68, mediana 0,93 | O livro reconhecido em todos os fotogramas da gravação do filme 1, para um limiar de 0,62 | Documento 24 |
| 107 de 107 | Os testes dos cenários do protótipo, todos a passar | `prototype/test_scenarios.py` (_commit_ f2351c2) |
| 100 a 140 M€ | O investimento inicial de uma caixa em cada casa, para 500 000 casas, que a proposta evita | Documento 17, §4 |

## O que é real

- Real: os ecrãs da app, gravados com o protótipo a funcionar, e as frases que se tornam cenários; a filmagem, da câmara do _kit_, no laboratório.
- Resultado dos modelos, calculado depois da filmagem: as caixas das pessoas e do livro.
- Encenado ou feito na montagem: o alarme, as notificações, as luzes e o ar condicionado a desligarem-se, a porta, o contador de pessoas e, no filme, a comparação de rostos.
- Provado sem montagem, com as mesmas gravações: o aviso do livro dispara pela regra; o membro da equipa registado, com consentimento, é reconhecido e o desconhecido não (alarme em 2 de 4 repetições; nas outras, o sistema pergunta); com a casa vazia, chega o aviso com os dois cartões.

## Dez perguntas

1. O vídeo é real? Um sistema real, com alguns momentos encenados; quando passamos a mesma gravação pelo sistema, sem montagem, é a regra que dispara o aviso do livro.
2. O que fez o portátil? Fez de casa, de servidores da Altice e de modelo de linguagem, tudo ao mesmo tempo.
3. É o modelo de linguagem que decide? Não: os modelos veem, decide um motor de regras, e o modelo de linguagem escreve a regra e as mensagens.
4. Como sabe que saí sem o livro? A porta fecha depois de sair alguém da família e a câmara verifica se o livro ficou; se não o vê, o resultado é “incerto”, sem alarme.
5. Quanto custa com 500 000 casas? Cerca de 0,49 € por casa e por mês; com imagens completas, 2,41 €; com uma caixa em cada casa, 6,55 a 8,64 €; com uma NPU no _router_, cerca de 0,36 €.
6. Privacidade e rostos? Na proposta, o vídeo não sai de casa; sai só a zona que mudou; os rostos são opcionais e exigem consentimento, os padrões faciais nunca saem de casa e o modelo de linguagem só recebe texto.
7. Falsos alarmes? Limiares, confirmações seguidas, a fotografia em cada aviso e a escolha da família entre perguntar e tocar logo o alarme; em casas reais, mede-se no piloto.
8. Quanto trabalho dá integrar? Um separador _Things_, um botão de assistente, cinco ferramentas MCP novas e o serviço; as ações usam as 18 ferramentas que já existem.
9. Como leram o sensor da porta sem o nosso _backend_? Pelo servidor MCP que a Altice deu às equipas, a cada 4 s, sem nunca alterar nada.
10. Replica-se? Basta uma câmara, uma app e uma interface como o MCP; em França, 39,01 % das pessoas usam dispositivos de casa conectada, contra 23,99 % em Portugal (Eurostat, 2024).
