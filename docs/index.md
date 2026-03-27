# poc-k8s-cluster

Bare-metal Kubernetes cluster on Talos Linux v1.12.5 with 3 Dell OptiPlex 3080 Micro nodes (1 control-plane + 2 workers).

**Cluster name:** `iva` | **Managed from:** Omarchy (Arch Linux) launcher box

**Stack:** Talos Linux · Kubernetes v1.35.2 · Cilium v1.19.1

---

## Current Version: alpha-0.0.2

The cluster is bootstrapped and operational with 3 nodes. All documentation below reflects this state.

| Document | Description |
|---|---|
| [Cluster Plan](plan.md) | Architecture, network topology, software stack, open questions |
| [Runbook](runbook.md) | Step-by-step guide to bootstrapping and operating the Talos cluster |
| [Compute Capacity](compute-capacity.md) | CPU, RAM, storage, and workload capacity estimates |
| [Inference Capacity](inference-capacity.md) | LLM inference speed across hardware tiers |
| [GPU Inference](gpu-inference.md) | Phase 2: adding GPU nodes for real inference speed |
| [OS Install](os-install.md) | Talos raw-image flashing strategy |

---

## Next: alpha-0.1.0 / public-beta-1.0.0

See [Next Steps](next-steps.md) for the roadmap — getting 4 nodes online (alpha-0.1.0) and scaling to 40+ machines for the full AI floor (public-beta-1.0.0).

---

## Quick Links

- [Changelog](changelog.md) — version history
- [Next Steps](next-steps.md) — what's planned next
