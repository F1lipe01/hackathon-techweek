# Video 1 · Presentation · storyboard v4

The bar is unchanged: side by side with a Claude launch film, frame by frame, in the 4K export (`--scale=2`). The team's review of v3 kept the start and the "Basta perguntar" part; v4 answers the rest of their notes.

What changes from v3:
- **A new opening:** a rapid-fire montage of everyday questions, one shot per beat with a boom, then a hard stop and the first clean tracking.
- **No book in video 1** (video 2 covers it): no kit desk and no three-photo registration. The keys carry the story: registered in the app, found, and forgotten at the door.
- **Brighter and airier throughout:** daylight, warm whites, no moody scene. Phones are composited over bright, defocused real homes, with depth of field, a soft shadow, a slight 3D tilt and camera moves; notifications arrive on a hand-held phone.
- **The grandmother is a real older person:** her normal mornings, then the empty kitchen at noon.
- **Sound on every move:** a whoosh on camera moves, a swipe on UI slides, a lock-on on each box, a shutter on photos, a boom on the montage cuts.
- **End card:** "ThingTracker" and "by Altice Labs", text only.

Rules for every frame:
- **Show, don't tell.** Every use case is real footage, our box locking on, then the alert on a phone.
- **Tracking is clean from the first frame.** Corner brackets that fit the object exactly (keyframed by hand against the footage where the detector's box is loose), a smooth lock-on, a label chip with the object's name. No scores in the montage; the real recognition numbers stay in video 2.
- **One line per title**, measured in code; the render fails if a title wraps.
- **A varied motion vocabulary:** hard cuts on the beat, camera push-ins, whip-pans with motion blur, a bracket mask, match cuts, a parallax tilt of the phone, rolling counters, light leaks. The word-by-word reveal is used at most twice.
- **Honesty labels in small type:** "imagens de arquivo" on stock, "conceito" where the prototype does not do it today, "ilustração" for drawn effects. No knife box on stock (no clip has a real knife). No child's face. Stock people only from behind or in profile; nobody presented as an intruder.
- **Language:** the app UI in English (it copies the English app); everything else in PT-PT.

Review notes applied (Video 2 review, also binding here):
- **Sound:** no beeps on lock-ons, no crinkly whooshes, no squeezed swipes. Lock-ons are soft clicks, transitions a low air whoosh, UI slides silent until the cleaner kit (`sfx/v3`) lands; booms only on the montage cuts, the stop hit before the drop.
- **Labels and scores sit on top of their rectangles**, never in a sentence beside them. Boxes are attached to the image's transform, so they never jitter in a zoom.
- **Something always moves;** no flicker, no harsh flashes, no repeated frames (calm shots are held stills with a smooth push, not slowed footage).
- **Readable:** titles on one grid (x = 110 px; bottom-left on footage, mid-left beside phones), the camera pushes into the phone's UI element that matters, no tiny floating cards.
- **Icons:** clean line icons that draw on (a key, a wallet, glasses, a bell); no wand, no stars, no colour emoji.

## Shot list (89 s on the fast music bed, 120 BPM: a beat is 15 frames)

| # | Picture | Text | Sound |
|---|---|---|---|
| 1 | Montage, one shot per beat over the bed's rising intro: keys on the hall table, a dog by its bowl, an older woman in the morning, sunglasses, a kettle, a parcel at the door, a hand locking the front door, a cat on the counter (a pill box and a wallet replace the kettle and the cat when their clips land). Clean bracket boxes and name chips. | One question per shot: “Onde estão as chaves?”, “O cão já comeu?”, “A minha mãe já acordou?”, “Onde deixei os óculos?”, “Deixei a chaleira ligada?”, “A encomenda chegou?”, “Fechei a porta?”, “O gato subiu à bancada?” | a boom on every cut |
| 2 | Hard stop: one beat of white, just before the drop. | – | the stop hit, then silence |
| 3 | On the drop: the keys on the hall table; the brackets lock on, the camera pushes in, the corners close into the ThingTracker mark. | “A câmara da casa passa a saber onde estão as coisas.” | lock-on, whoosh, boom |
| 4 | Register: a phone over a bright, defocused living room; “Add thing” → “Keys” → the keys shown to the camera (push-in on the camera view) → “Keys added”. | “Mostra-se uma vez.” · ilustração | taps, shutters |
| 5 | Ask: the phone tilts in; “Where are my keys?”; the answer card (push-in), whose photo grows into the frame: the hall table, the keys boxed. | “Basta perguntar.” | typing, notify, whoosh, lock-on |
| 6 | A sentence becomes a sensor: the sensor card (push-in); whip-pan to the same hall as someone leaves by the door; a hand-held phone wakes with “Saíste sem as chaves.” | “Uma frase torna-se um sensor.” | typing, whip, door, notify |
| 7 | How it works, in the music's breakdown: one line drawn in a single stroke. | “Nenhum vídeo nem imagem completa sai de casa.” | whoosh |
| 8 | White-out, one line, the riser into the lift. | “Ninguém configura nada. A app percebe a casa.” | riser |
| 9 | On the lift: a cat on a bright counter, the real “gato” box; the proposal accepted with one tap; the lamp turns red; the alert. | “A cozinha, mais segura.” · conceito | click, tap, notify |
| 10 | The dog by its empty bowl, “cão” and “tigela” boxes; the day runs to 18:00; the alert. | (card only) · conceito | click, notify |
| 11 | The grandmother's normal mornings (a real older woman, from behind, boxed); today, the kitchen empty until noon, the clock red at 12:00; the daughter's phone. | “Meio-dia, e a avó não veio à cozinha.” | click, tick, notify |
| 12 | The night, lifted bright (a silhouette, boxed); then the next morning, the home's memory answers “What happened last night?” with the two unusual events, one pinned. | “O que aconteceu às 4h?” · conceito | whip, notify, tap |
| 13 | End card on the bed's final hit, text only. | “ThingTracker” · “by Altice Labs” | the music's final hit |

Assets: stock in `public/stock/` (licensed, with real OWLv2 boxes in `boxes/`), the music bed and sfx in `public/audio/` (see its manifest). Clips still to come are drawn as labelled placeholders until they land.
