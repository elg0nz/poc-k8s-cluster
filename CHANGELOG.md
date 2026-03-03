# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

## [0.0.3] - 2026-03-03

### Added
- `INFERENCE_CAPACITY.md` — hardware tier comparison for LLM inference speed across 5 scenarios: OptiPlex CPU-only (3 nodes and all 20), OptiPlex + USB-C eGPU, Mac Mini M4 single node, Mac Mini M4 multi-node, and prosumer rig (~$8–12K)
- `CHANGELOG.md` — this file
- Version headers added to all docs

### Changed
- `CAPACITY.md` renamed to `COMPUTE_CAPACITY.md` to better reflect its scope (general compute, RAM, storage)
- `README.md` updated to reference renamed and new files
- `HOW_TO_ADD_GPU_INFERENCE.md` updated reference from `CAPACITY.md` to `COMPUTE_CAPACITY.md`

---

## [0.0.2] - 2026-03-02

### Added
- `CAPACITY.md` — cluster-wide compute estimates, LLM inference throughput per node, and storage planning
- `HOW_TO_ADD_GPU_INFERENCE.md` — two paths to GPU inference: dedicated GPU worker nodes (Option A) and eGPU via Thunderbolt 3 (Option B); includes GPU performance reference table and recommended Phase 2 plan

---

## [0.0.1] - 2026-03-02

### Added
- `README.md` — project overview and contents index
- `PLAN.md` — full cluster plan: hardware baseline, node roles, network topology, software stack (k3s, Longhorn, MetalLB, Traefik, Prometheus/Grafana, Loki, Flux), installation phases, definition of done, and timeline
