# LLM Inference Capacity: Hardware Tiers Compared

**What is "t/s"?** Tokens per second — roughly the speed at which an AI model generates text. One token ≈ ¾ of a word. At 10 t/s, you get about 7-8 words per second — noticeably slower than reading speed. At 40+ t/s, output feels instant.

**What is a "model"?** A large language model (LLM) is the AI brain. Bigger models (more parameters) are generally smarter but need more memory and are slower to run. Think of it like RAM for a program — the model weights must fit in memory or the system grinds to a halt.

**What is "quantization"?** A compression technique that shrinks model weights to take up less memory, with a small quality trade-off. Q4 = compressed to 4 bits, roughly 4× smaller than the original. This is how you run a 70B-parameter model on consumer hardware.

---

## Hardware Tiers at a Glance

| Tier | Hardware | Speed | Best Models | Est. Cost |
|---|---|---|---|---|
| 1a | OptiPlex cluster — 3 inference nodes | ~9–18 t/s | Llama 3.1 8B, Mistral 7B | Already owned |
| 1b | OptiPlex cluster — scaled to 20 nodes | ~60–120 t/s | Llama 3.1 8B, Mistral 7B | Additional nodes needed |
| 2 | OptiPlex + USB-C eGPU | ~80–105 t/s | Llama 3.1 8B–27B (quantized) | +$1,500–2,500 |
| 3 | Mac Mini M4 (single) | ~18–50 t/s | Llama 3.1 8B–70B (quantized) | ~$800–1,400 |
| 4 | Mac Mini M4 (multi-node) | ~80–100+ t/s | Scaled replicas of smaller models | ~$1,600–5,600 |
| 5 | Prosumer LLM Rig | ~35–55 t/s | Llama 4 Scout, Gemma 3 27B, Qwen 32B | ~$8,000–12,000 |

> **Why does the prosumer rig score lower t/s than cheaper setups on small models?** It runs much *larger* models — the 20–50 t/s is on 27B–109B parameter models, not 8B. On the same small model, the prosumer rig would be far faster. Think of it as a truck that's slower on a drag strip but can carry 10× the load.

---

## Tier 1 — OptiPlex 3080 Micro Cluster (CPU-only)

**What we have:** Currently 3 Dell OptiPlex 3080 Micro mini-PCs (designed to scale to 20 nodes), each with an Intel i5/i7 10th-gen CPU, 8GB RAM, and 256GB NVMe SSD. No graphics cards — inference runs entirely on the CPU. The cluster runs Talos Linux with Kubernetes.

**Speed: ~3–6 t/s per node (8B) | ~9–18 t/s (3 inference nodes) | ~60–120 t/s (all 20 nodes)**

The CPU in a regular PC was never designed for AI. It works — but it's like using a kitchen knife to chop firewood. You can do it, but it's slow. With only 8GB DDR4 per node (~20–25 GB/s memory bandwidth), inference is memory-bandwidth-bound and RAM-constrained.

**What fits in memory (8GB per node):**
- Llama 3.2 3B Q4 (~2 GB) — fits comfortably, **7–12 t/s** per node ✅
- Llama 3.1 8B Q4 (~4.6 GB) — fits tightly, **3–6 t/s** per node (little headroom for OS + Kubernetes) ⚠️
- Mistral 7B Q4 (~4.5 GB) — similar to 8B, **4–6 t/s** per node ⚠️
- Anything larger — does not fit in 8GB RAM ❌

**The cluster strategy — two modes:**

*Mode A (default plan — 3 inference nodes):* We dedicate 3 nodes as inference workers, leaving the rest for general workloads (web services, databases, etc.). Each runs one independent model replica, each handling separate user requests. Combined: ~9–18 t/s for 8B Q4, or ~21–36 t/s for 3B Q4.

*Mode B (scaled to 20 nodes):* If the cluster is expanded to all 20 nodes and repurposed entirely for inference — or during off-hours when general workloads are idle — all 20 nodes can each run a model replica. Combined: ~60–120 t/s for Llama 3.1 8B Q4, or ~140–240 t/s for 3B Q4. The 3B model is the sweet spot for these nodes — it fits comfortably and runs at conversational speed.

**What this is good for:** Experimentation, demos, and scaling concurrent users by running many replicas in parallel. Not suitable for running a single large model — 8GB per node is a hard ceiling on model size. A RAM upgrade to 16GB per node would significantly improve 8B model performance.

