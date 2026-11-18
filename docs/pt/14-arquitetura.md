# Arquitetura do _ThingTracker_

Versão 1, quarta-feira, 18 de novembro de 2026. Documento destinado ao júri e aos engenheiros da Altice Labs, bem como à equipa, com o detalhe técnico suficiente para avaliar a viabilidade da solução, sem código. A Figura 1 resume a arquitetura descrita nas secções seguintes.

![Arquitetura do ThingTracker](../architecture/thingtracker-architecture.png)

Figura 1. Arquitetura do _ThingTracker_, gerada por `../architecture/build_diagram.py`.

## 1. A ideia num parágrafo

A câmara é o sensor mais rico da casa, mas hoje limita-se a comunicar “movimento detetado”. O _ThingTracker_ transforma-a numa fonte de informação. Modelos de visão _open-source_, a correr localmente em casa, reconhecem os objetos que importam à família (as chaves, a carteira, os óculos, o comando da televisão), os lugares onde costumam estar (a secretária, a mesa da entrada) e a presença de pessoas, e guardam uma memória do que foi visto, onde e quando.

Um modelo de linguagem converte uma única frase numa regra precisa (“avisa-me se a caneca ficar na secretária quando não estiver ninguém em casa”), responde a perguntas a partir dessa memória (“onde estão as minhas chaves?”) e avalia, a partir de um único recorte, os raros casos duvidosos. As ações chegam aos dispositivos Altice já instalados (lâmpada, tomada, alarme) através do servidor MCP (“_Model Context Protocol_”) da Altice, tal como os restantes comandos chegam hoje.

Dois princípios orientam tudo o que se descreve a seguir:

1. Ver em casa, raciocinar sob contrato. A visão acontece em casa, sem custo por imagem e apenas quando há movimento ou som. O raciocínio acontece na nuvem, raramente, e só com texto ou com um recorte.
2. A IA escreve a regra e a regra corre em casa. O modelo de linguagem é usado quando se cria um sensor, e não em cada imagem, o que torna o sistema barato, rápido, previsível e auditável.

## 2. Requisitos

| # | Requisito | Objetivo | Como se cumpre |
|---|---|---|---|
| F1 | Seguir os objetos que o utilizador nomeia e distingui-los de objetos semelhantes | “As suas chaves”, e não “quaisquer chaves” | Deteção de vocabulário aberto e uma assinatura visual por objeto (§4.2) |
| F2 | Responder a “onde está X?” com o lugar, a hora e uma fotografia | Resposta em ≤ 3 s | Índice da última observação na Memória da casa; o modelo de linguagem só redige a resposta |
| F3 | Criar um sensor a partir de uma frase | Sem ecrãs de configuração | O modelo de linguagem compila a frase numa regra (§5) |
| F4 | Atuar sobre os dispositivos da casa | O mesmo caminho que a aplicação já usa | Ferramentas MCP (`update_device_capabilities`, estado de segurança) |
| F5 | Adicionar um objeto, sugerido ou mostrado à câmara | Cerca de 10 s por objeto | Sugestões da análise da divisão; registo em 3 segundos |
| F6 | Continuar a funcionar quando a câmara muda de posição ou faz _zoom_ | Sem redesenhar zonas à mão | Os lugares são encontrados pelo nome em cada imagem, e não guardados como píxeis (§4.3) |
| N1 | Privacidade | Nenhum vídeo nem imagem completa sai de casa para análise; as pessoas só são reconhecidas se a família o autorizar | Filtro de privacidade, perceção local e regras sobre os dados (§7) |
| N2 | Custo | Menos de 0,50 € por casa e por mês com o modelo de linguagem na nuvem | Custos medidos por pedido × utilização (ver o caso de negócio) |
| N3 | Latência, do evento à ação | ≤ 3 s | §8 |
| N4 | Adoção pela Altice | Nenhuma aplicação nova e nenhum caminho novo até aos dispositivos | Um separador na aplicação existente, ferramentas MCP e cenários da plataforma |
| N5 | Replicação | Qualquer operador presente na plataforma | Serviço de plataforma _multi-tenant_; software no _edge_, e não equipamento à medida |

