# k3s Cluster Plan v1
**Hardware:** 20× Dell OptiPlex 3080 Micro  
**Stack:** k3s (lightweight Kubernetes)

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
| Total draw | ~1.3kW max (20 nodes) — confirm circuit capacity |

---

## Cluster Architecture

### Node Roles (20 nodes total)

| Role | Count | Notes |
|---|---|---|
| Control plane | 3 | HA etcd quorum. Odd number required. |
| Worker — general | 14 | Deployments, services, ingress |
| Worker — inference | 3 | Reserved for LLM/AI workloads (if applicable) |

> Adjust inference node count based on actual workload. If no GPU, all workers are general-purpose.

### Network Topology

```
[Switch / VLAN]
     │
     ├── Control plane × 3  (static IPs: 10.0.1.10–12)
     ├── Workers × 17       (static IPs: 10.0.1.20–36)
     └── [Ingress LB]       (MetalLB pool: 10.0.1.100–120)
```

- All nodes on same L2 segment (1GbE switch, unmanaged OK for v1)
- Static IP assignment via DHCP reservation or `/etc/netplan`
- DNS: internal CoreDNS (k3s built-in) + upstream resolver

---

## Software Stack

### k3s — Why Not Full k8s

- Single binary, ships with containerd + flannel + CoreDNS + Traefik + MetalLB
- ~512MB RAM overhead per node vs ~2GB for kubeadm
- HA mode with embedded etcd (no external etcd needed)
- Ideal for edge/bare-metal, production-viable at this scale

### Core Components

| Component | Tool | Notes |
|---|---|---|
| Container runtime | containerd (bundled) | — |
| CNI | Flannel (bundled) | VXLAN mode |
| Ingress | Traefik v2 (bundled) | Or swap for nginx-ingress |
| Load balancer | MetalLB | Layer 2 mode for bare metal |
| Storage | Longhorn | Distributed block storage across nodes |
| Secrets | External Secrets Operator + Vault / 1Password | TBD |
| Monitoring | Prometheus + Grafana | kube-prometheus-stack helm chart |
| Logging | Loki + Promtail | Lightweight, same Grafana UI |
| GitOps | Flux v2 | Recommend over ArgoCD for simplicity |

---

## Installation Plan

### Phase 1 — Base OS (all 20 nodes)

1. Flash Ubuntu Server 22.04 LTS (x86_64)
2. Configure static IPs, SSH keys, disable swap
3. Set hostnames: `cp-01..03`, `wk-01..17`
4. Harden: `ufw`, `fail2ban`, unattended-upgrades

```bash
# Disable swap (required for k3s)
swapoff -a
sed -i '/ swap / s/^/#/' /etc/fstab
```

### Phase 2 — k3s Install

**Control plane (first node — embedded etcd):**
```bash
curl -sfL https://get.k3s.io | sh -s - server \
  --cluster-init \
  --tls-san <VIP_OR_LB_IP> \
  --node-ip 10.0.1.10
```

**Control plane (nodes 2–3 — join cluster):**
```bash
curl -sfL https://get.k3s.io | sh -s - server \
  --server https://10.0.1.10:6443 \
  --token <NODE_TOKEN> \
  --node-ip 10.0.1.11
```

**Workers (all 17):**
```bash
curl -sfL https://get.k3s.io | K3S_URL=https://10.0.1.10:6443 \
  K3S_TOKEN=<NODE_TOKEN> sh -
```

> Automate with Ansible — single `ansible-playbook site.yml` runs all 20 nodes.

### Phase 3 — Core Services

```bash
# Longhorn (distributed storage)
helm install longhorn longhorn/longhorn \
  --namespace longhorn-system --create-namespace

# Monitoring stack
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace

# MetalLB
helm install metallb metallb/metallb -n metallb-system --create-namespace
# Configure IP pool: 10.0.1.100-120
```

### Phase 4 — GitOps

```bash
# Flux bootstrap (GitHub)
flux bootstrap github \
  --owner=<org> \
  --repository=<gitops-repo> \
  --branch=main \
  --path=./clusters/main
```

All future deployments via Git PR → merge → auto-sync.

---

## Definition of Done

- [ ] All 20 nodes running, healthy in `kubectl get nodes`
- [ ] 3-node control plane HA verified (kill one CP node, cluster stays up)
- [ ] Longhorn storage provisioning working (PVC create/mount/delete)
- [ ] Prometheus scraping all nodes, Grafana dashboards live
- [ ] At least one workload deployed via Flux GitOps
- [ ] Network ingress working (Traefik routing external traffic)
- [ ] Runbook written: how to add/remove a node, how to upgrade k3s

---

## Timeline

| Date | Milestone |
|---|---|
| Mar 3 (Mon) | Cable run, nodes powered on, SSH verified, static IPs set |
| Mar 5 (Wed) | Base OS on all 20 nodes, hostnames set, swap disabled |
| Mar 7 (Fri) | k3s installed, 3-node HA control plane verified |
| **Mar 10 (Mon)** | **✅ Target: full cluster running k3s, all 20 nodes healthy** |
| Mar 12 (Wed) | Core services: Longhorn, MetalLB, Traefik |
| Mar 14 (Fri) | Prometheus + Grafana live, first workload deployed |
| Mar 17 (Mon) | GitOps with Flux, runbook written, floor can self-serve |

---

## Open Questions

1. **CPU model** — confirm via `dmidecode -t processor` on any node
2. **Network** — switch confirmed ✅. VLANs? Uplink speed?
3. **Power** — confirmed ✅. UPS available?
4. **Physical access** — confirmed ✅ (on-site). Remote management for later: PiKVM or WoL + SSH.
5. **Storage goal** — distributed block (Longhorn) vs NFS vs object storage (MinIO)?
6. **Workload** — LLM inference nodes needed now? GPU plans? (see `how_to_add_gpu_inference.md`)
7. **Budget** — cabling, UPS included or separate procurement?

---

## Notes

- OptiPlex 3080 Micro has no IPMI/iDRAC. Remote management: PiKVM per shelf or Wake-on-LAN + SSH.
- CPU-only LLM inference: llama.cpp on i5/i7 nodes yields ~2–8 tok/sec per node. Viable for 7B quantized models.
- Pin k3s version at install time. Do not auto-upgrade cluster nodes.
