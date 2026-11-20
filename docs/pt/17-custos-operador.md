# Custos para o operador: os modelos de visão do _ThingTracker_ em 500 000 casas

Estado a 18 de novembro de 2026. Todos os valores resultam do _script_ [`deliverables/opcost/model.py`](../../deliverables/opcost/model.py) (`python3 deliverables/opcost/model.py`), que imprime cada tabela. Os valores externos têm uma fonte numerada no fim; os restantes estão assinalados como PRESSUPOSTO, com a respetiva justificação. Tal como no [caso de negócio](16-viabilidade-negocio.md), considera-se 1 USD = 1 EUR e os preços não incluem IVA.

## Em resumo

- A pergunta. O caso de negócio apresenta o custo do modelo de linguagem por casa (cerca de 0,43 € por mês). Este documento calcula o custo para o operador dos modelos de visão, que depende do local onde correm, e responde à objeção de que um equipamento por casa, ou uma frota de servidores, é muito caro com 500 000 clientes, e de que é por isso que as empresas recorrem aos _hyperscalers_.
- Com imagens completas, a objeção confirma-se. Analisar todas as imagens com movimento, em resolução completa, custa à Altice 2,41 € por casa e por mês em servidores próprios, entre 3,93 € e 4,26 € em _GPU_ alugadas a pedido num _hyperscaler_ e entre 6,55 € e 8,64 € com uma caixa em cada casa. Com o serviço adicional a 3,99 €, nenhuma destas opções deixa margem.
- A via recomendada custa cerca de 0,49 € por casa e por mês com uma câmara (0,98 € com duas). A deteção de movimento, que é barata, fica em casa, na câmara ou no _router_. Só a zona da imagem que mudou segue para os servidores da Altice, e o trabalho que não é urgente aguarda numa fila por um momento de menor carga, pelo que os servidores não são dimensionados para o pico da noite. Sobra cerca de 1,25 € por casa e por mês.
- O pressuposto principal: 2 h de movimento por câmara e por dia, analisadas a 1 imagem por segundo, numa _GPU_ a 25 % da sua velocidade máxima. Cada um destes valores pode duplicar ou reduzir para metade o custo (secção 9).
- Se o _router_ tiver uma _NPU_ capaz de correr os modelos, o custo desce para cerca de 0,36 € por casa e por mês, mas ainda nada demonstra que tenha.

## 1. O que se calcula

A câmara do _ThingTracker_ fica em repouso até uma verificação de movimento de baixo custo (a comparação de duas pequenas imagens em tons de cinzento, a cada 0,5 s) detetar uma alteração. Só então correm, durante alguns segundos, os modelos pesados: o _OWLv2_ encontra na imagem os objetos registados e o _DINOv2_ calcula a assinatura visual de cada candidato. No protótipo, só saem de casa pequenos recortes. A questão é saber onde devem correr estes modelos com 500 000 casas:

| Opção | Onde correm os modelos pesados | Quem paga a eletricidade |
|---|---|---|
| A. Em casa | No _router_, se tiver uma _NPU_, ou numa pequena caixa ligada a ele | O cliente |
| B. Servidores da Altice | Servidores com _GPU_ num centro de dados em Portugal | A Altice |
| C. _Hyperscaler_ | _GPU_ alugadas numa região da UE (AWS, Azure) | A Altice, incluída no preço por hora |

## 2. Quanto trabalho existe, e quando

O caso de negócio pressupõe 2 h de movimento por câmara e por dia. O trabalho não se distribui de forma uniforme: concentra-se ao fim do dia. Não existe um perfil diário medido para as casas portuguesas, pelo que a distribuição por hora é um PRESSUPOSTO (pouco movimento de noite, picos às 7–8 h e às 19–21 h; ver `HOURLY_WEIGHT` no modelo).

| Grandeza | Cálculo | Valor |
|---|---|---|
| Fração do tempo com movimento | 2 h / 24 h | 8,33 % |
| Câmaras com movimento na hora de maior carga (20 h) | 2 h × 10,34 % do movimento diário | 20,67 % |
| Quarto de hora de maior carga (PRESSUPOSTO: × 1,2) | 20,67 % × 1,2 | 24,81 % |
| Fator de pico | 24,81 % / 8,33 % | 2,98 |
| Imagens analisadas por câmara e por mês | 2 h × 3600 s × 1 imagem/s × 30,4 dias | 218 880 |

