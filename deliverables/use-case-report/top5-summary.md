# Casa Atenta: one home assistant, every device

::: lead
Team IT-Porto · Challenge #3, Altice Labs · Tue 17 Nov 2026 · **v4, short version**<br>
It replaces the v3 recommendation (Casa Saudável on its own). The full v3 report (`top5-use-cases.pdf`) still holds the evidence on damp, cold and fire.
:::

::: note
**What changed.** v3 planned around the kit as it is today (one plug, one contact, no camera) instead of around a goal. The camera only lacks its power adapter, and it also has a microphone, a speaker and a siren. At the kick-off Hugo asked for the opposite of v3: «tirar partido dos vários tipos de sensores e equipamentos e também não menosprezar a fonte de dados que é uma câmara». Lost & found, scored 4.5 in v3 for lack of a powered camera, scores 7.7 once every device is combined.
:::

## 1. The recommendation

**Build Casa Atenta: one AI assistant that uses every device in the kit, plus the phones on the home Wi-Fi.**

- **Lead the pitch with what only the camera can do:**
  - «Onde deixei os óculos?» (Where did I leave my glasses?);
  - the moment someone leaves home and forgets something.
- **Keep damp and cold as the third moment.** It has the strongest official figures.
- **Smoke and the alarm are always on in the background.**

## 2. Every device has a role

| Device | Gives the assistant | In Casa Atenta |
|---|---|---|
| **Camera: video** | Sight | Remembers where objects were last left, using our own vision model on the video feed Altice provides |
| **Camera: microphone + speaker** | Hearing, voice | A spoken question after pressing a button; a spoken answer. **To test:** depends on Altice's video relay; fallback, the laptop speaker |
| **Camera: motion detection, siren** | Alertness | Wakes the vision model only when something moves; sounds the siren when there's danger |
| **Phones on the Wi-Fi** | Who is home | Arrivals and departures, and when the house is empty. «O seu telemóvel está em casa» (your phone is at home). No new device on Altice's platform |
| **Door/window contact** | Touch | The moment of leaving; a window left open |
| **Plug, with energy metering** | Hands | Switches off what was left on (heater, iron). Never switches a heater on |
| **Colour bulb** | A signal anyone can see | Amber: something was left behind. Blue: time to air the room. Red: smoke. **Offline since 4 Nov:** re-pair it |
| **Temperature + humidity** | Comfort and health | Damp and cold, compared with the weather outside from IPMA (the Portuguese weather service) |
| **Smoke sensor** | Danger | Plug off, red light, siren, a message to the family |
| **Security hub** | Protection | Arms the alarm only after an explicit "yes" (**untested**) |

## 3. What it does: three moments

