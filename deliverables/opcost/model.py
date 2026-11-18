"""Operator-side cost of ThingTracker's vision models at 500 000 homes.

Prints every table used in docs/17-operator-costs.md and docs/pt/17-custos-operador.md, so the numbers can be
reproduced:  python3 deliverables/opcost/model.py

Conventions (same as the business case, docs/16-business-case.md):
- 1 USD = 1 EUR (business-case convention; it slightly overstates USD prices in euros).
- Prices net of VAT. Hardware for the home amortised over 36 months.
- [Sn] = source number in the documents; "ASSUMPTION" = our estimate, with the reasoning next to it.
"""

# ---------------------------------------------------------------- inputs: the service
HOMES = 500_000
MOTION_H_PER_DAY = 2.0         # ASSUMPTION carried from the business case: 2 h of motion per camera per day
FPS_IN_MOTION = 1.0            # frames analysed per second while the scene changes (prototype: 1 to 2)
DAYS = 30.4
HOURS_MONTH = 730.0

# ASSUMPTION: share of a camera's daily motion that falls in each hour (0h..23h): low at night, peaks at 7-8 h
# and 19-21 h. Only the shape matters; it is normalised below. No published profile for Portuguese homes was found.
HOURLY_WEIGHT = [1, .5, .3, .3, .3, .5, 2, 5, 5, 3, 2.5, 2.5, 3.5, 3.5, 2.5, 2.5, 3, 4, 6, 7.5, 8, 7, 4.5, 2.5]
BURST = 1.2                    # ASSUMPTION: busiest 15 minutes vs the busiest hour's average

# ---------------------------------------------------------------- inputs: the models
# Compute per analysed frame, from the architecture (our arithmetic, see flops_vit):
#   OWLv2 base patch16 at 960 x 960 -> 60 x 60 = 3600 patches + 1 token, 12 layers, width 768, MLP 3072.
#   DINOv2 small patch14 on a 224 x 224 crop -> 256 patches + 1 token, 12 layers, width 384.
def flops_vit(tokens, width, layers=12):
    """Forward FLOPs of a ViT encoder: per layer 12*N*D^2 MACs (QKV, projection, MLP 4x) + 2*N^2*D MACs (attention)."""
    macs = layers * (12 * tokens * width ** 2 + 2 * tokens ** 2 * width)
    return 2 * macs

OWL_960 = flops_vit(3601, 768)
OWL_640 = flops_vit(1601, 768)   # hybrid: only the changed region, resized to 640 x 640 (ASSUMPTION: accuracy to be validated)
DINO = flops_vit(257, 384)
CROPS_PER_FRAME = 3              # ASSUMPTION: candidates fingerprinted per frame
HEADS = 1.03                     # ASSUMPTION: +3 % for OWLv2's box and class heads
FRAME_FULL = OWL_960 * HEADS + CROPS_PER_FRAME * DINO
FRAME_ROI = OWL_640 * HEADS + CROPS_PER_FRAME * DINO

MAC_S_PER_FRAME = 0.57 + CROPS_PER_FRAME * 0.022   # measured on the team's MacBook (Apple M1 Pro, MPS), docs/14 sec. 3

# Accelerators: peak dense FP16 tensor throughput from the vendor spec, times an ASSUMED utilisation.
UTIL = 0.25   # ASSUMPTION: 25 % of dense FP16 peak with TensorRT FP16 on a ViT; cross-check with NanoOWL below
ACCEL = {   # name: (dense FP16 TFLOPS, source note)
    "T4": (65.0, "S1: 65 TFLOPS FP16"),
    "L4": (121.0, "S2: 242 TFLOPS FP16 with sparsity, halved"),
    "Jetson Orin Nano Super": (67 / 4, "S6: 67 INT8 TOPS (sparse); /2 dense, /2 FP16 (ASSUMPTION)"),
}
NANOOWL_AGX_FPS_B16_768 = 25.0   # S5: NanoOWL, OWL-ViT B/16 at 768, Jetson AGX Orin, TensorRT

