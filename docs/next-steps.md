# Next Steps

---

## alpha-0.1.0 — Get the Cluster Running

### Hardware Needs

!!! note "Procurement"
    Ray handles hardware procurement. Ask Vidya for his recommendations on parts and vendors.

**Current state:** Only the Omarchy box (DNS server), one control-plane node, and zero worker nodes are running. The bottleneck is power supplies — we don't have enough to power the remaining machines.

| Item | Qty | Why | Link |
|---|---|---|---|
| OptiPlex 65W chargers (or USB-C chargers with barrel adapters) | 4+ | Power the 4 already-flashed nodes | — |
| DYMO LetraTag Bluetooth label maker | 1 | Label each machine with hostname, IP, and specs | [DYMO LetraTag on Amazon](https://www.amazon.com/DYMO-LetraTag-Bluetooth-Technology-Pistachio/dp/B0BC9RG8JS/) |

With 4 chargers we can bring up 1 control-plane + 3 workers, which is enough to run real workloads.

### Hardware Inventory

Specs vary across the OptiPlex fleet — CPU model, RAM size, and NVMe capacity are not uniform. Before deploying workloads, inventory every machine:

- **CPU** — `talosctl read /proc/cpuinfo` (i3 vs i5 vs i7, core count)
- **RAM** — `talosctl read /proc/meminfo` (8GB vs 16GB)
- **NVMe** — `talosctl read /sys/block/nvme0n1/size` (128GB vs 256GB vs 512GB)

Label each machine with the DYMO labeler (hostname, IP, CPU, RAM) so specs are visible at a glance on the physical hardware.

### Software Plan

Once the 4 nodes are online (all 4 machines are already flashed and ready to boot):

- Deploy multiple [NemoClaw](https://github.com/NVIDIA/NemoClaw) instances on the cluster
- Make them available to select members on our floor for early testing

---

## public-beta-1.0.0 — Open to the AI Floor

Scale the cluster to all 40+ machines and open access to all AI floor citizens.

### Network Infrastructure

The Omarchy NUC currently serves as the DHCP server for the cluster. This is a single point of failure and not suitable for 40+ nodes. Replace it with a dedicated network appliance:

- Deploy a **Ubiquiti gateway/router** (e.g., UniFi Dream Machine or EdgeRouter) to handle DHCP, DNS, and network management
- Migrate all DHCP reservations (MAC-to-IP mappings) from the Omarchy box to the new appliance
- The Omarchy NUC can then be repurposed as a general-purpose launcher box or retired

### Access Model

- **Bring your own token** — each user provides their own AI provider API key
- We provide a small pool of courtesy API tokens for users who don't have their own
- Secrets management: build a lightweight app using [SOPS](https://github.com/getsops/sops) + GPG so users can safely upload their tokens, encrypted at rest and inaccessible to other users

### Hardware Needs

!!! note "Procurement"
    Ray handles hardware procurement. Ask Vidya for his recommendations on parts and vendors.

| Item | Qty | Why | Link |
|---|---|---|---|
| Indoor Cat5e cables (flat, flexible — not outdoor-rated rigid cables) | 40+ | Replace the current stiff outdoor cables | [Cable Matters 10-pack on Amazon](https://www.amazon.com/Cable-Matters-Ethernet-Internet-Network/dp/B0D6YSSJ9R/) |
| Pass-through RJ45 connectors | 1+ pack | Clean, reliable terminations for custom cable lengths | [Cable Matters pass-through connectors on Amazon](https://www.amazon.com/Cable-Matters-Through-Stranded-Connectors/dp/B07PXMN2VK/) |
| RJ45 strain reliefs | 1+ pack | Protect connector joints from cable stress | [Cable Matters strain reliefs on Amazon](https://www.amazon.com/Cable-Matters-4-Pack-Strain-Relief/dp/B0049QNV3E/) |
| NVMe USB enclosures | 3–10 | Parallelize flashing across multiple drives at once | [UGREEN NVMe enclosure on Amazon](https://www.amazon.com/UGREEN-Enclosure-Tool-Free-Thunderbolt-Compatible/dp/B09T97Z7DM/) |

With this hardware we can bulk-flash the remaining 40+ machines. Help with crimping the Ethernet cables would be appreciated.

---

## Definition of Done

### alpha-0.1.0
- [ ] 4 nodes powered and online (1 CP + 3 workers)
- [ ] Hardware inventory complete (CPU, RAM, NVMe for every machine)
- [ ] All machines physically labeled
- [ ] NemoClaw deployed and accessible to select floor members

### public-beta-1.0.0
- [ ] 40+ machines running and joined to the cluster
- [ ] BYOT (bring your own token) access model live
- [ ] SOPS + GPG secrets management app deployed
- [ ] All AI floor citizens have access
- [ ] Indoor cabling and clean network terminations in place
- [ ] DHCP/DNS migrated from Omarchy NUC to dedicated Ubiquiti gateway