---

## Tier 2 — OptiPlex + USB-C eGPU (Thunderbolt 3)

**What it is:** An external GPU enclosure connected to the OptiPlex via its Thunderbolt 3 (USB-C) port. The OptiPlex doesn't have a PCIe slot for a graphics card, but Thunderbolt 3 can carry enough bandwidth to run an external one.

**Speed: ~80–105 t/s for 7B–8B models Q4 | ~40–50 t/s for Gemma 3 27B Q4**

A GPU (graphics processing unit) was designed to do millions of simple math operations in parallel — exactly what LLM inference needs. An RTX 3090 has ~936 GB/s of memory bandwidth vs the i5-10500T's ~20–25 GB/s — roughly 40× faster at feeding data to the processor.

**The Thunderbolt penalty is smaller than you'd think:** The common claim is 30–40% slower, but that's a *gaming* number driven by constant CPU-to-GPU data exchange every frame. LLM inference is different — once the model is loaded into VRAM, token generation happens entirely inside the GPU. The Thunderbolt link is barely involved. Community benchmarks show only a **~5–15% penalty** for LLM generation when the model fits in VRAM. Model loading is slower, and prompt processing takes a ~10–20% hit, but the generation speed you feel during conversation is nearly native.

**Practical setup (per node):**
- eGPU enclosure: Razer Core X or Sonnet Breakaway Box (~$300–500)
- GPU: NVIDIA RTX 3090 24GB VRAM (~$700–900 used) or RTX 4090 24GB (~$1,400–1,800)
- One eGPU per OptiPlex node (max one Thunderbolt 3 port)
- Requires Linux driver setup — not plug-and-play

**What fits in VRAM (24GB with RTX 3090/4090):**
- Llama 3.1 8B Q4 (~4.6 GB) — runs great, ~80–105 t/s ✅
- Gemma 3 27B Q4 (~16 GB) — fits, ~40–50 t/s on RTX 4090 ✅
- Llama 3.1 70B Q4 (~40 GB) — too large for 24GB VRAM alone; requires offloading to system RAM, drops to ~2–5 t/s ❌
- Models up to ~27B Q4 run fully in VRAM ✅

**What this is good for:** A big leap from CPU-only with minimal hardware changes. Good for medium-scale inference of 7B–27B models. One eGPU node delivers more throughput on 8B than all 3 current OptiPlex CPUs combined (and would still outperform all 20 at full scale).

---

## Tier 3 — Mac Mini M4 (Single Node)

**What it is:** Apple's Mac Mini with the M4 chip uses a fundamentally different architecture called "unified memory" — the CPU, GPU, and Neural Engine all share the same high-bandwidth memory pool. There's no separate VRAM. This makes it uniquely efficient for LLM inference.

**Speed: ~18–30 t/s for 8B on base M4 | ~40–50 t/s for 8B on M4 Pro | ~4–5 t/s for 70B on M4 Pro**

**Why Apple Silicon is different:** A typical gaming PC has CPU RAM (fast but separate from GPU) and VRAM (on the graphics card). Moving data between them is a bottleneck. Apple's unified memory eliminates that bottleneck — the full memory pool is accessible at GPU speeds. The base M4 has 120 GB/s memory bandwidth; the M4 Pro has 273 GB/s.

**Mac Mini M4 configurations:**

| Config | Unified Memory | Memory Bandwidth | 8B Q4 speed | What fits | Est. Cost |
|---|---|---|---|---|---|
| M4 (base) | 16 GB | 120 GB/s | 18–20 t/s (llama.cpp) / 25–30 t/s (MLX) | Up to ~13B models | ~$800 |
| M4 (upgraded) | 24 GB | 120 GB/s | 18–20 t/s (llama.cpp) / 25–30 t/s (MLX) | Up to ~20B models | ~$1,000 |
| M4 Pro | 24–48 GB | 273 GB/s | 40–50 t/s | Up to 70B models (70B runs at ~4–5 t/s) | ~$1,400 |

> **llama.cpp vs MLX:** MLX is Apple's own inference framework, optimized for Apple Silicon. It's typically 30–50% faster than llama.cpp on Macs. The trade-off: MLX only works on Macs, while llama.cpp is universal.

**What this is good for:** A self-contained inference machine that's quiet, power-efficient (~20–30W), and requires no Linux driver headaches. The M4 Pro at 40–50 t/s for 8B is competitive with an eGPU setup — and far simpler. The 70B at ~4–5 t/s is technically possible but painfully slow (about human reading speed).

