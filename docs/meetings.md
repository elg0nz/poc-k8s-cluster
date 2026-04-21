# Meetings

## 2026-04-24 — v0.5.0 Planning Session

**Date:** Friday, April 24, 2026
**Time:** 2:00 PM Pacific
**Proposed by:** Glo

### Agenda

Planning session for **version 0.5.0**. Glo will walk through the hardware setup process, then we'll discuss the software goals for making the cluster accessible to tenants.

#### Part 1 — Hardware (demo + hands-on)

1. **Flashing Talos onto OptiPlex NVMe drives** — Glo will demo the full process: pulling the NVMe from an OptiPlex 3080 Micro, flashing it with the Talos image, and reinstalling it
2. **Crimping network cables** — How to crimp Ethernet cables for each machine so we're not dependent on pre-made lengths
3. **Joining new nodes to the cluster** — Once we have the power supplies, how to boot a freshly flashed drive and have it join the existing cluster

#### Part 2 — Software (discussion)

4. **Cloudflare Tunnel** — Set up a [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-tunnel/) so users can reach the cluster without us exposing it to the public internet
5. **Hosting OpenClaw via NemoClaw** — Deploy isolated OpenClaw instances per tenant using NemoClaw, with secrets managed through SOPS + GPG (see [SOPS + OpenClaw setup guide](sops-openclaw.md))
