# The event

Sources: kick-off transcript of 16 Nov (`sources/meetings/`), team Slack, template footers.

The **participant guide** is not filed here yet. It holds the evaluation criteria, the venue address and the mentor list, so several points below say "see guide".

## What it is

- Aveiro Tech City Hackathon, 4th edition, November 2026.
- About 117 participants in 31 teams (12 + 12 + 7), 18 mentors, 4 jurors.
- Three challenges run as three separate competitions. Teams only compete inside their own challenge.

| # | Challenge | Proposed by | Teams |
|---|---|---|---|
| 1 | Use the data the city of Aveiro already collects to support concrete decisions and actions | Câmara Municipal de Aveiro and "Instituto de Comunicações" as transcribed (probably Instituto de Telecomunicações) | 12 |
| 2 | Ctrl+F: automatic identification of urban furniture with computer vision | Universidade de Aveiro (inferred from the transcript) | 12 |
| **3** | **Connected Homes Reimagined: AI at the service of the home** | **Altice Labs** | **7**, capped by the number of hardware kits |

## Timeline

| Date | What | Notes |
|---|---|---|
| Wed 4 Nov | Registration deadline | Each member registered individually and selected "Team" |
| Fri 13 Nov | Hardware kit pick-up at Altice Labs, Aveiro | Arranged by phone with the organisers |
| Mon 16 Nov | Online kick-off, then challenge room with mentors from 18:00 | Done. Transcript filed |
| Mon 16 – Wed 18 Nov | Online phase, teams work on their own schedule | |
| Wed 18 Nov | **Mandatory mentor checkpoint** | Guide slot is 14:00–18:00; another time the same day is fine if the mentors agree. 10 to 30 minutes |
| Wed 18 Nov, 19:00 | **1st deliverable due** — succinct 2-page report (the executive-summary PDF) | Google Form |
| Thu 19 Nov | Organisers set up the venue | |
| Fri 20 Nov, 08:30–20:00 | **In-person day** at Fábrica Centro Ciência Viva | Attendance mandatory |
| Fri 20 Nov, 09:30 | Coding time starts | |
| Fri 20 Nov, from 16:00 | Intermediate pitches to the challenge's mentors and jury; finalists selected | 3 per challenge (participants' guide) |
| Fri 20 Nov, 17:30 | **Executive summary (PDF) + presentation (PPT) + repo link due** | Coffee break |
| Fri 20 Nov, 18:00–19:30 | Final pitches on stage | Finalists only |
| Fri 20 Nov, 20:00 | Winners announced + cocktail | |

## Evaluation

Two rounds, **different criteria**. These are the official criteria and weights from the rules (`sources/rules/normas-2026.pdf`, Articles 16 and 18) and the FAQ, which override the numbers given verbally at the kick-off. The jury scores exactly these, so a technically brilliant solution can still lose points on the softer ones.

| | Intermediate | Final |
|---|---|---|
| When | Fri 20 Nov, from 16:00 | Fri 20 Nov, from 18:00 |
| Judged by | Mentors **and** jurors | Jury (5 members) |
| Format | 3 min pitch + **2 min** Q&A | 5 min pitch + 3 min Q&A |
| Who | Every team | **3** teams per challenge |

**Intermediate criteria** — each scored 1–10, weight 25 %:

| Criterion | Weight |
|---|---|
| Fit and response to the challenge | 25 % |
| **Ease of adoption of the project by the challenger** (Altice Labs) | 25 % |
| Feasibility of implementation and future management (sustainability) | 25 % |
| Presentation of the solution | 25 % |

**Final criteria** — each 1–10:

| Criterion | Weight |
|---|---|
| Fit and response to the challenge | 20 % |
| Ease of adoption by the challenger (Altice Labs) | 20 % |
| Feasibility of implementation and future management (sustainability) | 20 % |
| **Possibility of replication in other territories and contexts** | 20 % |
| Presentation of the solution | 10 % |
| Documentation (deliverables) of the solution | 10 % |

What the criteria tell us to optimise for: it is not just the demo. Two fifths of the final score (40 %) is **adoption by Altice + replicability** — i.e. would Altice actually ship this, and would it work beyond our one kit. Build and pitch for that.

> **Resolved on 20 Nov.** The official participants' guide (Drive, read 20 Nov) settles it: **3** finalists per challenge and a **3 + 2** min intermediate pitch, from 16:00; the presentation is due as PPT (PDF accepted) by 17:30 via Google Drive and must mention the tools used. The earlier note: the written rules and the FAQ both said the intermediate selects **up to six** teams per challenge, with a **3 + 1** min pitch. At the kick-off Rui said only the **3** best teams advance, with **3 + 2** min. The written documents (version vf1) are the formal rule; the kick-off was later and verbal. With only 7 teams in our challenge, "up to 6 advance" would mean almost everyone does. Worth a one-line check with the mentors.

- The whole team does not need to be at the intermediate pitch. Some can pitch while the rest keep working.
- Time is enforced: when it runs out you finish your sentence and stop.
- Finalists are only revealed when they are called to the stage, so **every team must prepare the full pitch**.

## Deliverables

From the rules (Article 14) and FAQ Q18. There are **two submission moments**:

