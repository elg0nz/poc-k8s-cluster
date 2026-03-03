# Cluster Capacity Estimates

**Hardware:** 20× Dell OptiPlex 3080 Micro  
**Status:** Estimates — CPU model TBD (confirm via `dmidecode -t processor`)

---

## Confirmed Specs

| Spec | Value |
|---|---|
| RAM | 8GB DDR4 3200MHz per node |
| Storage | 256GB NVMe SSD per node (WD PC SN530, PCIe Gen3 x4) |
| Network | 1GbE per node |
| Power | ~65W max per node |

---

## CPU Scenarios

The OptiPlex 3080 Micro shipped with 10th Gen Intel Core (Comet Lake). Two likely configs:

| Config | Cores | Threads | Base / Boost | TDP |
|---|---|---|---|---|
| i5-10500T (likely) | 6c / 12t | 12 | 2.3 / 3.8 GHz | 35W |
| i7-10700T (possible) | 8c / 16t | 16 | 2.0 / 4.5 GHz | 35W |

> **Action:** Run `dmidecode -t processor` on any node to confirm. The estimates below cover both cases.

---

## Cluster-Wide Compute

| Metric | i5-10500T (20 nodes) | i7-10700T (20 nodes) |
|---|---|---|
| Total physical cores | 120 | 160 |
| Total threads | 240 | 320 |
| Total RAM | 160 GB | 160 GB |
| Total NVMe storage | 5.12 TB raw | 5.12 TB raw |
| Usable storage (Longhorn 2-replica) | ~2.5 TB | ~2.5 TB |
| Max power draw | ~1.3 kW | ~1.3 kW |

---

## Kubernetes Allocatable (estimated)

k3s reserves ~10% CPU + ~512MB RAM per node for system overhead.

| Resource | Per Node | Cluster Total (20 nodes) |
|---|---|---|
| Allocatable CPU (i5) | ~10.8 cores | ~216 cores |
| Allocatable CPU (i7) | ~14.4 cores | ~288 cores |
| Allocatable RAM | ~7.5 GB | ~150 GB |
| Allocatable storage | ~128 GB | ~2.5 TB (Longhorn 2x) |

---

## What You Can Run

### General Workloads

| Workload | Resources | Per Node | Cluster Total | Notes |
|---|---|---|---|---|
| NGINX (reverse proxy / static) | 0.1 CPU, 64MB | ~50 instances | ~1,000 instances | Trivial overhead; run as DaemonSet for ingress |
| FastAPI / Node.js services | 0.5 CPU, 256MB | ~12–15 replicas | ~250–300 replicas | Standard microservice sizing |
| PostgreSQL | 2 CPU, 2GB RAM | ~3 instances | ~60 instances | Use Longhorn PVC for data persistence |
| Redis | 0.25 CPU, 512MB | ~10 instances | ~200 instances | — |
| Jupyter notebooks | 1 CPU, 2GB | ~3 per node | ~60 cluster-wide | Good for member data science workloads |
| OpenClaw Gateway | 0.5 CPU, 512MB | ~6 instances | ~120 instances | One per team/member; stateless, scales horizontally |
| OpenClaw Agent sessions | 1 CPU, 1GB | ~5 sessions | ~100 concurrent sessions | Each active agent session ~1 CPU; session count drives sizing |

### LLM Inference (CPU-only, no GPU)

CPU-only inference via `llama.cpp` or `ollama`. Performance scales with core count and memory bandwidth.

| Model | Quantization | VRAM needed | Tok/sec per node (i5) | Tok/sec per node (i7) | Notes |
|---|---|---|---|---|---|
| Llama 3.2 3B | Q4_K_M | ~2 GB | 15–25 tok/sec | 20–35 tok/sec | Fast, lightweight |
| Llama 3.1 8B | Q4_K_M | ~5 GB | 6–12 tok/sec | 8–16 tok/sec | Good quality/speed tradeoff |
| Llama 3.1 8B | Q8 | ~9 GB | 3–6 tok/sec | 4–8 tok/sec | Exceeds 8GB RAM — requires swap or split |
| Mistral 7B | Q4_K_M | ~4.5 GB | 8–14 tok/sec | 10–18 tok/sec | Strong reasoning |
| Phi-3 Mini 3.8B | Q4_K_M | ~2.5 GB | 12–20 tok/sec | 15–28 tok/sec | Efficient, good for code |
| DeepSeek-R1 7B | Q4_K_M | ~5 GB | 5–10 tok/sec | 7–14 tok/sec | Strong reasoning, slower |

