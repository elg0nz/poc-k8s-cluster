# poc-k8s-cluster

Bare-metal Kubernetes cluster on Talos Linux v1.12.5 with 3 Dell OptiPlex 3080 Micro nodes (1 control-plane + 2 workers).

Cluster name: `iva` · Managed from an Omarchy (Arch Linux) launcher box.

**Stack:** Talos Linux · Kubernetes v1.35.2 · Cilium v1.19.1

---

## Contents

- [RUNBOOK.md](RUNBOOK.md) — complete guide to bootstrapping and operating the Talos cluster (current cluster state, troubleshooting)
- [PLAN.md](PLAN.md) — original cluster plan: architecture, network topology, timeline, open questions
- [COMPUTE_CAPACITY.md](COMPUTE_CAPACITY.md) — estimated compute, RAM, storage, and general workload capacity for the OptiPlex nodes
- [INFERENCE_CAPACITY.md](INFERENCE_CAPACITY.md) — LLM inference speed across hardware tiers (OptiPlex, eGPU, Mac Mini M4, prosumer rig)
- [HOW_TO_ADD_GPU_INFERENCE.md](HOW_TO_ADD_GPU_INFERENCE.md) — Phase 2: adding GPU nodes for real inference speed