---

## Tier 4 — Mac Mini M4 (Multi-Node)

**What it is:** Running two or more Mac Minis together, either as independent replicas (each handling separate user requests) or as a distributed inference cluster (multiple machines sharing a single large model).

**Speed: ~80–100 t/s (2× M4 Pro nodes, 8B replicas) | scales linearly for independent replicas**

**Two ways to use multiple Mac Minis:**

**Option A — Independent replicas (easy, recommended):**
Each Mac Mini runs its own copy of the same model. A load balancer routes user requests across both. Throughput roughly doubles with each node added. Simple to set up, great for handling many concurrent users.

**Option B — Distributed inference (advanced):**
Multiple Macs share the weights of one large model across their combined memory. Allows running models too large for any single node. Requires specialized software (mlx-lm or llama.cpp with tensor split) and a fast network connection between nodes. Performance gains are smaller than Option A due to inter-node communication overhead.

**Example 2-node setup (2× Mac Mini M4 Pro, 48GB each):**
- Combined memory: 96GB
- Can run Llama 3.1 70B Q4 (~40GB) with headroom ✅
- Independent replicas at 8B: ~80–100 t/s combined
- Distributed 70B: ~8–12 t/s (faster than single-node ~4–5 t/s, but networking overhead is real)

**What this is good for:** Scaling inference capacity for growing teams. Each Mac Mini added = more concurrent capacity. More power-efficient per dollar than a prosumer GPU rig for smaller models.

---

## Tier 5 — Prosumer LLM Rig (~$8,000–12,000)

**What it is:** A custom-built desktop workstation designed specifically for local AI inference. Think of it as a gaming PC taken to the extreme — chosen for maximum VRAM and memory bandwidth rather than gaming frame rates.

**Speed: ~35–55 t/s on 27B–32B models | ~8–15 t/s on Llama 4 Scout 109B (needs offload)**

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
- **Gemma 3 27B** (Google): Excellent reasoning, fits in a single 4090 with quantization — **~50–55 t/s**
- **Qwen 32B** (Alibaba): Strong at coding and multilingual tasks — **~35–50 t/s**
- **Llama 4 Scout** (109B total parameters, 17B active via MoE): Meta's flagship open model — **~8–15 t/s** (Q4 is ~55–60GB, needs CPU offloading or aggressive Q2/Q3 quantization to fit in 48GB VRAM)

> **What is MoE?** "Mixture of Experts" — an architecture where a huge model (109B parameters total) only activates a small fraction (17B) at any moment. This means it has the knowledge of a 109B model but runs closer to the speed of a 17B model. Most of the frontier models use this trick.

**What this is good for:** Teams or individuals who want genuinely frontier-level open-source model quality running privately on local hardware. No API fees, no data leaving your premises, no rate limits.

---

## Side-by-Side Summary

```
Speed (t/s)     Model size supported
    │
120─┤  ── OptiPlex × 20 nodes at scale (CPU, 8B replicas) ─────────
    │
105─┤                             ──── OptiPlex + eGPU (8B model) ──
100─┤                             ──── Mac Mini M4 × 2 (8B replicas)
    │
 55─┤                ──── Prosumer Rig (Gemma 27B / Qwen 32B) ─────
 50─┤                       ──── Mac Mini M4 Pro (8B model) ───────
    │
 25─┤                       ──── Mac Mini M4 base (8B, MLX) ───────
 18─┤  ── OptiPlex × 3 nodes current (CPU, 8B) ─
 15─┤                              ──── Prosumer Rig (Scout 109B) ─
    │
  5─┤                                   ── Mac Mini M4 Pro (70B) ──
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

*Speed estimates based on published llama.cpp and MLX community benchmarks (LocalScore, OpenLLMBenchmarks, Puget Systems, community Reddit benchmarks), Intel 10th Gen specs, Apple M4 memory bandwidth specs, and NVIDIA RTX 3090/4090 inference benchmarks. Actual throughput varies by model, quantization level, context length, software version, and system configuration. Confirm CPU model on the OptiPlex nodes via `dmidecode -t processor` — estimates above use i5-10500T as baseline.*

*Source research: Perplexity AI hardware requirements report (March 2026), community benchmarks from r/LocalLLaMA, LocalScore.ai, Bizon Tech, and DatabaseMart.*