SERVER_TARGET_LOAD = 0.70        # ASSUMPTION: run accelerators at most 70 % busy at the peak, for latency
SPARE = 1.10                     # ASSUMPTION: +10 % spare accelerators (failures, maintenance)

# ---------------------------------------------------------------- inputs: prices (USD = EUR)
CLOUD = {   # name: (accelerator, $/hour, source)
    "AWS g4dn.xlarge on-demand, Ireland": ("T4", 0.587, "S7"),
    "AWS g4dn.xlarge spot, Ireland": ("T4", 0.2604, "S8"),
    "AWS g6.xlarge on-demand, Frankfurt": ("L4", 1.0064, "S7"),
    "Azure NC4as T4 v3 on-demand, West Europe": ("T4", 0.658, "S9"),
    "Azure NC4as T4 v3 spot, West Europe": ("T4", 0.321762, "S9"),
    "Azure NC4as T4 v3 1-year reserved": ("T4", 3686.0 / 8760, "S9"),
    "Azure NC4as T4 v3 3-year reserved": ("T4", 6566.0 / (3 * 8760), "S9"),
}
AUTOSCALE_OVERHEAD = 1.15   # ASSUMPTION: autoscaling lags the load and rounds up to whole instances

# Option B, Altice's own servers in Portugal
L4_PRICE = 2500.0           # ASSUMPTION: NVIDIA publishes no list price; resellers show $2,700 to $7,400 per card (S12)
HOST_PER_4_GPU = 8000.0     # ASSUMPTION: 2U server, CPUs, memory, network, for 4 L4 cards, without the cards
HOST_W = 250.0              # ASSUMPTION: host power without the cards
GPU_IDLE_W, GPU_MAX_W = 20.0, 72.0   # max from S2; idle ASSUMPTION
PUE = 1.54                  # S10: Uptime Institute 2025 global average (newer, large sites are lower)
DC_EUR_KWH = 0.1135         # S11: Eurostat nrg_pc_205, Portugal, 2026-S1, band ID, excl. VAT
COLO_EUR_KW_MONTH = 150.0   # ASSUMPTION: rack space and cooling per kW of IT capacity, energy excluded
OPS_SHARE_YEAR = 0.08       # ASSUMPTION: maintenance, spares and staff, 8 % of hardware cost a year
SERVER_MONTHS = 48          # ASSUMPTION: server depreciation, 4 years

# Network (both B and C): Altice carries the frames from the home to a datacentre
NET_EUR_MBPS_MONTH = 0.50   # ASSUMPTION: cost of backbone or transit capacity per Mbps of peak, per month
KB_FRAME_960 = 80.0         # ASSUMPTION: JPEG of a 960 x 540 frame (about 1.2 bit per pixel)
KB_FRAME_ROI = 40.0         # ASSUMPTION: JPEG of the changed region, at most 640 x 640
STREAM_MBPS = 2.0           # ASSUMPTION: the camera's H.265 main stream, 2304 x 1296 at 20 fps
CLOUD_INGRESS = 0.0         # S9: Azure "Standard Data Transfer In" = $0.00 per GB
CLOUD_EGRESS_GB = 0.08      # S9: Azure West Europe, after the first 100 GB; only small results go out

# Option A, a device at home
HOME_DEVICES = {   # name: (price, idle W, active W, analyses OWLv2 at 960?, note)
    "A1 NPU in a new router (premium)": (15.0, 0.5, 2.0, False, "ASSUMPTION: premium per router; no public price"),
    "A2 Raspberry Pi 5 4GB + AI HAT+ 13 TOPS": (110 + 70 + 20, 3.0, 8.0, False, "S3 $110, S4 $70, +$20 case and power (ASSUMPTION)"),
    "A3 Jetson Orin Nano Super kit": (249 + 20, 5.0, 20.0, True, "S6 $249, +$20 storage (ASSUMPTION)"),
}
HOME_MONTHS = 36            # business case
HOME_LOGISTICS = 15.0       # ASSUMPTION: shipping and handling per device
AFR = 0.03                  # ASSUMPTION: 3 % of devices fail per year
REPLACE_EXTRA = 30.0        # ASSUMPTION: logistics of a replacement
HOUSE_EUR_KWH = 0.2367      # business case: Eurostat nrg_pc_204, Portugal, 2026-S1 (paid by the customer)
ROUTER_MONTHS = 60          # ASSUMPTION: router life

