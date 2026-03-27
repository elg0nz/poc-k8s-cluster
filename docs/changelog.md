# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased — public-beta-1.0.0]

### Planned
- Scale to 40+ nodes, open access to all AI floor citizens
- Bring-your-own-token access model with courtesy API tokens
- Secrets management app (SOPS + GPG)
- Indoor cabling and network hardware refresh

---

## [Unreleased — alpha-0.1.0]

### Planned
- Acquire 4+ OptiPlex chargers (or USB-C with adapters) to power the flashed nodes
- Bring 4 nodes online (1 CP + 3 workers)
- Deploy NemoClaw instances for select floor members

### Added
- `next-steps.md` — planned work for alpha-0.1.0 and public-beta-1.0.0
- Reorganized repository as a Read the Docs site (MkDocs + Material theme)
- GitHub Pages deployment via GitHub Actions

---

## [alpha-0.0.2] — 2026-03-23

Current release. The cluster is bootstrapped and operational on Talos Linux.

### Added
- `runbook.md` — complete step-by-step guide to bootstrapping the Talos Linux Kubernetes cluster (BIOS config, image building, flashing, bootstrapping, Cilium CNI installation)
- `inference-capacity.md` — hardware tier comparison for LLM inference across 5 scenarios (OptiPlex CPU-only, eGPU, Mac Mini M4, multi-Mac, prosumer rig)
- `changelog.md`

### Changed
- All docs migrated from k3s + Ubuntu plan to Talos Linux v1.12.5 + Kubernetes v1.35.2 + Cilium v1.19.1
- `plan.md` — rewritten for Talos-based architecture (1 CP + 2 workers, 192.168.10.x network)
- `compute-capacity.md` — updated for Talos overhead, current 3-node state with 20-node projections (renamed from `CAPACITY.md`)
- `gpu-inference.md` — updated for Talos cluster (GPU nodes join via kubelet since Talos lacks NVIDIA driver support)
- `os-install.md` — rewritten for Talos raw-image flashing (replaces Ubuntu manual/PXE strategy)

### Contains
- `plan.md` — cluster architecture, network topology, software stack, open questions
- `runbook.md` — full bootstrapping and operations guide
- `compute-capacity.md` — CPU, RAM, storage, workload capacity estimates
- `inference-capacity.md` — LLM inference speed across hardware tiers
- `gpu-inference.md` — Phase 2 GPU inference paths
- `os-install.md` — Talos image flashing strategy

---

## [alpha-0.0.1] — 2026-03-02

Initial release. Planning and capacity analysis for a 20-node k3s cluster on Ubuntu.

### Added
- `README.md` — project overview and contents index
- `plan.md` — full cluster plan: hardware baseline, node roles, network topology, k3s software stack, installation phases, timeline
- `compute-capacity.md` — cluster-wide compute estimates, LLM inference throughput, storage planning
- `gpu-inference.md` — two paths to GPU inference (dedicated GPU nodes, eGPU via Thunderbolt 3)
