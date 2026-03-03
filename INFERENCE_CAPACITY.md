# LLM Inference Capacity: Hardware Tiers Compared

**Version:** 0.0.3 · [Changelog](CHANGELOG.md)

**What is "t/s"?** Tokens per second — roughly the speed at which an AI model generates text. One token ≈ ¾ of a word. At 10 t/s, you get about 7-8 words per second — noticeably slower than reading speed. At 40+ t/s, output feels instant.

**What is a "model"?** A large language model (LLM) is the AI brain. Bigger models (more parameters) are generally smarter but need more memory and are slower to run. Think of it like RAM for a program — the model weights must fit in memory or the system grinds to a halt.

**What is "quantization"?** A compression technique that shrinks model weights to take up less memory, with a small quality trade-off. Q4 = compressed to 4 bits, roughly 4× smaller than the original. This is how you run a 70B-parameter model on consumer hardware.

---

## Hardware Tiers at a Glance

| Tier | Hardware | Speed | Best Models | Est. Cost |
|---|---|---|---|---|
| 1a | OptiPlex cluster — 3 inference nodes | ~18–36 t/s | Llama 3.1 8B, Mistral 7B | Already owned |
| 1b | OptiPlex cluster — all 20 nodes | ~120–240 t/s | Llama 3.1 8B, Mistral 7B | Already owned |
| 2 | OptiPlex + USB-C eGPU | ~100–180 t/s | Llama 3.1 8B–34B (quantized) | +$1,500–2,500 |
| 3 | Mac Mini M4 (single) | ~45–70 t/s | Llama 3.1 8B–70B (quantized) | ~$800–1,400 |
| 4 | Mac Mini M4 (multi-node) | ~90–200+ t/s | Scaled replicas of smaller models | ~$1,600–5,600 |
| 5 | Prosumer LLM Rig | ~20–50 t/s | Llama 4 Scout, Gemma 3 27B, Qwen 32B | ~$8,000–12,000 |

> **Why does the prosumer rig score lower t/s than cheaper setups on small models?** It runs much *larger* models — the 20–50 t/s is on 27B–109B parameter models, not 8B. On the same small model, the prosumer rig would be far faster. Think of it as a truck that's slower on a drag strip but can carry 10× the load.

---

## Tier 1 — OptiPlex 3080 Micro Cluster (CPU-only)

**What we have:** 20× Dell OptiPlex 3080 Micro mini-PCs, each with an Intel i5/i7 10th-gen CPU, 8GB RAM, and 256GB NVMe SSD. No graphics cards — inference runs entirely on the CPU.

**Speed: ~6–12 t/s per node | ~18–36 t/s (3 inference nodes) | ~120–240 t/s (all 20 nodes)**

The CPU in a regular PC was never designed for AI. It works — but it's like using a kitchen knife to chop firewood. You can do it, but it's slow. Each OptiPlex node can run a small compressed model (7B parameters, Q4 quantized) at conversation speed.

**What fits in memory (8GB per node):**
- Llama 3.2 3B Q4 (~2 GB) — fast, lightweight ✅
- Llama 3.1 8B Q4 (~5 GB) — fits, leaves little headroom ✅
- Anything larger — does not fit in 8GB RAM ❌

**The cluster strategy — two modes:**

*Mode A (default plan — 3 inference nodes):* We dedicate 3 nodes as inference workers, leaving the rest for general workloads (web services, databases, etc.). Each runs one independent model replica, each handling separate user requests. Combined: ~18–36 t/s.

*Mode B (all 20 nodes as inference):* If the cluster is repurposed entirely for inference — or during off-hours when general workloads are idle — all 20 nodes can each run a model replica. Combined: ~120–240 t/s for Llama 3.1 8B Q4. This is comparable to a mid-range GPU setup, just spread across 20 machines instead of one card.

**What this is good for:** Experimentation, demos, and scaling concurrent users by running many replicas in parallel. Not suitable for running a single large model — 8GB per node is a hard ceiling on model size.

---

## Tier 2 — OptiPlex + USB-C eGPU (Thunderbolt 3)

**What it is:** An external GPU enclosure connected to the OptiPlex via its Thunderbolt 3 (USB-C) port. The OptiPlex doesn't have a PCIe slot for a graphics card, but Thunderbolt 3 can carry enough bandwidth to run an external one.

