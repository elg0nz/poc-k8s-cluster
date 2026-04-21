# poc-k8s-cluster

A bare-metal Kubernetes cluster where folks on our AI floor can safely host their own [OpenClaw](https://github.com/anthropics/openclaw) instances — without sharing API keys, without exposing services to the public internet, and without needing to know how Kubernetes works.

## What we're building

We're turning a shelf of Dell OptiPlex 3080 Micro machines into a shared compute platform. Each person gets their own isolated OpenClaw environment deployed through [NemoClaw](https://github.com/NVIDIA/NemoClaw), with secrets encrypted via [SOPS](https://github.com/getsops/sops) so API keys never appear in plaintext.

The cluster runs on [Talos Linux](https://www.talos.dev/) — an immutable, hardened OS built specifically for Kubernetes — with [Cilium](https://cilium.io/) handling networking and tenant isolation.

**Access is through [Cloudflare Tunnels](https://developers.cloudflare.com/cloudflare-tunnel/)**, so users can reach their OpenClaw instances from anywhere without us opening ports or exposing the cluster directly to the internet. The tunnel connects outbound from inside our network to Cloudflare's edge, and Cloudflare handles authentication and routing back to the right tenant.

## Current status

**Version:** alpha-0.0.2 — cluster is bootstrapped with 3 nodes (1 control-plane + 2 workers). Not yet serving tenants.

**Next milestone:** [v0.5.0](meetings.md) — flash remaining machines, crimp cables, set up Cloudflare Tunnel, and deploy the first OpenClaw instances.

See [Next Steps](next-steps.md) for the full roadmap.

## Documentation

| Document | What it covers |
|----------|---------------|
| [Cluster Plan](plan.md) | Architecture, network topology, hardware, software stack |
| [Runbook](runbook.md) | Step-by-step guide to bootstrapping and operating the cluster |
| [Compute Capacity](compute-capacity.md) | CPU, RAM, storage specs and projections |
| [Inference Capacity](inference-capacity.md) | LLM inference speed across hardware tiers |
| [GPU Inference](gpu-inference.md) | Phase 2: adding GPU nodes |
| [OS Install](os-install.md) | Talos raw-image flashing strategy |
| [SOPS + OpenClaw](sops-openclaw.md) | Multi-tenant OpenClaw deployment with ArgoCD and SOPS (WIP) |
| [Meetings](meetings.md) | Agendas and notes |
| [Next Steps](next-steps.md) | Roadmap for upcoming versions |
| [Changelog](changelog.md) | Version history |

## Quick Links

- [GitHub repo](https://github.com/elg0nz/poc-k8s-cluster) — source code and raw docs
- [Browse the docs site](https://elg0nz.github.io/poc-k8s-cluster/)
