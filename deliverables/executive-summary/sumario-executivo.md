equipa: IT-Porto
desafio: #3 Connected Homes Reimagined: a IA ao serviço da casa

## Descrição do desafio

A Altice Labs desafia-nos a repensar a casa conectada com inteligência artificial: serviços que tornem o dia a dia em casa mais simples, mais útil ou mais seguro, e que as pessoas queiram mesmo usar. O desafio é aberto, com uma condição técnica: integrar o servidor MCP da plataforma Cognitive Home, através do qual um agente de IA lê e controla uma casa real. O kit inclui sensores, uma tomada que mede energia, uma lâmpada de cor e uma câmara. A ficha pede para pensar «para além dos comandos», combinando «contexto, intenção, informação e ação», e os mentores pediram para não menosprezar a câmara como fonte de dados.

## Estratégia

Partimos de um problema de todos os dias, não do equipamento: **perder coisas em casa**. Chaves, carteira, óculos, telemóvel. É um incómodo para qualquer pessoa e um dos sinais de alerta conhecidos da demência (Alzheimer's Association). Em Portugal, 2,29 % da população vive com demência, 238 401 pessoas, o 3.º valor mais alto da UE (Alzheimer Europe, 2025), e 517 146 pessoas com 65 ou mais anos vivem sozinhas (INE, Censos 2021). Daí, três escolhas:

- **A câmara passa de vigilância a memória.** Hoje, a câmara do kit só comunica à plataforma «movimento detetado». Damos-lhe memória das coisas que o utilizador escolhe: onde e quando foram vistas pela última vez.
- **Construir sobre o que a Altice já tem.** Um separador na aplicação existente, novas ferramentas no MCP e regras gravadas como cenários da plataforma: o caminho mais curto para lançar, em qualquer operador da plataforma, como a SFR em França.
- **Privacidade desde a conceção.** O utilizador decide o que a câmara analisa; o resto é descartado de imediato (RGPD, art. 25.º).

O mercado confirma a aposta. Um robô aspirador de 1 499,99 USD (Narwal Flow 2) já promete lembrar-se de onde ficaram carteiras e telemóveis, e o Ring pesquisa objetos em vídeo gravado; não encontrámos nenhuma câmara doméstica fixa que mantenha uma memória «visto pela última vez». Em Portugal, só 23,99 % das pessoas usaram um sistema de casa conectada em 2024, contra 33,04 % na UE (Eurostat). A NOS e a Vodafone vendem alarmes com câmara interior por mensalidade (Vodafone: 45,50 €/mês); a MEO, com 40,9 % dos acessos de banda larga fixa (ANACOM, 4.º trimestre de 2025), vende um kit de alarme sem câmara. O Track Things dá à MEO uma razão para vender a câmara.

## Ideias para a proposta de solução

**Track Things: a casa lembra-se das coisas que importam.** O utilizador cria «coisas» (chaves, carteira, óculos, o gato, a máquina do café) e escolhe o que quer saber de cada uma; a aplicação sugere outras a partir do que a câmara vê. Quatro momentos:

- «Onde estão as chaves?» «Na mesa da entrada, às 08:42», com o recorte da imagem como prova.
- A pessoa vai sair e as chaves ficaram na mesa: a casa avisa à porta e a luz pisca.
- A casa ficou vazia com a máquina do café ligada: a tomada desliga-se e a casa diz quanto se poupou.
- Alguém no corredor sem nenhum telemóvel conhecido em casa: chega uma fotografia com dois botões, sirene ou alarme. Nada soa sem um «sim».

[[figura: fluxo.png]]

**Como funciona.** Um **filtro de privacidade** só deixa passar as zonas escolhidas (uma mesa, a porta). Um **detetor** encontra as coisas pelo nome e a **memória** guarda o quê, onde e quando, sem vídeo. As **regras** decidem os casos conhecidos; o **agente de IA** só entra quando há dúvida ou uma pergunta, e age na luz, na tomada e no alarme através do MCP.

**Privacidade.** O utilizador escolhe onde fica a câmara e que zonas são analisadas. Ninguém é identificado pelo rosto: o reconhecimento facial fica fora da primeira versão, porque a identificação biométrica à distância é de risco elevado no Regulamento da IA.

**Na Altice.** Um separador «Coisas» na aplicação da Altice, com pergunta livre e pacotes vendidos como extra: Perdidos e Achados, Visitas e Segurança, Regras Próprias; mais tarde, Crianças, Animais e Plantas. No MCP, quatro ferramentas novas (`list_things`, `create_thing`, `get_thing_last_seen`, `get_thing_timeline`), para que qualquer assistente, incluindo o da Altice, use a memória.

**Estado.** Feito: cliente MCP próprio, que lê os 7 equipamentos; tomada comandada pelo MCP, com resposta em cerca de 1 s; regra câmara → luz criada pelo MCP; câmara ligada à plataforma. Até sexta: ler o vídeo da câmara com o nosso código (a primeira tentativa ainda não teve resposta), o filtro, o detetor, a memória, duas regras e um protótipo web do separador, tudo demonstrado no kit real.

## Ferramentas de IA

- **Visão.** Detetores de vocabulário aberto (OWLv2 ou Grounding DINO, licença Apache-2.0) encontram objetos pelo nome que o utilizador lhes dá, e o ByteTrack (licença MIT) segue-os entre imagens. Evitamos o YOLO da Ultralytics: a licença AGPL obrigaria a Altice a abrir o código ou a comprar uma licença comercial.
- **Linguagem.** Um modelo de linguagem com visão (Claude, da Anthropic) entra só quando as regras não chegam: sugerir coisas na configuração, avaliar um evento ambíguo, responder a perguntas a partir da memória e transformar uma frase numa regra. Recebe recortes e o contexto da casa lido pelo MCP, nunca vídeo contínuo, e nunca é a única prova para disparar um alarme. Custo estimado: 0,26 USD por casa e por mês com o modelo mais pequeno, a 30 pedidos por dia.
- **Dados na UE.** A API da Anthropic não oferece processamento só na UE. Em produção: o Claude em regiões europeias do Amazon Bedrock, ou um modelo aberto (Qwen3-VL, Apache-2.0) alojado pela Altice.
- **No desenvolvimento.** Usámos o Claude Code (Claude Opus 5.5) para pesquisa, código e documentos. Cada número citado foi confirmado na fonte primária.

Fontes: INE, Censos 2021 (quadro Q1.04); Alzheimer Europe, Prevalence of Dementia in Europe 2025 (quadro 4); Alzheimer's Association, 10 Early Signs; Eurostat, isoc_iiot_use; ANACOM, serviços de acesso à internet, 4T2025; páginas da Narwal, Ring, NOS, Vodafone e MEO, e documentação da Anthropic, consultadas a 18/11/2026.