**Speed: ~100–180 t/s for 7B–8B models | ~20–30 t/s for 34B models (with CPU offloading)**

A GPU (graphics processing unit) was designed to do millions of simple math operations in parallel — exactly what LLM inference needs. Even a mid-range gaming GPU like an RTX 3090 is 20–40× faster than a CPU for this task.

**The Thunderbolt bottleneck:** Connecting via USB-C/Thunderbolt 3 instead of a direct internal slot introduces a ~30–40% speed penalty compared to a native setup. Imagine a highway that narrows to two lanes — data still flows, just slower. Still dramatically faster than CPU-only.

**Practical setup (per node):**
- eGPU enclosure: Razer Core X or Sonnet Breakaway Box (~$300–500)
- GPU: NVIDIA RTX 3090 24GB VRAM (~$700–900 used) or RTX 4090 24GB (~$1,400–1,800)
- One eGPU per OptiPlex node (max one Thunderbolt 3 port)
- Requires Linux driver setup — not plug-and-play

**What fits in VRAM (24GB with RTX 3090/4090):**
- Llama 3.1 8B Q4 (~5 GB) — runs great ✅
- Llama 3.1 70B Q4 (~40 GB) — too large for 24GB VRAM alone; requires offloading part of the model to system RAM, slowing it down significantly ⚠️
- Models up to ~20B Q4 run fully in VRAM ✅

**What this is good for:** A big leap from CPU-only with minimal hardware changes. Good for medium-scale inference of 7B–20B models. One GPU node handles more requests than all 3 CPU nodes combined.

---

## Tier 3 — Mac Mini M4 (Single Node)

**What it is:** Apple's Mac Mini with the M4 chip uses a fundamentally different architecture called "unified memory" — the CPU, GPU, and Neural Engine all share the same high-bandwidth memory pool. There's no separate VRAM. This makes it uniquely efficient for LLM inference.

**Speed: ~45–70 t/s for 7B–8B models | ~15–25 t/s for 70B models (on M4 Pro with 48GB)**

**Why Apple Silicon is different:** A typical gaming PC has CPU RAM (fast but separate from GPU) and VRAM (on the graphics card). Moving data between them is a bottleneck. Apple's unified memory eliminates that bottleneck — the full memory pool is accessible at GPU speeds. A Mac Mini M4 with 24GB of unified memory is competitive with a dedicated GPU setup for inference.

**Mac Mini M4 configurations:**

| Config | Unified Memory | Memory Bandwidth | What fits | Est. Cost |
|---|---|---|---|---|
| M4 (base) | 16 GB | 120 GB/s | Up to ~13B models | ~$800 |
| M4 (upgraded) | 24 GB | 120 GB/s | Up to ~20B models | ~$1,000 |
| M4 Pro | 24–48 GB | 273 GB/s | Up to 70B models | ~$1,400 |

**What this is good for:** A self-contained inference machine that's quiet, power-efficient (~20–30W), and requires no Linux driver headaches. If you need reliable 8B–70B inference in a single machine, an M4 Pro Mac Mini punches above its weight class.

---

## Tier 4 — Mac Mini M4 (Multi-Node)

**What it is:** Running two or more Mac Minis together, either as independent replicas (each handling separate user requests) or as a distributed inference cluster (multiple machines sharing a single large model).

**Speed: ~90–140 t/s (2 nodes, 8B replicas) | scales linearly for independent replicas**

**Two ways to use multiple Mac Minis:**

**Option A — Independent replicas (easy, recommended):**
Each Mac Mini runs its own copy of the same model. A load balancer routes user requests across both. Throughput roughly doubles with each node added. Simple to set up, great for handling many concurrent users.

**Option B — Distributed inference (advanced):**
Multiple Macs share the weights of one large model across their combined memory. Allows running models too large for any single node. Requires specialized software (mlx-lm or llama.cpp with tensor split) and a fast network connection between nodes. Performance gains are smaller than Option A due to inter-node communication overhead.

**Example 2-node setup (2× Mac Mini M4 Pro, 48GB each):**
- Combined memory: 96GB
- Can run Llama 3.1 70B Q4 (~40GB) with headroom ✅
- Independent replicas at 8B: ~90–140 t/s combined
- Distributed 70B: ~25–40 t/s (slower due to networking)

**What this is good for:** Scaling inference capacity for growing teams. Each Mac Mini added = more concurrent capacity. More power-efficient per dollar than a prosumer GPU rig for smaller models.

