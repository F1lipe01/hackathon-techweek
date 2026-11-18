equipa: IT-Porto
desafio: #3 Connected Homes Reimagined: a IA ao serviço da casa

## Descrição do desafio

O desafio n.º 3, proposto pela Altice Labs, convida as equipas a repensar a casa conectada com recurso à inteligência artificial, através de serviços que tornem o quotidiano mais simples, mais útil ou mais seguro. A única condição técnica do desafio é a integração do servidor MCP (Model Context Protocol) da plataforma Cognitive Home, que permite a um agente de IA consultar e controlar os dispositivos de uma casa real. A ficha do desafio pede que se pense «para além dos comandos», em soluções que combinem contexto, intenção, informação e ação. Na sessão de abertura, os mentores sublinharam o potencial da câmara como fonte de dados.

## Estratégia

A câmara é o sensor mais rico em informação de uma casa, mas encontra-se hoje subaproveitada, uma vez que, no kit, se limita a comunicar à plataforma que detetou movimento. Associada a um modelo de IA multimodal, capaz de interpretar imagens e texto, uma única câmara pode substituir vários sensores dedicados, e o próprio utilizador pode criar novos sensores virtuais com uma simples frase. Assim, em vez de um conjunto fechado de funcionalidades, propõe-se uma base para um número ilimitado de cenários, assente em três princípios:

- **A câmara como fonte de informação, e não de vigilância**, centrada nos objetos e nas situações definidos pelo utilizador.
- **Integração no ecossistema existente**, através de um separador na aplicação da Altice e de novas ferramentas no servidor MCP, com as regras guardadas como cenários da própria plataforma, o que facilita a adoção pela MEO e por outros operadores, como a SFR, em França.
- **Privacidade desde a conceção**, cabendo ao utilizador escolher onde fica a câmara e que zonas são analisadas; o resto da imagem é descartado de imediato, em linha com o artigo 25.º do RGPD.

O mercado nacional tem margem para crescer. Em 2024, apenas 23,99 % das pessoas em Portugal utilizaram um sistema de casa conectada, face a 33,04 % na União Europeia (Eurostat). A NOS e a Vodafone já comercializam alarmes com câmara interior mediante mensalidade, ao passo que a MEO, que detém 40,9 % dos acessos de banda larga fixa (ANACOM, 4.º trimestre de 2025), vende um kit de alarme sem câmara.

## Ideias para a proposta de solução

A solução proposta, o **Track Things**, transforma a câmara da casa num sensor universal, configurado em linguagem natural. O conceito resume-se a quatro verbos, **ver, perceber, lembrar e agir**, e aplica-se a tudo o que o utilizador considere importante, seja um objeto, uma criança, um animal, uma planta, uma pessoa autorizada ou um familiar idoso. Entre os cenários possíveis, destacam-se os seguintes:

- **Objetos.** Perante a pergunta «onde deixei as chaves?», o sistema indica onde e a que horas foram vistas pela última vez, mostra a imagem correspondente e faz piscar a lâmpada se alguém sair sem elas.
- **Crianças.** Se uma criança começar a trepar uma estante, a sirene toca, a luz fica vermelha e os pais recebem um aviso.
- **Animais e plantas.** O utilizador pode pedir, por exemplo, «avisa-me se o gato não beber água até às 18h» ou «diz-me se a planta não for regada esta semana».
- **Segurança e energia.** Se surgir um desconhecido no corredor sem nenhum telemóvel da família em casa, é enviada uma fotografia com a opção de ativar o alarme, e a tomada do aquecedor é desligada quando a casa fica vazia.

[[figura: fluxo.png]]

Do ponto de vista técnico, a imagem passa primeiro por um filtro de privacidade, que conserva apenas as zonas escolhidas pelo utilizador. O modelo de IA interpreta essas zonas à luz dos cenários definidos e do estado da casa, obtido através do MCP; os casos simples e frequentes são resolvidos por regras fixas. A memória regista o que viu, onde e quando, sem guardar vídeo. O reconhecimento de pessoas autorizadas será opcional e processado na própria casa, dado o risco elevado que o Regulamento Europeu da IA atribui à identificação biométrica à distância.

Para a integração na oferta da Altice, propõe-se um separador «Coisas» na aplicação, com um campo de pergunta livre e pacotes comercializáveis como serviço adicional, bem como quatro novas ferramentas no servidor MCP (`list_things`, `create_thing`, `get_thing_last_seen` e `get_thing_timeline`), para que qualquer assistente de IA possa consultar esta memória.

Até ao momento, a equipa desenvolveu um cliente MCP próprio, que lê o estado dos sete dispositivos do kit; comandou a tomada através do MCP, com resposta em cerca de um segundo; e criou um cenário que associa a deteção de movimento da câmara à lâmpada. Até 20 de novembro, prevê-se aceder ao vídeo da câmara em tempo real e construir, com dados simulados, um protótipo que reproduza a aplicação da Altice, para demonstração no kit real.

## Ferramentas de IA

- **Interpretação de imagem.** Um modelo de IA multimodal (Claude, da Anthropic) interpreta as zonas recortadas, avalia situações ambíguas, responde a perguntas a partir da memória e converte as frases do utilizador em regras. O modelo recebe apenas recortes e contexto, nunca vídeo contínuo, e nunca é o único critério para disparar um alarme. Estima-se um custo de 0,26 USD por casa e por mês com o modelo mais pequeno, para 30 pedidos diários.
- **Deteção contínua.** O seguimento de objetos recorre a detetores que reconhecem objetos descritos por texto (OWLv2 ou Grounding DINO, licença Apache-2.0) e ao ByteTrack (licença MIT), evitando modelos AGPL, como o YOLO da Ultralytics, que exigiriam uma licença comercial.
- **Localização dos dados.** Como a API da Anthropic não garante o processamento exclusivamente na UE, a versão comercial poderá recorrer ao Claude nas regiões europeias do Amazon Bedrock ou a um modelo aberto alojado pela Altice.
- **Desenvolvimento.** A equipa recorreu ao Claude Code (Claude Opus 5.5) na pesquisa, na programação e na redação, tendo validado os resultados e confirmado todos os números nas fontes primárias.

Fontes: Eurostat, isoc_iiot_use (2024); ANACOM, serviços de acesso à internet, 4.º trimestre de 2025; sítios da NOS, Vodafone, MEO e Anthropic, consultados a 18/11/2026.