| # | What | Deadline | Format |
|---|---|---|---|
| 1 | **Succinct report** of the approach to the problem | **Wed 18 Nov, 19:00** | Max 2 pages, obligatory |
| 2 | **Executive summary** | **Fri 20 Nov, 17:30** | PDF, max 2 pages, obligatory |
| 3 | **Presentation** | **Fri 20 Nov, 17:30** | PPT, obligatory |
| 4 | Link to the code repository | **Fri 20 Nov, 17:30** | Optional |

**Naming inconsistency, resolved pragmatically.** The written documents call the 18 Nov deliverable a "succinct report" and put the "executive summary" on the 20th. The kick-off, and the only 2-page template provided ("Sumário Executivo"), call the 18 Nov one the executive summary. Only one 2-page template and one slide template exist. So in practice:

- Write the **2-page PDF** using the Sumário Executivo template and submit it on the **18th**.
- Keep improving it and **resubmit the 2-page PDF on the 20th**, together with the **slides**.
- Treat them as the same document refined, unless the mentors say otherwise. Worth confirming at the checkpoint.

About the 2-page document:

- A short summary of work done and ideas to develop, for a mixed technical and non-technical audience.
- Sections in the template: challenge description, strategy, ideas for the proposed solution, AI tools.
- Make a copy of the template, fill in team name and challenge number, delete all the blue instruction text, export to PDF.
- It does not lock the solution; the team can keep developing and even change direction.

**Late submission can mean disqualification** (Article 14.2). There are no extensions. Submit early.

## Rules that affect the solution

From the rules and FAQ. These shape what we build and how we pitch:

- **Intellectual property goes to the challenger.** IP of the developed projects is assigned to the entity that set the challenge — here **Altice Labs** — for free non-commercial use and adaptation, with an obligation to share (Article 22.3, FAQ Q20). We do not keep ownership. So there is no reason to hold back, but also know the work becomes theirs.
- **AI tools are allowed** (FAQ Q17): coding assistants, content generation, data analysis. But the proposal must be original (no plagiarism), AI must not replace the team's own thinking, and the team must validate, test and fully understand the solution. The jury may question the technical choices, so be able to defend them. Using AI is neither a plus nor a minus by itself.
- **Originality.** All elements must be original or used with permission (Article 22.2). This applies to images and assets in our repo — credit or replace anything taken from the web (see `assets/README.md`).
- **Image and name rights.** By participating, teams authorise the organisers to use their names, images and solutions for promotion for 36 months (Article 23.3).
- **No conflict of interest for us.** Members affiliated with a challenger cannot enter that challenger's challenge (FAQ Q9). We are on the Altice challenge, so IT-Porto affiliation is not a problem here (it would be for Challenge #1, which Instituto de Telecomunicações co-runs).

## Prizes

€15,000 in total — nine monetary prizes, three per challenge: **€3,000** for 1st, **€1,500** for 2nd, **€500** for 3rd (Article 21). Only the top 3 per challenge get a prize, even though up to 6 may reach the final stage. (At the kick-off Rui implied all finalists get a prize — that matched his "3 finalists" figure, not the written "up to 6".)

The prize is paid to the **team representative** (Filipe), who splits it with the team. Payment may require, from the representative, up-to-date tax and social-security clearance certificates and an IBAN. Winners whose solution is not mature enough may be asked to finish it within 30 days for the prize to be confirmed.

## Rules and logistics

- **Language:** Portuguese is the official language. A team needs at least one Portuguese speaker.
- **Slack** is the official channel: announcements, general (logistics), random, and one channel per challenge. The challenge channels were made public during the kick-off, so use "browse channels" to join. General questions go in the challenge channel; private matters go by DM to a mentor.
- Mentors answer asynchronously. If one stays silent for a long time, tell the organisers.
- **Friday attendance is mandatory.** Leaving for about an hour, for example for an exam, is possible if agreed with Rui or Marta right after check-in. The organisation can issue a declaration to justify missed classes, on request.
- **Venue:** Fábrica Centro Ciência Viva de Aveiro ([map](https://maps.app.goo.gl/b5cENmcW2NtsTDho9)), about 20 minutes on foot from the train station, close to Fórum Aveiro. The venue provides Wi-Fi, workspace, AV equipment for the pitch, and meals (lunch, coffee breaks, drinks). Parts of the building have no mobile coverage.
- **Data and licences** must be respected whatever the challenge.

## Advice from the organisers

1. **Split the work early.** Brainstorm together, then give each person a responsibility such as data, interface or pitch. Agree internal checkpoints, because parts that work alone rarely work together first time.
2. **Use the mentors.** Do not stay blocked for long before asking.
3. **Read the evaluation criteria before starting** and ask about them if unsure.
4. **Rehearse the pitch with a stopwatch**, out loud, with the team.
5. **Have a plan B for the demo:** a recorded video or screenshots that can be opened quickly.
6. **Steer the AI, do not let it steer you.** AI use is expected, but "because the AI suggested it" is not an acceptable answer in Q&A. Understand and be able to justify every decision.
7. **Be honest about what works and what is simulated.** Simulating parts is fine with so little time. Hiding it is not.
8. **Submit before the deadline**, not at 18:59.
