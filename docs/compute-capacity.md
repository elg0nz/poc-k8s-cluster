# Cluster Capacity Estimates

**Hardware:** Dell OptiPlex 3080 Micro (3 nodes currently; 20 acquired)
**OS:** Talos Linux v1.12.5 · Kubernetes v1.35.2 · Cilium v1.19.1
**Status:** Estimates — CPU model TBD (confirm via `talosctl read /proc/cpuinfo`)

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

> **Action:** Run `talosctl read /proc/cpuinfo` on any node to confirm. The estimates below cover both cases.

---

## Current Cluster (3 nodes)

| Node | Role | IP |
|---|---|---|
| `talos-zzo-1sj` | control-plane | `192.168.10.32` |
| `talos-shv-9v1` | worker | `192.168.10.11` |
| `talos-d33-vyt` | worker | `192.168.10.43` |

| Metric | i5-10500T (3 nodes) | i7-10700T (3 nodes) |
|---|---|---|
| Total physical cores | 18 | 24 |
| Total threads | 36 | 48 |
| Total RAM | 24 GB | 24 GB |
| Total NVMe storage | 768 GB raw | 768 GB raw |
| Max power draw | ~195 W | ~195 W |

---

## Projected Cluster (20 nodes)

> These are projections for when all 20 acquired machines are deployed.

| Metric | i5-10500T (20 nodes) | i7-10700T (20 nodes) |
|---|---|---|
| Total physical cores | 120 | 160 |
| Total threads | 240 | 320 |
| Total RAM | 160 GB | 160 GB |
| Total NVMe storage | 5.12 TB raw | 5.12 TB raw |
| Max power draw | ~1.3 kW | ~1.3 kW |

---

## Kubernetes Allocatable (estimated)

Talos Linux is a minimal, immutable OS purpose-built for Kubernetes. It has lower system overhead than general-purpose distributions: the OS runs entirely in RAM (~200MB) with no SSH daemon, package manager, or shell. Estimated system reservation is ~5% CPU + ~400MB RAM per node (kubelet, containerd, Cilium agent, Talos machined).

### Current cluster (3 nodes)

| Resource | Per Node | Cluster Total (3 nodes) |
|---|---|---|
| Allocatable CPU (i5) | ~11.4 cores | ~34.2 cores |
| Allocatable CPU (i7) | ~15.2 cores | ~45.6 cores |
| Allocatable RAM | ~7.6 GB | ~22.8 GB |
| Allocatable storage | ~230 GB (local) | ~690 GB (local, no replication) |

### Projected cluster (20 nodes)

| Resource | Per Node | Cluster Total (20 nodes) |
|---|---|---|
| Allocatable CPU (i5) | ~11.4 cores | ~228 cores |
| Allocatable CPU (i7) | ~15.2 cores | ~304 cores |
| Allocatable RAM | ~7.6 GB | ~152 GB |
| Allocatable storage | ~230 GB (local) | ~4.6 TB (local, no replication) |

> Storage replication depends on the distributed storage solution chosen (TBD). Usable capacity with 2-replica replication would be roughly half the raw total.

---

## What You Can Run

### General Workloads

| Workload | Resources | Per Node | Current Cluster (3) | Projected (20) | Notes |
|---|---|---|---|---|---|
| NGINX (reverse proxy / static) | 0.1 CPU, 64MB | ~50 instances | ~150 | ~1,000 | Trivial overhead; run as DaemonSet for ingress |
| FastAPI / Node.js services | 0.5 CPU, 256MB | ~12–15 replicas | ~36–45 | ~250–300 | Standard microservice sizing |
| PostgreSQL | 2 CPU, 2GB RAM | ~3 instances | ~9 | ~60 | Use PVC for data persistence (storage TBD) |
| Redis | 0.25 CPU, 512MB | ~10 instances | ~30 | ~200 | — |
| Jupyter notebooks | 1 CPU, 2GB | ~3 per node | ~9 | ~60 | Good for member data science workloads |
| OpenClaw Gateway | 0.5 CPU, 512MB | ~6 instances | ~18 | ~120 | One per team/member; stateless, scales horizontally |
| OpenClaw Agent sessions | 1 CPU, 1GB | ~5 sessions | ~15 | ~100 | Each active agent session ~1 CPU; session count drives sizing |

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

> 8GB RAM per node is the hard constraint. Models requiring >6GB weights in RAM leave little headroom for the OS and Kubernetes components. Stick to Q4 quantized models <=7B for reliable single-node inference. For larger models, consider model parallelism across 2–3 nodes (experimental with llama.cpp `--split-mode`).