# Price and other costs, business case
PRICE_NET = 3.99 / 1.23     # EUR 3.99 add-on, 23 % VAT -> 3.24
OTHER_COSTS = 1.51          # business case C05: cloud AI 0.43, backend 0.10, support 0.42, acquisition 0.56

# ---------------------------------------------------------------- helpers
def eur(x, d=2):
    return f"{x:,.{d}f}"

def table(title, head, rows):
    print(f"\n## {title}\n")
    print("| " + " | ".join(head) + " |")
    print("|" + "|".join("---" for _ in head) + "|")
    for r in rows:
        print("| " + " | ".join(str(c) for c in r) + " |")

# ---------------------------------------------------------------- 1. load: duty cycle and peak
w = [x / sum(HOURLY_WEIGHT) for x in HOURLY_WEIGHT]
duty = MOTION_H_PER_DAY / 24
peak_hour_share = MOTION_H_PER_DAY * max(w)          # share of cameras in motion in the busiest hour
peak_share = peak_hour_share * BURST                  # busiest 15 minutes
peak_factor = peak_share / duty

table("1. Load per camera", ["Quantity", "Arithmetic", "Value"], [
    ["Duty cycle", f"{MOTION_H_PER_DAY} h / 24 h", f"{duty:.2%}"],
    ["Busiest hour", f"{MOTION_H_PER_DAY} h x {max(w):.4f} (share of daily motion at {w.index(max(w))} h)", f"{peak_hour_share:.2%}"],
    ["Busiest 15 minutes", f"{peak_hour_share:.2%} x {BURST}", f"{peak_share:.2%}"],
    ["Peak factor", f"{peak_share:.2%} / {duty:.2%}", f"{peak_factor:.2f}"],
    ["Frames analysed per camera a month", f"{MOTION_H_PER_DAY} h x 3600 s x {FPS_IN_MOTION} fps x {DAYS} days", eur(MOTION_H_PER_DAY * 3600 * FPS_IN_MOTION * DAYS, 0)],
])

# ---------------------------------------------------------------- 2. compute per frame and per accelerator
mac_eff = FRAME_FULL / MAC_S_PER_FRAME / 1e12
fps_acc = {}
rows = []
for name, (tf, note) in ACCEL.items():
    eff = tf * UTIL
    fps_acc[name] = (eff * 1e12 / FRAME_FULL, eff * 1e12 / FRAME_ROI)
    rows.append([name, f"{tf:.1f} ({note})", f"{tf:.1f} x {UTIL:.0%} = {eff:.1f}",
                 f"{fps_acc[name][0]:.1f}", f"{fps_acc[name][1]:.1f}"])
rows.append(["MacBook M1 Pro (measured)", "-", f"{mac_eff:.2f} (implied by {MAC_S_PER_FRAME:.3f} s per frame)",
             f"{1 / MAC_S_PER_FRAME:.2f}", "-"])
nano_eff = NANOOWL_AGX_FPS_B16_768 * flops_vit(2305, 768) / 1e12
print(f"\nOWLv2 B/16 at 960: {OWL_960 / 1e12:.3f} TFLOP; at 640: {OWL_640 / 1e12:.3f} TFLOP; DINOv2-S crop: {DINO / 1e9:.1f} GFLOP")
print(f"Frame, full 960: {FRAME_FULL / 1e12:.3f} TFLOP; frame, changed region 640: {FRAME_ROI / 1e12:.3f} TFLOP")
print(f"Cross-check: NanoOWL B/16 at 768 on AGX Orin = {NANOOWL_AGX_FPS_B16_768} fps x {flops_vit(2305, 768) / 1e12:.3f} TFLOP = {nano_eff:.1f} effective TFLOPS")
table("2. Throughput per accelerator (frames per second, OWLv2 + 3 DINOv2 crops)",
      ["Accelerator", "Dense FP16 TFLOPS", "Effective TFLOPS (ASSUMPTION)", "Full frame 960", "Changed region 640"], rows)

