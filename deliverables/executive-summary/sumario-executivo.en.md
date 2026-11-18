team: IT-Porto
challenge: #3 Connected Home, Reimagined: AI serving the home

## Challenge description

Challenge no. 3, set by Altice Labs, asks teams to rethink the connected home with artificial intelligence, through services that make everyday life simpler, more useful or safer. The only technical requirement is to integrate the MCP (“Model Context Protocol”) server of the Cognitive Home platform, which lets an AI agent query and control the devices of a real home. The challenge brief asks for solutions “beyond commands”.

## Strategy

The camera is the most versatile sensor in the home, but at the moment it is underused: in the challenge kit, it only reports that it has detected motion. The team’s strategy is to turn the camera into a source of information. Open-source vision models, running at home or on an Altice server, recognise objects and places, and analyse images only when there is motion or sound. A language model, used only when needed, turns sentences into rules and answers questions. The proposal rests on three principles: the camera as a source of information, not only of surveillance; integration with the Altice app and MCP server; and privacy by design (Article 25 of the GDPR).

The Portuguese market has room to grow: in 2024, 23.99 % of people aged 16 to 74 in Portugal used a connected-home system, against 33.04 % in the European Union (Eurostat), and MEO, with 40.4 % of fixed broadband accesses (ANACOM), sells an alarm kit whose camera only takes photos when there is motion.

## Ideas for the proposed solution

The proposed solution, ThingTracker, turns the home’s camera into a universal sensor, set up in natural language. The concept comes down to four simple actions: see, perceive/interpret, remember/relate and act, as the example in Figure 1 shows.

[[figura: figura-exemplo.en | From the visual enrolment of a thing to the action]]

To enrol a thing, a child for example, the user enters its name in the app and shows it to the camera for a few seconds. The local detector looks for the child, and the images make a digital and visual fingerprint of the thing, stored at home and in Altice’s database. The user can then ask “where is the child?”.

A sentence such as “tell me if the child is in danger” goes to the ThingTracker service, which sends it to the language model together with the enrolled things. The model works out what danger means, for the child and for others (a detergent, the stove), and returns structured rules, saved as a scenario through the MCP and evaluated at home; the actions go through the MCP. The same principle applies to other cases:

- Lost and found: with the wallet enrolled, if the user leaves home without it, they are alerted.
- Pets: if the door opens and the dog is no longer seen, the user is alerted.
- Older people: if no one goes into the kitchen by noon, a relative is alerted.
- Parcels: if the outdoor camera sees a parcel at the door, the user is alerted.
- Connected hob: if it is left on with no one in the kitchen, the user is alerted.

Each camera is one place: two or three are expected per home (kitchen, living room, entrance), plus an optional outdoor one; the customer chooses where they go, outside bedrooms and bathrooms. The system also suggests scenarios from what the camera learns about the home, without the user having to set them up: if it sees a cat, it suggests “tell me if the cat doesn’t go to its food bowl by 20:00”; if it sees a child, “tell me if the child gets hurt”. The user turns them on with one tap or creates their own. Figure 2 shows the complete architecture.

[[figura: arquitetura.en | ThingTracker architecture: at home, on the Altice platform and in the language model]]

So far, the team has connected to the MCP, accessed the kit camera’s live video and built a prototype that detects and recognises objects, answers questions and runs rules. In a test with a book, eight views taken with a phone were enough to recognise it on the kit camera (similarity of 0.70, against a threshold of 0.62).

## AI tools

- Open-source vision models: the prototype uses OWLv2 and DINOv2 (Apache-2.0, 0.7 GB, about 0.6 s per image on a laptop); the final solution adds Depth Anything V2 Small and ByteTrack. They can run on Altice servers or on the router, if it has AI capacity.
- Language model, under contract: Anthropic’s Claude, or an equivalent, provided that the contract excludes training on the data and includes a data processing agreement.
- Monthly cost to Altice, per home (estimate: 500,000 homes, 2 h of motion a day): €0.43 for the language model and €0.49 for vision, with motion detection at home and only the changed area analysed by Altice (€2.41 with full images).
- Development: Claude Code (Claude Opus 5.5) for research, programming and writing.

Sources: Eurostat (2024); ANACOM (Q2 2026); Hugging Face; AWS, Azure and NVIDIA (18 Nov 2026); team measurements.
