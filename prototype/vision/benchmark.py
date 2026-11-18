"""Time the three local models on this machine (no cloud, no cost).

    prototype/.venv-vision/bin/python prototype/vision/benchmark.py IMAGE.jpg
"""
import sys
import time

import torch
from PIL import Image
from transformers import (AutoImageProcessor, AutoModel, AutoModelForDepthEstimation,
                          Owlv2ForObjectDetection, Owlv2Processor)

dev = "mps" if torch.backends.mps.is_available() else "cpu"
img = Image.open(sys.argv[1]).convert("RGB")
print("device:", dev, "| image:", img.size)


def timed(fn, n=5):
    fn()  # warm-up
    if dev == "mps":
        torch.mps.synchronize()
    t = time.perf_counter()
    for _ in range(n):
        out = fn()
        if dev == "mps":
            torch.mps.synchronize()
    return out, (time.perf_counter() - t) / n * 1000


# 1. Open-vocabulary detection: find things by name
proc = Owlv2Processor.from_pretrained("google/owlv2-base-patch16-ensemble")
owl = Owlv2ForObjectDetection.from_pretrained("google/owlv2-base-patch16-ensemble").to(dev).eval()
queries = [["a key", "a wallet", "glasses", "a phone", "a mug", "a laptop", "a tv remote", "a light bulb", "a smart plug", "a person"]]
inputs = proc(text=queries, images=img, return_tensors="pt").to(dev)
with torch.no_grad():
    out, ms = timed(lambda: owl(**inputs))
res = proc.post_process_grounded_object_detection(outputs=out, threshold=0.2, target_sizes=torch.tensor([img.size[::-1]]).to(dev))[0]
found = [(queries[0][l], round(s.item(), 2), [round(v) for v in b.tolist()]) for s, l, b in zip(res["scores"], res["labels"], res["boxes"])]
print(f"OWLv2 base (detect by name, 10 queries): {ms:.0f} ms/frame | found: {found}")

# 2. Fingerprint: image embedding to recognise *your* object
dp = AutoImageProcessor.from_pretrained("facebook/dinov2-small")
dino = AutoModel.from_pretrained("facebook/dinov2-small").to(dev).eval()
crop = img.crop((0, 0, img.width // 2, img.height))
di = dp(images=crop, return_tensors="pt").to(dev)
with torch.no_grad():
    _, ms = timed(lambda: dino(**di).pooler_output, n=10)
print(f"DINOv2 small (fingerprint of one crop): {ms:.0f} ms")

# 3. Monocular depth: near/far without lidar
zp = AutoImageProcessor.from_pretrained("depth-anything/Depth-Anything-V2-Small-hf")
depth = AutoModelForDepthEstimation.from_pretrained("depth-anything/Depth-Anything-V2-Small-hf").to(dev).eval()
zi = zp(images=img, return_tensors="pt").to(dev)
with torch.no_grad():
    _, ms = timed(lambda: depth(**zi).predicted_depth)
print(f"Depth Anything V2 Small (depth map): {ms:.0f} ms/frame")
