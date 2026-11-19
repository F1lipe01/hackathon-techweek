# Folha de apoio do _pitch_

Uma página para quem apresenta, a 20 de novembro de 2026. O guião completo está no documento [21](21-pitch.md) e as respostas longas no documento [23](23-perguntas-engenharia.md).

## Abertura e fecho (A)

- Abertura: “O _ThingTracker_ põe a câmara que a Altice já vende a perceber o que vê, e a avisar a família quando é preciso.”
- Fecho: “O _ThingTracker_ já reconhece objetos nas imagens da câmara do _kit_, custa à Altice cerca de 49 cêntimos por casa e por mês, e usa a app e o MCP que a Altice já tem. Propomos começar com um piloto em casas de colaboradores da MEO.” Pausa. “A câmara da casa, atenta ao que importa.” Silêncio.

## A frase antes dos filmes

- 3 minutos (B): “Filmámos no laboratório, com a câmara do _kit_ e o nosso protótipo. As caixas vêm dos nossos modelos, aplicados à gravação; o alarme e o aviso foram encenados.”
- 5 minutos (A): “Filmámos no nosso laboratório, com a câmara do _kit_ e o protótipo. As caixas das pessoas e do livro vêm dos nossos modelos, aplicados à gravação; alguns momentos, como o alarme e as luzes a apagarem-se, foram encenados. Se quiserem, mostramos-vos a gravação original a passar pelo sistema.”

## A arquitetura em três frases (B)

1. Na demonstração, um _MacBook_ faz de casa e de servidores da Altice: recebe o _stream_ real da câmara do _kit_, corre todos os modelos e lê os dispositivos do _kit_ pelo servidor MCP da Altice.
2. Na proposta, sem _hardware_ novo, o processador do _router_ trata do movimento, da zona que mudou e dos rostos, que são opcionais e cujos padrões nunca saem de casa; os servidores da Altice correm os modelos de visão (_OWLv2_ e _DINOv2_ em GPU _L4_), a presença, as regras e o modelo de linguagem, só para texto.
3. Os modelos veem, o código decide e o modelo de linguagem só escreve; a presença resulta de três sinais: as câmaras, o sensor da porta e os telemóveis no Wi-Fi.

## Cinco números

| Número | O que é | Fonte |
|---|---|---|
| 0,49 € | Custo da visão por casa e por mês, com uma câmara, nos servidores da Altice, para 500 000 casas (estimativa) | Documento 17, §8 |
| 1,73 € | O máximo que a visão pode custar sem prejuízo, num serviço de 3,99 € por mês | Documento 17, §9 |
| 100 a 140 M€ | O _hardware_ de uma caixa em cada casa, para 500 000 casas | Documento 17, §4 |
| 0,70 para 0,62 | O livro na câmara do _kit_, num teste no laboratório, para o limiar de 0,62; uma garrafa obteve 0,10 | Documento 23, G3 |
| 68 de 68, mediana 0,93 | O livro encontrado e reconhecido em 68 de 68 fotogramas da gravação do filme 1, calculado depois da filmagem | Documento 24; documento 23, B1 |

## O que é real

- Real: os ecrãs da app, gravados com o protótipo a funcionar, e as frases que se tornam cenários.
- Filmagem real: a câmara do _kit_, no laboratório da equipa.
- Resultado dos modelos, calculado depois da filmagem: as caixas das pessoas e do livro.
- Feito na montagem, à mão ou encenado: o alarme, as notificações, as luzes e o ar condicionado a desligarem-se, a porta e o contador de pessoas, e os rostos (no registo, nenhum modelo procurou o rosto, e a comparação é ilustrativa).

## Dez perguntas

1. O vídeo é real? Um sistema real, com alguns momentos encenados; podemos mostrar a mesma gravação a passar pelo sistema, sem montagem.
2. O que fez o portátil? As três partes ao mesmo tempo: a casa, os servidores da Altice e o modelo de linguagem.
3. É o modelo de linguagem que decide? Não: os modelos veem, decide um motor de regras, e o modelo de linguagem escreve a regra e as mensagens.
4. Como sabe que saí sem o livro? A porta fecha depois de sair alguém da família e a câmara verifica se o livro ficou; se não o vê, o resultado é “incerto”, sem alarme.
5. Quanto custa com 500 000 casas? Cerca de 0,49 € por casa e por mês; com imagens completas, 2,41 €; com uma caixa em cada casa, 6,55 a 8,64 €; com uma NPU no _router_, cerca de 0,36 €.
6. Privacidade e rostos? Na proposta, o vídeo não sai de casa, só a zona que mudou; os rostos são opcionais e exigem consentimento, os padrões faciais nunca saem de casa e o modelo de linguagem só recebe texto.
7. Falsos alarmes? Limiares, confirmações seguidas, a fotografia em cada aviso e a escolha da família entre perguntar e tocar logo; em casas reais, mede-se no piloto.
8. Quanto trabalho dá integrar? Um separador _Things_, um botão de assistente, cinco ferramentas MCP novas e o serviço; as ações usam as 18 ferramentas que já existem.
9. Como leram o sensor da porta sem o nosso _backend_? Pelo servidor MCP que a Altice deu às equipas, a cada 4 s, sem nunca alterar nada.
10. Replica-se? Basta uma câmara, uma app e uma interface como o MCP; em França, 39,01 % das pessoas usam dispositivos de casa conectada, contra 23,99 % em Portugal (Eurostat, 2024).
