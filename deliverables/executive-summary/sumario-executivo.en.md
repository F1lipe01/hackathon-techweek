team: IT-Porto
challenge: #3 Connected Home, Reimagined: AI serving the home

## Challenge description

Challenge no. 3, set by Altice Labs, asks teams to rethink the connected home with artificial intelligence, through services that make everyday life simpler, more useful or safer. The only technical requirement is to integrate the MCP (“Model Context Protocol”) server of the Cognitive Home platform, which lets an AI agent query and control the devices of a real home. The challenge brief asks for solutions “beyond commands”, and the mentors highlighted the camera’s potential as a source of data.

## Strategy

The camera is the most versatile sensor in the home, but today it is underused: in the challenge kit, it only reports that it has detected motion. The team’s strategy is to turn the camera into a source of information. Open-source vision models, running at home or on an Altice server, recognise objects and places, and analyse images only when there is motion or sound; the rest of the time, the camera stays idle. A language model, used only when needed, turns sentences into rules and answers questions. The proposal rests on three principles: the camera as a source of information, not only of surveillance; integration with the Altice app and MCP server; and privacy by design (Article 25 of the GDPR).

The Portuguese market has room to grow: in 2024, 23.99 % of people aged 16 to 74 in Portugal used a connected-home system, against 33.04 % in the European Union (Eurostat), and MEO, with 40.4 % of fixed broadband accesses (ANACOM), sells an alarm kit whose camera only takes photos when there is motion.

## Ideas for the proposed solution

The proposed solution, ThingTracker, turns the home’s camera into a universal sensor, set up in natural language. The concept comes down to four simple actions: see, perceive/interpret, remember/relate and act, as the example in Figure 1 shows.

[[figura: figura-exemplo.en | From the visual enrolment of an object to the action]]

To enrol an object, the user enters its name in the app and shows the object to the camera for a few seconds. The English name (“book”) is the search term for the local detector, and the images make a digital and visual fingerprint of the thing, stored with the local models and in Altice’s database, linked to the customer. The user can then ask “where is my book?”; if there is more than one, the system asks which one.

A sentence such as “tell me if I leave home without my book” goes to the ThingTracker service, which sends it to the language model together with the enrolled objects and the available MCP tools. The model returns a structured rule, saved as a platform scenario through the MCP; the rule is evaluated at home and the actions go through the MCP. The same principle applies to other cases:

- Children: if a child climbs a bookcase, the parents receive an alert and, if they confirm, the siren sounds.
- Pets and plants: “tell me if the cat hasn’t drunk any water by 18:00”.
- Older people: if no one goes into the kitchen by noon, a relative is alerted.
- Authorised people and security: if a stranger comes in while none of the family’s phones is at home, the user receives a photo and can arm the alarm; recognising family members is optional and requires consent.
- Energy: if the camera sees no one for 30 minutes, the smart plug switches off the heater.

The system also suggests scenarios based on the home’s profile: if the camera detects children, it suggests, for example, “tell me if the children are doing something wrong, something that could hurt them, or acting strangely”; if it detects a dog, it suggests scenarios for the pet. The user accepts the suggestions or creates their own. Figure 2 shows the complete architecture.

[[figura: arquitetura.en | ThingTracker architecture: at home, on the Altice platform and in the language model]]

So far, the team has connected to the MCP, accessed the kit camera’s live video and built a prototype that detects objects, answers questions and runs rules.

## AI tools

- Open-source vision models: the prototype uses OWLv2 and DINOv2 (Apache-2.0, 0.7 GB, about 0.6 s per image on a laptop); the final solution adds Depth Anything V2 Small and ByteTrack. They can run on an Altice server or, when real time is needed, on the home’s own router, if it has AI capacity, or on a small box connected to it.
- Language model, under contract: Anthropic’s Claude, or an equivalent, provided that the contract excludes training on the data and includes a data processing agreement.
- Monthly cost per home, excluding hardware: about €0.43 for the language model and under €0.15 of electricity for local vision, with 2 h of motion a day.
- Development: Claude Code (Claude Opus 5.5) for research, programming and writing.

Sources: Eurostat (isoc_iiot_use, 2024); ANACOM (Q2 2026); model cards (Hugging Face); team measurements.