### Parallel Inference (2 worker nodes — current cluster)

With the 2 current worker nodes running independent replicas:

| Model | Config | Combined throughput |
|---|---|---|
| Llama 3.2 3B Q4 | 2 nodes x 1 instance | 30–50 tok/sec |
| Llama 3.1 8B Q4 | 2 nodes x 1 instance | 12–24 tok/sec |
| Mistral 7B Q4 | 2 nodes x 1 instance | 16–28 tok/sec |

These are independent replicas (not distributed inference) — each node handles separate requests. Useful for concurrent users, not for running a single large model faster.

> **Projected (3+ dedicated inference nodes):** With dedicated inference workers at scale, combined throughput scales linearly (e.g., 3 nodes running Llama 3.1 8B Q4 = 18–36 tok/sec combined).

---

## Storage

> **Storage strategy is TBD.** No distributed storage solution is deployed yet. All capacity below refers to local NVMe on each node.

| Use case | Capacity |
|---|---|
| Raw NVMe per node | 256 GB |
| Total raw (3 nodes) | 768 GB |
| Total raw (20 nodes, projected) | 5.12 TB |
| Model storage (local path) | Store model weights on local node NVMe — no replication needed, and local NVMe is fastest for sequential reads |

> When a distributed storage solution is selected, usable capacity will depend on the replication factor (e.g., 2-replica halves raw capacity, 3-replica yields ~1/3).

---

## Example: AI Floor Member Stack

A typical member running an AI project on the cluster:

| Service | CPU | RAM | Notes |
|---|---|---|---|
| NGINX (ingress) | 0.1 | 64MB | Shared cluster-wide via DaemonSet — no per-member cost |
| OpenClaw Gateway | 0.5 | 512MB | One per member team |
| OpenClaw Agent (1 active session) | 1.0 | 1GB | Scales with concurrent agent activity |
| FastAPI backend | 0.5 | 256MB | Member's app |
| PostgreSQL | 2.0 | 2GB | With PVC (storage solution TBD) |
| Redis | 0.25 | 512MB | Cache / task queue |
| **Total per member** | **~4.35 CPU** | **~4.3 GB** | — |

**Current cluster (3 nodes):** With ~22.8 GB allocatable RAM and ~34 allocatable cores, the cluster can support **~5 full member stacks** on the 2 worker nodes before hitting RAM limits. The control-plane node should be reserved for system workloads.

**Projected (20 nodes):** With ~152 GB allocatable RAM and ~228 allocatable cores, the cluster can support **~35 full member stacks simultaneously** before hitting RAM limits.

---

## Realistic Day-One Cluster Layout (current: 3 nodes)

```
Control plane x 1  — Talos system, etcd, API server, Cilium
Worker x 2         — general workloads + inference
```

With 3 nodes, there is no dedicated inference tier. Workers handle both application workloads and inference requests. This is sufficient for PoC/development purposes.

### Projected layout (20 nodes)

```
Control plane x 3     — Talos system, etcd, API server (HA)
Inference workers x 3 — 1x Llama 3.1 8B Q4 per node (18–36 tok/sec combined)
General workers x 14  — ~160+ allocatable cores, ~106 GB RAM for user workloads
```

This would give the cluster:
- **~200+ concurrent microservices** on the general pool
- **3 independent LLM instances** for member inference (Llama 8B or similar)
- **Grafana, Prometheus, Loki** with negligible overhead on the general pool
- Distributed storage capacity dependent on chosen solution and replication factor

---

## Bottlenecks to Watch

| Bottleneck | Impact | Mitigation |
|---|---|---|
| 8GB RAM per node | Limits model size; no headroom for large quantizations | Stick to Q4 <=7B; avoid swap in production |
| 1GbE network | ~125 MB/s per node — fine for most workloads, slow for large model transfers | Pre-stage model weights locally; don't stream from NFS |
| No GPU | CPU inference only; 5–25 tok/sec vs 500+ tok/sec on A100 | Acceptable for PoC; Phase 2 requires different hardware |
| No IPMI/iDRAC | Can't remote-power or console into nodes | PiKVM per shelf or Wake-on-LAN + SSH |
| 3 nodes (current) | Single control-plane node is not HA; limited worker capacity | Scale to 3 CP + N workers as nodes are brought online |
| No distributed storage | Data is local-only; node failure loses local data | Select and deploy a storage solution (Rook-Ceph, Longhorn, etc.) |

---

*Estimates based on published Intel 10th Gen benchmarks and llama.cpp community benchmarks on similar hardware. Confirm CPU model before finalizing inference node allocation.*
