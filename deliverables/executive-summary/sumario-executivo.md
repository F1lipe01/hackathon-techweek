equipa: IT-Porto
desafio: #3 Connected Homes Reimagined: a IA ao serviço da casa

## Descrição do desafio

O desafio n.º 3, proposto pela Altice Labs, pede às equipas que repensem a casa conectada com inteligência artificial, através de serviços que tornem o dia a dia mais simples, útil ou seguro. A única condição técnica é a integração do servidor MCP (“_Model Context Protocol_”) da plataforma _Cognitive Home_, que permite a um agente de IA consultar e controlar os dispositivos de uma casa real. A ficha do desafio procura soluções que vão “para além dos comandos”, e os mentores sublinharam o potencial da câmara como fonte de dados.

## Estratégia

A câmara é o sensor mais versátil da casa, mas está hoje subaproveitada: no kit do desafio, limita-se a comunicar que detetou movimento. A estratégia da equipa consiste em transformar a câmara numa fonte de informação. Modelos de visão _open-source_, a funcionar em casa, reconhecem objetos e lugares, e só analisam imagens quando há movimento ou som; no resto do tempo, a câmara fica em repouso. Um modelo de linguagem, usado só quando necessário, converte frases em regras e responde a perguntas. Assim, uma única câmara substitui vários sensores específicos e cada utilizador cria os seus próprios sensores com uma frase. A proposta assenta em três princípios: a câmara como fonte de informação, e não só de vigilância; a integração no que já existe, através da aplicação e do servidor MCP da Altice; e a privacidade desde a conceção, com a análise feita em casa, sem vídeo guardado e com zonas excluídas pelo utilizador (artigo 25.º do RGPD).

O mercado nacional tem margem para crescer: em 2024, 23,99 % das pessoas em Portugal utilizaram um sistema de casa conectada, face a 33,04 % na União Europeia (Eurostat), e a MEO, que detém 40,9 % dos acessos de banda larga fixa (ANACOM), vende um kit de alarme sem câmara.

## Ideias para a proposta de solução

A solução proposta, o _ThingTracker_, transforma a câmara da casa num sensor universal, configurado em linguagem natural. O conceito resume-se a quatro verbos, ver, perceber, lembrar e agir, como mostra o exemplo da Figura 1.

[[figura: figura-exemplo | Um exemplo de utilização, da frase à ação]]

O mesmo princípio aplica-se a tudo o que o utilizador considere importante:

- Crianças: se uma criança trepar uma estante, a sirene toca e os pais recebem um aviso.
- Animais e plantas: “avisa-me se o gato não beber água até às 18h” ou “se a planta não for regada esta semana”.
- Pessoas idosas: se ninguém passar pela cozinha até ao meio-dia, um familiar recebe um aviso.
- Pessoas autorizadas e segurança: se entrar um desconhecido sem telemóveis da família em casa, o utilizador recebe uma fotografia e pode ativar o alarme; o reconhecimento dos familiares é opcional e exige o consentimento de cada um.
- Energia: a tomada inteligente desliga o aquecedor quando a casa fica vazia.

A Figura 2 mostra a arquitetura: os modelos de visão e a memória ficam em casa, a plataforma da Altice recebe um separador “_Things_” na aplicação e quatro novas ferramentas no servidor MCP, e um único serviço chama o modelo de linguagem.

[[figura: arquitetura | Arquitetura do _ThingTracker_: em casa, na plataforma Altice e no modelo de linguagem]]

Até ao momento, a equipa ligou-se ao MCP com um cliente próprio, que consulta os sete dispositivos do kit e comanda a tomada em cerca de um segundo, acedeu ao vídeo em direto da câmara e construiu um protótipo da aplicação com o novo separador, para uma demonstração no kit real a 20 de novembro.

## Ferramentas de IA

- Modelos de visão _open-source_, em casa: o _OWLv2_, o _DINOv2_, o _Depth Anything V2_ e o _ByteTrack_ detetam, identificam e seguem objetos e estimam a profundidade, com licenças de uso comercial livre (Apache-2.0 e MIT). Ocupam cerca de 0,8 GB e demoram 0,6 s por imagem num portátil.
- Modelo de linguagem, sob contrato: o _Claude_, da Anthropic, ou um modelo equivalente, desde que o contrato exclua o uso dos dados para treino e inclua um acordo de tratamento de dados, de preferência com servidores na UE.
- Custos por casa e por mês: o modelo de linguagem custa cerca de 0,43 €, com base no custo medido por pedido; a visão local consome menos de 0,15 € de eletricidade, para cerca de 2 horas de movimento por dia, a que acresce o equipamento onde corre.
- Desenvolvimento: a equipa recorreu ao _Claude Code_ (_Claude Opus 5.5_) na pesquisa, na programação e na redação; validou os resultados e confirmou os números nas fontes primárias.

Fontes: Eurostat, isoc_iiot_use (2024); ANACOM, serviços de acesso à internet em local fixo, 4.º trimestre de 2025; fichas dos modelos no _Hugging Face_; medições da equipa a 18/11/2026.