Um conjunto de servidores dimensionado para o pico é, portanto, cerca de três vezes maior do que a carga média exige.

## 3. Quanto trabalho exige uma imagem, e a que velocidade a processa cada acelerador

Não foi encontrada nenhuma medição publicada do _OWLv2_ ou do _DINOv2_ numa _T4_ ou numa _L4_. Por isso, o trabalho de cada imagem é calculado a partir da arquitetura dos modelos, e a fração da velocidade máxima de cada _chip_ efetivamente atingida é um pressuposto.

- O _OWLv2 base patch16_ lê imagens de 960 × 960 (configuração do modelo, [S14]): 60 × 60 = 3600 blocos, 12 camadas de largura 768. Uma camada de um _ViT_ custa 12·N·D² multiplicações-somas nas partes lineares e 2·N²·D na atenção, pelo que o codificador exige 1,09 TFLOP por imagem. Somando 3 % para as cabeças de deteção (PRESSUPOSTO) e três recortes do _DINOv2 small_, de 12 GFLOP cada, uma imagem exige 1,16 TFLOP.
- Se for analisada apenas a zona que mudou, redimensionada para 640 × 640 (1600 blocos), a imagem exige 0,41 TFLOP. Falta testar se o _OWLv2_ mantém a precisão nesta dimensão (PRESSUPOSTO).
- No portátil da equipa (Apple M1 Pro, com MPS), mediram-se 0,57 s para o _OWLv2_ e 22 ms por recorte do _DINOv2_, ou seja, 0,64 s por imagem, o equivalente a 1,8 TFLOPS efetivos.

PRESSUPOSTO: uma _GPU_ com _TensorRT_ em FP16 atinge 25 % do seu máximo FP16 denso nestes modelos. Verificação cruzada: o _NanoOWL_ da NVIDIA corre o _OWL-ViT B/16_ a 768 × 768 (0,59 TFLOP) a 25 imagens por segundo num _Jetson AGX Orin_ [S5], o que corresponde a 14,7 TFLOPS efetivos; o pressuposto atribui 16,2 TFLOPS a uma _T4_, um valor da mesma ordem.

| Acelerador | Máximo FP16 denso | Efetivo (25 %) | Imagens/s, imagem completa | Imagens/s, zona alterada |
|---|---|---|---|---|
| NVIDIA _T4_ | 65 TFLOPS [S1] | 16,2 TFLOPS | 14,0 | 39,3 |
| NVIDIA _L4_ | 121 TFLOPS (242 com esparsidade, a dividir por dois) [S2] | 30,2 TFLOPS | 26,1 | 73,1 |
| _Jetson Orin Nano Super_ | 16,8 TFLOPS (67 TOPS INT8 esparsos [S6], ÷ 4, PRESSUPOSTO) | 4,2 TFLOPS | 3,6 | 10,1 |
| _MacBook_ M1 Pro (medido) | — (medido, não derivado de um máximo) | 1,8 TFLOPS | 1,6 | Não calculado |

## 4. Opção A: um equipamento em cada casa

O equipamento é amortizado em 36 meses, como no caso de negócio. PRESSUPOSTOS: 15 € de envio por caixa, avaria anual de 3 % dos equipamentos, 30 € por substituição e, no caso do _router_, o acréscimo de preço distribuído por uma vida útil de 60 meses.

| Equipamento | Preço | Operador, €/casa/mês | €/câmara, com 2 câmaras | Eletricidade do cliente, €/mês | Investimento para 500 000 casas | Corre o _OWLv2_ a 960? |
|---|---|---|---|---|---|---|
| A1. _NPU_ num _router_ novo | Acréscimo de 15 € (PRESSUPOSTO, sem preço público) | 0,36 | 0,18 | 0,11 | 7,5 M€ | Desconhecido; provavelmente exige um detetor mais leve |
| A2. _Raspberry Pi 5_ 4 GB + _AI HAT+_ 13 TOPS | 110 $ [S3] + 70 $ [S4] + 20 $ de caixa e fonte (PRESSUPOSTO) = 200 € | 6,55 | 3,27 | 0,59 | 107,5 M€ | Não: o _Hailo-8L_, de 13 TOPS, exige um detetor mais leve |
| A3. _Jetson Orin Nano Super_ | 249 $ [S6] + 20 $ de armazenamento = 269 € | 8,64 | 4,32 | 1,08 | 142,0 M€ | Sim, cerca de 3,6 imagens/s |

