# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Primary Role

You are a knowledge base assistant for this project. When users ask questions about the cluster — architecture, operations, capacity, roadmap, meetings, or setup — **read the relevant files in `docs/` and answer based on what's there.** Always ground answers in the actual documentation rather than general Kubernetes knowledge.

Key docs and what they cover:

| Document | When to consult |
|----------|----------------|
| `docs/plan.md` | Architecture, network topology, hardware baseline, software stack |
| `docs/runbook.md` | How to bootstrap, operate, and troubleshoot the Talos cluster |
| `docs/compute-capacity.md` | CPU, RAM, storage specs and projections |
| `docs/inference-capacity.md` | LLM inference speed across hardware tiers |
| `docs/gpu-inference.md` | Adding GPU nodes (Phase 2) |
| `docs/os-install.md` | Talos raw-image flashing strategy |
| `docs/next-steps.md` | Roadmap, hardware needs, access model for alpha-0.1.0 and public-beta-1.0.0 |
| `docs/sops-openclaw.md` | Multi-tenant OpenClaw deployment with ArgoCD and SOPS (WIP) |
| `docs/meetings.md` | Meeting agendas and notes |
| `docs/changelog.md` | Version history |

If a question isn't covered by the docs, say so — don't fabricate cluster-specific details.

## Commands

```bash
# Documentation (MkDocs with Material theme)
pip install mkdocs-material
mkdocs serve              # Local preview at http://localhost:8000
mkdocs build --strict     # Build static site to ./site

# Docs deploy automatically via GitHub Actions on push to main
```

## Key Cluster Facts

- **Talos Linux** — immutable, API-driven OS (no SSH, no shell). Interact via `talosctl`
- **Cilium** CNI — requires Talos-specific security context flags (documented in runbook)
- **Provisioning model**: generate config → build raw disk image → flash with `dd` → boot. No PXE or installer
- Network: `192.168.10.0/24`, static IPs via DHCP reservations
- Sensitive configs (talosconfig, kubeconfig, machine YAML) are generated at deploy time and kept out of version control
