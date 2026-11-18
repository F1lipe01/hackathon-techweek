equipa: IT-Porto
desafio: #3 Connected Home, Reimagined: a IA ao serviço da casa

## Descrição do desafio

O desafio n.º 3, proposto pela Altice Labs, pede às equipas que repensem a casa conectada com inteligência artificial, através de serviços que tornem o dia a dia mais simples, útil ou seguro. A única condição técnica é a integração do servidor MCP (“_Model Context Protocol_”) da plataforma _Cognitive Home_, que permite a um agente de IA consultar e controlar os dispositivos de uma casa real. A ficha pede soluções “para além dos comandos” e os mentores sublinharam o potencial da câmara como fonte de dados.

## Estratégia

A câmara é o sensor mais versátil da casa, mas está hoje subaproveitada: no kit do desafio, limita-se a comunicar que detetou movimento. A estratégia da equipa consiste em transformar a câmara numa fonte de informação. Modelos de visão _open-source_, a funcionar em casa, reconhecem objetos e lugares e só analisam imagens quando há movimento ou som; no resto do tempo, a câmara fica em repouso. Um modelo de linguagem, usado só quando necessário, converte frases em regras e responde a perguntas. A proposta assenta em três princípios: a câmara como fonte de informação, e não só de vigilância; a integração na aplicação e no servidor MCP da Altice; e a privacidade desde a conceção (artigo 25.º do RGPD).

O mercado nacional tem margem para crescer: em 2024, 23,99 % das pessoas dos 16 aos 74 anos em Portugal usaram um sistema de casa conectada, face a 33,04 % na União Europeia (Eurostat), e a MEO, com 40,4 % dos acessos de banda larga fixa (ANACOM), vende um kit de alarme cuja câmara só tira fotografias quando há movimento.

## Ideias para a proposta de solução

A solução proposta, o _ThingTracker_, transforma a câmara da casa num sensor universal, configurado em linguagem natural. O conceito resume-se a quatro ações simples: ver, perceber/interpretar, lembrar/relacionar e agir, como mostra o exemplo da Figura 1.

[[figura: figura-exemplo | Do registo visual de um objeto à ação]]

Para registar um objeto, o utilizador indica o nome na aplicação e mostra-o à câmara durante alguns segundos. O nome em inglês (“_keys_”) serve de pesquisa ao detetor local e as imagens geram uma assinatura visual, guardada nos modelos locais e na base de dados da Altice do cliente. O utilizador pode então perguntar “onde estão as chaves?”; havendo mais do que umas, o sistema pergunta quais.

Uma frase como “avisa-me se sair de casa sem as chaves” segue para o Serviço _ThingTracker_, que a envia ao modelo de linguagem com os objetos registados e as ferramentas MCP disponíveis. O modelo devolve uma regra estruturada, gravada como cenário da plataforma através do MCP; a regra é avaliada em casa e as ações seguem pelo MCP. O mesmo princípio aplica-se a outros casos:

- Crianças: se uma criança trepar uma estante, a sirene toca e os pais recebem um aviso.
- Animais e plantas: “avisa-me se o gato não beber água até às 18h”.
- Pessoas idosas: se ninguém passar na cozinha até ao meio-dia, um familiar é avisado.
- Pessoas autorizadas e segurança: se entrar um desconhecido sem telemóveis da família em casa, o utilizador recebe uma fotografia e pode ativar o alarme; o reconhecimento dos familiares é opcional e exige consentimento.
- Energia: se a câmara não vir ninguém em 30 minutos, a tomada inteligente desliga o aquecedor.

O sistema também propõe cenários a partir do perfil da casa: se a câmara detetar crianças, sugere, por exemplo, “avisa-me se as crianças estiverem a fazer algo errado, algo que as possa magoar ou a agir de forma estranha”; se detetar um cão, sugere cenários para o animal. O utilizador aceita as propostas ou cria as suas. A Figura 2 mostra a arquitetura completa.

[[figura: arquitetura | Arquitetura do _ThingTracker_: em casa, na plataforma Altice e no modelo de linguagem]]

Até ao momento, a equipa ligou-se ao MCP, acedeu ao vídeo em direto da câmara do kit e construiu um protótipo que deteta objetos, responde a perguntas e executa regras com essa câmara.

## Ferramentas de IA

- Modelos de visão _open-source_, em casa: _OWLv2_, _DINOv2_, _Depth Anything V2 Small_ e _ByteTrack_ (Apache-2.0 e MIT) ocupam 0,8 GB e analisam uma imagem em 0,6 s num portátil.
- Modelo de linguagem, sob contrato: o _Claude_, da Anthropic, ou equivalente, desde que o contrato exclua o treino com os dados e inclua um acordo de tratamento de dados.
- Custo mensal por casa, além do equipamento: cerca de 0,43 € no modelo de linguagem (medido por pedido) e menos de 0,15 € de eletricidade na visão local (2 h de movimento por dia).
- Desenvolvimento: _Claude Code_ (_Claude Opus 5.5_) na pesquisa, programação e redação.

Fontes: Eurostat (isoc_iiot_use, 2024); ANACOM (2.º trimestre de 2026); fichas dos modelos (_Hugging Face_); medições da equipa.