> ⚠️ 8GB RAM per node is the hard constraint. Models requiring >6GB weights in RAM leave little headroom for the OS and k3s. Stick to Q4 quantized models ≤7B for reliable single-node inference. For larger models, consider model parallelism across 2–3 nodes (experimental with llama.cpp `--split-mode`).

### Parallel Inference (3 inference nodes)

With 3 dedicated inference worker nodes running independent replicas:

| Model | Config | Combined throughput |
|---|---|---|
| Llama 3.2 3B Q4 | 3 nodes × 1 instance | 45–75 tok/sec |
| Llama 3.1 8B Q4 | 3 nodes × 1 instance | 18–36 tok/sec |
| Mistral 7B Q4 | 3 nodes × 1 instance | 24–42 tok/sec |

These are independent replicas (not distributed inference) — each node handles separate requests. Useful for concurrent users, not for running a single large model faster.

---

## Storage

| Use case | Capacity |
|---|---|
| Raw NVMe per node | 256 GB |
| Longhorn distributed (2-replica) | ~2.5 TB usable |
| Longhorn distributed (3-replica) | ~1.7 TB usable |
| Model storage (no replication needed) | Up to 5 TB raw — store models on local node path |

> Recommendation: Store LLM model weights on local node storage (not Longhorn) — no need for replication, and local NVMe is faster for sequential reads.

---

## Example: AI Floor Member Stack

A typical member running an AI project on the cluster:

| Service | CPU | RAM | Notes |
|---|---|---|---|
| NGINX (ingress) | 0.1 | 64MB | Shared cluster-wide via DaemonSet — no per-member cost |
| OpenClaw Gateway | 0.5 | 512MB | One per member team |
| OpenClaw Agent (1 active session) | 1.0 | 1GB | Scales with concurrent agent activity |
| FastAPI backend | 0.5 | 256MB | Member's app |
| PostgreSQL | 2.0 | 2GB | With Longhorn PVC |
| Redis | 0.25 | 512MB | Cache / task queue |
| **Total per member** | **~4.35 CPU** | **~4.3 GB** | ~35 full member stacks across cluster |

With 150GB allocatable RAM and ~216 allocatable cores: **the cluster can support ~35 full member stacks simultaneously** before hitting RAM limits.

---

## Realistic Day-One Cluster Layout

Assuming i5-10500T, 3 control plane + 3 inference workers + 14 general workers:

```
Control plane × 3     — k3s system overhead, etcd, API server
Inference workers × 3 — 1× Llama 3.1 8B Q4 per node (18–36 tok/sec combined)
General workers × 14  — ~140+ allocatable cores, ~105 GB RAM for user workloads
```

This gives you a cluster that can:
- Serve **~200+ concurrent microservices** on the general pool
- Run **3 independent LLM instances** for member inference (Llama 8B or similar)
- Store **~2.5 TB** of shared distributed data (Longhorn)
- Host **Grafana, Prometheus, Loki** with negligible overhead on the general pool

---

## Bottlenecks to Watch

| Bottleneck | Impact | Mitigation |
|---|---|---|
| 8GB RAM per node | Limits model size; no headroom for large quantizations | Stick to Q4 ≤7B; avoid swap in production |
| 1GbE network | ~125 MB/s per node — fine for most workloads, slow for large model transfers | Pre-stage model weights locally; don't stream from NFS |
| No GPU | CPU inference only; 5–25 tok/sec vs 500+ tok/sec on A100 | Acceptable for PoC; Phase 2 requires different hardware |
| No IPMI/iDRAC | Can't remote-power or console into nodes | PiKVM per shelf or Wake-on-LAN + SSH |

---

*Estimates based on published Intel 10th Gen benchmarks and llama.cpp community benchmarks on similar hardware. Confirm CPU model before finalizing inference node allocation.*