# ---------------------------------------------------------------- 3. per scenario
def scenario(cams_per_home, roi=False, smoothing=False):
    cams = HOMES * cams_per_home
    avg_fps = cams * duty * FPS_IN_MOTION
    peak_fps = cams * peak_share * FPS_IN_MOTION
    # hybrid: 30 % of the work is urgent (a rule is waiting on it); the rest can wait in a queue and run off-peak
    size_fps = (0.3 * peak_fps + 0.7 * avg_fps) if smoothing else peak_fps
    return cams, avg_fps, peak_fps, size_fps, (1 if roi else 0)

def option_b(cams_per_home, roi=False, smoothing=False):
    cams, avg_fps, peak_fps, size_fps, k = scenario(cams_per_home, roi, smoothing)
    per_gpu = fps_acc["L4"][k]
    gpus = size_fps / (per_gpu * SERVER_TARGET_LOAD) * SPARE
    hosts = gpus / 4
    capex = gpus * L4_PRICE + hosts * HOST_PER_4_GPU
    dep = capex / SERVER_MONTHS
    load = avg_fps / (gpus * per_gpu)
    it_kw_avg = (gpus * (GPU_IDLE_W + (GPU_MAX_W - GPU_IDLE_W) * load) + hosts * HOST_W) / 1000
    it_kw_max = (gpus * GPU_MAX_W + hosts * HOST_W) / 1000
    energy = it_kw_avg * PUE * HOURS_MONTH * DC_EUR_KWH
    colo = it_kw_max * COLO_EUR_KW_MONTH
    ops = capex * OPS_SHARE_YEAR / 12
    kb = KB_FRAME_ROI if roi else KB_FRAME_960
    net = peak_fps * kb * 8 / 1000 * NET_EUR_MBPS_MONTH
    total = dep + energy + colo + ops + net
    return dict(cams=cams, avg=avg_fps, peak=peak_fps, size=size_fps, per_gpu=per_gpu, gpus=gpus, hosts=hosts,
                capex=capex, dep=dep, load=load, kw=it_kw_avg, kwmax=it_kw_max, energy=energy, colo=colo, ops=ops,
                net=net, total=total, home=total / HOMES, cam=total / cams)

def option_c(cams_per_home, offer, roi=False, smoothing=False):
    cams, avg_fps, peak_fps, size_fps, k = scenario(cams_per_home, roi, smoothing)
    acc, usd_h, _ = CLOUD[offer]
    per_gpu = fps_acc[acc][k] * SERVER_TARGET_LOAD
    if "reserved" in offer:   # held 24 h a day, sized for the peak (or the smoothed peak)
        inst = size_fps / per_gpu * SPARE
        hours = inst * HOURS_MONTH
    else:                     # follows the load hour by hour
        hourly = [cams * MOTION_H_PER_DAY * x * FPS_IN_MOTION for x in w]
        if smoothing:
            hourly = [0.3 * h + 0.7 * avg_fps for h in hourly]
        hours = sum(h / per_gpu for h in hourly) * DAYS * AUTOSCALE_OVERHEAD
        inst = max(hourly) * BURST / per_gpu
    compute = hours * usd_h
    kb = KB_FRAME_ROI if roi else KB_FRAME_960
    net = peak_fps * kb * 8 / 1000 * NET_EUR_MBPS_MONTH + avg_fps * kb * 3600 * HOURS_MONTH / 1e6 * CLOUD_INGRESS
    egress = max(0.0, HOMES * 0.01 - 100) * CLOUD_EGRESS_GB   # ASSUMPTION: 10 MB of results per home a month
    total = compute + net + egress
    return dict(inst=inst, hours=hours, compute=compute, net=net, egress=egress, total=total,
                home=total / HOMES, cam=total / cams)

