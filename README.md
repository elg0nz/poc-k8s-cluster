# poc-k8s-cluster

A production-grade k3s cluster plan for 20× bare-metal nodes (Dell OptiPlex 3080 Micro).

Covers node roles, network topology, software stack, installation steps, GitOps, and definition of done.

**Stack:** k3s · Longhorn · MetalLB · Traefik · Prometheus/Grafana · Loki · Flux

---

## Contents

- [PLAN.md](PLAN.md) — full cluster plan: architecture, installation, timeline, open questions
- [CAPACITY.md](CAPACITY.md) — estimated compute, RAM, storage, and LLM inference throughput
- [HOW_TO_ADD_GPU_INFERENCE.md](HOW_TO_ADD_GPU_INFERENCE.md) — Phase 2: adding GPU nodes for real inference speed
