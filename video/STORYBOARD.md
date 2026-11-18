# Video 1 · Presentation · storyboard v3

The bar: put it side by side with a Claude launch film and see no difference, frame by frame, in the 4K export (`--scale=2`, 3840×2160). The team's verdict on v2: idea 7, implementation 4. It lacked creativity and taste, every animation was the same, one title broke onto two lines, there were 8 repeated photos, and "nothing needs configuring" was abstract cards nobody understood.

Rules for every frame:
- **Show, don't tell.** Every use case is a scene: real footage (the lab or licensed stock in `public/stock/`, with real OWLv2 boxes from `public/stock/boxes/`), our boxes locking on, then the alert arriving on a phone. Words support the picture; they never replace it.
- **One idea per shot**, with a clear focal point.
- **Titles fit on one line** at their size. Measure them; never let a phrase wrap. If it doesn't fit, cut words.
- **A varied motion vocabulary.** Do not reuse the same entrance twice in a row. The palette:
  - a hard cut on the beat;
  - the camera pushing in or pulling out on footage;
  - a whip-pan with motion blur;
  - a mask wipe with the ThingTracker corner brackets;
  - a match cut (box → card, phone → phone);
  - a parallax tilt of the phone;
  - a counter rolling;
  - a word-by-word reveal (at most twice in the film);
  - a light leak or flash on the shutter.
- **Fewer and better images:** 3 photos, not 8.
- **Sound:** a music bed with the lift at the safety section. Effects on the action, 2–3 frames ahead of the picture: tap, shutter, lock-on, notification, door, floodlight. No cartoon whooshes. The audio files are in `public/audio/` (see its manifest).
- **Claims.** Real numbers come only from `public/real/recognition.json`. Proposals and illustrations are labelled as such. The app UI is in English, every other text is in PT-PT.

## Shot list (≈ 88 s)

| # | Time | Picture | Text on screen | Sound |
|---|---|---|---|---|
| 1 | 0–4 | Cold open: three quick real moments. Hands patting pockets by the door; a dog by an empty bowl; a cat landing on a kitchen counter. | (none) | music in, soft |
| 2 | 4–8 | Black, then one line | “Onde deixei as chaves?”, then a hard cut to “O cão já comeu?” | hit-soft |
| 3 | 8–14 | The kit camera's real desk footage; boxes lock on one by one (livro, garrafa, auscultadores); push in on the book; the brackets close into the ThingTracker mark. | “A câmara já vê tudo.”, then the logo and the line “A câmara da casa passa a saber onde estão as coisas.” | lock-on ×3, then hit-soft |
| 4 | 14–24 | Register: the colleague's phone footage in a phone frame at real speed. Three shutters (front cover, angle, flat); each flash throws a photo card to the right; the 3 cards fold into the visual fingerprint (an abstract grid of 384 values), then the app's “Book added”. | “Três fotografias. Uma assinatura.” | shutter ×3, tap |
| 5 | 24–32 | Find: the kit desk footage; the box draws around the book; a narrow mono panel prints 3 lines (OWLv2 → DINOv2 → 0,70 ≥ 0,62); the label “O teu livro · 0,70”. | “O teu livro. Não um livro qualquer.” | lock-on, soft confirm |
| 6 | 32–40 | Ask: the phone tilts in (parallax); the question is typed; the answer card arrives with the photo, which scales up into the frame. | “Basta perguntar.” (one line) | typing-soft, notify-info |
| 7 | 40–50 | Leave home: stock of a person leaving by the front door (from behind); the door sensor chip “porta aberta”; cut to hands holding a phone; the notification “Saíste sem o livro” lands with a gentle push-in. | “Uma frase torna-se um sensor.” | door-open, notify-safety |
| 8 | 50–53 | Transition to the safety section: white out, then one line. | “Ninguém configura nada. A app percebe a casa.” | riser, music lift |
| 9 | 53–60 | Cat and knife: stock of the cat on the counter with real boxes “gato” and “faca” (only if a knife is truly in frame) turning red; the proposal card appears first (“Avisar se o gato subir à bancada perto de uma faca?” → Ativar); then the alert on a phone. | “A cozinha mais segura.” | lock-on, notify-safety |
| 10 | 60–66 | Dog: stock of the dog in the home with its box; a day timeline slides under it (tigela: 0 visitas hoje); the card “O cão ainda não comeu hoje.” | (card only) | tick, notify-info |
| 11 | 66–72 | Older person: stock of the kitchen in the morning with a box “pessoa · 07:42”; then a split with an empty kitchen at 12:00 and the card on a relative's phone “Ninguém passou pela cozinha até ao meio-dia.” | “Quem cuida, fica descansado.” | notify-info |
| 12 | 72–78 | Outdoor: the garden at night, a person by the gate with the box “pessoa · 02:14”; the floodlight comes on (a light flash); the card “Alguém no quintal.” Then a fast cut: a parcel at the door with the box and the card “Encomenda à porta.” | “Também lá fora.” | floodlight, notify-safety |
| 13 | 78–84 | How it works, on one line of nodes with straight arrows, drawn in as a single stroke: Em casa (câmara → deteção de movimento) │ Altice (modelos de visão, só a zona que mudou → memória da casa → assistente → MCP) → app e dispositivos. | “Nenhum vídeo nem imagem completa sai de casa.” | swish |
| 14 | 84–88 | The mark, “ThingTracker”, then “Ver, perceber, lembrar e agir.” and “Equipa IT-Porto · Desafio Altice Labs #3”. | | resolve, hit-soft |

Labels on screen: "ilustração" or "proposta" wherever the prototype does not do it today; "imagens de arquivo" in small type on stock footage.