def option_a(cams_per_home, name):
    price, idle_w, act_w, owl, _ = HOME_DEVICES[name]
    months = ROUTER_MONTHS if name.startswith("A1") else HOME_MONTHS
    logistics = 0.0 if name.startswith("A1") else HOME_LOGISTICS   # the router ships anyway
    dep = (price + logistics) / months
    fail = AFR * (price + REPLACE_EXTRA) / 12
    act_h = min(24.0, MOTION_H_PER_DAY * cams_per_home)
    kwh = ((24 - act_h) * idle_w + act_h * act_w) * DAYS / 1000
    elec = kwh * HOUSE_EUR_KWH
    home = dep + fail
    return dict(price=price, dep=dep, fail=fail, home=home, cam=home / cams_per_home, kwh=kwh, elec=elec,
                capex=(price + logistics) * HOMES, owl=owl)

# ---------------------------------------------------------------- 4. print the options
for cph in (1, 2):
    rows = []
    for name in HOME_DEVICES:
        a = option_a(cph, name)
        rows.append([name, eur(a["price"], 0), f"({eur(a['price'], 0)} + logistics) / months = {a['dep']:.2f}",
                     f"{AFR:.0%} x ({eur(a['price'], 0)} + {REPLACE_EXTRA:.0f}) / 12 = {a['fail']:.2f}",
                     f"{a['home']:.2f}", f"{a['cam']:.2f}", f"{a['kwh']:.2f} kWh = {a['elec']:.2f}",
                     f"{a['capex'] / 1e6:.1f}", "yes" if a["owl"] else "no: lighter detector needed"])
    table(f"3.{cph} Option A, a device at home ({cph} camera(s) per home)",
          ["Device", "Price", "Amortisation EUR/month", "Failures EUR/month", "Operator EUR/home/month",
           "EUR/camera/month", "Customer electricity", "CapEx at 500 k, EUR M", "Runs OWLv2 at 960?"], rows)

for cph in (1, 2):
    b = option_b(cph)
    table(f"4.{cph} Option B, Altice's own L4 servers, full frames at 960, sized for the peak ({cph} camera(s) per home)",
          ["Step", "Arithmetic", "Value"], [
        ["Cameras", f"{HOMES:,} x {cph}", f"{b['cams']:,.0f}"],
        ["Average load", f"{b['cams']:,.0f} x {duty:.2%} x {FPS_IN_MOTION} fps", f"{b['avg']:,.0f} fps"],
        ["Peak load", f"{b['cams']:,.0f} x {peak_share:.2%} x {FPS_IN_MOTION} fps", f"{b['peak']:,.0f} fps"],
        ["L4 cards", f"{b['peak']:,.0f} / ({b['per_gpu']:.1f} x {SERVER_TARGET_LOAD:.0%}) x {SPARE}", f"{b['gpus']:,.0f}"],
        ["Hardware", f"{b['gpus']:,.0f} x {L4_PRICE:,.0f} + {b['hosts']:,.0f} hosts x {HOST_PER_4_GPU:,.0f}", f"EUR {b['capex'] / 1e6:.1f} M"],
        ["Depreciation", f"/ {SERVER_MONTHS} months", f"EUR {b['dep'] / 1e3:,.0f} k/month"],
        ["Energy", f"{b['kw']:,.0f} kW average x PUE {PUE} x {HOURS_MONTH:.0f} h x {DC_EUR_KWH}", f"EUR {b['energy'] / 1e3:,.0f} k/month"],
        ["Datacentre", f"{b['kwmax']:,.0f} kW x {COLO_EUR_KW_MONTH:.0f}", f"EUR {b['colo'] / 1e3:,.0f} k/month"],
        ["Operations", f"{OPS_SHARE_YEAR:.0%} x hardware / 12", f"EUR {b['ops'] / 1e3:,.0f} k/month"],
        ["Network", f"{b['peak']:,.0f} fps x {KB_FRAME_960:.0f} KB x 8 = {b['peak'] * KB_FRAME_960 * 8 / 1e6:,.1f} Gbps x {NET_EUR_MBPS_MONTH}/Mbps", f"EUR {b['net'] / 1e3:,.0f} k/month"],
        ["Total", "", f"EUR {b['total'] / 1e3:,.0f} k/month"],
        ["Per home / per camera", f"/ {HOMES:,} / {b['cams']:,.0f}", f"EUR {b['home']:.2f} / {b['cam']:.2f}"],
        ["Average use of the cards", f"{b['avg']:,.0f} / ({b['gpus']:,.0f} x {b['per_gpu']:.1f})", f"{b['load']:.0%}"],
    ])

