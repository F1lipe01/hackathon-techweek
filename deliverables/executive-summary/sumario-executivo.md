equipa: IT-Porto
desafio: #3 Connected Homes Reimagined: a IA ao serviço da casa

## Descrição do desafio

O desafio n.º 3, proposto pela Altice Labs, pede às equipas que repensem a casa conectada com inteligência artificial, através de serviços que tornem o dia a dia mais simples, útil ou seguro. A única condição técnica é a integração do servidor MCP (Model Context Protocol) da plataforma Cognitive Home, que permite a um agente de IA consultar e controlar os dispositivos de uma casa real. A ficha do desafio procura soluções que vão «para além dos comandos» e que combinem contexto, intenção, informação e ação. Na sessão de abertura, os mentores sublinharam o potencial da câmara como fonte de dados.

## Estratégia

A câmara é o sensor mais versátil da casa, mas está hoje subaproveitada: no kit do desafio, limita-se a comunicar à plataforma que detetou movimento. A estratégia da equipa consiste em transformar a câmara numa fonte de informação. Modelos de visão _open-source_, a funcionar em casa, reconhecem objetos e lugares. Um modelo de linguagem, usado só quando necessário, converte frases em regras e responde a perguntas. Assim, uma única câmara substitui vários sensores específicos e cada utilizador cria os seus próprios sensores com uma frase. A proposta assenta em três princípios:

- **Informação, e não vigilância.** O sistema acompanha os objetos e as situações que o utilizador escolhe.
- **Integração no que já existe.** Um separador na aplicação da Altice, novas ferramentas no MCP e regras guardadas como cenários facilitam a adoção pela MEO e por outros operadores.
- **Privacidade desde a conceção.** A análise decorre em casa, cada imagem é apagada logo a seguir e não se guarda vídeo; o utilizador define as zonas excluídas (artigo 25.º do RGPD).

O mercado nacional tem margem para crescer. Em 2024, 23,99 % das pessoas em Portugal utilizaram um sistema de casa conectada, face a 33,04 % na União Europeia (Eurostat). A NOS e a Vodafone já vendem alarmes com câmara interior, com mensalidades de 42 € a 46 €, ao passo que a MEO, que detém 40,9 % dos acessos de banda larga fixa (ANACOM, 4.º trimestre de 2025), vende um kit de alarme sem câmara.

## Ideias para a proposta de solução

A solução proposta, o **ThingTracker**, transforma a câmara da casa num sensor universal, configurado em linguagem natural. O conceito resume-se a quatro verbos, **ver, perceber, lembrar e agir**, como mostra o exemplo seguinte.

[[figura: figura-exemplo]]

O mesmo princípio aplica-se a tudo o que o utilizador considere importante:

- **Crianças.** Se uma criança começar a trepar uma estante, a sirene toca, a luz fica vermelha e os pais recebem um aviso.
- **Animais e plantas.** «Avisa-me se o gato não beber água até às 18h» ou «diz-me se a planta não for regada esta semana».
- **Pessoas idosas.** Se a rotina habitual não se cumprir, por exemplo, se ninguém passar pela cozinha até ao meio-dia, um familiar recebe um aviso.
- **Pessoas autorizadas e segurança.** Se entrar um desconhecido sem que haja telemóveis da família em casa, o utilizador recebe uma fotografia e pode ativar o alarme. O reconhecimento dos familiares é opcional, exige o consentimento de cada um e é feito em casa.
- **Energia.** A tomada inteligente desliga o aquecedor quando a casa fica vazia ou liga a chaleira quando alguém chega à cozinha de manhã.

[[figura: figura-arquitetura]]

Na plataforma, propõe-se um separador «Coisas» na aplicação, quatro novas ferramentas no MCP, que permitem a qualquer assistente de IA consultar esta memória, e um acionador que inicia um cenário quando é visto um objeto ou uma pessoa.

Até ao momento, a equipa ligou-se ao MCP com um cliente próprio, que consulta os sete dispositivos do kit e comanda a tomada em cerca de um segundo, acedeu ao vídeo em direto da câmara e construiu um protótipo da aplicação com o novo separador, para uma demonstração no kit real a 20 de novembro.

## Ferramentas de IA

- **Modelos de visão _open-source_, em casa.** O OWLv2, o DINOv2, o Depth Anything V2 e o ByteTrack detetam, identificam e seguem objetos e estimam a profundidade, com licenças que permitem o uso comercial (Apache-2.0 e MIT). Ocupam cerca de 0,8 GB, demoram 0,6 s por imagem num portátil e não enviam imagens para fora de casa.
- **Modelo de linguagem, sob contrato.** Pode ser o Claude, da Anthropic, ou outro modelo equivalente, desde que o contrato exclua o uso dos dados para treino e inclua um acordo de tratamento de dados, de preferência com servidores na UE. Com base no custo medido por pedido, estima-se um gasto de cerca de 0,43 € por casa e por mês.
- **Desenvolvimento.** A equipa recorreu ao Claude Code (Claude Opus 5.5) na pesquisa, na programação e na redação; validou os resultados e confirmou os números nas fontes primárias.

Fontes: Eurostat, isoc_iiot_use (2024); ANACOM, serviços de acesso à internet em local fixo, 4.º trimestre de 2025; sítios da NOS e da Vodafone, consultados a 18/11/2026; fichas dos modelos no Hugging Face.
