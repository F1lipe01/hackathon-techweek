equipa: IT-Porto
desafio: #3 Connected Home, Reimagined: a IA ao serviço da casa

## Descrição do desafio

O desafio n.º 3, proposto pela Altice Labs, pede às equipas que repensem a casa conectada com inteligência artificial, através de serviços que tornem o dia a dia mais simples, útil ou seguro. A única condição técnica é a integração do servidor MCP (“_Model Context Protocol_”) da plataforma _Cognitive Home_, que permite a um agente de IA consultar e controlar os dispositivos de uma casa real. A ficha pede soluções “para além dos comandos”.

## Estratégia

A câmara é o sensor mais versátil da casa, mas está hoje subaproveitada: no kit do desafio, limita-se a comunicar que detetou movimento. A estratégia da equipa consiste em transformar a câmara numa fonte de informação. Modelos de visão _open-source_, a funcionar em casa ou num servidor da Altice, reconhecem objetos e lugares e só analisam imagens quando há movimento ou som. Um modelo de linguagem, usado só quando necessário, converte frases em regras e responde a perguntas. A proposta assenta em três princípios: a câmara como fonte de informação, e não só de vigilância; a integração na aplicação e no servidor MCP da Altice; e a privacidade desde a conceção (artigo 25.º do RGPD).

O mercado nacional tem margem para crescer: em 2024, 23,99 % das pessoas dos 16 aos 74 anos em Portugal usaram um sistema de casa conectada, face a 33,04 % na União Europeia (Eurostat), e a MEO, com 40,4 % dos acessos de banda larga fixa (ANACOM), vende um kit de alarme cuja câmara só tira fotografias quando há movimento.

## Ideias para a proposta de solução

A solução proposta, o _ThingTracker_, transforma a câmara da casa num sensor universal, configurado em linguagem natural. O conceito resume-se a quatro ações simples: ver, perceber/interpretar, lembrar/relacionar e agir, como mostra o exemplo da Figura 1.

[[figura: figura-exemplo | Do registo visual de um objeto à ação]]

Para registar um objeto, o utilizador indica o nome na aplicação e mostra-o à câmara durante alguns segundos. O nome em inglês (“_book_”) serve de pesquisa ao detetor local e as imagens geram uma assinatura digital e visual da _thing_, guardada em casa e na base de dados da Altice. O utilizador pode então perguntar “onde está o livro?”; se houver dois, o sistema pergunta qual.

Uma frase como “avisa-me se sair de casa sem o livro” segue para o Serviço _ThingTracker_, que a envia ao modelo de linguagem com os objetos registados. O modelo devolve uma regra estruturada, gravada como cenário através do MCP e avaliada em casa; as ações seguem pelo MCP. O mesmo princípio aplica-se a outros casos:

- Crianças: se uma criança trepar uma estante, os pais são avisados e decidem se a sirene toca.
- Animais e plantas: “avisa-me se o gato não beber água até às 18h”.
- Pessoas idosas: se ninguém passar na cozinha até ao meio-dia, um familiar é avisado.
- Pessoas autorizadas e segurança: se entrar um desconhecido sem telemóveis da família em casa, o utilizador recebe uma fotografia e pode ativar o alarme; o reconhecimento dos familiares é opcional e exige consentimento.
- Energia: se a câmara não vir ninguém em 30 minutos, a tomada desliga o aquecedor.

O sistema também propõe cenários a partir do que a câmara aprende sobre a casa, sem que o utilizador os tenha de configurar: se vir um gato, sugere “avisa-me se o gato não for à taça da comida até às 20h”; se vir uma criança, “avisa-me quando chegar a casa”. O utilizador ativa-os com um toque ou cria os seus. A Figura 2 mostra a arquitetura completa.

[[figura: arquitetura | Arquitetura do _ThingTracker_: em casa, na plataforma Altice e no modelo de linguagem]]

Até ao momento, a equipa ligou-se ao MCP, acedeu ao vídeo em direto da câmara do kit e construiu um protótipo que deteta e reconhece objetos, responde a perguntas e executa regras. Num teste com o livro, oito vistas captadas com o telemóvel bastaram para o reconhecer na câmara do kit (semelhança de 0,70, para um limiar de 0,62).

## Ferramentas de IA

- Modelos de visão _open-source_: o protótipo usa o _OWLv2_ e o _DINOv2_ (Apache-2.0, 0,7 GB, cerca de 0,6 s por imagem num portátil); a solução final junta o _Depth Anything V2 Small_ e o _ByteTrack_. Podem correr em servidores da Altice ou no _router_, se tiver capacidade de IA.
- Modelo de linguagem, sob contrato: o _Claude_, da Anthropic, ou equivalente, desde que o contrato exclua o treino com os dados e inclua um acordo de tratamento de dados.
- Custo mensal para a Altice, por casa (estimativa: 500 000 casas, uma câmara, 2 h de movimento por dia): 0,43 € no modelo de linguagem e 0,49 € na visão, com a deteção de movimento em casa e só a zona alterada analisada em servidores da Altice (2,41 € com imagens completas; cerca de 4 € na nuvem).
- Desenvolvimento: _Claude Code_ (_Claude Opus 5.5_) na pesquisa, programação e redação.

Fontes: Eurostat (isoc_iiot_use, 2024); ANACOM (2.º trimestre de 2026); fichas dos modelos (_Hugging Face_); AWS, Azure e NVIDIA (18/11/2026); medições da equipa.
