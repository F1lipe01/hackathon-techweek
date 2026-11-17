# Market research — evidence for choosing the use case

State on **Tue 17 Nov 2026**. Every figure below was read at its primary source on 17 Nov 2026. Eurostat values were re-pulled through the Eurostat API with every non-geo dimension filtered explicitly. **Facts are in the tables.** Our own reasoning is marked **Inference**. Anything not confirmed at its source is marked **UNVERIFIED**.

Strength of evidence:
- **Strong:** an official statistic, a law, or a WHO guideline, read at the source.
- **Medium:** an official operational count, a secondary official document, or a company's own document.
- **Weak:** a vendor survey or the press.

How it was checked: see the [verification log](#appendix--verification-log). The use-case write-up built on this page is [`deliverables/use-case-report/`](../deliverables/use-case-report/).

## 1. Summary

1. **Damp and cold homes are Portugal's best-documented home problem.**
   - Damp: 32.1 % of people live with leaks, damp or rot (INE, 2025), and INE says this has worsened for three years. Portugal was 2nd worst in the EU in 2023.
   - Cold: 15.6 % can't keep their home warm (2025), against 8.8 % for the EU.
   - Both have legal national targets for 2030: 20 % for damp, 10 % for cold.
2. **Older people carry most of it.** People aged 65+ in Portugal have the EU's 2nd-worst damp (27.4 %, 2023) and are joint 2nd worst for cold homes (22.2 %, 2025). 517,146 people aged 65+ live alone (Census 2021, +27 % since 2011). 36 % of people aged 65–74 have never used the internet.
3. **Fire is a strong case, burglary a weak one, in Portugal.**
   - Fire: 30 people died in dwelling fires in 2025, and smoke detection inside a home is not mandatory.
   - Burglary: it is falling and is less than half the rate of France or Spain. It is a stronger problem in France.
4. **Kit fit follows our live sensors:**
   - damp and cold: humidity, temperature, window contact and plug;
   - living alone: door and plug activity;
   - fire: smoke sensor and plug.

   Camera-dependent ideas, lost & found included, can't be shown today.
5. **By weighted final score, after two rounds of AI-assisted advisor review:**
   1. **Casa Saudável**, a damp and cold engine for every home: 8.00
   2. **Casa que Cuida**, the same engine for a parent living alone, watching the home rather than the person: 7.60
   3. **Calor Certo**, a cold-home and cost coach: 7.10

   Routine monitoring of older people was dropped: Altice's Family Care, Aging in place and eHealth Smart Assisted Living already cover it (§5). Recommended pitch: Casa Saudável, told through an older mother living alone. The team decides. Full write-up: [`deliverables/use-case-report/`](../deliverables/use-case-report/).

## 2. Who the customer is

### Known

| Fact | Value | Date | Source | Strength |
|---|---|---|---|---|
| Business model | A white-label, multi-tenant platform sold to telecom operators ("Telcos"), who sell it to their residential customers. The page now says **B2B2C** | 2025 brochure; page Oct 2026 | [Connected Home brochure](https://www.alticelabs.com/wp-content/uploads/2025/05/BR_ConnectedHome_ALB_EN-1.pdf), pp. 2–6; [product page](https://www.alticelabs.com/products/cognitive-home/) | Medium |
| **The product has been renamed "Cognitive Home"** | The old `/products/connected-home/` URL redirects there; the page was modified 12 Oct 2026 | Oct 2026 | product page | Medium |
| Segments | "Although the solution targets residential households, it is also suitable" for offices and buildings. The brochure lists "Residential" and "SOHO/SME" | 2025 | brochure | Medium |
| Operator deployments | **SFR Maison Sécurisée** (France) is "a self-monitoring solution fully developed by Altice Labs", for "the Residential and Small Office/Home Office segments" | Apr 2024 | [Altice Labs blog](https://www.alticelabs.com/blog/connected-home-from-altice-labs-featured-in-the-recent-launch-by-sfr/) | Medium |
| SFR offer today | Hub with 4G backup, 2 motion detectors, a camera and a door/window detector; alerts to trusted contacts. €19.99/month list price; SFR Box customers get €5/month off | Nov 2026 | [sfr.fr/maison](https://www.sfr.fr/maison/) | Medium |
| **MEO is not named** in the brochure | Brochure p. 15 shows the SFR logo plus one logo with no label. "MEO" appears nowhere in the text | 2025 | brochure | Medium |
| MEO consumer offer found | A third-party "Kit Alarme Starter Ajax" with no monthly fee and no monitoring centre. **No MEO smart-home subscription found**; meo.pt builds its pages with JavaScript, so this absence is not certain | Nov 2026 | [meo.pt, Ajax kit](https://www.meo.pt/alarme-para-casa-starter-ajax) | Medium |
| MEO share of fixed broadband accesses | **40.9 %** of all fixed broadband accesses (NOS 33.3, Vodafone 21.7, DIGI/NOWO 3.3); **39.0 %** of residential accesses; 53.2 % of fibre | Q4 2025 | [ANACOM, internet access services 4T2025](https://www.anacom.pt/streaming/SAI4T2025.pdf?contentId=1828507&field=ATTACHED_FILE), Tabelas 4 and 6 | Strong |
| Fixed broadband reach | 4,817 thousand fixed internet accesses; 90.6 residential accesses per 100 families | Q4 2025 | same | Strong |

The Q2 2026 operator shares (press: MEO 40.4 %) could not be read at ANACOM, whose pages load by JavaScript. Q4 2025 is the latest verified quarter.

### Proxies: national household statistics (INE Census 2021)

Altice's own customer demographics are not public, and none are invented here.

| Proxy | Value | Year | Source | Strength |
|---|---|---|---|---|
| Private households | 4,149,096 (2011: 4,043,726) | 2021 | [INE, family structures, press release](https://www.ine.pt/ngt_server/attachfileu.jsp?look_parentBoui=595681359&att_display=n&att_download=y) | Strong |
| One-person households | 1,027,871 = **24.8 %** of households (2011: 21.4 %) | 2021 | same, and [INE publication, table Q1.04](https://www.ine.pt/xportal/xmain?xpid=INE&xpgid=ine_publicacoes&PUBLICACOESpub_boui=66321126&PUBLICACOESmodo=2) | Strong |
| One-person households of people aged 65+ | **12.5 %** of all households (2011: 10.1 %) | 2021 | same press release | Strong |
| People aged 65+ living alone | **517,146** (2011: 406,942) | 2021 | Sum of INE table Q1.04 age bands 65–69, 70–74 and 75+. **The sum is ours**; it reproduces INE's 12.5 % and 50.3 % | Strong |
| Households with internet access | 91.1 % | 2025 | [INE IUTICF 2025](https://www.ine.pt/ngt_server/attachfileu.jsp?look_parentBoui=762433102&att_display=n&att_download=y); Eurostat `isoc_ci_in_h` 91.08 | Strong |
| One-person households with internet (survey scope ages 16–74) | 85.09 % (FR 89.81, EU 90.17) | 2025 | [Eurostat `isoc_ci_in_h`](https://ec.europa.eu/eurostat/databrowser/view/isoc_ci_in_h/default/table?lang=en) | Strong |

**Inference (an illustration, not a market size).** Suppose MEO's residential share (39.0 %) applied evenly to the 517,146 people aged 65+ living alone. The result is 517,146 × 0.39 = 201,687 people.
- **This overstates the reach.** ANACOM counts accesses, not households of this type, and 36 % of people aged 65–74 have never used the internet (§3.3). Altice's real customer base is not public.
- **Use it only to show the order of scale** in Q&A. Don't put it on a slide as a fact.

### Open questions for the mentors

1. Who is Connected Home aimed at today: families, people living alone, older people, SOHO? Which segment do MEO and SFR want to grow?
2. What do current users actually use it for: security, energy, automation? Which features go unused?
3. Who pays in a care scenario: the older person, or an adult child on a family plan?
4. Can the platform send notifications or keep event history for a third-party service? The MCP does neither ([10-mcp-in-practice.md](10-mcp-in-practice.md)).
5. Are humidity, temperature and the plug part of the standard bundle that operators sell, or only of the hackathon kit?

## 3. Problem evidence

### 3.1 Damp and mould → temperature/humidity sensor, window contact, plug for a dehumidifier

| Fact | Value | Year | Source | Strength |
|---|---|---|---|---|
| People living with a leaking roof, damp walls/floors/foundation, or rot | **PT 29.0 % · FR 21.1 % · EU27 15.6 %** | 2023 (latest Eurostat year; the module runs every 3 years) | [Eurostat `ilc_mdho01`](https://ec.europa.eu/eurostat/databrowser/view/ilc_mdho01/default/table?lang=en) | Strong |
| Portugal's EU rank | **2nd of 27** (Cyprus 32.1, Portugal 29.0, Spain 23.0; France 5th) | 2023 | same | Strong |
| Same, people aged 65+ | **PT 27.4 % · FR 13.0 % · EU27 12.1 %**; Portugal **2nd** after Cyprus (31.1) | 2023 | same, `age=Y_GE65` | Strong |
| Same, below 60 % of median income | PT 38.4 % · FR 33.7 % · EU27 23.6 % | 2023 | same, `rskpovth=B_60` | Strong |
| INE's yearly series for Portugal | **29.0 % (2023) → 30.9 % (2024) → 32.1 % (2025)**; in poverty 38.4 → 40.4 → 41.8. INE: "apresenta um agravamento nos últimos três anos" (has worsened over the last three years) | 2023–2025 | [INE, ICOR 2025 release, Figura 22](https://www.ine.pt/ngt_server/attachfileu.jsp?look_parentBoui=765651766&att_display=n&att_download=y) | Strong |
| National target | **20 % in 2030**, 10 % in 2040, < 5 % in 2050 (25.2 % in 2020) | 2024 law | [RCM n.º 11/2024, n.º 2 c)](https://files.diariodarepublica.pt/1s/2024/01/00500/0006900121.pdf) (ELPPE 2023–2050) | Strong |
| Health effect | Occupants of damp or mouldy buildings "are at increased risk of respiratory symptoms, respiratory infections and exacerbation of asthma"; "no quantitative health-based guideline values or thresholds can be recommended" | 2009 | [WHO guidelines for indoor air quality: dampness and mould](https://iris.who.int/handle/10665/164348), pp. xiii, xv | Strong |
| Humidity numbers in the WHO text (background chapter only, **not guideline values**) | Relative humidity above about 50 % favours dust mites (p. 33). Surfaces stay mould-free below 75–80 % RH (p. 38) | 2009 | same | Strong (as background) |

**Inference:** the damp indicator is moving away from its 2030 target (25.2 % in 2020, 32.1 % in 2025). Any humidity alert we build must be framed as building-science guidance, not as a WHO threshold.

### 3.2 Cold homes and energy poverty → temperature sensor, plug metering, plug for a heater

| Fact | Value | Year | Source | Strength |
|---|---|---|---|---|
| People unable to keep their home adequately warm | **PT 15.6 % · FR 11.5 % · EU27 8.8 %** (2024: 15.7 · 11.8 · 9.2; 2023: 20.8 · 12.1 · 10.6) | 2025 | [Eurostat `ilc_mdes01`](https://ec.europa.eu/eurostat/databrowser/view/ilc_mdes01/default/table?lang=en); INE ICOR 2025 says the same | Strong |
| Portugal's EU rank | 5th in 2025, after Greece 18.1, Lithuania 16.7 (provisional), Bulgaria 16.1 and Spain 15.9. **1st, tied with Spain, in 2023** | 2023–2025 | same | Strong |
| Same, people aged 65+ | **PT 22.2 % · FR 10.2 % · EU27 8.4 %**; Portugal **joint 2nd** with Bulgaria, after Lithuania (25.5, provisional), of 26 countries reporting (no 2025 value for Luxembourg). 2024: 22.0 % (break in series) | 2025 | [Eurostat `hlth_dhc140`](https://ec.europa.eu/eurostat/databrowser/view/hlth_dhc140/default/table?lang=en). This is a different table: its all-ages total doesn't equal `ilc_mdes01`'s, so don't mix them | Strong |
| Same, one adult aged 65+ (household type) | PT 26.9 % · FR 14.5 % · EU27 11.4 % (2024: 27.3 · 14.7 · 11.9) | 2025 | `ilc_mdes01`, `hhcomp=A1_GE65` | Strong |
| Same, below 60 % of median income | PT 30.6 % · FR 23.5 % · EU27 19.6 % (2024: 30.9 · 22.4 · 19.7) | 2025 | `ilc_mdes01`, `rskpovth=B_60` | Strong |
| Arrears on utility bills | **PT 3.6 %** · FR 8.0 % · EU27 7.0 % | 2025 | [Eurostat `ilc_mdes07`](https://ec.europa.eu/eurostat/databrowser/view/ilc_mdes07/default/table?lang=en) | Strong |
| Household electricity price, band DC (2,500–4,999 kWh/year), all taxes included | PT €0.2367 · FR €0.2485 · EU27 €0.2832 per kWh | 1st half 2026 | [Eurostat `nrg_pc_204`](https://ec.europa.eu/eurostat/databrowser/view/nrg_pc_204/default/table?lang=en) | Strong |
| National target, cold homes | **10 % in 2030**, 5 % in 2040, < 1 % in 2050 (17.5 % in 2020) | 2024 law | [RCM n.º 11/2024, n.º 2 a)](https://files.diariodarepublica.pt/1s/2024/01/00500/0006900121.pdf) | Strong |
| National target, households spending more than 10 % of income on energy | 700,000 in 2030 (1,202,567 in 2016) | 2024 law | same, n.º 2 d) | Strong |
| Social electricity tariff beneficiaries | 747,292 electricity; 803,703 including gas | Aug 2026 | [DGEG, August 2026 run](https://dgeg.gov.pt/pt/destaques/tarifa-social-de-energia-processamento-de-agosto-de-2026-concluido-com-sucesso/) | Strong |
| WHO: minimum indoor temperature | "18 °C has been proposed as a safe and well-balanced indoor temperature to protect the health of general populations during cold seasons". **Strong recommendation**; a higher minimum may be needed for older people, children and the chronically ill | 2018 | [WHO Housing and Health Guidelines](https://iris.who.int/handle/10665/276001), §4.1, p. 34 | Strong |
| Excess winter mortality, Portugal | **UNVERIFIED**: only press citing DGS was found; no primary DGS/INSA document opened | — | — | — |

**Inference:** Portugal combines high cold-home rates with low bill arrears and a near-EU purchasing-power price. People under-heat rather than fall behind on bills. A product that helps people heat the right room, at the right time, for a known cost fits the problem better than bill alerts.

### 3.3 Older people living alone → door contact, plug activity, temperature, smoke, device freshness

| Fact | Value | Year | Source | Strength |
|---|---|---|---|---|
| People aged 65+ living alone (one-person households) | **517,146**; 2011: 406,942 (**Inference:** +27.1 %, our arithmetic) | 2021 | INE Census, table Q1.04 (see §2) | Strong |
| Of those, aged 75+ | 303,902, of whom 232,378 women | 2021 | same | Strong |
| Share of one-person households where the person is 65+ | 50.3 % (2011: 46.9 %) | 2021 | [INE publication, p. 8](https://www.ine.pt/ngt_server/attachfileu.jsp?look_parentBoui=595746151&att_display=n&att_download=y) | Strong |
| Share of people aged 65+ who live alone | **PT 25.7 % · FR 37.1 % · EU27 32.2 %** | 2025 | [Eurostat `ilc_lvps30`](https://ec.europa.eu/eurostat/databrowser/view/ilc_lvps30/default/table?lang=en) | Strong |
| Population aged 65+ | 2,665,777; ageing index 188.8 (2021: 178.3) | 31 Dec 2025 | [INE, population estimates 2025](https://www.ine.pt/xportal/xmain?xpid=INE&xpgid=ine_destaques&DESTAQUESdest_boui=770295679&DESTAQUESmodo=2) | Strong |
| Projected share aged 65+ in 2050 (central scenario) | **34.5 %** | 2050 | [INE, projections 2025–2100](https://www.ine.pt/ngt_server/attachfileu.jsp?look_parentBoui=753199150&att_display=n&att_download=y). Based on the pre-revision 2024 population | Strong |
| Same, EU comparison | **PT 33.9 % · FR 27.3 % · EU27 29.0 %**; old-age dependency ratio 2050: PT 62.9 · FR 48.0 · EU27 50.4 | 2050 | [Eurostat EUROPOP2023 `proj_23ndbi`](https://ec.europa.eu/eurostat/databrowser/view/proj_23ndbi/default/table?lang=en) | Strong |
| GNR *Censos Sénior*: older people flagged as living alone and/or isolated, or vulnerable | **43,074** (2024 edition: 42,873). GNR territory only; three conditions mixed | Oct–Nov 2025 | [GNR, results of Censos Sénior 2025](https://www.gnr.pt/comunicado.aspx?linha=9391) | Medium |
| People aged 65–74 who have never used the internet | **PT 36.07 % · FR 12.32 % · EU27 16.4 %** | 2025 | [Eurostat `isoc_ci_ifp_iu`](https://ec.europa.eu/eurostat/databrowser/view/isoc_ci_ifp_iu/default/table?lang=en) | Strong |
| "37.8 % of people aged 80+ live alone" (handoff) | **UNVERIFIED, do not use.** Traced to a seminar talk. It measures "households without family nuclei", which is wider than living alone | — | — | — |
| Projections of one-person or older households | **Not found** at INE, Eurostat or OECD | — | — | — |
| Context: the 28 April 2025 blackout | "On 28 April 2025, at 12:33 CEST, the power systems of continental Spain and Portugal experienced a total blackout." Used in the report to motivate a power-cut message to families | 2025 | [ENTSO-E, Iberian blackout](https://www.entsoe.eu/publications/blackout/28-april-2025-Iberian-blackout) | Strong |

**Inference:**
- More older people live alone in absolute numbers (+27 % in ten years), and Portugal will be among the EU's oldest populations by 2050.
- Portugal's *share* of people aged 65+ living alone is below the EU's, so the same service has a larger addressable share in France and the EU.
- Over a third of people aged 65–74 have never used the internet, so the older person should not need an app. Passive sensors, plus a family- or carer-facing interface, fit the evidence.

### 3.4 Burglary → contact sensor, alarm modes

| Fact | Value | Year | Source | Strength |
|---|---|---|---|---|
| Home burglary with forced entry, climbing or false keys | 8,237 (2023) → 7,881 (2024) → **7,546 (2025)**, −4.3 % | 2025 | [RASI 2025](https://www.ssi.gov.pt/publicacoes/relatorio-anual-de-seguranca-interna/RASI2025.pdf), p. 36 (PDF p. 41) | Strong |
| Robbery at home | 448 → 497 → **420**, −15.5 % | 2025 | RASI 2025, p. 40 | Strong |
| Home theft without forced entry | 3,945, −2.9 % | 2025 | RASI 2025, p. 84 | Strong |
| Ten-year trend, the same category | 19,312 (2014) → 16,186 (2015) → 7,881 (2024) | 2014–2024 | [Eurostat `crim_off_cat`, ICCS05012](https://ec.europa.eu/eurostat/databrowser/view/crim_off_cat/default/table?lang=en) | Strong |
| Rate per 100,000 inhabitants | **PT 74.07** · FR 295.47 · IT 263.84 · ES 166.79 · DE 93.98. No EU aggregate exists | 2024 | same | Strong |
| RASI's own explanation | The fall "é influenciada pela disponibilidade e acessibilidade de tecnologia de segurança residencial (câmaras, alarmes, fechaduras inteligentes) e ainda as mudanças nos padrões de vida (mais teletrabalho, menos ausências prolongadas)" (is influenced by available, affordable home-security technology — cameras, alarms, smart locks — and by changes in how people live: more teleworking, fewer long absences). In thefts without forced entry, "a porta ou janela podem estar abertas" (the door or window may be open) | 2025 | RASI 2025, p. 84 (PDF p. 89) | Strong (qualitative) |

**Inference:** in Portugal the evidence supports "security tech works and people are home more". It does not support "burglary is rising". As a lead problem, burglary is stronger for France, about 4× Portugal's rate.

### 3.5 Home fires → smoke sensor, plug cut-off

| Fact | Value | Year | Source | Strength |
|---|---|---|---|---|
| Fires in dwellings (building type I), mainland | **5,182**: 77.24 % of fires in buildings in use | 2025 | [ANEPC, Anuário de Segurança Contra Incêndio em Edifícios 2025](https://prociv.gov.pt/media/xmtdifgu/anuario_scie_2025.pdf) | Strong |
| Deaths in urban fires, mainland | 37 (on-site count), of which **30 in dwellings**; 139 seriously injured. Average 35 a year since 2020 | 2025 | same, Figuras 55–58 | Strong |
| Dwelling fires at night | 35.82 % | 2025 | same | Strong |
| Is a detector or alarm mandatory inside a home? | **No.** "Estão também isentos os fogos de habitação, qualquer que seja a categoria de risco do edifício" (individual dwellings are also exempt, whatever the building's risk category) | 2020 law | [Portaria n.º 135/2020, art. 126.º n.º 2](https://files.diariodarepublica.pt/1s/2020/06/10700/0000200214.pdf), Pág. 129. Amendments after 2020 not checked | Strong |
| Share of fire deaths who are elderly | **Not found** in an official source | — | — | — |
| EU comparison | **Not available.** Eurostat has no separate cause-of-death category for smoke and fire | — | — | — |

### 3.6 Routines and time at home

| Fact | Value | Year | Source | Strength |
|---|---|---|---|---|
| **Who ran the 2015 survey** (the handoff said INE) | **INUT**, by **CESIS with CITE**, not INE. 10,146 respondents aged 15+ | 2015 | [INUT policy brief](https://eeagrants.cig.gov.pt/wp-content/uploads/2017/06/inut_policybrief_en.pdf), p. 4 | Medium (a study, not official statistics) |
| Unpaid work on the last working day | Women 4 h 23 min a day, men 2 h 38 min | 2015 | same, p. 10 | Medium |
| INE's own time-use survey | "Inquérito à Ocupação do Tempo", **1999** (published 2001) | 1999 | [INE catalogue](https://www.ine.pt/xportal/xmain?xpid=INE&xpgid=ine_publicacoes&PUBLICACOESpub_boui=138463&PUBLICACOESmodo=2) | Strong |
| Portugal in the EU time-use survey (HETUS) | **Absent** from the 2000/2010 and 2020 waves | — | Eurostat `tus_00age`, `tus_20age` | Strong (official absence) |
| Official evidence on time older people spend at home | **Not found** | — | — | — |
| Official qualitative signal: more time at home | RASI 2025 credits part of the fall in burglary to "mais teletrabalho, menos ausências prolongadas" (more teleworking, fewer long absences) | 2025 | RASI 2025, p. 84 | Strong (qualitative) |

**Inference:** no current statistic shows how long people stay at home in Portugal; the newest data is 11 years old, and INE's is 27. Do not claim "people spend more time at home" with a number. The RASI sentence is the only official support for it, and it is qualitative.

### 3.7 Smart-home adoption

Eurostat `isoc_iiot_use`, individuals who used a connected home system or device in the last 3 months. The 2024 definitions changed, so 2022 values are **not comparable**.

| Indicator | PT | FR | EU27 | Year | Source | Strength |
|---|---|---|---|---|---|---|
| Any connected home system (`I_IOT_DOM2`) | **23.99 %** | 39.01 % | 33.04 % | 2024 | [Eurostat `isoc_iiot_use`](https://ec.europa.eu/eurostat/databrowser/view/isoc_iiot_use/default/table?lang=en) | Strong |
| Energy management (`I_IOT_DEM2`) | 9.33 % | 14.57 % | 14.22 % | 2024 | same | Strong |
| Security and safety (`I_IOT_DSEC2`) | 8.49 % | 14.16 % | 11.76 % | 2024 | same | Strong |
| Any connected home system, ages 65–74 | **8.8 %** | 22.41 % | 18.97 % | 2024 | same, `ind_type=Y65_74` | Strong |

**Inference:** Portugal is behind on use, especially among older people. That is room to grow, but it also says the product must be easy. For 65–74s in Portugal, assume no app on their side.

### 3.8 Lost & found (the team's earlier idea)

| Fact | Value | Year | Source | Strength |
|---|---|---|---|---|
| Time spent looking for misplaced items | 2.5 days a year (US); TV remote is the most-lost item | Fieldwork Oct 2016 | [Pixie press release](https://www.prnewswire.com/news-releases/lost-and-found-the-average-american-spends-25-days-each-year-looking-for-lost-items-collectively-costing-us-households-27-billion-annually-in-replacement-costs-300449305.html): a tracker vendor, "over 1,700" US respondents | **Weak** |
| Search time by US state | 9 h 45 min to 30 h 17 min a year | 2023 | [Shane Co. survey](https://theloupe.wpengine.com/articles-and-news/stuff-each-state-loses-the-most/): a jeweller, "over 2,000" respondents, extrapolated | **Weak** |
| "17 h a year, 16 min per item" (widely quoted, credited to Shane Co.) | Not on the Shane Co. page | — | — | **UNVERIFIED, do not use** |
| Official, Portuguese or peer-reviewed household survey | **None found** | — | — | — |
| Kit dependency | Needs the camera, which has no power adapter today; the MCP has no vision; one fixed view | 17 Nov 2026 | [10-mcp-in-practice.md](10-mcp-in-practice.md) | — |

**Inference:** judged fairly, the idea is appealing, and the mentors did say "don't underestimate the camera". The evidence is US vendor marketing, though, and it can't be shown today. If the team wants it, back it with a small survey of our own and fix the camera first.

## 4. Kit-fit matrix

From [10-mcp-in-practice.md](10-mcp-in-practice.md) and [11-project-baseline.md](11-project-baseline.md).

**Cross-cutting MCP limits:**
- current state only, so history means polling and keeping our own log;
- no notification tool;
- no delete-scenario tool;
- the plug is the only verified actuator.

| Problem | Sensing (live today?) | MCP tools | Acting | Status today | Main gap |
|---|---|---|---|---|---|
| Damp & mould | Humidity + temperature ✓ (reports every 5–30 min); window contact ✓ (reads "open"; **open→closed change via the MCP untested**) | `get_home_devices`, `get_device_details` | Plug on/off ✓ verified → dehumidifier; native rule via `post_new_scenario` (humidity trigger **untested**; permanent) | **Observe + act today** | One sensor = one room; trends need our own log; outdoor data from IPMA (API tested 17 Nov: 227 stations, hourly temperature and humidity) |
| Cold & energy | Temperature ✓; plug metering fields exist (W/V/A, daily counter) but are **untested with a load**, and the counter's unit is unknown; window contact ✓ | same | Plug → heater, **off only** (heaters must not be switched on remotely); `post_timer_device` (untested) | **Observe today; act (off) today** | Tariff can't be set via MCP (we hold it); one plug = one appliance |
| Older person alone | Temperature/humidity ✓; smoke ✓; `lastCommunicationTime` ✓ (the bulb has really been silent since 04 Nov); door/plug activity possible but **routine monitoring dropped** (it duplicates Family Care) | same, polled | Messages to family: **our own channel** (not in the MCP) | **Observe today; alert channel is ours** | How the platform reports a powered-off hub is untested; consent and GDPR design |
| Burglary / away | Door contact ✓; alarm state ✓ | `get_home_security_status`, `patch_home_security_status`, alarm history | Arm/disarm (**untested**, mislabelled read-only, Home mode has a 0 s delay); plug for presence simulation | **Partly** | Arming risky in a demo; camera siren offline |
| Home fire | Smoke ✓; tamper, battery ✓; freshness ✓ | same + alarm history | Plug cut-off ✓ at the next poll (≤ 60 s); at once only via a native scenario, if a smoke trigger works (**untested**) | **Observe + act today** | Real smoke can't be produced in a demo; what the test button does is unknown (ask mentors) |
| Lost & found | Camera ✗ (no 12 V adapter) | none for vision | — | **Not possible today** | Camera power; vision model and object memory are ours; one fixed view |

## 5. Overlap with Altice's existing offer

Altice's current list comes from the [Cognitive Home page](https://www.alticelabs.com/products/cognitive-home/) (Oct 2026) and the [2025 brochure](https://www.alticelabs.com/wp-content/uploads/2025/05/BR_ConnectedHome_ALB_EN-1.pdf). Two lines on the page matter most:

> **Family Care** — "continuous, real-time care for all household members, with a particular focus on the elderly and children, through privacy-first ambient sensing and routine monitoring using motion sensors and the existing Wi-Fi network."
>
> **Aging in place** — "Assists elderly or disabled individuals through smart displays that offer two-way communication."

The 2025 brochure adds three relevant lines:
- "The Connected Home scenarios will be powered by generative AI to enable the automatic generation of scenario scripts."
- Family Care "sends alerts to caregivers when an anomaly is detected in an elderly or sick person."
- Aging in place panel: routines maintained, with alerts "when people forget to engage in certain activities or anomalies are detected, such as falls". The layout is multi-column, so this is our reading of the extracted text.

The product page also lists a related product, **eHealth Smart Assisted Living** ("remote health monitoring"). The brochure lists **"Multiple home management"** among platform features, and Smart Security alerts by "push notifications, SMS, and voice calls".

**Inference:** routine and anomaly monitoring of older people is already Altice's territory. Home-condition health (damp, the cold-versus-damp trade-off, a silent house) is not in their published material.

| Candidate | Lands in Altice's row | What would be new on top | Overlap |
|---|---|---|---|
| A. Older person living alone | Family Care; Aging in place | **Home conditions as a health risk** (cold below WHO's 18 °C, damp, smoke), not just "did they move". It works **without a motion sensor**, using door, plug, temperature and smoke devices Altice already supports. A family-facing assistant explains in plain Portuguese and says when data is stale | **High on routine monitoring, low on home-health.** Pitch it as a module for Family Care, not as a new product |
| B. Damp and mould | Automation and comfort; Energy | **Health framing**: ventilation advice combining indoor humidity with IPMA outdoor data; checks the window was really opened and closed; a dehumidifier only when needed | Low: humidity is not in Altice's list |
| C. Cold home and cost | Intelligent energy management ("consumption monitoring with alerts…Eco Mode"; "automating the start and stop of highly energy-consuming activities according to the…cheapest time") | Comfort-to-health target (18 °C), cost per hour from the plug's own metering, a "window open while heating" warning | **High** |
| D. Fire risk | Reliable Security ("emergency alerts…of intrusion, fire…") | Context: a heater on the plug is cut off when smoke is detected; detector battery and freshness are checked proactively; who is at home | Medium |
| E. Away caretaker | Reliable Security; SFR Maison Sécurisée | Honest limits ("I can't confirm the light is off: no report since 4 Nov"), presence simulation | **High** |
| F. AI rule builder | Automation ("scenario-based automation powered by AI"); brochure: GenAI scenario scripts | Little | **High** |
| G. Lost & found | Nothing | Everything | None, but camera-dependent |

## 6. Scoring

Each criterion is scored 1–10 using the official weights ([01-event.md](01-event.md)):
- **Intermediate:** fit, adoption, feasibility and presentation, 25 % each.
- **Final:** fit, adoption, feasibility and replicability 20 % each; presentation and documentation 10 % each.

Totals are computed by script. Presentation and documentation depend mostly on how well we execute, so here they score how demo-able the case is and how strong its evidence base is. **These are our judgements, not the jury's.**

**Version 3.** This version follows two rounds of AI-assisted review by an Altice mentor, a juror, a fact-checker and a pitch coach. What the review found and what changed is in [the use-case report, §11](../deliverables/use-case-report/top5-use-cases.md). The juror role, scoring version 1 independently, put the damp case 0.3 ahead of the older-person case. The mentor role showed that routine monitoring of older people duplicates Altice's Family Care and Aging in place.

| Rank | Use case | Fit | Adoption | Feasibility | Replicability | Presentation | Documentation | **Intermediate** | **Final** |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Casa Saudável**: damp and cold engine for every home ("arejar ou aquecer?") | 8 | 9 | 7 | 8 | 8 | 8 | **8.00** | **8.00** |
| 2 | **Casa que Cuida**: the same engine for a parent living alone; watches the home, not the person | 9 | 6 | 7 | 8 | 8 | 8 | **7.50** | **7.60** |
| 3 | **Calor Certo**: cold-home comfort and cost coach | 7 | 6 | 7 | 8 | 7 | 8 | **6.75** | **7.10** |
| 4 | **Vigia da Casa**: fire and safety-net watch | 7 | 7 | 7 | 6 | 7 | 7 | **7.00** | **6.80** |
| 5 | **Modo Ausência**: away-from-home caretaker | 6 | 6 | 6 | 7 | 6 | 5 | **6.00** | **6.10** |
| 6 | **Regras em Conversa**: AI rule builder | 5 | 6 | 6 | 8 | 5 | 4 | **5.50** | **5.90** |
| 7 | **Perdidos e Achados**: lost & found with the camera | 6 | 3 | 3 | 7 | 4 | 3 | **4.00** | **4.50** |

The one-line reasoning for each score in candidates 1–5 is in the use-case report, §3–§7. For 6 and 7:

**Regras em Conversa**
- Fit 5: close to "controlling devices through AI", which the brief says is not enough.
- Adoption 6: it runs on Altice's native rule engine, but GenAI scenario scripts are already on their roadmap.
- Feasibility 6: scenario tools untested; no delete tool.
- Replicability 8: works anywhere.
- Presentation 5: hard to make surprising.
- Documentation 4: only indirect evidence.

**Perdidos e Achados**
- Fit 6: the mentors said not to underestimate the camera, but the evidence is weak.
- Adoption 3: continuous indoor video outside the platform; privacy; the RTSP feed has no authentication.
- Feasibility 3: the power adapter is a cheap fix, but the MCP has no vision and there is one fixed view.
- Replicability 7: a universal annoyance.
- Presentation 4: nothing to show without the camera.
- Documentation 3: US vendor surveys only.

## 7. Shortlist

Ranked by final score. **The team decides.**

| # | Candidate | Final | Intermediate | Why it is on the list | Biggest risk |
|---|---|---|---|---|---|
| 1 | **Casa Saudável** | 8.00 | 8.00 | One in three people affected, worsening, with a national 2030 target; humidity is absent from Altice's published offer; the best kit fit | Untested contact transitions and plug metering (test on Thursday); slow humidity sensor |
| 2 | **Casa que Cuida** | 7.60 | 7.50 | The strongest local evidence (people aged 65+ in Portugal: 2nd worst in the EU for damp, joint 2nd for cold; 517,146 living alone); a human story; "the house went quiet" alert | Consent and GDPR; must stay clear of Family Care (no routine monitoring) |
| 3 | **Calor Certo** | 7.10 | 6.75 | Strong figures; watts turning into euros | Overlaps Altice's energy pack; heaters are off-only |

**Recommendation in the report:** lead with Casa Saudável as the product, using an older mother living alone as its persona (*Pitch A*). Switch to the all-households version (*Pitch B*) if Altice says Family Care or SmartAL already covers home conditions.

## 8. Pitch-ready figures (Portuguese)

Each sentence uses a verified value with its source and year. Values are copied exactly. Where a number is our own arithmetic, the sentence says so.

1. Quase um em cada três portugueses (32,1%) vive numa casa com infiltrações, humidade ou apodrecimento, e o indicador agravou-se nos últimos três anos (INE, ICOR 2025).
2. Em 2023, Portugal foi o 2.º país da UE com mais população a viver em casas com humidade: 29,0%, contra 15,6% na média da UE (Eurostat, ilc_mdho01).
3. Entre as pessoas com 65 ou mais anos, 27,4% vivem com humidade em casa, o 2.º valor mais alto da UE e mais do dobro da média europeia, de 12,1% (Eurostat, ilc_mdho01, 2023).
4. Em 2025, 15,6% dos portugueses não tinham capacidade financeira para manter a casa adequadamente aquecida, contra 8,8% na UE (Eurostat, ilc_mdes01; INE, ICOR 2025).
5. Entre as pessoas com 65 ou mais anos, a proporção sobe para 22,2%, ex aequo com a Bulgária e logo atrás da Lituânia, contra 8,4% na UE (Eurostat, hlth_dhc140, 2025).
6. A Estratégia Nacional de Longo Prazo para o Combate à Pobreza Energética fixa para 2030 as metas de 10% de população sem capacidade para aquecer a casa e de 20% a viver com infiltrações ou humidade (RCM n.º 11/2024).
7. A OMS recomenda, com recomendação forte, 18 °C como temperatura interior segura nas estações frias (OMS, Housing and Health Guidelines, 2018).
8. Em 2021 viviam sozinhas 517 146 pessoas com 65 ou mais anos, contra 406 942 em 2011 (INE, Censos 2021, quadro Q1.04; soma das faixas etárias feita pela equipa).
9. No cenário central do INE, as pessoas com 65 ou mais anos serão 34,5% da população em 2050 (INE, Projeções de População Residente 2025-2100).
10. Em 2025, 36,07% dos portugueses entre os 65 e os 74 anos nunca tinham usado a internet, contra 16,4% na UE (Eurostat, isoc_ci_ifp_iu).
11. Em 2025 morreram 30 pessoas em incêndios em habitações no continente, e a lei isenta as habitações da obrigação de ter sistema de alarme de incêndio (ANEPC, Anuário SCIE 2025; Portaria n.º 135/2020, art. 126.º, n.º 2).
12. Em 2024, só 23,99% dos portugueses usaram um sistema de casa conectada, contra 33,04% na UE; entre os 65 e os 74 anos, apenas 8,8% (Eurostat, isoc_iiot_use).
13. A MEO tem 40,9% dos acessos à internet em local fixo em Portugal (ANACOM, 4.º trimestre de 2025).
14. Na UE, 32,2% das pessoas com 65 ou mais anos vivem sozinhas; em França, 37,1% (Eurostat, ilc_lvps30, 2025).
15. A Maison Sécurisée da SFR, em França, foi desenvolvida integralmente pela Altice Labs (Altice Labs, 2024).
16. O RASI 2025 atribui parte da descida dos furtos em residência à tecnologia de segurança residencial e a "mais teletrabalho, menos ausências prolongadas" (RASI 2025, p. 84).

## 9. Questions for the checkpoint

| # | Question | Why we ask |
|---|---|---|
| 1 | Which customer segment do MEO and SFR want to grow? In a care scenario, who pays: the older person or a family member? | Decides who the product talks to (§2) |
| 2 | What does **Family Care** detect today, and with which sensors? Would a home-health module (cold, damp, smoke) on top of it be new to you? | Our top candidate overlaps it (§5) |
| 3 | Is there a platform API for **events or push notifications** we may use, or should we poll? | The MCP has neither history nor notifications ([10-mcp-in-practice.md](10-mcp-in-practice.md)) |
| 4 | Can you **delete scenarios** we create in our home? | No delete tool, so each test is permanent |
| 5 | Can we press the **smoke sensor's test button** without triggering the hub alarm or emergency contacts? | Needed for a fire demo (D, and A's smoke check) |
| 6 | May we test **arming the alarm** in the lab? | The tool is mislabelled read-only, and Home mode has a 0 s delay |
| 7 | Can we put our own **dehumidifier or heater** on the plug at the venue? | Needed for live action in B and C |
| 8 | Status of the **camera power adapter** and the **Light** re-pairing | Decides whether G is possible, and whether the bulb can show status |
| 9 | Are we free to use outside data (**IPMA**) and an external **LLM API**? Any data-residency constraints? | Architecture and privacy questions in Q&A |
| 10 | Finalists: up to 6 or 3? Q&A: 1 or 2 minutes? Is the 18 Nov report the Sumário Executivo template, resubmitted on the 20th? | Open since the kick-off ([07-open-questions.md](07-open-questions.md)) |

## Appendix — verification log

**Date:** 17 Nov 2026. **Method:** four research agents searched in parallel, then Claude re-checked the key figures at the source. Downloads were kept in a scratch folder outside the repo and are not committed. The links above point to the official URLs.

**Re-checked at source in the verification pass:**
- every Eurostat value, re-pulled through the API with all dimensions filtered;
- INE ICOR 2025, Figura 22;
- INE family-structures release (24.8 %, 12.5 %) and table Q1.04 cells (517,146 and 406,942);
- INE projections (34.5 % in 2050);
- RCM 11/2024, n.º 2;
- WHO 2018 §4.1;
- ANEPC 2025 (5,182 dwelling fires; 37 and 30 deaths);
- RASI 2025, pp. 36, 40 and 84;
- Portaria 135/2020, art. 126.º;
- ANACOM 4T2025, Tabelas 4 and 6;
- GNR Censos Sénior 2025;
- the Altice Cognitive Home page (Family Care, Aging in place, Energy);
- the Altice Labs SFR blog post;
- the brochure text (segments, GenAI scenarios).

**Tested directly:** the IPMA open-data observations API (17 Nov, 227 stations, hourly temperature and humidity).

**AI use:** the research agents, the re-checking pass and the advisor review were all AI-assisted. The team is responsible for the result and should be able to defend each figure from its source.

**Checked by the research agents only** (page references recorded, not re-opened): WHO 2009 pages, DGEG social tariff, INE 2025 estimates, INE IUTICF, INUT, Pixie and Shane Co., SFR prices, the MEO Ajax kit.

**Discrepancies with the handoff, and inside the sources:**

| Item | Finding |
|---|---|
| EU damp 2023 | **15.6** in the current database; 15.5 in the older *Housing in Europe 2024* text. Use 15.6 |
| "Elderly 22.0 %" cold homes | Real, but from `hlth_dhc140` (age 65+), not `ilc_mdes01`. The 2024 value carries a break flag; 2025 is 22.2 |
| Cold homes 2024 | Confirmed (15.7 / 9.2). **2025 is now out** (15.6 / 8.8) |
| "37.8 % of 80+ live alone" | **UNVERIFIED**; it measures a wider category. Not used |
| "INE time-use survey 2015" | Wrong body: it was INUT, by CESIS and CITE. INE's survey is from 1999 |
| MEO ≈40 % | Confirmed: **40.9 %** of fixed accesses, Q4 2025 (ANACOM). The handoff link pointed to the press |
| "Altice sells to MEO" | Not stated in the brochure, which names no operator in its text. SFR is confirmed |
| Product name | Connected Home is now **Cognitive Home** (Oct 2026) |
| INE projections base | Uses the 2024 population from before INE's June 2026 revision, so projected ageing may be overstated |
| "30.9 %" | Means two different things: cold homes among people in poverty (2024), and the INE damp total (2024). Always name the indicator |

**Flags (planted or hidden content):**
- **No text addressed to an AI and no embedded instructions** in any file opened.
- **The 2025 Altice brochure carries a hidden paragraph** on pp. 1 and 16. It describes "Connected Home" as a B2B unified-communications suite, which contradicts the visible brochure. It is not an instruction, most likely a template leftover, but a tool that only extracts the PDF text would report it as fact. Not used.
- **sfr.fr/maison has a hidden screen-reader price** (€9.99) that differs from the visible one.

**Blocked sources:**
- ANACOM's Q2 2026 operator shares (the page loads by JavaScript);
- DGPJ crime statistics (now a Power BI app);
- an INSA repository PDF (anti-bot page);
- Diário da República detail pages (JavaScript; the official issue PDFs were used instead);
- parts of meo.pt (JavaScript).