---

## Tier 5 — Prosumer LLM Rig (~$8,000–12,000)

**What it is:** A custom-built desktop workstation designed specifically for local AI inference. Think of it as a gaming PC taken to the extreme — chosen for maximum VRAM and memory bandwidth rather than gaming frame rates.

**Speed: ~20–50 t/s on large models (Llama 4 Scout 109B, Gemma 3 27B, Qwen 32B quantized)**

This tier exists for one reason: running genuinely large models locally. The models above are 27B–109B parameters — roughly 3–10× larger than what fits on any of the tiers above. At this scale, you get AI that is substantially more capable: better reasoning, better coding, better at following complex instructions.

**Reference build (from research, 2026):**

| Component | Part | Why it matters | Est. Cost |
|---|---|---|---|
| GPU(s) | 2× NVIDIA RTX 4090 24GB | 48GB combined VRAM; fastest consumer GPU for inference | ~$3,000–4,000 |
| CPU | AMD Threadripper PRO (32+ cores) | Handles model offloading, preprocessing | ~$1,500 |
| RAM | 256GB DDR5 | Large buffer for model weights that overflow VRAM | ~$1,000 |
| Storage | 2TB NVMe SSD | Fast model loading | ~$300 |
| PSU + Case | 1600W PSU, full tower | Powers two high-end GPUs safely | ~$1,000 |
| **Total** | | | **~$8,000–12,000** |

**What is VRAM?** Video RAM — the dedicated memory inside a graphics card. It's much faster than regular RAM at the specific operations LLMs need. More VRAM = larger models without slowdowns. The two RTX 4090s give 48GB combined, enough for 27B–109B quantized models.

**Models this runs well:**
- **Llama 4 Scout** (109B total parameters, 17B active via MoE): Meta's flagship open model
- **Gemma 3 27B** (Google): Excellent reasoning, fits in a single 4090 with quantization
- **Qwen 32B** (Alibaba): Strong at coding and multilingual tasks

> **What is MoE?** "Mixture of Experts" — an architecture where a huge model (109B parameters total) only activates a small fraction (17B) at any moment. This means it has the knowledge of a 109B model but runs closer to the speed of a 17B model. Most of the frontier models use this trick.

**What this is good for:** Teams or individuals who want genuinely frontier-level open-source model quality running privately on local hardware. No API fees, no data leaving your premises, no rate limits.

---

## Side-by-Side Summary

```
Speed (t/s)     Model size supported
    │
240─┤  ── OptiPlex × 20 nodes (CPU, 8B replicas) ──────────────────
    │
200─┤                             ──── OptiPlex + eGPU (8B model) ──
180─┤
    │
140─┤                             ──── Mac Mini M4 × 2 (8B replicas)
    │
 70─┤                       ──── Mac Mini M4 (8B model) ────────────
    │
 50─┤                ──── Prosumer Rig (27B–109B model) ────────────
    │
 36─┤  ── OptiPlex × 3 nodes (CPU, 8B) ─
    │
  0─┴─────────────────────────────────────────────────────────────────
     7B      27B     70B     109B    (model size)
```

The tiers don't compete directly — they target different model sizes. A Mac Mini M4 is fast on 8B models but struggles with 70B. A prosumer rig is "slower" in t/s but running a model 10× larger and far more capable.

---

## Recommended Path

| If you want to... | Start here |
|---|---|
| Prove the concept, no extra spend | OptiPlex CPU-only (we already have it) |
| Cheap GPU acceleration without new machines | Add 1× RTX 3090 + eGPU enclosure to one OptiPlex (~$1,200) |
| Best single-node inference per dollar | Mac Mini M4 Pro 48GB (~$1,400) |
| Scale for concurrent users easily | Add more Mac Minis (linear throughput scaling) |
| Run the largest open-source models locally | Prosumer rig (~$8K–12K) |

---

*Speed estimates based on published llama.cpp and MLX community benchmarks, Intel 10th Gen specs, Apple M4 memory bandwidth specs, and NVIDIA RTX 3090/4090 inference benchmarks. Actual throughput varies by model, quantization level, software version, and system configuration. Confirm CPU model on the OptiPlex nodes via `dmidecode -t processor` — estimates above use i5-10500T as baseline.*

*Source research: Perplexity AI hardware requirements report (March 2026).*