for cph in (1, 2):
    rows = []
    for offer in CLOUD:
        c = option_c(cph, offer)
        rows.append([offer, f"{CLOUD[offer][1]:.4f}", f"{c['inst']:,.0f}", f"{c['hours'] / 1e6:.2f}",
                     f"{c['compute'] / 1e3:,.0f}", f"{c['net'] / 1e3:,.0f}", f"{c['home']:.2f}", f"{c['cam']:.2f}"])
    table(f"5.{cph} Option C, hyperscaler GPUs, full frames at 960 ({cph} camera(s) per home)",
          ["Offer", "USD/hour", "Instances at the peak", "Instance-hours a month (M)", "Compute k/month",
           "Network k/month", "EUR/home/month", "EUR/camera/month"], rows)

# ---------------------------------------------------------------- 5. bandwidth
cam_month_frames = MOTION_H_PER_DAY * 3600 * FPS_IN_MOTION * DAYS
table("6. Upstream data per camera and peak bandwidth at 500 000 cameras", ["What leaves the home", "GB per camera a month", "Peak Gbps, 500 k cameras", "Network EUR/home/month"], [
    ["Continuous stream, 24 h", f"{STREAM_MBPS * 1e6 / 8 * 86400 * DAYS / 1e9:,.0f}", f"{HOMES * STREAM_MBPS / 1000:,.0f}", f"{STREAM_MBPS * NET_EUR_MBPS_MONTH:.2f}"],
    ["Full frames 960 x 540, 1 fps in motion", f"{cam_month_frames * KB_FRAME_960 / 1e6:.1f}", f"{HOMES * peak_share * KB_FRAME_960 * 8 / 1e6:,.0f}", f"{peak_share * KB_FRAME_960 * 8 / 1000 * NET_EUR_MBPS_MONTH:.2f}"],
    ["Changed region only, 1 fps in motion", f"{cam_month_frames * KB_FRAME_ROI / 1e6:.1f}", f"{HOMES * peak_share * KB_FRAME_ROI * 8 / 1e6:,.0f}", f"{peak_share * KB_FRAME_ROI * 8 / 1000 * NET_EUR_MBPS_MONTH:.2f}"],
    ["Crops only (heavy models at home)", f"{cam_month_frames * 8 / 1e6:.1f}", f"{HOMES * peak_share * 8 * 8 / 1e6:,.0f}", "about 0"],
])

