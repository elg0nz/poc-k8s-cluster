# Talos Kubernetes Cluster Plan
**Cluster name:** `iva`
**Hardware:** Dell OptiPlex 3080 Micro (bare-metal)
**Stack:** Talos Linux + Kubernetes + Cilium

---

## Hardware Baseline

| Spec | Value |
|---|---|
| Node | Dell OptiPlex 3080 Micro |
| Form factor | ~1.2L UCFF, VESA-mountable |
| CPU | Intel i3/i5/i7 10th gen (confirm model via `dmidecode -t processor`) |
| RAM | 8GB DDR4 3200MHz per node (confirmed) |
| Storage | 256GB NVMe SSD per node (WD PC SN530, PCIe Gen3 x4 — confirmed) |
| Network | 1GbE onboard (Intel) — WiFi not used in cluster |
| Power | 65W max per node |

---

## Cluster Architecture

### Node Roles (3 active, designed to scale)

| Role | Count | IP | Notes |
|---|---|---|---|
| Control plane | 1 | `192.168.10.32` | Runs etcd, API server. Single CP for now; can expand to 3 for HA. |
| Worker | 2 | `192.168.10.11`, `192.168.10.43` | General-purpose workloads. Add more by flashing the same worker image. |

> Additional workers can be added at any time by flashing the pre-built worker image to a new NVMe and booting. See [Runbook](runbook.md) Part 6.

### Network Topology

```
[Router / DHCP]
     │
     ├── Control plane   (192.168.10.32)
     ├── Worker 1         (192.168.10.11)
     └── Worker 2         (192.168.10.43)
```

- All nodes on same L2 segment (192.168.10.0/24)
- IP assignment via DHCP reservations on the router (by MAC address)
- DNS: CoreDNS (bundled with Kubernetes) + upstream resolver
- No VLANs in current setup

### Launcher Box

| Item | Value |
|---|---|
| OS | Omarchy (Arch Linux) |
| Tools | Docker, `talosctl`, `kubectl`, `cilium` CLI, `zstd` |
| kubeconfig | `~/talos-iva/kubeconfig` (merged into `~/.kube/config`) |
| talosconfig | `~/talos-iva/talosconfig` |
| kubectl context | `admin@iva` |

---

## Software Stack

### Talos Linux — Why Not a General-Purpose OS

- Immutable, API-managed Linux distribution purpose-built for Kubernetes
- No SSH, no shell, no package manager — reduced attack surface
- Automatic handling of swap, kernel parameters, and container runtime
- Disk image flashed once; config embedded at build time
- Upgrades are atomic image swaps via `talosctl upgrade`

### Core Components

| Component | Version | Notes |
|---|---|---|
| OS | Talos Linux v1.12.5 | Immutable, API-driven |
| Kubernetes | v1.35.2 | Bundled with Talos |
| Container runtime | containerd v2.1.6 | Bundled with Talos |
| Kernel | 6.18.15-talos | Talos custom kernel |
| CNI | Cilium v1.19.1 | Installed via `cilium` CLI with Talos-specific flags |

---

## Installation Summary

All installation steps are documented in the [Runbook](runbook.md). The high-level flow:

1. **Generate config** — `talosctl gen config` produces `controlplane.yaml`, `worker.yaml`, and `talosconfig`
2. **Build images** — Talos imager container builds raw disk images with config embedded
3. **Flash NVMe** — `dd` the image onto each node's NVMe (via USB enclosure on the launcher box)
4. **Boot and bootstrap** — First control-plane node: `talosctl bootstrap` to initialize etcd
5. **Install Cilium** — `cilium install` with Talos-specific security context flags
6. **Add workers** — Flash worker image, boot, node auto-joins the cluster

No manual OS installation, no SSH provisioning, no swap configuration needed.

---

## Definition of Done

- [x] Control-plane node running and healthy (`kubectl get nodes`)
- [x] At least one worker node joined and Ready
- [x] Cilium CNI installed and operational (`cilium status`)
- [x] `kubectl` and `talosctl` working from the launcher box
- [ ] Expand to 3 control-plane nodes for HA etcd quorum
- [ ] All available OptiPlex nodes added as workers
- [ ] Monitoring stack deployed (Prometheus + Grafana)
- [ ] At least one workload deployed
- [ ] Load balancer solution deployed (MetalLB or Cilium LB)

---

## Open Questions

1. **HA control plane** — currently single CP node. Plan to add 2 more for etcd quorum. Requires dedicated IPs and DHCP reservations.
2. **CPU model** — confirm via `talosctl -n 192.168.10.32 read /proc/cpuinfo` or check BIOS.
3. **Storage** — no distributed storage yet. Evaluate Longhorn, Rook-Ceph, or local-path-provisioner based on workload needs.
4. **Load balancer** — no ingress/LB solution yet. Cilium can handle L2/BGP LB, or deploy MetalLB separately.
5. **Monitoring** — Prometheus + Grafana stack not yet deployed.
6. **Workloads** — determine first production workloads for the cluster.
7. **Remote management** — no IPMI/iDRAC on OptiPlex. Consider PiKVM or Wake-on-LAN for remote power cycling.
8. **Backups** — etcd snapshot strategy for disaster recovery (`talosctl etcd snapshot`).

---

## Notes

- OptiPlex 3080 Micro BIOS must be set to AHCI mode (not Intel RST) for NVMe visibility. See [Runbook](runbook.md) hardware notes.
- Talos config files (`controlplane.yaml`, `worker.yaml`) contain private keys and tokens. Do not commit to version control.
- The same worker image can be flashed to any number of identical machines — no per-node configuration needed.
- CPU-only LLM inference: llama.cpp on i5/i7 nodes yields ~2-8 tok/sec per node. Viable for 7B quantized models.
