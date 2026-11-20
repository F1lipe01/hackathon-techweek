# Folha de apoio do _pitch_

Uma página para o Filipe, a 20 de novembro de 2026. O guião completo está no documento [21](21-pitch.md) e as respostas longas no documento [23](23-perguntas-engenharia.md). Ronda intermédia, a partir das 16h00: 3 min de _pitch_ e 2 min de perguntas (duas ou três). Final, a partir das 18h00: 5 min e 3 min. A mensagem de adoção dirige-se a Pedro Almeida, responsável da Altice pela plataforma que o _ThingTracker_ estende.

## Ordem e tempos

- 3 minutos, até aos 2:43: capa · hoje · possível · _ThingTracker_ · conceitos · filme do livro (25 s) · como funciona · custos · começar · fecho.
- 5 minutos, até aos 4:32: capa · hoje · possível · _ThingTracker_ · os três filmes (20 s cada) · como funciona · modelos · custos · replicação · começar · repositório · fecho.

## Abertura e fecho

- Capa: “Boa tarde. Somos a equipa IT-Porto, do Instituto de Telecomunicações.”
- Hoje, por omissão: “Hoje, a câmara de casa só grava. Uma criança pega numa cápsula de detergente, e o telemóvel diz apenas ‘movimento detetado’. E depois?”
- Hoje, em alternativa: “Onde deixaram as chaves esta manhã? A câmara de casa até as viu, mas só sabe gravar, e o telemóvel diz apenas ‘movimento detetado’. E depois?” (com esta, em “possível”, diz-se “a criança em perigo” em vez de “onde ficaram as chaves”)
- Possível: “Com IA, a câmara percebe o que vê: onde ficaram as chaves, quem entrou em casa, o que ficou ligado. Cada família cria os seus avisos, com uma frase.”
- _ThingTracker_: “Por isso criámos o _ThingTracker_: a câmara que a Altice já vende capta as imagens, a IA percebe-as e a família recebe o aviso.”
- Fecho: “O _ThingTracker_ já reconhece objetos nas imagens da câmara do _kit_, custa à Altice cerca de 49 cêntimos por casa e por mês, e usa a app e o MCP que a Altice já tem. Propomos começar já pelo piloto.” Pausa. “A câmara da casa, atenta ao que importa.” Silêncio.

## Antes do primeiro filme

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
- Provado sem montagem, com as mesmas gravações: o aviso do livro dispara pela regra; o Filipe é reconhecido e o desconhecido não (alarme em 2 de 4 repetições; nas outras, o sistema pergunta); com a casa vazia, chega o aviso com os dois cartões.

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