Cálculo para A2: (200 € + 15 €) / 36 = 5,97 €, mais avarias, 3 % × (200 € + 30 €) / 12 = 0,57 €, o que dá 6,55 € por mês. Eletricidade: (22 h × 3 W + 2 h × 8 W) × 30,4 dias = 2,49 kWh × 0,2367 €/kWh = 0,59 €, a pagar pelo cliente (as potências são um PRESSUPOSTO; o intervalo de 7 a 25 W do _Jetson_ é oficial [S6]).

O preço da memória fez subir o dos pequenos computadores: o _Raspberry Pi 5_ de 4 GB custava 60 $ no lançamento e 110 $ em abril de 2026 [S3]. Uma caixa em cada casa exige um investimento inicial de 100 a 140 M€ para 500 000 casas, que é a versão mais forte da objeção. A opção A só é viável se o _router_ ou a câmara que a Altice já instala conseguir correr os modelos.

## 5. Opção B: servidores próprios da Altice em Portugal, imagens completas, dimensionados para o pico

| Passo | Cálculo | 1 câmara por casa | 2 câmaras |
|---|---|---|---|
| Carga média | 500 000 × 8,33 % × 1 imagem/s | 41 667 imagens/s | 83 333 imagens/s |
| Carga de pico | 500 000 × 24,81 % × 1 imagem/s | 124 031 imagens/s | 248 062 imagens/s |
| Placas _L4_ | 124 031 / (26,1 × 70 % de ocupação, PRESSUPOSTO) × 1,1 de reserva | 7466 | 14 933 |
| Equipamento | 7466 × 2500 € (PRESSUPOSTO [S12]) + 1867 servidores × 8000 € (PRESSUPOSTO) | 33,6 M€ | 67,2 M€ |
| Amortização | / 48 meses (PRESSUPOSTO) | 700 mil € | 1400 mil € |
| Energia | 699 kW em média × PUE 1,54 [S10] × 730 h × 0,1135 €/kWh [S11] | 89 mil € | 178 mil € |
| Espaço e refrigeração no centro de dados | 1004 kW × 150 €/kW (PRESSUPOSTO) | 151 mil € | 301 mil € |
| Operação | 8 % do equipamento por ano (PRESSUPOSTO) | 224 mil € | 448 mil € |
| Rede | 79 Gbps no pico × 0,50 € por Mbps (PRESSUPOSTO) | 40 mil € | 79 mil € |
| Total por mês | Amortização + energia + espaço + operação + rede | 1203 mil € | 2407 mil € |
| Por casa / por câmara | Total ÷ 500 000 casas / ÷ câmaras | 2,41 € / 2,41 € | 4,81 € / 2,41 € |

Dimensionadas para o pico, as placas só estão ocupadas, em média, 21 % do tempo. Essa capacidade parada é o custo real a que a objeção se refere.

## 6. Opção C: _GPU_ de um _hyperscaler_ numa região da UE, imagens completas

As instâncias a pedido e as _spot_ acompanham a carga hora a hora (mais 15 % pelo atraso no ajuste, PRESSUPOSTO); as instâncias reservadas funcionam 24 h por dia e são dimensionadas para o pico. A entrada de dados na nuvem é gratuita (Azure, “_Standard Data Transfer In_”: 0,00 $ [S9]); só saem resultados de pequena dimensão, a 0,08 $/GB depois dos primeiros 100 GB [S9].

| Oferta | $/hora | Instâncias no pico | €/casa/mês, 1 câmara | €/casa/mês, 2 câmaras |
|---|---|---|---|---|
| AWS _g4dn.xlarge_ (_T4_), a pedido, Irlanda [S7] | 0,587 | 12 635 | 4,26 | 8,52 |
| AWS _g6.xlarge_ (_L4_), a pedido, Frankfurt [S7] | 1,0064 | 6788 | 3,93 | 7,86 |
| Azure _NC4as T4 v3_, a pedido, Europa Ocidental [S9] | 0,658 | 12 635 | 4,77 | 9,53 |
| AWS _g4dn.xlarge_, _spot_, Irlanda [S8] | 0,2604 | 12 635 | 1,93 | 3,87 |
| Azure _NC4as T4 v3_, _spot_ [S9] | 0,3218 | 12 635 | 2,37 | 4,74 |
| Azure _NC4as T4 v3_, reserva a 1 ano (3686 $) [S9] | 0,4208 | 13 899 | 8,62 | 17,24 |
| Azure _NC4as T4 v3_, reserva a 3 anos (6566 $) [S9] | 0,2498 | 13 899 | 5,15 | 10,30 |