1. **«Onde está?»** (Where is it?)
   - When the camera sees movement, our vision model notes where the keys, glasses, wallet or remote were put down.
   - Asked, the house answers aloud and sends the picture: «As chaves estão na mesa da entrada, desde as 18h40.» (The keys are on the hall table, since 18:40.)
   - For the phone: «Está em casa, ligado ao Wi-Fi; a câmara viu-o no sofá às 21h14.» (It's at home, on the Wi-Fi; the camera saw it on the sofa at 21:14.)
2. **Leaving home.**
   - The door opens, and the house checks everything at once: «Espere: as chaves ficaram na mesa, e o aquecedor está ligado.» (Wait: the keys are still on the table, and the heater is on.) The bulb turns amber.
   - When the last phone leaves the Wi-Fi, the house switches off the plug and asks «Quer ativar o alarme?» (Do you want to arm the alarm?).
   - When someone comes back, it offers to disarm.
3. **A healthy home.**
   - The bulb turns blue, and the house says: «Boa altura para arejar: lá fora o ar tem menos água.» (A good time to air the room: the air outside holds less water.) No app needed.
   - The family is told if a room stays cold.

**Always on:**
- On smoke: plug off, red light, siren, and a message.
- When nobody is home and the camera sees a person: a snapshot to the phone.

## 4. Why: the evidence

| Fact | Figure | Source |
|---|---|---|
| Dementia | **Portugal 2.29 %** of the population (238,401 people), against **2.02 %** in the EU27. 3rd highest in the EU, after Italy and Greece (our ranking of the table) | Alzheimer Europe, *Prevalence of Dementia in Europe 2025*, Table 4 |
| Misplacing things | An official early warning sign of dementia (sign 7 of 10), and also an ordinary everyday problem | Alzheimer's Association, *10 Early Signs* |
| Houses left open | 3,945 home thefts without forced entry in 2025, where "a porta ou janela podem estar abertas" (the door or window may be open). An upper bound, not a count of open doors | RASI 2025, p. 84 |
| The big players | Google's "Ask Home" searches camera footage in plain language: 20 countries, **not Portugal**, and built to find events, not objects | Google Home Help, read 17 Nov 2026 |
| Altice today | Its cameras serve security: cloud recordings, a timeline of events, snapshots during security events. No footage search, no finding objects | Cognitive Home brochure, Oct 2026 |
| Damp, people aged 65+ | **27.4 %** in Portugal against 12.1 % in the EU; 2nd in the EU | Eurostat `ilc_mdho01`, 2023 |
| People aged 65+ living alone | **517,146** | INE, Census 2021 |

**Limit:** misplacing things is *one of* the common memory complaints, not *the* most common (forgetting names comes first). Vendor surveys are not used.

## 5. Scores (out of 10, official criteria and weights)

| Option | Fit | Adoption | Feasibility | Replicability | Presentation | Documentation | Intermediate | **Final** |
|---|---|---|---|---|---|---|---|---|
| **Casa Atenta**: every device, all three moments | 9 | 8 | 6 | 9 | 8 | 8 | 7.75 | **8.00** |
| Casa Saudável alone (v3's pick) | 7 | 9 | 7 | 8 | 8 | 8 | 7.75 | 7.80 |
| Memory + leaving only | 9 | 7 | 6 | 9 | 9 | 6 | 7.75 | 7.70 |
| Casa que Cuida (family view, older person) | 8 | 6 | 7 | 8 | 8 | 8 | 7.25 | 7.40 |
| Vigia with the camera (smoke + intrusion) | 7 | 6 | 6 | 7 | 8 | 7 | 6.75 | 6.70 |

**Why:**
- **Fit:** the brief asks for surprise, everyday use, combined devices and the camera. Casa Saudável alone uses neither the camera nor most of the kit, so its fit drops from 8 to 7.
- **Adoption:** built on what Altice already sells; nothing in their offer finds objects. Held back by the privacy of an indoor camera, which is why damp and cold (no privacy risk) stay in.
- **Feasibility is the risk:** camera adapter, sound path, small-object vision, phone presence. Each has a fallback (§7).
- **The top three tie at 7.75 in the intermediate round.** The numbers can't separate them; the brief can.

## 6. Privacy and the law, built in

- **The camera never stores people or faces.** It keeps one cropped image per object, for 72 hours at most, and stores no video. People are blacked out before any image leaves the house. There is no face recognition.
- **The microphone listens only after a button is pressed, and stores no audio.**
  - Portuguese law bans sound capture by video-surveillance cameras (Lei 58/2019, art. 19.º, n.º 4).
  - Recording someone's words without consent is a crime (Código Penal, art. 199.º).
- **Phone presence uses only phones the household registers.** It keeps a home/away state, not a history.
- **One button pauses the camera and the microphone.** The assistant says it is an AI.

## 7. The demo, and what is live

| Step | Live | Fallback if a test fails |
|---|---|---|
| Keys put on the table → «Onde estão as chaves?» → answer with the picture | Camera + vision model (keys about 1–2 m from the camera, good light) | A recording, labelled |
| The answer is spoken | The camera speaker, if Altice's relay carries sound back | The laptop speaker, with a European Portuguese system voice |
| The door opens → «as chaves ficaram na mesa, e o aquecedor está ligado» + amber light | Contact (open/closed **untested**), plug drawing power (a lamp stands in for the heater), bulb | A recording; the bulb step shown in the log |
| The phone leaves → plug off → «Quer ativar o alarme?» | Phone presence (the wait is shortened, and we say so); plug off is verified | A "vou sair" (I'm leaving) button in the chat |
| Blue light: time to air | Live temperature and humidity + IPMA | — |

**Simulated, and said aloud:** the smoke, arming the alarm (unless the mentors allow it), and any history over several days.

## 8. The pitch (3 min, PT-PT)

::: pitch
**[Gancho]** «Onde é que eu deixei os óculos?» A Dona Maria tem 81 anos, vive sozinha, e faz esta pergunta todos os dias. A Dona Maria é uma personagem; os números não são.

**[Problema]** Em Portugal, 2,29% da população vive com demência, acima da média europeia, que é de 2,02%. E perder objetos com frequência é um dos sinais de alerta. Mas a casa da Dona Maria já tem câmara, sensores e uma tomada inteligente. Vê tudo. Só não presta atenção.

**[Solução]** A Casa Atenta junta todos os equipamentos da casa num só assistente. Vê, com a câmara. Ouve e fala, pela própria câmara. Sabe quem está em casa, pelos telemóveis ligados ao Wi-Fi. Sente a porta, o fumo, a temperatura e a humidade. E age: desliga a tomada, muda a cor da luz, faz soar a sirene.

**[Três momentos]** Primeiro: «Onde estão os óculos?» A casa lembra-se: «Estão na mesa da sala, ao lado do comando.» Segundo: alguém abre a porta para sair, e a casa verifica tudo num instante: «Espere: as chaves ficaram na mesa da entrada, e o aquecedor está ligado.» A luz fica laranja. Quando a casa fica vazia, desliga a tomada e pergunta se deve ativar o alarme. Terceiro: a luz fica azul, porque é boa altura para arejar. Entre as pessoas com 65 ou mais anos, Portugal é o segundo país da União Europeia com mais humidade em casa.

**[Demonstração]** *[pousar as chaves na mesa]* Vejam: pousamos as chaves e perguntamos onde estão. A resposta vem da câmara deste kit, ao vivo, com a imagem. Agora abrimos a porta. *[aviso e luz]* O fumo e o histórico de vários dias são simulados, e estão identificados.

**[Privacidade]** A câmara não guarda pessoas nem rostos: guarda onde ficaram as coisas, durante 72 horas, no máximo. O microfone só ouve depois de se carregar num botão. E tudo se pode pôr em pausa.

**[Porquê a Altice]** A Altice já vende a câmara e os sensores, e usa a câmara para a segurança. Nós usamo-la no dia a dia. A Google já pesquisa vídeos de câmaras com IA, mas não em Portugal, e para encontrar acontecimentos, não objetos. E para saber quem está em casa não é preciso hardware novo: basta o Wi-Fi.

**[Fecho]** A casa já está conectada. *[pausa]* Agora, também presta atenção.
:::

**Timing:** about 370 words, roughly 2:45. If a rehearsal runs over, cut the third moment down to its first sentence.

**Q&A to expect:**
- **"Isso não é vigilância?"** (Isn't that surveillance?) No people, no faces, no video: only where things were left, deleted after 72 h. The microphone works only on a button.
- **"Uma câmara chega para a casa toda?"** (Is one camera enough for the whole house?) No. It covers the places where things get left (the hall, the living room). In the product, that means one or two cameras.
- **"E se a IA se enganar?"** (And if the AI gets it wrong?) It always shows the picture and the time. With no recent sighting, it says «não tenho a certeza» (I'm not sure).
- **"Isto não é o Family Care?"** (Isn't this Family Care?) Family Care watches the person's routine; we watch objects and the home.

## 9. What to do now

**Today:**
1. **Buy the camera's power adapter:** 12 V, 2 A, barrel 5.5 × 2.1 mm, centre-positive. Check the camera's label first. Without it, nothing in §3.1 or §3.2 can be tested.
2. **Get the bulb back online.** If it won't connect, ask the mentors to re-pair it.

**As soon as the camera has power (about 1 hour):** test that the video plays in VLC; whether the stream has sound and a 2-second sound plays through the camera; whether the vision model finds keys at 1–2 m; that a team member's phone (not the Redmi hotspot) shows up from the Mac; the door contact going from open to closed; the plug's energy reading with a lamp plugged in.

**At Wednesday's checkpoint, ask:**
1. "May we run a vision model on the camera feed, and can your relay carry sound back to the camera's speaker?"
2. "Can the bulb be re-paired?"
3. "May we test arming the alarm?"
4. "Is a camera inside the home acceptable for Altice if it stores no people, only objects?"

**Before 19:00:** the 2-page Sumário must be rewritten for Casa Atenta. The draft in the full report is still the v3 one.
