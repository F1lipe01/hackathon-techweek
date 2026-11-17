# Top 5 use cases: what to build, why, and how to pitch it

::: lead
Team IT-Porto · Challenge #3, Altice Labs: *Connected Homes Reimagined: AI at the service of the home* · Aveiro Tech City Hackathon 2026<br>
Version 3, Tue 17 Nov 2026, after two rounds of AI-assisted advisor review (§11). Written to final-report standard, for the team's decision before the Wednesday checkpoint.
:::

::: note
**How to read this.**
- **Language:** explanations are in English, the team's working language. Every **pitch script** and the **draft Sumário Executivo** are in European Portuguese, ready to use.
- **Sources:** every figure comes from [`docs/12-market-research.md`](../../docs/12-market-research.md), which gives its source link, year and indicator code. Figures were found by AI research agents and read at source on 17 Nov 2026; key figures were re-checked in a second pass (§10).
- **Labels:**
  - **Inference** marks our own reasoning, not a fact.
  - **Simulated** marks anything in a demo that is not live data from our kit.
  - **Untested** marks something the kit or the MCP should do but we have not yet seen it do.
- **The team decides.** This report ranks and recommends; it does not choose for us.
:::

## 1. Executive summary

**The problem we found.** In Portugal, the home itself can be a health problem, and older people carry most of it.

- **Damp:** **32.1 %** of people live with leaks, damp or rot (INE, 2025), and INE says this has worsened for three years. In 2023 Portugal was **2nd worst in the EU** (29.0 % against 15.6 %).
- **Cold:** **15.6 %** can't keep their home adequately warm, against 8.8 % in the EU (2025).
- **Older people:** among people aged 65+, Portugal is 2nd worst in the EU for damp (27.4 %, 2023) and joint 2nd for cold homes (22.2 %, 2025).
- **Living alone:** 517,146 people aged 65+ lived alone in 2021.
- **Online:** 36.07 % of people aged 65–74 had never used the internet in 2025.

**What our kit can do about it.** The live sensors are the ones these problems need:
- temperature and humidity;
- the window/door contact;
- smoke;
- the plug, which is also the one verified actuator.

Two behaviours the demo needs are **untested**: the contact changing from open to closed, and plug metering under a load. Both get tested before we build on them (§9). The camera and the bulb are not needed.

**The ranking** (seven candidates against the official criteria and weights; totals computed by script):

| # | Use case | Intermediate | Final | One line |
|---|---|---|---|---|
| **1** | **Casa Saudável**: damp and cold engine for every home | **8.00** | **8.00** | "Arejar ou aquecer?" The AI settles the trade-off and acts |
| **2** | **Casa que Cuida**: the same engine for a parent living alone | **7.50** | **7.60** | Watches the home, not the person; tells the family what a fault means |
| **3** | **Calor Certo**: cold-home comfort and cost coach | **6.75** | **7.10** | 18 °C and what it cost, in euros |
| **4** | **Vigia da Casa**: fire and safety-net watch | **7.00** | **6.80** | Smoke with context; a detector that checks itself |
| **5** | **Modo Ausência**: away-from-home caretaker | **6.00** | **6.10** | "I'm away until Sunday." It checks the house and says what it can't confirm |
| 6 | Regras em Conversa: AI rule builder | 5.50 | 5.90 | Already on Altice's roadmap |
| 7 | Perdidos e Achados: lost & found with the camera | 4.00 | 4.50 | Camera has no power; the MCP has no vision; weak evidence |

**Recommendation: lead with Casa Saudável as the product, and use an older mother living alone as its persona.**
- **The pitch is ready** in §3 (*Pitch A*). The jury hears the new part first: the home decides between airing and heating, live. Then the human part: the daughter is told, without the mother needing an app.
- **Why it leads:**
  - Humidity appears nowhere in Altice's published offer.
  - It runs on device types the platform already supports.
  - Any broadband household is a customer.
  - Leading with the home, not the person, avoids spending the 1-minute Q&A on "isn't this Family Care?".
- **#2's parts become extensions** (the family view, and what a fault means for the house); #3 and #4 become features (cost display, smoke).
- **#5 is not built.**
- **Checkpoint question that could change this:** "Do Family Care or eHealth Smart Assisted Living use temperature or humidity, or alert the family about home conditions?" If yes, drop the persona and pitch Casa Saudável for all households (*Pitch B*, §3).

**What changed after review (§11).**
- Routine monitoring of the older person was removed (Altice already promises it).
- Heaters are switched off only, never on remotely.
- Untested kit behaviour is labelled.
- A merged pitch was written.
- Two scores came down.

## 2. What we have: the shared foundation

### 2.1 The kit and the MCP, honestly

| Part | Status, 17 Nov |
|---|---|
| Temperature + humidity sensor | ✓ Live. Reports every 5–30 min; 22.6 °C and 64.3 % read on 16 Nov |
| Window/door contact | ✓ Live, reads "open". **An open → closed change through the MCP is untested** |
| Smoke sensor | ✓ Live (state, tamper, battery). What the test button does is unknown: ask the mentors |
| Plug | ✓ **On/off verified** by ID and by name (device acknowledged in ~1 s). Metering fields exist (W, V, A, daily counter) but are **untested with a load**; the daily counter's unit is unknown |
| Security hub | ✓ Alarm mode, network mode (ethernet/Wi-Fi/cellular) and battery readable. Battery read **0** on 16 Nov, and the hub has no SIM. **Arming untested**: Home mode has a 0 s delay, and the arming tool is mislabelled `readOnlyHint: true` |
| Data freshness | ✓ Every device reports its last contact. The bulb had not reported since 04 Nov on 17 Nov, a live example of "I can't confirm" (check again on Friday) |
| IPMA open data (outdoor) | ✓ Tested 17 Nov: hourly temperature and humidity from 227 stations |
| Camera / colour bulb | ✗ No 12 V adapter / not reporting. Not needed by any of the top 5 |
| MCP limits | Current state only (**no history**), **no notifications**, **no delete-scenario**, so every scenario we create is permanent |

Sources: [`docs/10-mcp-in-practice.md`](../../docs/10-mcp-in-practice.md), [`docs/11-project-baseline.md`](../../docs/11-project-baseline.md).

### 2.2 One plug, one contact: who plays what

The kit has **one** plug and **one** contact sensor. Each demo gives them one role; the product would have one plug per appliance and one contact per window or door.

| Device in the kit | #1 Casa Saudável | #2 Casa que Cuida | #3 Calor Certo | #4 Vigia da Casa | #5 Modo Ausência |
|---|---|---|---|---|---|
| Contact (×1) | Window | Window | Window | — | Door |
| Plug (×1) | Dehumidifier (a lamp stands in, labelled) | Same as #1; on smoke it is cut, as a heater would be | Heater, **switched off only** | Heater, cut on smoke | Presence lamp |
| Temp/humidity (×1) | ✓ | ✓ | ✓ | — | — |
| Smoke (×1) | — | ✓ | — | ✓ | — |
| Hub | — | Network mode and battery: "what a fault means" | — | Same as #2 | Arming (simulated) |

### 2.3 One engine for all five