Cálculo para a primeira linha: 41 667 imagens/s em média ao longo do dia; cada _T4_ processa 14,0 × 70 % = 9,8 imagens/s, o que dá cerca de 3,56 milhões de horas de instância por mês × 0,587 $ = 2,09 M$, mais 40 mil € de rede: 4,26 € por casa. As instâncias _spot_ parecem baratas, mas nada garante 12 600 _GPU_ livres numa só região às 20 h.

A vantagem do _hyperscaler_ é real: cobra a curva diária e não o pico. Ainda assim, com imagens completas, fica mais caro do que os servidores próprios da Altice, porque o preço por hora inclui a margem, o centro de dados e a energia.

## 7. Largura de banda: o que sai de casa

| O que sai de casa | GB por câmara e por mês | Pico com 500 000 câmaras | Rede, €/casa/mês |
|---|---|---|---|
| Vídeo contínuo, 24 h (2 Mbps, PRESSUPOSTO) | 657 | 1000 Gbps | 1,00 |
| Imagens completas 960 × 540, 1 imagem/s com movimento (80 KB, PRESSUPOSTO) | 17,5 | 79 Gbps | 0,08 |
| Só a zona alterada (40 KB, PRESSUPOSTO) | 8,8 | 40 Gbps | 0,04 |
| Só recortes (modelos pesados em casa, como no protótipo) | 1,8 | 8 Gbps | cerca de 0 |

Enviar o vídeo das câmaras para a nuvem está fora de questão: move 37 vezes mais dados do que as imagens enviadas apenas quando há movimento. É a verificação de movimento em casa que torna viável qualquer opção centralizada.

## 8. A via híbrida recomendada

1. A verificação de movimento fica sempre em casa, na câmara ou no _router_. Trata-se de uma comparação simples de duas imagens de 160 × 90 em tons de cinzento, sem acelerador de IA.
2. Só se envia a zona que mudou, redimensionada para um máximo de 640 × 640. O trabalho por imagem desce de 1,16 para 0,41 TFLOP e o envio reduz-se para metade.
3. O trabalho que não é urgente aguarda. Atualizar “onde está o livro” pode esperar alguns minutos; uma regra como “avisa-me se sair de casa sem o livro” não pode. PRESSUPOSTO: 30 % das imagens são urgentes e são tratadas no pico; os restantes 70 % ficam em fila e são processados ao ritmo médio. Os servidores passam a ser dimensionados para 66 376 imagens/s, em vez de 124 031.
4. As imagens são agrupadas em lotes nos servidores com _GPU_ da Altice (ou em _GPU_ reservadas na nuvem), que ficam ocupados, em média, 40 % do tempo, em vez de 21 %.

| Via híbrida, 500 000 casas | 1 câmara | 2 câmaras |
|---|---|---|
| Em servidores _L4_ próprios da Altice (1427 placas, 6,4 M€ de equipamento) | 0,49 € | 0,98 € |
| Em _T4_ da Azure, reserva a 3 anos | 1,01 € | 2,02 € |
| Em _T4_ da AWS, a pedido | 1,53 € | 3,07 € |

Cada uma das duas medidas, isoladamente (servidores _L4_ próprios, uma câmara): só a zona alterada dá 0,87 €; só a fila dá 1,33 €.

## 9. Síntese e ponto de equilíbrio

No caso de negócio, o serviço adicional custa 3,99 € por mês (3,24 € sem o IVA de 23 %). Os restantes custos de funcionamento (modelo de linguagem, servidores da aplicação, apoio ao cliente e angariação) somam 1,51 €, pelo que a visão pode custar, no máximo, 1,73 € por casa e por mês antes de o serviço dar prejuízo.