Atualmente, aplicam-se as seguintes restrições:
- Existe uma única câmara Wi-Fi (_Tuya SC034-WNV3_), acessível por RTSP (“_Real Time Streaming Protocol_”) através do _relay_ _go2rtc_ disponibilizado pela organização, em H.265, 2304 × 1296 e 20 fps (verificado com o _ffprobe_ a 18 de novembro). A abertura do _stream_ demora cerca de 5 s, porque o descodificador espera por uma imagem-chave, pelo que o protótipo mantém uma ligação aberta e lê da memória a imagem mais recente, sem necessidade do _VLC_ nem de qualquer _plug-in_.
- O servidor MCP tem 18 ferramentas, sem notificações _push_ nem um fluxo geral de eventos (existe apenas o histórico do alarme, `get_home_security_alarm_history`), e o _token_ de autenticação dura cerca de 24 h.
- A central do kit não consegue executar modelos de visão, uma vez que é um _gateway_ LTE e não um equipamento de computação.
- A demonstração corre num portátil.

## 3. Componentes

### Em casa: o serviço local

Cada casa tem uma instância do serviço local. Em produção, correria no _gateway_ residencial do operador, caso este disponha de uma NPU (“_Neural Processing Unit_”), ou numa pequena caixa _edge_; na demonstração, corre num portátil. Todos os modelos são _open-source_ e de uso comercial livre, conforme verificado nas fichas dos modelos a 18 de novembro: o _OWLv2_, o _DINOv2_ e o _Depth Anything V2 Small_ têm licença Apache-2.0, e o _ByteTrack_ tem licença MIT. Do _Depth Anything V2_, só a versão _Small_ cumpre este requisito, uma vez que as versões _Base_, _Large_ e _Giant_ têm licença CC-BY-NC-4.0, que proíbe o uso comercial.

| Componente | Função | Tecnologia | Notas |
|---|---|---|---|
| Captura | Fica em repouso até haver movimento ou som, sinalizados pela deteção de movimento da própria câmara, pelo som ou por uma comparação de baixo custo entre imagens consecutivas; só então lê 1 a 2 imagens por segundo de cada câmara, por RTSP, na rede da casa. Quando nada muda, nada é reanalisado e a memória mantém as últimas posições | _ffmpeg_ / _OpenCV_ | Nunca grava vídeo |
| Filtro de privacidade | Aplica as máscaras (zonas que nunca são analisadas) e apaga cada imagem depois da perceção | No mesmo processo | A única imagem completa que chega a existir fica em memória durante menos de um segundo |
| Perceção: deteção | Encontra objetos e lugares pelo nome, em qualquer imagem | _OWLv2_ (vocabulário aberto) | Um objeto novo não exige treino |
| Perceção: seguimento | Mantém a identidade de cada deteção de imagem para imagem | _ByteTrack_ (MIT) | Permite saber que “a caneca passou da secretária para o sofá” |
| Perceção: assinaturas visuais | Compara uma deteção com o objeto registado | _Embeddings_ de imagem do _DINOv2_ | Distingue as suas chaves das chaves de uma visita |
| Perceção: profundidade | Distância relativa na imagem, a partir de uma única câmara | _Depth Anything V2 Small_ | Separa “em cima da mesa” de “atrás da mesa”. É uma aproximação, e não um LiDAR |
| Perceção: pessoas | Presença e contagem; postura, para quedas ou para alguém a trepar (numa fase posterior). Só reconhece um membro da família se a família o tiver registado, com o consentimento dessa pessoa | Deteção de pessoas; reconhecimento facial no próprio dispositivo (opcional); um modelo de pose numa fase posterior | Desativado por omissão. Os padrões faciais nunca saem de casa |
| Memória da casa | Observações: objeto, lugar, hora, posição e miniatura. Índice da última observação e cronologias. Quem está em casa, a partir dos telemóveis conhecidos ligados ao Wi-Fi | Base de dados local | Guardada durante 30 dias, sem vídeo |
| Motor de regras | Avalia a cada segundo as regras compiladas sobre a memória e escolhe uma resposta numa escala: nada, lembrar, avisar, agir ou escalar | Avaliador de regras determinístico | Só recorre ao modelo de linguagem, através da plataforma, nos casos duvidosos |
| Registo de objetos | Reúne o contexto de cada objeto: o nome, a assinatura visual e o lugar habitual. Transforma cerca de 3 segundos de um objeto mostrado à câmara em cerca de 8 recortes, na sua assinatura visual e na sua fotografia | Deteção + _DINOv2_ | Aceita também 3 fotografias tiradas com o telemóvel |
| Canal seguro | Uma única ligação de saída, autenticada, à plataforma Altice | mTLS / OAuth, conforme a plataforma exigir | A única via de entrada ou de saída do _edge_ |