| Step | What it does | On Friday | Real or simulated | In the product |
|---|---|---|---|---|
| **1. Poll** | Reads every device, plus freshness | Our MCP client ([`mcp/client/chmcp.py`](../../mcp/client/chmcp.py)) calls `get_home_devices` (read-only) every 60 s, and every few seconds during the demo if the MCP allows it (test Thursday) | **Real** | Platform events, not polling |
| **2. Log** | Keeps the history the MCP doesn't | SQLite on a laptop | **Real** for Friday; **simulated** for "last week" (replayed, labelled) | Platform history |
| **3. Reason** | Context (IPMA weather, tariff, time) + intention (the household's preferences) + information (sensors) | Deterministic rules decide. An LLM turns what the family says into confirmed settings ("a mãe tem asma; não a acordem antes das 9"), explains decisions and answers questions | **Real** | Same split; the LLM is called only for setup, explanations and questions |
| **4. Act** | Switches the plug; at most one native scenario | `update_device_capabilities` (verified). One `post_new_scenario`, because it can't be deleted: smoke → plug off, if the mentors confirm a smoke trigger works (**untested**) | **Real** (plug) | Native scenarios, so it works even when the AI is down |
| **5. Explain** | Plain-Portuguese messages; answers "Como está a casa?" (how's the house?) | A Telegram bot as a **stand-in** | Real channel; the family member is a team member (**simulated** persona) | The operator app's push, then SMS, then voice call (channels the platform already uses for alerts) |

**Design rules** (each one doubles as a Q&A answer):
1. **Honest about data.** If a device hasn't reported, the agent says so and doesn't guess.
2. **Never switch a heater on remotely.** Many portable-heater manuals warn against use with timers or remote switches. We have not checked a specific standard; it is the safe choice anyway. The agent may **suggest** heating and may **switch a heater off** (smoke, a window left open, a time limit). It never switches one on. Alarm changes always need an explicit "yes", and the agent never sends `factoryReset` or `restart`.
3. **Response time is the poll interval.** On Friday, "at the next check". In the product, platform events and native scenarios react at once.
4. **No camera, no microphone.** Privacy-first, and independent of the device that doesn't work.
5. **No invented thresholds.** WHO backs 18 °C as a minimum indoor temperature (strong recommendation) and says older people may need more. WHO gives **no** humidity threshold, so ours is a configurable setting, and we say so.
6. **The appliance must resume on power.** A dehumidifier with electronic controls may not restart when the plug switches on, so test it (§9).

<div class="pagebreak"></div>

## 3. Use case #1: Casa Saudável

> **"Arejar ou aquecer?" (air the house, or heat it?) The home settles the trade-off between damp and cold, acts, and says what it cost.**
> Damp and cold engine for every home · Intermediate **8.00** · Final **8.00**

### The problem, in figures

| Fact | Value | Source |
|---|---|---|
| People living with leaks, damp or rot | **32.1 %** in 2025, up from 29.0 % (2023) and 30.9 % (2024). INE: "agravamento nos últimos três anos" (worsening over the last three years) | INE, ICOR 2025, Figura 22 |
| EU comparison | **PT 29.0 % · ES 23.0 % · FR 21.1 % · EU27 15.6 %**; Portugal 2nd of 27 | Eurostat `ilc_mdho01`, 2023 |
| People aged 65+ | **PT 27.4 %** · EU27 12.1 %; 2nd in the EU | same, 2023 |
| Unable to keep the home warm | **PT 15.6 %** · FR 11.5 % · EU27 8.8 %. One adult aged 65+: **PT 26.9 %** · EU27 11.4 % | Eurostat `ilc_mdes01`, 2025 |
| National targets for 2030 | Damp **20 %** (25.2 % in 2020); cold homes **10 %** (17.5 % in 2020) | Government resolution RCM n.º 11/2024 (national energy-poverty strategy) |
| Health | Damp and mould raise the risk of respiratory symptoms, infections and worse asthma. WHO sets **no** numeric humidity threshold | WHO, dampness and mould guidelines, 2009 |
| Minimum temperature | 18 °C, **strong** recommendation; possibly higher for older people | WHO Housing and Health Guidelines, 2018 |

**Inference:**
- Damp is the one problem here whose indicator is moving *away* from its national 2030 target.
- Damp and cold pull in opposite directions: airing removes water but also heat. Settling that trade-off is reasoning, not a command.

### What it does

- **Measures the real amount of water in the air.** It converts indoor temperature and relative humidity into **absolute humidity** (g/m³), then does the same for the nearest IPMA station.
  - Opening the window only helps when the outdoor air holds less water. Comparing relative humidity alone is a common mistake.
- **Advises with a countdown:** "Abra a janela da sala agora; feche às 11h12. Lá fora o ar tem menos água e 10 minutos chegam." (Open the living-room window now; close it at 11:12. The outside air holds less water, and 10 minutes is enough.)
  - The length comes from the temperature difference, so airing doesn't turn into heating the street.
- **Confirms with the window contact** that the window was opened and closed, and reminds you if it wasn't.
- **Acts when airing won't do.** If humidity stays high at the next reading (5–30 min later), it switches on the dehumidifier on the plug, and reports the energy the plug measured multiplied by your tariff.
- **Watches the cold side.** It counts hours below 18 °C (or the household's own higher target) and warns of overnight condensation risk, comparing the indoor dew point with IPMA's forecast minimum.
- **Weekly message:** hours above your humidity setting, hours below your temperature target, what it did, what it cost.

### Build and demo

| Piece | Status | Build |
|---|---|---|
| Indoor temperature and humidity | ✓ Live | Engine + absolute-humidity and dew-point calculation |
| IPMA outdoor data | ✓ Tested | Fetch the station nearest the venue |
| Window contact | ✓ Live; **open → closed untested** | Thursday test (Wednesday morning if possible); airing logic |
| Dehumidifier on the plug | Plug on/off ✓; appliance needed, and it must resume on power | A lamp stands in if needed (**labelled**) |
| Energy measured by the plug | **Untested with a load** | Thursday test with a kettle or lamp |

**Demo (≈40 s).** Open the window at the start of the block and keep talking while the next check picks it up.
1. The live indoor reading beside the live IPMA reading.
2. The agent's advice, with its countdown.
3. The window change detected at the next check, and the agent confirming.
4. The "daughter" (a team member) asks "Como está a casa da mãe?" and gets a live answer with each reading's time.

**If the contact test fails,** the window step is shown as a recording, and said aloud. **Simulated, and said aloud:**
- the multi-day history;
- the weekly report;
- the dehumidifier step, which in reality waits for the next humidity reading 5–30 min later and is shown with the time shortened.

### Scores

| Criterion | Score | Why |
|---|---|---|
| Fit | 8 | Daily and preventive. The AI settles a real trade-off (water against heat against cost) that a single rule can't. Less emotional than #2 on its own, which is why Pitch A uses the persona |
| Adoption | 9 | Humidity appears nowhere on Altice's Cognitive Home page or in its 2025 brochure. Device types the platform already supports; any broadband household is a customer; low privacy risk |
| Feasibility | 7 | Sensors live, but the contact transition, plug metering, the appliance restart and the scenario trigger are all untested. Needs an appliance at the venue |
| Replicability | 8 | The same Eurostat indicator exists EU-wide (France 21.1 %, Spain 23.0 %, Cyprus 32.1 %); a smaller problem in the north |
| Presentation | 8 | Strong figures and a window step that can be live if the test passes. With the persona, a human story |
| Documentation | 8 | Strong official sources; no primary user research yet |

### Pitch A (recommended, 3 min, PT-PT): Casa Saudável, told through Dona Maria

::: pitch
**[Gancho]** A Dona Maria tem 81 anos e vive sozinha. Todos os invernos ouve o mesmo conselho: «areje a casa». E a casa fica mais fria, e continua húmida. A Dona Maria é uma personagem; os números não são.

**[Problema]** Em 2025, mais de um quarto das pessoas com 65 ou mais anos que vivem sozinhas, 26,9%, não conseguia manter a casa aquecida: mais do dobro da média europeia. Entre as pessoas com 65 ou mais anos, Portugal é o segundo país da União Europeia com mais humidade em casa. A OMS liga a humidade a problemas respiratórios e recomenda pelo menos 18 graus no inverno. E arejar e aquecer puxam em sentidos opostos: abrir a janela tira humidade, mas também tira calor.

**[Solução]** A Casa Saudável resolve este dilema com sensores que a plataforma da Altice já integra e com os dados abertos do IPMA. O sistema calcula a quantidade real de água no ar, dentro e fora de casa, e decide: «Abra a janela agora; feche às 11h12.» Confirma pelo sensor que a janela foi fechada. Se arejar não chegar, liga o desumidificador. Um aquecedor, nunca o liga à distância: sugere, e a pessoa decide.

**[A família]** A Dona Maria não tem de fazer nada, nem de usar uma aplicação: 36% das pessoas entre os 65 e os 74 anos nunca usaram a internet. Quem recebe as mensagens é a filha: «A sala da sua mãe está a 15,8 graus desde ontem às 18h. Sugiro telefonar-lhe.»

**[Demonstração]** *[abrir a janela no início do bloco e continuar a falar]* Vejam: este é o valor real do sensor, e este é o da estação do IPMA mais próxima. Abrimos a janela e, na verificação seguinte, o sistema deteta-o e responde. A filha, que aqui é um de nós, pergunta no telemóvel: «Como está a casa da mãe?» A resposta vem deste kit, ao vivo, com a hora de cada leitura. O histórico de vários dias é simulado, e está identificado.

**[Porquê a Altice]** Para a Altice, não há hardware novo, e a humidade ainda não está na sua lista de casos de uso. Serve qualquer casa com banda larga, e a filha pode juntar a casa da mãe à sua conta, com a gestão de várias casas que a plataforma já prevê. Complementa o Family Care: o Family Care vê a pessoa; nós vemos a casa.

**[Fecho]** A casa já está conectada. *[pausa]* Agora também sabe cuidar de quem lá vive.
:::

**Timing:** ≈390 words including the demo narration, about 2:45 at a steady pace. If a rehearsal runs over, cut the Family Care sentence first (keep it for Q&A).

**If the contact test fails,** replace the demo's second sentence with: «Este passo é uma gravação, e está identificado.»

### Pitch B (all households, 3 min, PT-PT)

Use this if the checkpoint says older-person care is covered on Altice's side.

::: pitch
**[Gancho]** «Areje a casa.» É o conselho de sempre. E, muitas vezes, falha.

**[Problema]** Em 2025, 32,1% dos portugueses viviam numa casa com infiltrações, humidade ou apodrecimento, e o INE regista um agravamento nos últimos três anos. Em 2023, Portugal foi o segundo país da União Europeia com mais humidade em casa, com quase o dobro da média europeia. A Organização Mundial da Saúde associa casas húmidas a mais sintomas respiratórios e crises de asma. Ao mesmo tempo, 15,6% dos portugueses não conseguem manter a casa aquecida. E arejar e aquecer puxam em sentidos opostos: abrir a janela tira humidade, mas também tira calor e custa dinheiro.

**[Solução]** A Casa Saudável resolve este dilema com os sensores que a plataforma da Altice já integra (temperatura e humidade, o sensor da janela e a tomada inteligente), mais os dados abertos do IPMA. O sistema calcula a quantidade real de água no ar, dentro e fora de casa, e a inteligência artificial explica: «Abra a janela agora; feche às 11h12. Lá fora o ar tem menos água do que cá dentro, e 10 minutos chegam.» Confirma pelo sensor que a janela foi fechada. Se arejar não chegar, liga o desumidificador na tomada e diz quanto gastou.

**[Além dos comandos]** Ninguém deu uma ordem. A casa juntou o contexto, a intenção de quem lá vive e a informação dos sensores, através do MCP. Depois agiu, e explicou porquê.

**[Demonstração]** *[abrir a janela no início do bloco]* Vejam: este é o valor real do sensor, e este é o da estação do IPMA mais próxima. Abrimos a janela e, na verificação seguinte, o sistema deteta-o e responde. O histórico de vários dias que vão ver é simulado, e está identificado.

**[Porquê a Altice]** Para a Altice, não há hardware novo: o sensor e a tomada já existem na plataforma. E a humidade ainda não está na lista de casos de uso da Altice. Serve qualquer casa com banda larga, e sobretudo as pessoas com 65 ou mais anos: em Portugal, 27,4% vivem com humidade em casa, o segundo valor mais alto da União Europeia.

**[Fecho]** A meta nacional é descer para 20% até 2030, e estamos a afastar-nos dela. Esta casa ajuda a voltar ao caminho.
:::

### Likely Q&A

1. **"Where is the AI, if rules decide?"** The safety decisions are rules on purpose: auditable, and able to run as native scenarios. The model turns what the family says into confirmed settings ("a mãe tem asma; não a acordem antes das 9"), combines indoor, outdoor and cost data into one piece of advice, and answers any question with live data.
2. **"Why not a dehumidifier with its own humidistat?"** It doesn't know the window is open, what the air outside holds, or what it costs, and it never says that ten free minutes of airing would do.
3. **"Which humidity level triggers it?"** A configurable setting. WHO publishes no numeric limit, and we don't invent one. The airing advice is physics (absolute humidity), not a threshold.
4. **"Doesn't Reliable Security already cover water?"** It alerts on water *leaks*, which is a burst pipe. Damp and condensation are a slow health problem that no leak sensor sees.
5. **"Does it reduce mould?"** We claim behaviour (air at the right time, dehumidify only when needed, measure it). Without field data, we claim no percentage.

<div class="pagebreak"></div>

## 4. Use case #2: Casa que Cuida

> **The Casa Saudável engine for a parent who lives alone. It watches the home, not the person, and tells the family what a reading or a fault means.**
> Intermediate **7.50** · Final **7.60**

In the recommended plan, these parts extend Pitch A. Used alone, #2 leads with the older person.

### The problem, in figures

| Fact | Value | Source |
|---|---|---|
| People aged 65+ living alone | **517,146** in 2021 (2011: 406,942) | INE, Census 2021, table Q1.04 (our sum of INE's age bands) |
| Unable to keep the home warm, aged 65+ | **PT 22.2 %** · EU27 8.4 %; joint 2nd with Bulgaria, after Lithuania (25.5, provisional), of 26 countries reporting | Eurostat `hlth_dhc140`, 2025 |
| Same, one adult aged 65+ (household type) | PT 26.9 % · EU27 11.4 % | Eurostat `ilc_mdes01`, 2025 |
| Living with damp, aged 65+ | **PT 27.4 %** · EU27 12.1 %; 2nd in the EU | Eurostat `ilc_mdho01`, 2023 |
| WHO | 18 °C minimum; "a higher minimum… may be necessary for vulnerable groups including older people" | WHO 2018, §4.1 |
| Never used the internet, ages 65–74 | **PT 36.07 %** · EU27 16.4 % | Eurostat `isoc_ci_ifp_iu`, 2025 |
| Flagged by the GNR as alone, isolated or vulnerable | 43,074 (GNR territory only; three conditions combined) | GNR, Censos Sénior 2025 |

### What we deliberately left out, and why

Altice already covers routine and health monitoring:
- **Aging in place.** Its 2025 brochure promises alerts "when people forget to engage in certain activities or anomalies are detected, such as falls" (our reading of multi-column text; docs/12 §5).
- **Family Care** "sends alerts to caregivers when an anomaly is detected in an elderly or sick person", with "motion sensors and the existing Wi-Fi network".
- **eHealth Smart Assisted Living** offers remote health monitoring.

So version 1's "no door or kettle activity by 08:15" alert is **removed**. Casa que Cuida watches **the home's conditions** and leaves routine to Family Care.

### What it does

- **Tells the family what the home is doing:** "A sala da sua mãe está a 15,8 graus desde ontem às 18h. Sugiro telefonar-lhe e propor ligar o aquecedor." (Your mother's living room has been at 15.8 °C since 6 pm yesterday. I suggest calling her and offering to switch the heater on.) The family chooses the threshold, at or above WHO's 18 °C.
- **Runs the Casa Saudável engine:** airing at the right time, the dehumidifier when needed, overnight condensation warnings.
- **Answers "Como está a casa da mãe?"** (how is mum's house?) with conditions first and the time of each reading. Summaries, not a minute-by-minute log.
- **Says what a fault means for the house.** The platform already knows when the hub changes state. We tell the daughter the consequence: "Faltou a luz em casa da sua mãe às 16h42; o hub está na bateria. A sala vai arrefecer, e o detetor de fumo só é vigiado enquanto a bateria durar." (The power went off at your mother's at 16:42; the hub is on battery. The living room will cool, and the smoke detector is watched only while the battery lasts.)
  - This reads the hub's network mode and battery state. **Untested**: our hub has no SIM and its battery read 0 on 16 Nov.
  - The Iberian blackout of 28 April 2025 cut power across mainland Portugal and Spain (ENTSO-E). **Inference:** that is when a family would want this message.
- **Smoke:** the family is alerted, and the appliance on the plug is switched **off**.

### Who it is for, and who pays

- **The person at home** does nothing, and nothing in their routine changes.
- **The person who uses it** is a daughter, son or carer with a smartphone.
- **How it is sold** (inference, to confirm on Wednesday):
  - Altice's brochure lists **"Multiple home management"**, so the first customer could be the adult child who is already a broadband customer and adds the mother's home.
  - Where there is no fibre, an LTE hub covers the house; the kit's gateway is an LTE IoT gateway.
  - Altice Labs licenses the platform to operators (B2B2C). SFR is confirmed as a customer; MEO is not named in Altice's material.
- **Reach:** only 8.8 % of Portuguese aged 65–74 use any connected-home system (Eurostat, 2024). Damp hits 38.4 % of people at risk of poverty (2023). **Inference:** the national energy-poverty strategy is the route to a pilot for the poorest homes, to discuss with Altice.

### Consent, privacy and GDPR

Three different people are involved: the person at home, the account holder and the payer. Home-condition data used for care **may** be treated as health data (GDPR Art. 9). That is our reading, to confirm. Design answers:
- the older person's explicit consent;
- no camera or microphone;
- summaries only, no raw timeline;
- data minimisation;
- an LLM provider acting as a processor, with EU processing chosen where available.

Open question: what happens if the person can no longer consent (Portugal's "maior acompanhado" regime).

### Build and demo

| Piece | Status | Build |
|---|---|---|
| Casa Saudável engine | See #1 | Shared |
| Family channel | Not in the MCP | Telegram bot (**stand-in** for push, SMS or voice) + LLM answers from live MCP reads |
| "What a fault means" | Freshness ✓; hub network mode and battery readable | Rules on hub state. **Test on Thursday** how a powered-off hub shows, and that it reconnects cleanly (press no buttons) |

**Demo:**
- **Live:** the "daughter" asks and gets an answer with reading times. Also the bulb with no report since 4 November, a real stale device (check on Friday; fallback: the camera, silent since 9 November).
- **Simulated, and said aloud:** the older person and the daughter are personas; any multi-day history; a power-cut message, if shown, uses a shortened wait.

### Scores

| Criterion | Score | Why |
|---|---|---|
| Fit | 9 | The same reasoning engine plus a family-facing assistant that explains consequences. Useful and beyond commands |
| Adoption | 6 | Sits beside Family Care, Aging in place and SmartAL, all aimed at older people. Routine removed, but the space is crowded. "Multiple home management" helps; consent and GDPR are still open |
| Feasibility | 7 | All live; hub-state behaviour and reconnection need testing; our own channel |
| Replicability | 8 | Living alone is more common elsewhere (EU 32.2 %, France 37.1 %), but cold and damp among people aged 65+ in France are near the EU average (10.2 %, 13.0 %). The worst areas are in southern and eastern Europe |
| Presentation | 8 | A human story, but little *action* in its own demo; strongest when combined with #1, as in Pitch A |
| Documentation | 8 | Census, Eurostat, WHO, GNR; payer and consent model still to confirm |

### Pitch (3 min, PT-PT): the older-person face, if used on its own

::: pitch
**[Gancho]** Em 2021, mais de 517 mil pessoas com 65 ou mais anos viviam sozinhas em Portugal. Mais de um quarto das que vivem sozinhas, 26,9%, não conseguia manter a casa aquecida em 2025.

**[Problema]** Entre as pessoas com 65 ou mais anos, Portugal é o segundo país da União Europeia com mais humidade em casa. E está em segundo lugar, empatado, na percentagem de pessoas que não conseguem manter a casa aquecida: 22,2%, mais do dobro da média europeia. A Organização Mundial da Saúde faz uma recomendação forte: pelo menos 18 graus em casa no inverno, e talvez mais para os mais velhos. E 36% das pessoas entre os 65 e os 74 anos nunca usaram a internet. *[pausa]* Uma aplicação para o idoso não resolve.

**[Solução]** A Casa que Cuida não vigia a pessoa: vigia a casa. A rotina já tem soluções, incluindo na plataforma da Altice. Nós olhamos para o que a casa está a fazer à saúde de quem lá vive. A família recebe, em português simples: «A sala da sua mãe está a 15,8 graus desde ontem às seis da tarde. Sugiro telefonar-lhe e propor ligar o aquecedor.» Ou: «Hoje é um bom dia para arejar a sala: lá fora o ar tem menos água.» O idoso não tem de fazer nada.

**[O que uma falha significa]** Um alarme comum avisa que o equipamento falhou. Nós dizemos à família o que isso quer dizer: «Faltou a luz em casa da sua mãe às 16h42. A sala vai arrefecer, e o detetor de fumo só é vigiado enquanto a bateria durar.»

**[Demonstração]** Vejam: a filha, que aqui é um de nós, pergunta no telemóvel «Como está a casa da mãe?». A resposta vem deste kit, ao vivo, com a hora de cada leitura. E reparem: a lâmpada não comunica desde 4 de novembro, e é verdade. *[confirmar na sexta de manhã; alternativa: a câmara, sem contacto desde 9 de novembro]* A senhora e a filha são personagens; os dados são reais.

**[Porquê a Altice]** Complementa o Family Care, sem sensor de movimento nem câmara. E a filha pode juntar a casa da mãe à sua conta, com a gestão de várias casas que a plataforma já prevê.

**[Fecho]** A casa já está conectada. *[pausa]* Nós pusemos a casa a cuidar de quem lá vive.
:::

**Stretching it to the 5-minute final:**
- Add replicability: "Na União Europeia, 32,2% das pessoas com 65 ou mais anos vivem sozinhas; em França, onde a SFR já vende um serviço desenvolvido pela Altice Labs, 37,1%." (In the EU, 32.2 % of people aged 65+ live alone; in France, where SFR already sells a service developed by Altice Labs, 37.1 %.) Add that the worst cold and damp areas are in southern and eastern Europe.
- Add the safety rules (never switches a heater on; confirmation before any alarm change).
- Add consent and the business model.

### Likely Q&A

1. **"Isn't this Family Care?"** Family Care watches the person; we watch the home's conditions. In 15 seconds: "O Family Care vê a pessoa; nós vemos a casa." (Family Care sees the person; we see the house.)
2. **"Doesn't our hub already report when it goes offline?"** "A plataforma sabe que o hub mudou de estado; nós dizemos à filha o que isso significa: faltou a luz, a sala vai arrefecer, o detetor só é vigiado enquanto houver bateria." (The platform knows the hub changed state; we tell the daughter what it means: the power went off, the room will cool, the detector is watched only while there's battery.)
3. **"Why not switch the heater on automatically?"** Nobody should switch a heater on, unseen, in an 80-year-old's room. We suggest; a person decides; we only switch off.
4. **"Who pays, and does it reach the homes in your statistics?"** "O primeiro cliente é o filho que já é cliente e junta a casa da mãe; à mãe não pedimos nada. Para as casas mais pobres, a estratégia nacional de pobreza energética é o caminho para um piloto, a discutir convosco." (The first customer is the son who's already a customer and adds his mother's home; we ask nothing of the mother. For the poorest homes, the national energy-poverty strategy is the route to a pilot, to discuss with you.)
5. **"What does it cost to run?"** We measure tokens per answer on Friday's runs and give € per home per month in the final. No figure before we have measured it.

<div class="pagebreak"></div>

## 5. Use case #3: Calor Certo

> **Says when a room is below a healthy temperature, suggests when to heat, and shows what it cost.**
> Cold-home comfort and cost coach · Intermediate **6.75** · Final **7.10**

### The problem, in figures

| Fact | Value | Source |
|---|---|---|
| Unable to keep the home adequately warm | **PT 15.6 % · FR 11.5 % · EU27 8.8 %** | Eurostat `ilc_mdes01` / INE, 2025 |
| Same, people at risk of poverty | PT 30.6 % · EU27 19.6 % | same |
| Arrears on utility bills | **PT 3.6 %** · EU27 7.0 % | Eurostat `ilc_mdes07`, 2025 |
| Household electricity price (band DC, all taxes) | PT €0.2367/kWh · EU27 €0.2832 | Eurostat `nrg_pc_204`, 1st half 2026 |
| National target | 10 % by 2030 (17.5 % in 2020) | RCM n.º 11/2024 |
| Social electricity tariff | 747,292 beneficiaries (electricity) | DGEG, Aug 2026 |

**Inference:** Portuguese households rarely fall behind on bills (3.6 %), yet many are cold. They appear to under-heat. What helps is making the cost of healthy heating known and small.

### What it does

- Compares room temperature with **18 °C**, or the household's own higher target, at the times that matter.
- **Suggests** heating on waking and before bed, rather than all evening. It shows the **cost in euros**: the energy the plug measured multiplied by the tariff the user enters (the MCP can't set a tariff).
- **Switches the heater off** if the window has been open for a while, or after the household's time limit. **It never switches one on.**
- **Monthly:** hours below the target, kWh, euros. No savings figure is claimed without data.

### Build and demo

- **Live, if Thursday's tests pass:** temperature; plug power; the window warning.
- **Simulated:** the monthly report.

### Scores

| Criterion | Score | Why |
|---|---|---|
| Fit | 7 | Useful; close to classic energy management |
| Adoption | 6 | **Overlaps** Altice's energy management (dashboard, alerts, Eco Mode, cheapest-time automation) and comfort automation ("temperature adjustments based on occupancy"). New: a health target and cost in conversation |
| Feasibility | 7 | Plug metering untested; we hold the tariff; never switching on limits automation |
| Replicability | 8 | The same Eurostat indicator exists EU-wide |
| Presentation | 7 | Watts turning into euros is concrete; less emotional |
| Documentation | 8 | Eurostat, INE, WHO, RCM 11/2024, DGEG |

### Pitch (3 min, PT-PT)

::: pitch
**[Gancho]** Em Portugal, não deixamos de pagar as contas. Ao que parece, deixamos de aquecer a casa.

**[Problema]** Em 2025, só 3,6% dos portugueses tinham contas da luz, da água ou do gás em atraso, cerca de metade da média europeia. Mas 15,6% não conseguiam manter a casa adequadamente aquecida, cerca de 1,8 vezes a média europeia (8,8%). Entre as pessoas em risco de pobreza, eram 30,6%. A Organização Mundial da Saúde recomenda pelo menos 18 graus em casa no inverno.

**[Solução]** O Calor Certo usa o sensor de temperatura e a tomada inteligente, que mede a energia. Diz quando a sala está abaixo dos 18 graus e sugere aquecer ao acordar e antes de deitar, em vez da noite inteira. E mostra em euros quanto custou: a energia medida pela tomada, multiplicada pelo preço do tarifário. Se a janela ficar aberta com o aquecedor ligado, avisa e pode desligá-lo. Ligar um aquecedor à distância, isso nunca faz: sugere, e a pessoa decide.

**[Demonstração]** *[só se os testes de quinta passarem; senão, gravação identificada]* Ligamos um aparelho à tomada: na verificação seguinte, a potência aparece e o assistente diz quanto custa por hora. Abrimos a janela: na verificação seguinte, chega o aviso. O relatório mensal que vão ver é simulado.

**[Porquê a Altice]** Não substitui a gestão de energia da Altice: dá-lhe um objetivo de saúde. O painel mostra quilowatts; o Calor Certo diz se a sala chegou aos 18 graus e quanto custou.

**[Escala]** A estratégia nacional quer reduzir para 10%, até 2030, a percentagem de pessoas que não conseguem aquecer a casa. Há 747 292 beneficiários da tarifa social de eletricidade: um canal possível para chegar a quem mais precisa, e uma ideia para discutirmos.

**[Fecho]** Calor certo: nem mais, nem menos, e sempre a saber quanto custa.
:::

**Q&A notes:**
- **Overlap with Altice's energy management:** admit it, then point to the health target.
- **"Does it save money?":** we show measured cost and claim no percentage.
- **The social-tariff channel** is an idea for discussion, not an agreement.

<div class="pagebreak"></div>

## 6. Use case #4: Vigia da Casa

> **A smoke detector that does more than beep: it cuts the heater, tells the family, checks itself, and explains what a fault means.**
> Fire and safety-net watch · Intermediate **7.00** · Final **6.80**

### The problem, in figures

| Fact | Value | Source |
|---|---|---|
| Dwelling fires, mainland | **5,182**, 77.24 % of fires in buildings in use | ANEPC, SCIE yearbook 2025 |
| Deaths | 37 in urban fires, **30 of them in dwellings** (counted at the scene); an average of 35 a year since 2020 | same |
| At night | 35.82 % of dwelling fires | same |
| Is a fire alarm mandatory in a home? | **No**: "Estão também isentos os fogos de habitação, qualquer que seja a categoria de risco do edifício onde se localizem" (dwellings are also exempt, whatever the risk category of the building they are in) | Portaria n.º 135/2020, art. 126.º, n.º 2 (2020 text; later amendments not checked) |
| EU comparison | **Not available**: Eurostat has no separate fire cause of death | — |

### What it does

- **On smoke:** switches the heater on the plug off at the next check, or at once through a native scenario if the mentors confirm a smoke trigger works (**untested**). It alerts the family with what it knows: the detector's state, when it last reported, and that the heater was cut.
- **Every day:** checks the detector's battery, tamper state and last report: "O detetor de fumo não comunica há 2 dias; verifique a bateria." (The smoke detector hasn't reported for 2 days; check the battery.)
- **What a fault means:** as in #2.

### Build and demo

- **Live:** detector state, battery and freshness; the plug cut-off; the stale-device example.
- **Simulated:** the smoke itself, unless the mentors confirm the test button is safe.

### Scores

| Criterion | Score | Why |
|---|---|---|
| Fit | 7 | Context and action around smoke; explaining faults adds novelty |
| Adoption | 7 | A sellable add-on to Altice's Reliable Security (which already alerts on fire). Health checks are standard in alarm platforms, but a home with no detector is a potential customer |
| Feasibility | 7 | Smoke and plug live; the fire is simulated; the scenario trigger is untested |
| Replicability | 6 | No comparable EU figure; rules differ by country |
| Presentation | 7 | "30 deaths, and no obligation" lands; partly simulated |
| Documentation | 7 | Strong ANEPC and legal sources; no age breakdown |

### Pitch (3 min, PT-PT)

::: pitch
**[Gancho]** A meio da noite, o detetor apita. Quem vive sozinho, de porta fechada, pode não o ouvir. E se a pilha acabou, nem apita.

**[Problema]** Em 2025, a ANEPC registou 5 182 incêndios em habitações no continente, e 30 mortes no local. Mais de um terço destes incêndios aconteceu à noite. E a lei isenta as habitações da obrigação de ter um sistema de alarme de incêndio.

**[Solução]** O Vigia da Casa dá contexto ao detetor de fumo. Se detetar fumo, desliga a tomada do aquecedor e avisa a família com o que sabe. Todos os dias, verifica o próprio detetor: bateria, sabotagem, última comunicação. E quando alguma coisa falha, diz à família o que isso significa. Por exemplo: faltou a luz, e o detetor só é vigiado enquanto a bateria durar.

**[Demonstração]** O estado do detetor, a bateria e a última comunicação são reais, deste kit. Aliás, este kit tem uma lâmpada que não comunica desde 4 de novembro, e o sistema diz isso, em vez de fingir. *[confirmar na sexta de manhã]* O fumo é simulado, por razões óbvias. O corte da tomada é real.

**[Porquê a Altice]** A Altice já envia alertas de incêndio. Nós acrescentamos prevenção e contexto, com o detetor que a plataforma já integra. E como a lei não obriga a ter alarme em casa, cada casa sem detetor é um cliente possível.

**[Replicabilidade]** Não há uma estatística europeia comparável, mas o desenho funciona com qualquer detetor ligado à plataforma.

**[Fecho]** «O detetor de fumo não comunica há 2 dias; verifique a bateria.» Um detetor que não se limita a apitar: protege.
:::

**Q&A notes:**
- It is not a certified fire-alarm system; it complements one.
- With cooking smoke, the heater is still switched off and the family confirms.
- There is no EU statistic, and we say so.

<div class="pagebreak"></div>

## 7. Use case #5: Modo Ausência

> **"I'm away until Sunday." The home checks itself, protects itself, and says what it can't confirm.**
> Away-from-home caretaker · Intermediate **6.00** · Final **6.10**

### The problem, honestly

| Fact | Value | Source |
|---|---|---|
| Home burglary with forced entry | 7,546 in 2025 (−4.3 %), down from 19,312 in 2014 | RASI 2025; Eurostat `crim_off_cat` |
| Police-recorded rate per 100,000 inhabitants | **PT 74.07** · FR 295.47 · IT 263.84 · ES 166.79 | Eurostat `crim_off_cat`, 2024 |
| RASI's explanation | Home-security technology and "mais teletrabalho, menos ausências prolongadas" (more teleworking, fewer long absences). Thefts without forced entry happen when "a porta ou janela podem estar abertas" (the door or window may be open) | RASI 2025, p. 84 |

**Inference:** in Portugal this is a peace-of-mind product, not a response to a rising threat. France's recorded rate is about 4× Portugal's.

### What it does

- It checks the door and windows, the plug and the alarm state.
- It **activates the alarm only after an explicit "yes"**.
- It simulates presence with a lamp on the plug.
- If you come back early, opening the door and sending a message is enough for it to propose disarming.
- It states its limits: "Não consigo confirmar a lâmpada: não comunica desde 4 de novembro." (I can't confirm the bulb: it hasn't reported since 4 November.)

### Build and demo

- **Live:** the door state (transition untested), the honest limits, the plug.
- **Simulated unless the mentors allow it:** arming.

### Scores

| Criterion | Score | Why |
|---|---|---|
| Fit | 6 | Door, alarm, plug and honest limits; Filipe's original scenario, but close to existing security |
| Adoption | 6 | The core of Altice's Reliable Security and of SFR Maison Sécurisée: easy to place, little new |
| Feasibility | 6 | Arming and timers untested; camera siren offline |
| Replicability | 7 | A bigger problem in France, Italy and Spain |
| Presentation | 6 | Relatable; live arming is risky |
| Documentation | 5 | Portuguese data shows burglary falling, a weak problem statement |

### Pitch (3 min, PT-PT)

::: pitch
**[Gancho]** Quem nunca voltou atrás para ver se fechou a janela?

**[Problema]** Os furtos em residência com arrombamento estão a descer: 7 546 em 2025. O Relatório Anual de Segurança Interna atribui parte da descida à tecnologia de segurança residencial e a mais teletrabalho. Mas continua a haver furtos sem arrombamento, em que a porta ou a janela podem ter ficado abertas. E quem sai de casa nem sempre tem a certeza de que deixou tudo bem.

**[Solução]** O Modo Ausência percebe a intenção («vou estar fora até domingo») e verifica a casa: portas e janelas, tomadas, alarme. Só ativa o alarme com confirmação explícita. Simula presença com a tomada. Se voltar mais cedo, basta abrir a porta e enviar uma mensagem para o sistema propor desativar o alarme. E diz o que não consegue garantir.

**[Demonstração]** Neste momento, esta casa diz-nos que a lâmpada não comunica desde 4 de novembro. *[confirmar na sexta de manhã]* Não finge. O estado da porta é real; a ativação do alarme é simulada, por segurança.

**[Porquê a Altice]** Não é segurança nova: é uma camada de verificação e de conversa sobre a segurança que a Altice já tem. Em França, onde a taxa de furtos em residência registada pela polícia é cerca de quatro vezes a portuguesa, a SFR já vende a Maison Sécurisée, desenvolvida pela Altice Labs.

**[Fecho]** Sair de casa descansado, com uma casa que diz a verdade.
:::

<div class="pagebreak"></div>

## 8. Not shortlisted, and why

| Candidate | Final | Why not |
|---|---|---|
| **Regras em Conversa** (Mushahid's AI rule builder) | 5.90 | Altice's brochure: "scenarios will be powered by generative AI to enable the automatic generation of scenario scripts". The brief warns against "simply controlling devices through AI". Kept as a *feature*: the LLM turns the family's words into confirmed settings, and writes the one native scenario |
| **Perdidos e Achados** (lost & found) | 4.50 | The camera has no power, the MCP has no vision, and the feed has no authentication. The only evidence is US vendor surveys (weak) |
| **Routine monitoring of an older person** (part of version 1's #1) | — | Removed after review: Altice's Aging in place, Family Care and SmartAL already cover activity, anomaly and health alerts |

## 9. What to do next

### Before Wednesday 19:00

1. **Run two tests on Wednesday morning, if possible:**
   - the window contact, open → closed through the MCP;
   - the plug with a load (watts and the daily counter).

   If either fails or isn't run, the Sumário keeps its "a validar no kit" wording.
2. **At the checkpoint**, ask (in this order):
   1. "Do Family Care or eHealth Smart Assisted Living use temperature or humidity, or alert the family about home conditions?" *This decides Pitch A or Pitch B.*
   2. Which segment do MEO and SFR want to grow? Would a care case be sold through "Multiple home management", and at what price?
   3. Is there a platform event or push API, or must we poll? How fast may we poll? Can a smoke sensor trigger a scenario? Can you delete test scenarios?
   4. Is the smoke-sensor test button safe? May we test arming? May we bring a dehumidifier for the plug?
   5. Report a bug: `patch_home_security_status` is annotated `readOnlyHint: true` but arms the alarm. *This earns credibility and protects other teams.*
   6. Camera adapter and bulb status; finalist count and Q&A length; whether the 18 Nov report uses the Sumário Executivo template.
3. **Finish the Sumário** (appendix): fill in the model and coding assistant names, and adjust it to the checkpoint answer. The checkpoint (14:00–18:00) can leave as little as an hour before 19:00, so it is written for Pitch A already.
4. **A team member personally opens the source** of each figure used on stage: about eight, all linked in docs/12. The rules require that we understand and can defend them.

### Thursday: tests before we build on assumptions

| Test | Why |
|---|---|
| Contact open → closed, and how fast it shows (if not done Wednesday) | Every window demo |
| Plug with a load: watts, the daily counter's unit and update rate | Cost figures |
| The dehumidifier (or stand-in) resumes when the plug switches on | Appliance restart |
| Polling every few seconds: does the MCP allow it? | Demo timing |
| Hub powered off for a few minutes: what the platform shows (network mode, battery), and that it reconnects cleanly (**press no buttons**) | "What a fault means" |
| The IPMA station nearest the venue | Outdoor data |
| Tokens per LLM answer | € per home per month for the final |
| Telegram bot delivery from the venue network | The channel |

### Build plan (our estimate; the team assigns owners)

| Stream | Scope | Owner | Done when |
|---|---|---|---|
| **Engine** | Poller + SQLite log + freshness + absolute humidity and dew point + rules + plug actions (off-only for heaters) | ___ (hint: whoever knows `mcp/client/chmcp.py`) | Rules fire on real readings |
| **Conversation** | LLM with the MCP tools + family words → confirmed settings + Telegram stand-in + IPMA + "Como está a casa da mãe?" | ___ | A phone gets a correct, fresh answer from live data |
| **Story** | Slides, Pitch A (3 min) and the 5-min version, the replayed history (labelled), **a recorded backup video**, timed Q&A practice | ___ (hint: the Portuguese speaker who pitches) | Two full timed run-throughs; the backup plays offline |

**Friday:**
- Bring the hotspot or access point, an ethernet cable, the stand-in lamp, and the dehumidifier or kettle if allowed.
- Log in to the MCP in the morning; the session lasts about 24 h.
- Check the bulb is still stale before using it on stage.
- Freeze the demo by early afternoon and record the backup.

## 10. Method, AI use and limits

- **How the evidence was gathered:**
  - AI research agents searched official sources (INE, Eurostat, ANACOM, RASI, ANEPC, DGEG, WHO, Diário da República) and read each figure at source on 17 Nov 2026.
  - A second pass re-checked the key figures against the primary documents. The DGEG and WHO 2009 page references were not re-opened.
  - Vendor surveys are labelled weak; press is used only to find the primary source.
  - Full tables, links, discrepancies and the verification log are in [`docs/12-market-research.md`](../../docs/12-market-research.md).
- **Scores** are the team's own judgement against the official criteria; weighted totals are computed by script.
- **AI-assisted review.** The report went through two review rounds by AI agents playing an Altice mentor, a juror, a fact-checker and a European Portuguese pitch coach. The team assessed each finding (§11). AI use is allowed by the rules (FAQ Q17), on condition that the team understands and can defend every choice. This section is here so that we can.
- **Not known, and not used as fact:**
  - Altice's customer data;
  - current Portuguese time-use data (newest 2015; INE's 1999);
  - the share of fire deaths who are elderly;
  - excess winter mortality at a primary source;
  - LLM running cost (to be measured).

## 11. Advisor review: what it found and what changed

**Round 1** (on version 1):

| Reviewer (AI role) | Main findings | What we changed |
|---|---|---|
| **Altice mentor** | Version 1's #1 demoed only the part that overlaps Family Care and Aging in place (routine alerts); humidity is the new part. A remotely switched heater is a liability. Telegram isn't an operator channel. Who pays is a guess. Polling won't scale. Suggested "arejar ou aquecer?" and a "the house went quiet" alert | Routine monitoring removed. Damp engine moved to #1. Off-only heater rule. "Product" column in §2.3. Multiple-home management and LTE hub as the sales route. Suggestions adopted |
| **Juror** | Scored version 1's #1 a point lower on every criterion, which put the damp case ahead. One plug and one contact were silently given several roles. Heater safety contradicted our own rule. Replicability swapped indicators. The review section was an empty placeholder | Scores revised. Device-role table. Heater rule. Honest replicability lines. This section filled in |
| **Fact-checker** | Core figures correct at source and totals correct. But: untested kit behaviour stated as working; "at once" with 60 s polling; smoke presented as something Altice lacks; AI research not disclosed; years mixed in one comparison | "Untested" labels. Response-time rule. Smoke builds on Altice's alerts. AI-use section. Like-for-like years |
| **Pitch coach (PT-PT)** | No Brazilianisms. #1 over 3 min; #4 and #5 short. ~20 phrasing fixes. Cut replicability first at 3 min (not scored in the intermediate round) | Scripts rewritten and re-timed; replicability moved to the 5-min extension |

**Round 2** (on version 2):

| Reviewer (AI role) | Main findings | What we changed |
|---|---|---|
| **Jury and Altice panel** | Scores within 2 points of ours on every criterion; ranking unchanged. But: the recommended merged pitch didn't exist. "No alarm tells you it can't watch" ignores the hub's 4G and battery backup. The Sumário stated untested behaviour as fact. eHealth Smart Assisted Living (SmartAL) not considered. Demo silence of up to 60 s. Appliance restart not considered. No owners. Vague checkpoint question | **Pitch A written** (persona-led Casa Saudável). The "fault" alert reframed as consequence ("what it means"). Sumário wording "a validar". SmartAL added. Demo stage directions and fast polling. Restart test. Owner column. Exact checkpoint question. #1 feasibility 8 → 7 and #2 adoption 7 → 6, presentation 9 → 8 |
| **Fact-checker and PT proofreader** | Every figure and derived comparison re-verified via the Eurostat API. Two demo steps and the Sumário still implied untested steps were live. Device-role table inconsistent for #2 and #4. Blackout mislabelled as inference. "Before waking" heating breaks the off-only rule. "Pobreza" should be "risco de pobreza". ~20 PT-PT touches | Stage directions for untested steps. Full simulated list in the Sumário. Table fixed. Blackout sourced (ENTSO-E). "Ao acordar e antes de deitar". Wording fixed throughout |

**Scores across versions** (final):

| Use case | v1 | v2 | v3 |
|---|---|---|---|
| Casa Saudável (damp) | 8.20 | 8.20 | **8.00** |
| Casa que Cuida (v1: with routine monitoring) | 8.40 | 7.90 | **7.60** |
| Calor Certo | 7.40 | 7.10 | **7.10** |
| Vigia | 6.90 | 6.80 | **6.80** |
| Modo Ausência | 6.50 | 6.10 | **6.10** |

The round-2 panel's own totals were 7.70 and 7.20 for the top two, still ranking the damp case first.

<div class="pagebreak"></div>

## Appendix: draft Sumário Executivo (PT-PT)

*For the recommended option, Pitch A: Casa Saudável, with the case of an older mother living alone. It follows the template's four sections. Check the length in the template (max. 2 pages) and delete all of the template's blue instruction text before exporting. Fill in the name of the language model and the coding assistant the team actually uses. If Wednesday's tests pass, replace "a validar no kit" with the result.*

**Equipa:** IT-Porto · **Desafio #3:** Altice Labs, *Connected Homes Reimagined: a IA ao serviço da casa*

### Descrição do desafio

A Altice Labs desafia as equipas a reimaginar a casa conectada com inteligência artificial: serviços que tornem o dia a dia em casa mais simples, mais útil ou mais seguro, e que vão além do simples controlo de dispositivos por comandos. A ferramenta MCP Connected Home deve estar integrada na solução. O MCP é um protocolo que permite a um modelo de IA ler e comandar os dispositivos da casa. O desafio pede que a IA combine contexto, intenção, informação e ação.

### Estratégia

Escolhemos o problema a partir de dados oficiais. Em Portugal, a própria casa pode ser um problema de saúde.
- Em 2025, 32,1% dos portugueses viviam numa casa com infiltrações, humidade ou apodrecimento, e o indicador agravou-se nos últimos três anos (INE). Em 2023, Portugal foi o 2.º país da UE com mais humidade em casa (Eurostat).
- 15,6% não conseguiam manter a casa adequadamente aquecida, contra 8,8% na UE (Eurostat, 2025).
- Entre as pessoas com 65 ou mais anos, Portugal é o 2.º país da UE com mais humidade em casa (27,4%, 2023). Está também em 2.º lugar, ex aequo com a Bulgária, na percentagem de pessoas que não conseguem manter a casa aquecida (22,2%, 2025).
- Em 2021, 517 146 pessoas com 65 ou mais anos viviam sozinhas (INE, Censos 2021; soma da equipa). Em 2025, 36,07% das pessoas entre os 65 e os 74 anos nunca tinham usado a internet (Eurostat).

Daí quatro decisões:
- **o produto** é a saúde da casa (humidade e frio), um tema que não encontrámos na oferta pública da Altice;
- **o caso principal** é o de uma pessoa idosa que vive sozinha e que não precisa de fazer nada;
- **quem usa** é a família;
- **a solução** usa apenas os sensores que o kit e a plataforma já têm (temperatura e humidade, janela, fumo e tomada com medição de energia), sem câmara nem microfone, por privacidade e porque a câmara do kit não tem alimentação.

Comparámos sete casos de uso com os critérios e pesos oficiais. A Casa Saudável foi o caso mais bem pontuado (8,0 em 10), e não duplica o acompanhamento de rotina que a Altice já oferece.

### Ideias para a proposta de solução

A **Casa Saudável** é um assistente de IA que resolve o dilema de todos os invernos: arejar ou aquecer?
- **Humidade:** o sistema calcula a humidade absoluta (a quantidade real de água no ar) dentro e fora de casa, com dados abertos do IPMA. Diz quando arejar ajuda e durante quanto tempo, e confirma pelo sensor da janela que esta foi fechada (a validar no kit). Se arejar não chegar, liga o desumidificador na tomada e indica a energia gasta (a medição de energia está a validar no kit).
- **Frio:** compara a temperatura com os 18 °C recomendados pela OMS, ou com um valor mais alto escolhido pela família, e conta as horas abaixo desse valor. Sugere aquecer, mas nunca liga um aquecedor à distância; só o desliga (quando há fumo, com a janela aberta ou ao fim do tempo combinado).
- **Fumo e falhas:** quando há fumo, desliga a tomada e avisa a família. Se faltar a luz ou a internet, diz à família o que isso significa: a casa vai arrefecer, e o detetor de fumo só é vigiado enquanto houver bateria.

No produto, há uma tomada por aparelho. No kit, a única tomada faz de desumidificador.

No caso principal, as mensagens vão para a família, em português simples. A família pode perguntar «Como está a casa da mãe?» e recebe uma resposta construída com os dados reais e com a hora de cada leitura. Quando o sistema não sabe, diz que não sabe.

Ligação ao desafio: a IA junta contexto (meteorologia exterior, hora, custo), intenção (preferências da família, ditas por palavras e confirmadas como regras) e informação (sensores, via MCP). Depois age (tomada e mensagens). Para a Altice, é um módulo que os operadores podem vender, com equipamento que a plataforma já suporta e com a gestão de várias casas que a plataforma já prevê. É replicável: a humidade em casa atinge 21,1% em França e 23,0% em Espanha (Eurostat, 2023).

Na demonstração, as leituras dos sensores, os comandos à tomada e as respostas à família (por Telegram, em vez da aplicação do operador) são reais. São simulados e identificados como tal:
- o histórico de vários dias;
- a pessoa idosa e a filha (um membro da equipa);
- o fumo;
- o aparelho na tomada (se necessário, uma lâmpada no lugar do desumidificador);
- os tempos de espera, que encurtamos.

### Ferramentas de IA

- **Agente de IA (modelo de linguagem: ___):** liga-se ao servidor MCP Connected Home através de um cliente MCP desenvolvido pela equipa. Transforma as preferências da família em regras confirmadas, explica as decisões e responde a perguntas.
- **Regras fixas:** tudo o que envolve segurança é decidido por regras simples, e não pelo modelo de linguagem. É o caso do corte da tomada quando há fumo, de nunca ligar aquecedores à distância e da confirmação explícita antes de qualquer alteração ao alarme.
- **Registo próprio:** como o MCP só devolve o estado atual, o sistema consulta-o a intervalos regulares e guarda o histórico.
- **Dados abertos do IPMA:** fornecem as condições exteriores.
- **IA na pesquisa, na revisão e na programação (assistente: ___):** usada para procurar dados oficiais, rever este documento e apoiar o desenvolvimento. Os números foram confirmados nas fontes, com ligações no repositório, e a equipa compreende e valida todas as escolhas técnicas.