| Opção, 500 000 casas | €/casa/mês, 1 câmara | €/casa/mês, 2 câmaras | €/câmara/mês (1 / 2 câmaras) | Sobra dos 1,73 €, 1 câmara |
|---|---|---|---|---|
| A1. _NPU_ no _router_ (se conseguir correr os modelos) | 0,36 | 0,36 | 0,36 / 0,18 | 1,37 |
| A2. _Raspberry Pi 5_ + _AI HAT+_ em cada casa | 6,55 | 6,55 | 6,55 / 3,27 | −4,81 |
| A3. _Jetson Orin Nano Super_ em cada casa | 8,64 | 8,64 | 8,64 / 4,32 | −6,90 |
| B. Servidores _L4_ próprios, imagens completas, pico | 2,41 | 4,81 | 2,41 | −0,67 |
| C. AWS _L4_, a pedido | 3,93 | 7,86 | 3,93 | −2,20 |
| C. AWS _T4_, a pedido | 4,26 | 8,52 | 4,26 | −2,53 |
| C. AWS _T4_, _spot_ (sem garantia de capacidade) | 1,93 | 3,87 | 1,93 | −0,20 |
| C. Azure _T4_, reserva a 3 anos | 5,15 | 10,30 | 5,15 | −3,42 |
| Via híbrida em servidores _L4_ próprios (recomendada) | 0,49 | 0,98 | 0,49 | 1,25 |
| Via híbrida em _T4_ da Azure, reserva a 3 anos | 1,01 | 2,02 | 1,01 | 0,72 |
| Via híbrida em _T4_ da AWS, a pedido | 1,53 | 3,07 | 1,53 | 0,20 |

Sensibilidade (servidores _L4_ próprios, 1 câmara; via híbrida / imagens completas no pico, em € por casa e por mês):

| Alteração | Via híbrida | Imagens completas |
|---|---|---|
| Base | 0,49 | 2,41 |
| 2 imagens por segundo com movimento | 0,98 | 4,81 |
| 4 h de movimento por dia | 0,98 | 4,81 |
| _GPU_ a 15 % do máximo | 0,79 | 3,96 |
| _GPU_ a 35 % do máximo | 0,36 | 1,74 |
| _L4_ a 3500 € | 0,57 | 2,82 |

## 10. Resposta à objeção

- Uma caixa em cada casa é a opção mais cara: 100 a 140 M€ de equipamento para 500 000 casas e 6,55 € a 8,64 € por casa e por mês. Neste ponto, a objeção procede.
- Os _hyperscalers_ são mais baratos do que servidores parados, mas não do que servidores ocupados. A sua vantagem é cobrarem a curva diária. O trabalho do _ThingTracker_ pode ser redistribuído (verificação de movimento em casa, só a zona alterada, fila para o que não é urgente), o que mantém ocupados os servidores próprios da Altice e reduz o custo para 0,49 € por casa e por mês, contra 1,53 € para a mesma via híbrida na AWS a pedido.
- Os _hyperscalers_ são o ponto de partida certo. Com as 19 000 casas esperadas no caso de negócio, servidores próprios obrigariam a comprar à partida cerca de 55 placas; as _GPU_ a pedido na nuvem não têm custo fixo enquanto a taxa de adesão for desconhecida. A passagem para servidores próprios compensa à medida que a base cresce.
- O melhor cenário continua a ser o equipamento que já está em casa. Se os _routers_ ou as câmaras da Altice tiverem uma _NPU_ capaz de correr um detetor, o custo desce para cerca de 0,36 € por casa e por mês (A1). É a primeira pergunta a colocar à Altice.

## 11. Pressupostos a validar no piloto

Os valores anteriores assentam em pressupostos que se substituem por medições antes ou durante o piloto:

1. O débito: correr o _OWLv2_ e o _DINOv2_ com _TensorRT_ em FP16 numa _T4_ ou numa _L4_ e substituir o pressuposto de 25 %. Este valor altera todas as opções com servidores.
2. A precisão na zona alterada a 640 × 640, face às imagens completas a 960.
3. As horas de movimento e o pico da noite, a partir dos eventos de movimento que as câmaras da Altice já enviam.
4. A _NPU_ dos _routers_ e das câmaras da Altice, e se consegue correr um detetor (A1).
5. Os preços reais da Altice para _GPU_, espaço em centro de dados e capacidade de rede.

## Fontes