A tabela seguinte resume os recursos usados por cada modelo local. O espaço em disco corresponde ao ficheiro de pesos publicado no _Hugging Face_ (fp32), e o tempo foi medido na GPU do portátil da equipa (Apple, com MPS, “_Metal Performance Shaders_”). A eletricidade resulta do produto do tempo medido pela potência de uma caixa _edge_ de 15 W (pressuposto B15 do caso de negócio) e pelo preço de 0,2367 €/kWh praticado em Portugal no primeiro semestre de 2026 (Eurostat, `nrg_pc_204`). Como a câmara fica em repouso enquanto nada muda, os valores consideram, a título de exemplo, 2 horas de movimento por dia, analisadas a 1 imagem por segundo.

| Modelo | Função | Espaço em disco | Tempo medido | Eletricidade por mês (exemplo) | Resultado publicado |
|---|---|---|---|---|---|
| _OWLv2 base, patch16 ensemble_ | Detetar objetos, lugares e pessoas pelo nome | 0,62 GB | 0,57 s por imagem | ≈ 0,12 € | 40,5 AP nas classes raras do LVIS, sem treino específico, _zero-shot_ ([README do _scenic_](https://github.com/google-research/scenic/tree/main/scenic/projects/owl_vit)) |
| _ByteTrack_ | Seguir as deteções de imagem para imagem | Sem pesos (CPU) | Desprezável | ≈ 0 € | 80,3 MOTA no conjunto de teste do MOT17 ([artigo](https://arxiv.org/abs/2110.06864)) |
| _DINOv2 small_ (ViT-S/14) | Assinatura visual do objeto | 0,09 GB | 22 ms por recorte | < 0,01 € (1 recorte por imagem) | 81,1 % no ImageNet-1k, com _linear probe_ ([README](https://github.com/facebookresearch/dinov2)) |
| _Depth Anything V2 Small_ | Perto ou longe, sem LiDAR | 0,10 GB | 55 ms por imagem | ≈ 0,01 € | 95,3 % no DA-2K ([artigo](https://arxiv.org/abs/2406.09414), Tabela 3) |
| Total | | 0,81 GB | ≈ 0,65 s por imagem | ≈ 0,14 € | |

A caixa _edge_ completa, sempre ligada a 15 W, custa 2,59 € por mês em eletricidade (C10 do caso de negócio), valor que funciona como limite superior; o consumo dos modelos acima já está incluído nesse valor e não se lhe soma.

### Na plataforma Altice

| Componente | Função | Estado |
|---|---|---|
| Serviço _ThingTracker_ | É o _host_ MCP e o único componente que chama o modelo de linguagem. Recebe os pedidos da aplicação e os eventos das casas pelo canal seguro e executa o ciclo: envia ao modelo o pedido e a lista de ferramentas disponíveis, chama no servidor MCP a ferramenta que o modelo escolher e devolve o resultado ao modelo, até haver uma resposta. Escolhe o modelo e a região e limita o gasto por casa | Proposto; no protótipo, este papel cabe ao `prototype/server.py` |
| Servidor MCP | Controlo de dispositivos, cenários e estado de segurança (hoje com 18 ferramentas). Propõe-se acrescentar quatro ferramentas _Things_: `list_things`, `create_thing`, `get_thing_last_seen` e `get_thing_timeline` | As ferramentas atuais já existem; as ferramentas _Things_ são propostas |
| Aplicação Altice | Um novo separador _Things_: objetos sugeridos, registo de objetos, lugares e máscaras, sensores a partir de uma frase, “Perguntar” e avisos | Proposto; o protótipo encontra-se na pasta `prototype/` do repositório |
| Notificações | Os avisos chegam ao telemóvel pelo serviço de notificações que a aplicação já usa | A confirmar com a Altice (§11) |

### O modelo de linguagem

O modelo de linguagem é chamado apenas pelo Serviço _ThingTracker_, nunca pelo _edge_, pela aplicação ou pelo servidor MCP, e só para três tarefas. Nos termos do MCP, o modelo nunca se liga ao servidor MCP: pede uma ferramenta, e é o serviço que a chama.

| Tarefa | Entrada | Saída | Frequência |
|---|---|---|---|
| Compilar uma frase numa regra | A frase e os objetos, lugares e dispositivos da casa | Uma regra na linguagem de sensores (§5) | Quando um utilizador cria um sensor |
| Responder a uma pergunta | A pergunta e a parte relevante da memória, em texto | Uma frase e uma referência a uma observação (com a respetiva fotografia) | Sempre que se faz uma pergunta |
| Avaliar um caso duvidoso | Um recorte e a pergunta da regra | Sim, não ou incerto, com a justificação | Raramente, só quando a confiança local é baixa |

Pode usar-se qualquer modelo capaz, desde que o contrato garanta que os dados não são usados para treino, inclua um acordo de tratamento de dados, ou DPA (“_Data Processing Agreement_”), e assegure o processamento na UE. O protótipo usa o _Claude Haiku 5.5_ e o _Claude Sonnet 5.5_.

As opções seguintes foram verificadas nos termos e na documentação de cada fornecedor a 18 de novembro de 2026:

| Opção | Cumpre? | Como | Cuidados |
|---|---|---|---|
| _Claude_, via _Amazon Bedrock_ | Sim | Perfil entre regiões `eu.`, chamado a partir de uma região da UE (se for chamado a partir de Londres ou de Zurique, também encaminha os pedidos para essas regiões); os dados de entrada não são usados para treino; DPA da AWS para o RGPD | A API da própria Anthropic não tem opção para a UE (só “us” e “global”). No _Bedrock_, os modelos _Claude Fable 5_, _5.1_ e _5.2_ exigem a retenção dos dados durante 30 dias, para revisão (`aws_review`), o que não acontece com o _Claude Haiku 5.5_ nem com o _Claude Sonnet 5.5_ |
| _Claude_, via _Google Vertex AI_ | Sim | _Endpoint_ multirregião `eu` (só Estados-Membros da UE) | |
| OpenAI, via _Azure_ (_DataZone EU_) | Sim | Processamento na _Data Zone_ da UE, que pode incluir países da EFTA (Noruega, Suíça); sem acesso por parte da OpenAI; sem uso para treino; DPA da Microsoft | Evitar as implementações “Global” |
| API da OpenAI com residência na UE | Sim, com condições | `eu.api.openai.com`, num projeto novo; a região é “_Europe (EEA + Switzerland)_” | Só as organizações elegíveis a podem ativar, e o envio de imagens nessa região exige uma aprovação adicional da OpenAI |
| _Gemini_, via _Vertex AI_ | Sim | _Endpoint_ `eu`, treino só com autorização, DPA do Google Cloud | A API para programadores do _Gemini_ não tem opção de processamento na UE, e os dados podem ser guardados temporariamente ou em _cache_ em qualquer país. Aos utilizadores do EEE, da Suíça ou do Reino Unido aplicam-se os termos de dados do nível pago, e só os serviços pagos os podem servir, pelo que o nível gratuito, que admite revisão humana, não pode ser usado |
| Mistral | Sim, com condições | Dados guardados na UE por omissão; inferência na UE só através de `api.eu.mistral.ai` (países da UE e da EFTA, a 1,1 vezes o preço do _endpoint_ global); DPA | O _endpoint_ por omissão é global, sem compromisso quanto ao local da inferência. O treino com os dados está ativo por omissão e desativa-se no menu _Privacy_ do _Admin panel_. Evitar os modelos _Labs_ e _Preview_ |
| _DeepSeek_ ou _Kimi_, alojados pelos fornecedores | Não | | Dados guardados na China (_DeepSeek_, aplicação _Kimi_) ou em Singapura (API do _Kimi_); o treino com o conteúdo é permitido; sem DPA. A autoridade italiana de proteção de dados (Garante) limitou o _DeepSeek_ (janeiro de 2025), e a autoridade de proteção de dados de Berlim considerou ilegais as suas transferências para a China (junho de 2025) |
| _DeepSeek_ (_open-weight_), alojado pela Altice | Sim | Licença MIT, modelos com visão | Nenhum dado sai da Altice |
| _Qwen_ (_open-weight_), alojado pela Altice | Sim; os modelos maiores, após verificação jurídica | _Qwen3.8-27B_: Apache-2.0, com visão | Os modelos maiores usam a “_Qwen Community License 1.0_” (_Flash-Next_) ou a “_Qwen3.8-Max License_” (_2.4T_). Ambas exigem a indicação visível do nome do modelo acima de 100 milhões de utilizadores mensais ou de 20 milhões de dólares de receita mensal. A verdadeira restrição é a licença separada exigida a quem explore um “_Model as a Service or AI Work Assistant business_” (a licença _Max_ acrescenta uma condição sobre a receita do grupo acima de 50 milhões de dólares); o uso interno está isento. Exige uma verificação jurídica, como no caso do _Kimi_ |
| _Kimi_ (_open-weight_), alojado pela Altice | Sim, após verificação jurídica | _K2.5_: “MIT modificada”; _K3_ e _K3.1-Pro_: “_Kimi K3 License_”; com visão | O _K2.5_ exige a indicação visível do nome do modelo acima de 100 milhões de utilizadores ativos mensais ou de 20 milhões de dólares de receita mensal. A licença do _K3_ acrescenta um acordo separado para os operadores de modelos como serviço (_model-as-a-service_) com receita superior a 20 milhões de dólares (§2–3 da licença). Dada a dimensão do grupo Altice, é necessária uma verificação jurídica |
| _Llama 3.2_ com visão / _Llama 4_ | Não | | As licenças excluem dos modelos multimodais as empresas cujo estabelecimento principal se situe na UE. O _Llama 4 Scout_ e o _Llama 4 Maverick_ são multimodais e estão abrangidos; só os modelos de texto _Llama 3.x_ podem ser usados |

Em qualquer implementação, fixam-se os _endpoints_ da UE, chamados a partir de uma região da UE, e nunca o “global”. Algumas zonas “UE” incluem também países do EEE ou da EFTA (a _Data Zone_ da UE do _Azure_, a região europeia da OpenAI e o _endpoint_ europeu da Mistral).

## 4. Funcionamento: os fluxos principais

Cada passo indica onde é executado e, quando há dados a atravessar a fronteira da casa, o que atravessa.

### 4.1 Adicionar uma câmara e os seus lugares

1. O utilizador instala a câmara e dá-lhe um nome (“Sala”), como faz com qualquer dispositivo na aplicação.
2. No _edge_, faz-se uma análise da divisão: o detetor percorre uma vez a imagem completa e propõe os lugares que reconhece (sofá, secretária, prateleira, porta) e os objetos que vê (caneca, portátil, comando).
3. Na aplicação, o utilizador aceita os lugares, acrescenta máscaras para as zonas que nunca devem ser analisadas (a porta de uma casa de banho, uma janela para a rua) e escolhe os objetos sugeridos.
4. Nada da análise sai de casa; para a plataforma seguem apenas os nomes aceites.

### 4.2 Adicionar um objeto

Há duas formas de começar e um único fluxo:
- Sugerido: a partir da análise da divisão, com um toque por objeto.
- Manual: o utilizador escreve um nome.

Em seguida:
1. Na aplicação, surge a indicação “Mostre-o à câmara”. O utilizador segura o objeto à frente de qualquer câmara e roda-o devagar durante cerca de 3 s. Em alternativa, pode tirar 3 fotografias com o telemóvel.
2. No _edge_, o detetor delimita o objeto em cerca de 8 imagens, o _DINOv2_ converte os recortes numa assinatura visual e o melhor recorte passa a ser a fotografia do objeto.
3. Do _edge_ para a plataforma seguem o nome do objeto e a sua fotografia (em miniatura), para que a aplicação os possa mostrar, e a assinatura visual, que fica guardada na base de dados da plataforma, associada ao cliente.
4. A partir daí, uma deteção de “chaves” só conta como as suas chaves se a assinatura visual corresponder, o que evita confundi-las com as chaves de uma visita.

### 4.3 Seguimento e última observação

A câmara fica em repouso enquanto nada acontece. Os modelos de visão locais só entram em funcionamento quando há movimento ou som, sinalizados pela deteção de movimento da própria câmara, pelo som ou por uma comparação de baixo custo entre imagens consecutivas. A partir desse momento, e enquanto a cena estiver a mudar, o _edge_ repete para cada câmara, a cada 0,5 a 1 s, o ciclo seguinte:
1. Capta-se uma imagem e o filtro de privacidade remove as zonas com máscara.
2. Detetam-se os objetos registados, os lugares e as pessoas.
3. Seguem-se as deteções, associa-se cada uma a um objeto pela assinatura visual e atribui-se depois ao lugar com que se sobrepõe; a profundidade distingue “em cima” de “atrás”.
4. Só se escreve uma observação quando algo muda, isto é, quando um objeto aparece, muda de lugar ou desaparece. O resultado são algumas dezenas de observações por hora, e não 3 600 imagens.
5. Se a câmara mudar de posição ou fizer _zoom_, os lugares voltam a ser encontrados pelo nome na imagem seguinte, sem nada para redesenhar. O seguimento recomeça e as assinaturas visuais voltam a associar as identidades.

Quando nada muda, nada é reanalisado e a memória mantém as últimas posições conhecidas.

### 4.4 Uma frase torna-se um sensor

Exemplo: “Põe a luz vermelha se a caneca ficar esquecida na secretária quando não estiver ninguém em casa.”
1. Da aplicação, através da plataforma, seguem para o modelo de linguagem a frase e os nomes dos objetos, dos lugares e dos dispositivos.
2. O modelo de linguagem devolve uma regra na linguagem de sensores (§5), que a aplicação apresenta em linguagem corrente para o utilizador confirmar.
3. Da plataforma para o _edge_ segue a regra.
4. No _edge_, o Motor de regras avalia-a sobre a memória a cada segundo, sem custo por verificação.
5. Quando a regra dispara, segue um evento do _edge_ para a plataforma. A plataforma envia a ação através do MCP (`update_device_capabilities`, luz vermelha) e uma notificação para a aplicação, com a miniatura.
6. As ações mais intrusivas (sirene, armar o alarme) pedem sempre primeiro um “sim” na aplicação.

### 4.5 Uma pergunta

“Onde estão as minhas chaves?”
1. Da aplicação para a plataforma segue a pergunta.
2. A plataforma pede ao _edge_ `get_thing_last_seen("chaves")`, que devolve o lugar, a hora e a miniatura.
3. Da plataforma para o modelo de linguagem seguem a pergunta e esse texto, sem qualquer imagem. O modelo redige a resposta na língua do utilizador: “Na mesa da entrada, às 8h42.”
4. Na aplicação, a resposta aparece acompanhada da fotografia.

## 5. A linguagem de sensores

Cada frase é compilada numa regra pequena e explícita. O Motor de regras executa regras e nunca interpreta texto livre, como se vê no exemplo seguinte:

```json
{
  "title": "Caneca esquecida na secretária",
  "when":  { "thing": "caneca", "in_place": "secretária", "for": "10m" },
  "and":   { "home": "empty" },
  "then":  [ { "notify": "A caneca ficou esquecida na secretária." },
             { "device": "Light", "set": { "color": "red" } } ],
  "confirm_before_acting": false,
  "cooldown": "30m"
}
```

A linguagem admite os seguintes tipos de regra:

| Regra | Exemplo |
|---|---|
| presente / ausente | “Avisa-me se as chaves não estiverem na mesa da entrada às 8h” |
| permanência | “…esquecida na secretária durante 10 minutos” |
| sair sem | “Avisa-me à porta se eu sair sem as chaves” (sensor de porta + presença do telemóvel + chaves ainda visíveis) |
| ausência até uma hora limite | “Se o gato não tiver ido à taça da água até às 18h” |
| pessoa num lugar | “Alguém na entrada quando não está em casa nenhum telemóvel conhecido” |
| verificação visual | Regras a que nenhum detetor consegue responder (“a planta está murcha?”): uma verificação de um recorte pelo modelo de linguagem, com limite de frequência |

Cada regra mostra ao utilizador, em linguagem corrente, o que observa e o que fará. Sempre que possível, as regras ficam guardadas como cenários da plataforma, para aparecerem na aplicação ao lado dos cenários existentes.

## 6. Modelo de dados

| Entidade | Campos principais | Onde fica | Retenção |
|---|---|---|---|
| Câmara | id, nome, _stream_, máscaras | _Edge_, plataforma | Enquanto estiver instalada |
| Lugar | id, nome, câmara, última caixa delimitadora | _Edge_; os nomes também na plataforma | Enquanto estiver definido |
| Objeto | id, nome, fotografia, categoria | _Edge_, plataforma | Até ser apagado |
| Assinatura visual | id do objeto, cerca de 8 _embeddings_ | _Edge_ (para os modelos locais); base de dados da plataforma, associada ao cliente | Até o objeto ser apagado |
| Observação | objeto, lugar, hora, caixa, confiança, miniatura | _Edge_ | 30 dias; depois é apagada |
| Presença | telemóvel conhecido, em casa / fora, hora | _Edge_ | 30 dias |
| Sensor | regra (§5), proprietário, ativo, histórico | _Edge_, plataforma | Até ser apagado |
| Evento | sensor, hora, elementos de prova, ação executada | _Edge_, plataforma | 90 dias (registo de auditoria das ações executadas na casa) |

## 7. Privacidade e segurança

A tabela seguinte indica o que atravessa a fronteira da casa.

| Dados | Saem de casa? |
|---|---|
| Vídeo, imagens completas | Não são enviados para análise. A visualização em direto e as gravações do próprio utilizador continuam a funcionar como hoje na aplicação Altice, através do respetivo _relay_ |
| Rostos, identidades | Só se a família o ativar. Desativado por omissão; a família regista uma pessoa, com o consentimento dessa pessoa. O padrão facial fica no _edge_; um evento pode levar o nome escolhido pela família (“A Ana chegou”) |
| Assinaturas visuais (_embeddings_) | Sim, para a base de dados da plataforma, associadas ao cliente. Uma cópia fica no _edge_, para os modelos locais |
| Nomes de objetos, nomes de lugares, miniaturas de objetos | Sim, para a plataforma, para que a aplicação os possa mostrar |
| Eventos (sensor disparado, objeto visto) | Sim, para a plataforma |
| Um recorte de uma zona | Só num caso duvidoso, para o modelo de linguagem sob contrato, que não o guarda |
| Perguntas e frases | Sim, para o modelo de linguagem sob contrato |

Aplicam-se os seguintes princípios:
- Minimização dos dados, prevista na alínea c) do n.º 1 do artigo 5.º do Regulamento Geral sobre a Proteção de Dados (RGPD), e proteção de dados desde a conceção, prevista no artigo 25.º, através de máscaras, imagens apagadas depois de usadas, nenhum vídeo guardado pelo _ThingTracker_ e reconhecimento de pessoas desativado por omissão.
- Prevê-se que as câmaras em casa exijam uma avaliação de impacto sobre a proteção de dados (AIPD, artigo 35.º), que se prepararia com a Altice antes de qualquer piloto.
- O reconhecimento de pessoas é apenas opcional: está desativado por omissão, é ativado pessoa a pessoa, com consentimento explícito, nos termos da alínea a) do n.º 2 do artigo 9.º do RGPD, e é processado no _edge_. O Regulamento Europeu da Inteligência Artificial classifica a identificação biométrica à distância como de risco elevado, pelo que esta funcionalidade exige uma revisão jurídica e uma AIPD antes do lançamento, como refere o sumário executivo.
- Segurança informática:
  - um único canal de saída autenticado por casa;
  - nenhuma porta aberta no _edge_;
  - os _tokens_ da plataforma ficam no _edge_, nunca na aplicação;
  - nenhum segredo no código;
  - cada ação fica registada com a regra e os elementos que a motivaram.
- Segurança das ações: nada de ruidoso (sirene, alarme) acontece sem a confirmação do utilizador, e o modelo de linguagem nunca é o único fundamento de um alarme.

## 8. Desempenho e custo

Medições feitas no Mac da equipa (GPU Apple, 18 de novembro, `prototype/vision/benchmark.py`, com uma imagem de teste de 640 × 400):

| Passo | Medido | Notas |
|---|---|---|
| Deteção com o _OWLv2_, 10 objetos nomeados | 557 ms por imagem | Encontrou a lâmpada (0,40) e a tomada (0,59) na imagem de teste |
| Assinatura visual com o _DINOv2_ | 22 ms por recorte | |
| _Depth Anything V2 Small_ | 55 ms por imagem | |
| Ciclo completo de perceção | Cerca de 0,65 s | Ou seja, cerca de 1,5 imagens por segundo, por câmara, neste Mac |
| Comando MCP a um dispositivo (desligar a tomada) | Cerca de 1,3 s por chamada | Medido a 16 de novembro (ver o documento sobre o MCP na prática) |
| Do evento à ação | Cerca de 2 a 3 s | Perceção, depois a regra (milissegundos) e por fim o MCP |

Quanto ao custo, distinguem-se duas parcelas:
- A perceção local não tem custo por imagem, pois custa apenas a eletricidade e o equipamento onde corre. No exemplo de 2 horas de movimento por dia, a eletricidade consumida pelos modelos fica em cerca de 0,14 € por mês (§3).
- O custo do modelo de linguagem resulta dos custos medidos por pedido, de cerca de 0,0003 USD por avaliação de um caso duvidoso (_Claude Haiku 5.5_) e de cerca de 0,003 USD por pergunta ou novo sensor (_Claude Sonnet 5.5_). No cenário base, o modelo de linguagem custa cerca de 0,43 € por casa e por mês (de 0,10 a 1,78 €, consoante o cenário), valor que se refere apenas ao modelo de linguagem. O caso de negócio detalha este cálculo e mostra que é o equipamento local, e não a IA, que determina a economia do serviço.

## 9. Decisões e alternativas rejeitadas

| # | Decisão | Alternativas | Justificação |
|---|---|---|---|
| D1 | A perceção corre em casa | Enviar as imagens para um modelo de visão na nuvem | Privacidade (nenhuma imagem sai de casa), custo (nulo por imagem), latência e funcionamento sem ligação à internet |
| D2 | O modelo de linguagem compila regras e não observa as imagens | Perguntar ao modelo, em cada imagem, se a resposta é sim ou não (o primeiro protótipo da equipa) | As chamadas por imagem custam dinheiro, acrescentam 1 a 3 s cada uma e dão respostas diferentes; as regras compiladas são baratas, imediatas e auditáveis |
| D3 | Lugares definidos pelo nome e encontrados em cada imagem | Retângulos em píxeis, desenhados uma única vez | Os retângulos deixam de servir quando a câmara muda de posição ou faz _zoom_, pelo que só se mantêm como máscaras de privacidade |
| D4 | Assinaturas visuais obtidas no registo | Afinar um detetor para cada objeto (_fine-tuning_) | O registo demora 3 s, não exige treino e funciona no _edge_ |
| D5 | Um separador na aplicação Altice existente | Uma aplicação _ThingTracker_ separada | Uma só aplicação, uma só autenticação e um único sítio para os avisos; é o caminho mais curto para a Altice lançar o serviço |
| D6 | Modelo de linguagem sob contrato, independente do fornecedor | Comprometer-se com um único fornecedor | Permite à Altice escolher pelo preço, pela residência dos dados na UE ou pelo alojamento próprio, e evita ficar preso a um fornecedor |
| D7 | Um único canal seguro entre a casa e a plataforma | Cada componente chama a nuvem | Há só um ponto a proteger e a auditar, e a plataforma controla que modelo vê o quê |
| D8 | Reconhecimento de pessoas opcional e no próprio dispositivo | Nunca, ou sempre ativo | Os cenários de pessoas autorizadas precisam dele. A desativação por omissão, o consentimento pessoa a pessoa e o processamento no dispositivo mantêm controláveis o risco jurídico (Regulamento da IA, artigo 9.º do RGPD) e a questão da confiança |

## 10. Protótipo e solução final

| Parte | Protótipo (sexta-feira) | Solução final |
|---|---|---|
| Câmaras | Câmara do portátil ou um vídeo gravado; a câmara do kit, quando o _stream_ responder | Câmaras do kit, por RTSP, na rede local |
| Perceção | Modelos locais instalados e com desempenho medido; a demonstração analisa recortes de zonas | Cadeia completa de perceção local, numa NPU do _gateway_ ou numa caixa _edge_ |
| Modelo de linguagem | _Claude Haiku 5.5_ / _Claude Sonnet 5.5_, desativados por omissão, com respostas simuladas | Qualquer modelo sob contrato (§3) |
| Regras | O modelo responde à pergunta de cada zona | Regras compiladas, executadas pelo Motor de regras (§5) |
| Aplicação | Uma réplica web da aplicação Altice, com o separador _Things_ | Dentro da aplicação Altice real |
| Ações nos dispositivos | Chamadas MCP implementadas, em modo de simulação salvo se forem ativadas | As mesmas ferramentas, mais as ferramentas _Things_ |

## 11. Questões em aberto para a Altice

1. A plataforma disponibiliza eventos ou notificações _push_ que se possam usar, em vez de consultar periodicamente o servidor MCP?
2. Que _gateways_ residenciais têm NPU e poderiam alojar o serviço local? Caso contrário, a Altice forneceria uma pequena caixa juntamente com a câmara?
3. O _edge_ pode ler diretamente o _stream_ RTSP da câmara na rede da casa, em vez de passar pelo _relay_ na nuvem?
4. A Altice acrescentaria as ferramentas _Things_ ao servidor MCP? Como se aprovam novas ferramentas?
5. Que contratos de modelos de linguagem tem a Altice em vigor (residência dos dados na UE, DPA)?
6. É possível apagar cenários através do MCP? Atualmente, só é possível criá-los.
