# Operator costs — ThingTracker's vision models at 500,000 homes

State on **Wed 18 Nov 2026**. Every number below is printed by [`deliverables/opcost/model.py`](../deliverables/opcost/model.py) (`python3 deliverables/opcost/model.py`). Each external figure has a numbered source at the end; everything else is marked **ASSUMPTION**, with the reasoning. As in the [business case](16-business-case.md), 1 USD = 1 EUR and prices are net of VAT.

## Final design (20 Nov): fully local

The team's final decision: all perception and inference run on the home device, which is the router if it has an NPU, or a dedicated box such as a Raspberry Pi 5 with an AI accelerator or a Jetson Orin Nano Super. Images, video, visual fingerprints and face templates never leave the home; the Altice platform carries text only (accounts, metadata, the event log, notifications, the relay to the home, device actions through the MCP). Vision on Altice's servers, the hybrid path costed below at about €0.49 per home a month, is the alternative evaluated and not chosen: images would leave the home.

The chosen design costs equipment bought once, plus electricity (the team's price research, 20 Nov):

- **Equipment, bought once:** an indoor camera, about €45 (the average of 3 models on sale in Portugal); a light device, a Raspberry Pi 5, about €200; a heavy device, a Jetson Orin Nano Super, about €345; or a router with an NPU, about €15 more (an estimate).
- **Over 5 years,** the device comes to €3.33 a month (Raspberry Pi 5) or €5.75 a month (Jetson Orin Nano Super).
- **Electricity for the models** costs cents a month: below €0.01 for YOLOv8n, and up to €0.72 for OWLv2 at 12 h of motion a day (a team estimate on a Jetson Orin Nano).
- **Who buys the device.** A box paid for by Altice does not pay back at €3.99 a month: it leaves −€4.81 to −€6.90 per home a month (section 9, options A2 and A3). The model works with the AI on the router, or with equipment the customer buys.
- **The sections below are the earlier analysis (18 Nov)** and stay as context: the Jetson's $249 launch price, hardware amortised over 36 months, 1 USD = 1 EUR, and the hybrid path on Altice's own L4 servers.

Sources of the 20 Nov figures (the team's price research):

- Cameras: TP-Link Tapo C210 €42.00 (codi-tek.com, Lisbon); EZVIZ H8C SE €37.99 (worten.pt); Reolink E1 Pro €48.76 on sale, €64.99 regular (ipcam-shop.nl); the Portuguese range is €30–80 (4gnews.pt guide).
- Raspberry Pi 5 8 GB with power supply, case and storage: about €200, an estimate between the $130 MSRP, $199.95 on Amazon and €264.49 at an EU retailer.
- Jetson Orin Nano Super developer kit: $399 ≈ €345 (cnx-software price list; about $1.15 per €, an assumption).

## In one minute (earlier analysis, 18 Nov)

- **The question.** The business case shows the cost per home of the language model (about €0.43 a month). The mentors asked for the operator's cost of the vision models, which depends on where they run. They also objected that a device per home, or a fleet of servers, is very costly at 500,000 customers, which is why companies use hyperscalers.
- **The objection holds for full frames.** Analysing every frame in motion at full resolution costs Altice €2.41 per home a month on its own servers, €3.93 to €4.26 on hyperscaler GPUs on demand, and €6.55 to €8.64 with a box in every home. With the €3.99 add-on, none of these leaves a margin.
- **The path recommended on 18 Nov costs about €0.49 per home a month** (one camera; €0.98 with two). The cheap motion check stays at home, on the camera or the router. Only the region that changed goes to Altice's servers, and work that is not urgent waits in a queue for a quiet moment, so the servers are not sized for the evening peak. That leaves about €1.25 per home a month.
- **The key assumption:** 2 h of motion per camera a day, analysed at 1 frame per second, with a GPU running at 25 % of its peak speed. Each one doubles or halves the cost (section 9).
- **If the router has an NPU that can run the models,** the cost falls to about €0.36 per home a month, but nothing yet shows that it can.

## 1. What is being costed

ThingTracker's camera sits idle until a cheap motion check (two small grey images compared every 0.5 s) sees a change. Then the heavy models run for a few seconds: OWLv2 finds the registered things in the frame and DINOv2 makes a visual fingerprint of each candidate. Only small crops leave the home today. The question is where those heavy models run at 500,000 homes:

| Option | Where the heavy models run | Who pays the electricity |
|---|---|---|
| A. At home | In the router, if it has an NPU, or in a small box next to it | The customer |
| B. Altice's own servers | GPU servers in a datacentre in Portugal | Altice |
| C. Hyperscaler | Rented GPUs in an EU region (AWS, Azure) | Altice, inside the hourly price |

## 2. How much work, and when

The business case assumes 2 h of motion per camera a day. The work is not spread evenly: it peaks in the evening. We do not have a measured daily profile for Portuguese homes, so the hourly shape is an **ASSUMPTION** (low at night, peaks at 7–8 h and 19–21 h; see `HOURLY_WEIGHT` in the model).

| Quantity | Arithmetic | Value |
|---|---|---|
| Duty cycle | 2 h / 24 h | 8.33 % |
| Cameras in motion in the busiest hour (20 h) | 2 h × 10.34 % of the day's motion | 20.67 % |
| Busiest 15 minutes (**ASSUMPTION**: ×1.2) | 20.67 % × 1.2 | 24.81 % |
| Peak factor | 24.81 % / 8.33 % | 2.98 |
| Frames analysed per camera a month | 2 h × 3,600 s × 1 fps × 30.4 days | 218,880 |

A server farm sized for the peak is therefore about three times bigger than the average load needs.

## 3. How much work is one frame, and how fast is each accelerator

We found no published benchmark of OWLv2 or DINOv2 on a T4 or an L4. We therefore count the work in each frame from the models' architecture, and assume how much of each chip's peak speed is reached.

- OWLv2 base, patch 16, reads a 960 × 960 image (model configuration, [S14]): 60 × 60 = 3,600 patches, 12 layers of width 768. A ViT layer costs 12·N·D² multiply-adds for its linear parts plus 2·N²·D for attention, so the encoder costs **1.09 TFLOP** per frame. With +3 % for the box heads (**ASSUMPTION**) and three DINOv2-small crops at 12 GFLOP each, one frame is **1.16 TFLOP**.
- If only the region that changed is analysed, resized to 640 × 640 (1,600 patches), the frame costs **0.41 TFLOP**. Whether OWLv2 stays accurate at that size has to be tested (**ASSUMPTION**).
- Measured on the team's MacBook (Apple M1 Pro, MPS): 0.57 s for OWLv2 and 22 ms per DINOv2 crop, so 0.64 s per frame, an effective 1.8 TFLOPS.

**ASSUMPTION: a GPU running TensorRT in FP16 reaches 25 % of its dense FP16 peak on these models.** Cross-check: NVIDIA's NanoOWL runs OWL-ViT B/16 at 768 × 768 (0.59 TFLOP) at 25 frames per second on a Jetson AGX Orin [S5], an effective 14.7 TFLOPS; our assumption gives a T4 16.2 TFLOPS, the same order.

| Accelerator | Dense FP16 peak | Effective (25 %) | Frames/s, full frame | Frames/s, changed region |
|---|---|---|---|---|
| NVIDIA T4 | 65 TFLOPS [S1] | 16.2 TFLOPS | 14.0 | 39.3 |
| NVIDIA L4 | 121 TFLOPS (242 with sparsity, halved) [S2] | 30.2 TFLOPS | 26.1 | 73.1 |
| Jetson Orin Nano Super | 16.8 TFLOPS (67 sparse INT8 TOPS [S6], ÷4, **ASSUMPTION**) | 4.2 TFLOPS | 3.6 | 10.1 |
| MacBook M1 Pro (measured) | — (measured, not derived from a peak) | 1.8 TFLOPS | 1.6 | Not calculated |

## 4. Option A: a device in every home

Hardware is amortised over 36 months, as in the business case. **ASSUMPTIONS:** €15 shipping per box, 3 % of devices fail each year, €30 to replace one, and the router premium is spread over a 60-month router life.

| Device | Price | Operator €/home/month | €/camera, 2 cameras | Customer electricity €/month | Hardware at 500,000 homes | Runs OWLv2 at 960? |
|---|---|---|---|---|---|---|
| A1. NPU in a new router | €15 premium (**ASSUMPTION**, no public price) | 0.36 | 0.18 | 0.11 | €7.5 M | Unknown; probably needs a lighter detector |
| A2. Raspberry Pi 5 4 GB + AI HAT+ 13 TOPS | $110 [S3] + $70 [S4] + $20 case and power (**ASSUMPTION**) = €200 | 6.55 | 3.27 | 0.59 | €107.5 M | No: the 13 TOPS Hailo-8L needs a lighter detector |
| A3. Jetson Orin Nano Super kit | $249 [S6] + $20 storage = €269 | 8.64 | 4.32 | 1.08 | €142.0 M | Yes, about 3.6 frames/s |

Arithmetic for A2: (€200 + €15) / 36 = €5.97, plus failures 3 % × (€200 + €30) / 12 = €0.57, so €6.55 a month. Electricity: (22 h × 3 W + 2 h × 8 W) × 30.4 days = 2.49 kWh × €0.2367 = €0.59, paid by the customer (watts are an **ASSUMPTION**; the Jetson's 7–25 W range is official [S6]).

Memory prices have pushed small computers up: the Raspberry Pi 5 4 GB cost $60 at launch and $110 in April 2026 [S3]. **A box in every home costs €100–140 M up front at 500,000 homes, the strongest version of the objection.** Option A only works if the router or camera that Altice already installs can run the models.

## 5. Option B: Altice's own GPU servers in Portugal, full frames, sized for the peak

| Step | Arithmetic | 1 camera per home | 2 cameras |
|---|---|---|---|
| Average load | 500,000 × 8.33 % × 1 fps | 41,667 fps | 83,333 fps |
| Peak load | 500,000 × 24.81 % × 1 fps | 124,031 fps | 248,062 fps |
| L4 cards | 124,031 / (26.1 × 70 % busy, **ASSUMPTION**) × 1.1 spare | 7,466 | 14,933 |
| Hardware | 7,466 × €2,500 (**ASSUMPTION** [S12]) + 1,867 servers × €8,000 (**ASSUMPTION**) | €33.6 M | €67.2 M |
| Depreciation | / 48 months (**ASSUMPTION**) | €700 k | €1,400 k |
| Energy | 699 kW average × PUE 1.54 [S10] × 730 h × €0.1135/kWh [S11] | €89 k | €178 k |
| Datacentre space and cooling | 1,004 kW × €150/kW (**ASSUMPTION**) | €151 k | €301 k |
| Operations | 8 % of hardware a year (**ASSUMPTION**) | €224 k | €448 k |
| Network | 79 Gbps at the peak × €0.50 per Mbps (**ASSUMPTION**) | €40 k | €79 k |
| **Total a month** | Depreciation + energy + space + operations + network | **€1,203 k** | **€2,407 k** |
| **Per home / per camera** | Total ÷ 500,000 homes / ÷ cameras | **€2.41 / €2.41** | **€4.81 / €2.41** |

Sized for the peak, the cards are busy only 21 % of the time on average. That idle capacity is the real cost behind the objection.

## 6. Option C: hyperscaler GPUs in an EU region, full frames

On-demand and spot instances follow the load hour by hour (+15 % for scaling lag, **ASSUMPTION**); reserved instances run 24 h a day, sized for the peak. Data sent into the cloud is free (Azure "Standard Data Transfer In": $0.00 [S9]); only small results leave it, at $0.08/GB after the first 100 GB [S9].

| Offer | $/hour | Instances at the peak | €/home/month, 1 camera | €/home/month, 2 cameras |
|---|---|---|---|---|
| AWS g4dn.xlarge (T4), on-demand, Ireland [S7] | 0.587 | 12,635 | 4.26 | 8.52 |
| AWS g6.xlarge (L4), on-demand, Frankfurt [S7] | 1.0064 | 6,788 | 3.93 | 7.86 |
| Azure NC4as T4 v3, on-demand, West Europe [S9] | 0.658 | 12,635 | 4.77 | 9.53 |
| AWS g4dn.xlarge, spot, Ireland [S8] | 0.2604 | 12,635 | 1.93 | 3.87 |
| Azure NC4as T4 v3, spot [S9] | 0.3218 | 12,635 | 2.37 | 4.74 |
| Azure NC4as T4 v3, 1-year reserved ($3,686) [S9] | 0.4208 | 13,899 | 8.62 | 17.24 |
| Azure NC4as T4 v3, 3-year reserved ($6,566) [S9] | 0.2498 | 13,899 | 5.15 | 10.30 |

Arithmetic for the first row: 41,667 fps on average over the day, each T4 handles 14.0 × 70 % = 9.8 fps, so about 3.56 M instance-hours a month × $0.587 = $2.09 M, plus €40 k of network: €4.26 per home. Spot looks cheap, but there is no guarantee of 12,600 spare GPUs in one region at 20 h.

The hyperscaler's advantage is real: it charges for the daily curve, not for the peak. At full frames it still costs more than Altice's own servers, because the hourly price includes the margin, the datacentre and the energy.

## 7. Bandwidth: what leaves the home

| What leaves the home | GB per camera a month | Peak at 500,000 cameras | Network €/home/month |
|---|---|---|---|
| Continuous video stream, 24 h (2 Mbps, **ASSUMPTION**) | 657 | 1,000 Gbps | 1.00 |
| Full frames 960 × 540, 1 fps in motion (80 KB, **ASSUMPTION**) | 17.5 | 79 Gbps | 0.08 |
| Changed region only (40 KB, **ASSUMPTION**) | 8.8 | 40 Gbps | 0.04 |
| Crops only (heavy models at home, as in the prototype) | 1.8 | 8 Gbps | about 0 |

Streaming the cameras to the cloud is ruled out: it moves 37 times more data than frames sent during motion. The motion check at home is what makes any central option possible.

## 8. The hybrid path (recommended on 18 Nov, not chosen)

1. **The motion check always stays at home**, on the camera or the router. It is a tiny comparison of two 160 × 90 grey images, with no AI accelerator.
2. **Only the region that changed is sent**, resized to at most 640 × 640. That cuts the work per frame from 1.16 to 0.41 TFLOP and halves the upload.
3. **Work that is not urgent waits.** Updating "where is the book" can wait a few minutes. A rule such as "tell me if I leave without the book" cannot. **ASSUMPTION:** 30 % of frames are urgent and are served at the peak; the other 70 % are queued and processed at the average rate. Servers are then sized for 66,376 fps, not 124,031.
4. **Frames are batched on Altice's GPU servers** (or on reserved cloud GPUs), which stay 40 % busy on average instead of 21 %.

| Hybrid, 500,000 homes | 1 camera | 2 cameras |
|---|---|---|
| On Altice's own L4 servers (1,427 cards, €6.4 M of hardware) | **€0.49** | **€0.98** |
| On Azure T4, 3-year reserved | €1.01 | €2.02 |
| On AWS T4, on-demand | €1.53 | €3.07 |

Each half of the hybrid on its own (own L4 servers, one camera): the changed region alone gives €0.87; the queue alone gives €1.33.

## 9. Summary and break-even

The business case's add-on costs €3.99 a month (€3.24 net of 23 % VAT). Its other running costs (language model, backend, support, acquisition) are €1.51, so **vision can cost at most €1.73 per home a month** before the add-on loses money.

| Option, 500,000 homes | €/home/month, 1 camera | €/home/month, 2 cameras | €/camera/month | Left of €1.73, 1 camera |
|---|---|---|---|---|
| A1. NPU in the router (if it can run the models) | 0.36 | 0.36 | 0.36 / 0.18 | 1.37 |
| A2. Raspberry Pi 5 + AI HAT+ per home | 6.55 | 6.55 | 6.55 / 3.27 | −4.81 |
| A3. Jetson Orin Nano Super per home | 8.64 | 8.64 | 8.64 / 4.32 | −6.90 |
| B. Own L4 servers, full frames, peak | 2.41 | 4.81 | 2.41 | −0.67 |
| C. AWS L4, on-demand | 3.93 | 7.86 | 3.93 | −2.20 |
| C. AWS T4, on-demand | 4.26 | 8.52 | 4.26 | −2.53 |
| C. AWS T4, spot (no capacity guarantee) | 1.93 | 3.87 | 1.93 | −0.20 |
| C. Azure T4, 3-year reserved | 5.15 | 10.30 | 5.15 | −3.42 |
| **Hybrid on own L4 servers (recommended on 18 Nov)** | **0.49** | **0.98** | **0.49** | **1.25** |
| Hybrid on Azure T4, 3-year reserved | 1.01 | 2.02 | 1.01 | 0.72 |
| Hybrid on AWS T4, on-demand | 1.53 | 3.07 | 1.53 | 0.20 |

**Sensitivity** (own L4 servers, 1 camera; hybrid / full frames at the peak, € per home a month):

| Change | Hybrid | Full frames |
|---|---|---|
| Base | 0.49 | 2.41 |
| 2 frames per second in motion | 0.98 | 4.81 |
| 4 h of motion a day | 0.98 | 4.81 |
| GPU at 15 % of its peak | 0.79 | 3.96 |
| GPU at 35 % of its peak | 0.36 | 1.74 |
| L4 at €3,500 | 0.57 | 2.82 |

## 10. Answer to the objection

- **A box in every home is the most expensive option**: €100–140 M of hardware for 500,000 homes, and €6.55–8.64 per home a month. The objection holds.
- **Hyperscalers are cheaper than idle servers, not cheaper than busy ones.** Their advantage is paying for the daily curve. ThingTracker's work can be reshaped (motion check at home, only the changed region, a queue for what is not urgent), so Altice's own servers run busy and cost €0.49 per home a month, against €1.53 for the same hybrid on AWS on demand.
- **Hyperscalers are the right start.** At the business case's expected 19,000 homes, own servers would mean buying about 55 cards up front; on-demand cloud GPUs carry no fixed cost while the take rate is unknown. The move to own servers pays off as the base grows.
- **The best case is still hardware already in the home.** If Altice's routers or cameras have an NPU that can run a detector, the cost falls to about €0.36 per home a month (A1). That is the first question for Altice.

## 11. What must be checked

1. **Throughput.** Run OWLv2 and DINOv2 with TensorRT FP16 on a T4 or L4 and replace the 25 % assumption. This one number moves every server option.
2. **Accuracy on the changed region at 640 × 640**, against full frames at 960.
3. **Motion hours and the evening peak**, from the motion events that Altice's cameras already send.
4. **The NPU in Altice's routers and cameras**, and whether it can run a detector (A1).
5. **Altice's real prices** for GPUs, datacentre space and backbone capacity.

## Sources

All read on 18 Nov 2026. Downloaded files were read in their own folder; none contained text addressed to an AI.

- [S1] NVIDIA, T4 Tensor Core GPU: 65 TFLOPS FP16, 70 W. https://www.nvidia.com/en-us/data-center/tesla-t4/
- [S2] NVIDIA, L4 Tensor Core GPU: 242 TFLOPS FP16 with sparsity, 72 W. https://www.nvidia.com/en-us/data-center/l4/
- [S3] Raspberry Pi, Raspberry Pi 5 product brief, April 2026: 4 GB $110. https://pip-assets.raspberrypi.com/categories/892-raspberry-pi-5/documents/RP-008348-DS-6-raspberry-pi-5-product-brief.pdf (read through a search excerpt; the direct download came back empty, so re-check it). Price history: https://www.raspberrypi.com/news/more-memory-driven-price-rises/
- [S4] Raspberry Pi, AI HAT+: 13 TOPS (Hailo-8L) $70, 26 TOPS $110. https://www.raspberrypi.com/news/raspberry-pi-ai-hat/ ; the earlier AI Kit is "no longer in production": https://www.raspberrypi.com/products/ai-kit/
- [S5] NVIDIA-AI-IOT, NanoOWL README: OWL-ViT B/16 at 768, 25 fps on Jetson AGX Orin (TensorRT). https://github.com/NVIDIA-AI-IOT/nanoowl
- [S6] NVIDIA, Jetson Orin Nano Super Developer Kit: 67 INT8 TOPS, 7–25 W. https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/nano-super-developer-kit/ ; price $249: https://developer.nvidia.com/blog/nvidia-jetson-orin-nano-developer-kit-gets-a-super-boost/
- [S7] AWS, EC2 on-demand price list (the file behind the pricing page, published 17 Nov 2026): g4dn.xlarge $0.587/h in Ireland; g6.xlarge $1.0064/h in Frankfurt. https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/EU%20(Ireland)/Linux/index.json
- [S8] AWS, spot price feed of https://aws.amazon.com/ec2/spot/pricing/: g4dn.xlarge $0.2604/h in eu-west-1. https://website.spot.ec2.aws.a2z.com/spot.js
- [S9] Microsoft, Azure Retail Prices API, West Europe: NC4as T4 v3 $0.658/h, spot $0.321762/h, 1-year reservation $3,686, 3-year $6,566; data in $0.00/GB, data out $0.08/GB after 100 GB. https://prices.azure.com/api/retail/prices
- [S10] Uptime Institute, Global Data Center Survey 2025: average PUE 1.54 (from summaries of the report). https://intelligence.uptimeinstitute.com/resource/uptime-institute-global-data-center-survey-2025
- [S11] Eurostat, nrg_pc_205, electricity for non-household consumers, Portugal, 2026-S1, 2,000–19,999 MWh, excluding VAT: €0.1135/kWh (updated 19 Oct 2026). https://ec.europa.eu/eurostat/databrowser/view/nrg_pc_205/default/table
- [S12] No list price for the L4 is published. Resellers show about $2,700 to $7,390 per card (e.g. CDW, https://www.cdw.com/product/nvidia-gpu-computing-processor-l4-24-gb/8205397). Indicative only.
- [S13] ThingTracker business case: €3.99 add-on, €1.51 of other costs, household electricity €0.2367/kWh (Eurostat nrg_pc_204). [16-business-case.md](16-business-case.md)
- [S14] Google, OWLv2 base patch16 ensemble, model configuration (`image_size` 960, `patch_size` 16). https://huggingface.co/google/owlv2-base-patch16-ensemble