# ---------------------------------------------------------------- 6. hybrid and summary
summary = []
for cph in (1, 2):
    a2, a3, a1 = option_a(cph, list(HOME_DEVICES)[1]), option_a(cph, list(HOME_DEVICES)[2]), option_a(cph, list(HOME_DEVICES)[0])
    b = option_b(cph)
    bh = option_b(cph, roi=True, smoothing=True)
    cod = option_c(cph, "AWS g4dn.xlarge on-demand, Ireland")
    cl4 = option_c(cph, "AWS g6.xlarge on-demand, Frankfurt")
    cres = option_c(cph, "Azure NC4as T4 v3 3-year reserved")
    cspot = option_c(cph, "AWS g4dn.xlarge spot, Ireland")
    ch = option_c(cph, "Azure NC4as T4 v3 3-year reserved", roi=True, smoothing=True)
    chod = option_c(cph, "AWS g4dn.xlarge on-demand, Ireland", roi=True, smoothing=True)
    summary.append((cph, [
        ("A1 NPU in the router (if it can run the models)", a1),
        ("A2 Pi 5 + AI HAT+ per home", a2),
        ("A3 Jetson Orin Nano Super per home", a3),
        ("B Own L4 servers, full frames, peak", b),
        ("C AWS T4 on-demand, autoscaled", cod),
        ("C AWS L4 on-demand, autoscaled", cl4),
        ("C AWS T4 spot (no capacity guarantee)", cspot),
        ("C Azure T4 3-year reserved, peak", cres),
        ("Hybrid on own L4 servers", bh),
        ("Hybrid on Azure T4 3-year reserved", ch),
        ("Hybrid on AWS T4 on-demand", chod),
    ]))
    if cph == 1:
        hyb = bh
print(f"\nHybrid, own L4 servers, 1 camera: {hyb['gpus']:,.0f} cards, hardware EUR {hyb['capex'] / 1e6:.1f} M, "
      f"sized for {hyb['size']:,.0f} fps, average use {hyb['load']:.0%}")

margin_room = PRICE_NET - OTHER_COSTS
rows = []
for cph, items in summary:
    for label, d in items:
        rows.append([f"{cph}", label, f"{d['home']:.2f}", f"{d['cam']:.2f}", f"{margin_room - d['home']:.2f}"])
table(f"7. Summary: operator cost of vision at {HOMES:,} homes, and what is left of the EUR 3.99 add-on "
      f"({PRICE_NET:.2f} net - {OTHER_COSTS} other costs = {margin_room:.2f} before vision)",
      ["Cameras per home", "Option", "EUR/home/month", "EUR/camera/month", "Left per home, EUR/month"], rows)

# ---------------------------------------------------------------- 7. sensitivity of the hybrid (1 camera, own L4)
rows = []
for label, kw in [("Base", {}), ("2 fps in motion", {"FPS_IN_MOTION": 2.0}), ("Utilisation 15 %", {"UTIL": 0.15}),
                  ("Utilisation 35 %", {"UTIL": 0.35}), ("L4 at EUR 3,500", {"L4_PRICE": 3500.0}),
                  ("4 h of motion a day", {"MOTION_H_PER_DAY": 4.0})]:
    saved = {k: globals()[k] for k in kw}
    globals().update(kw)
    duty = MOTION_H_PER_DAY / 24
    peak_share = MOTION_H_PER_DAY * max(w) * BURST
    for name, (tf, _) in ACCEL.items():
        fps_acc[name] = (tf * UTIL * 1e12 / FRAME_FULL, tf * UTIL * 1e12 / FRAME_ROI)
    r = option_b(1, roi=True, smoothing=True)
    rows.append([label, f"{r['home']:.2f}", f"{option_b(1)['home']:.2f}"])
    globals().update(saved)
    duty = MOTION_H_PER_DAY / 24
    peak_share = MOTION_H_PER_DAY * max(w) * BURST
    for name, (tf, _) in ACCEL.items():
        fps_acc[name] = (tf * UTIL * 1e12 / FRAME_FULL, tf * UTIL * 1e12 / FRAME_ROI)
rows.append(["Hybrid, changed region only (no queue)", f"{option_b(1, roi=True)['home']:.2f}", "-"])
rows.append(["Hybrid, queue only (full frames)", f"{option_b(1, smoothing=True)['home']:.2f}", "-"])
table("8. Sensitivity, 1 camera per home, own L4 servers", ["Change", "Hybrid EUR/home/month", "Full frames, peak EUR/home/month"], rows)