Todas consultadas a 18 de novembro de 2026. Os ficheiros descarregados foram lidos numa pasta própria; nenhum continha texto dirigido a uma IA.

1. [S1] NVIDIA, _T4 Tensor Core GPU_: 65 TFLOPS FP16, 70 W. https://www.nvidia.com/en-us/data-center/tesla-t4/
2. [S2] NVIDIA, _L4 Tensor Core GPU_: 242 TFLOPS FP16 com esparsidade, 72 W. https://www.nvidia.com/en-us/data-center/l4/
3. [S3] Raspberry Pi, ficha do _Raspberry Pi 5_, abril de 2026: 4 GB a 110 $. https://pip-assets.raspberrypi.com/categories/892-raspberry-pi-5/documents/RP-008348-DS-6-raspberry-pi-5-product-brief.pdf (lida através de um excerto de pesquisa; a descarga direta veio vazia, pelo que deve ser confirmada). Histórico de preços: https://www.raspberrypi.com/news/more-memory-driven-price-rises/
4. [S4] Raspberry Pi, _AI HAT+_: 13 TOPS (_Hailo-8L_) a 70 $, 26 TOPS a 110 $. https://www.raspberrypi.com/news/raspberry-pi-ai-hat/ ; o anterior _AI Kit_ já não é produzido: https://www.raspberrypi.com/products/ai-kit/
5. [S5] NVIDIA-AI-IOT, README do _NanoOWL_: _OWL-ViT B/16_ a 768, 25 imagens/s no _Jetson AGX Orin_ (_TensorRT_). https://github.com/NVIDIA-AI-IOT/nanoowl
6. [S6] NVIDIA, _Jetson Orin Nano Super Developer Kit_: 67 TOPS INT8, 7 a 25 W. https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/nano-super-developer-kit/ ; preço de 249 $: https://developer.nvidia.com/blog/nvidia-jetson-orin-nano-developer-kit-gets-a-super-boost/
7. [S7] AWS, tabela de preços EC2 a pedido (o ficheiro usado pela página de preços, publicado a 17 de novembro de 2026): _g4dn.xlarge_ a 0,587 $/h na Irlanda; _g6.xlarge_ a 1,0064 $/h em Frankfurt. https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/EU%20(Ireland)/Linux/index.json
8. [S8] AWS, preços _spot_ da página https://aws.amazon.com/ec2/spot/pricing/: _g4dn.xlarge_ a 0,2604 $/h em eu-west-1. https://website.spot.ec2.aws.a2z.com/spot.js
9. [S9] Microsoft, _Azure Retail Prices API_, Europa Ocidental: _NC4as T4 v3_ a 0,658 $/h, _spot_ a 0,321762 $/h, reserva a 1 ano por 3686 $, a 3 anos por 6566 $; entrada de dados a 0,00 $/GB, saída a 0,08 $/GB depois de 100 GB. https://prices.azure.com/api/retail/prices
10. [S10] Uptime Institute, _Global Data Center Survey 2025_: PUE médio de 1,54 (segundo resumos do relatório). https://intelligence.uptimeinstitute.com/resource/uptime-institute-global-data-center-survey-2025
11. [S11] Eurostat, nrg_pc_205, eletricidade para clientes não domésticos, Portugal, 1.º semestre de 2026, 2000 a 19 999 MWh, sem IVA: 0,1135 €/kWh (atualizado a 19 de outubro de 2026). https://ec.europa.eu/eurostat/databrowser/view/nrg_pc_205/default/table
12. [S12] A NVIDIA não publica preço de tabela para a _L4_. Os revendedores apresentam valores entre cerca de 2700 $ e 7390 $ por placa (por exemplo, CDW, https://www.cdw.com/product/nvidia-gpu-computing-processor-l4-24-gb/8205397). Valor apenas indicativo.
13. [S13] Caso de negócio do _ThingTracker_: serviço adicional a 3,99 €, 1,51 € de outros custos, eletricidade doméstica a 0,2367 €/kWh (Eurostat nrg_pc_204). [16-viabilidade-negocio.md](16-viabilidade-negocio.md)
14. [S14] Google, _OWLv2 base patch16 ensemble_, configuração do modelo (`image_size` 960, `patch_size` 16). https://huggingface.co/google/owlv2-base-patch16-ensemble
