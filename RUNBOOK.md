# Talos Kubernetes Cluster Runbook

A complete guide to bootstrapping a bare-metal Talos Linux Kubernetes cluster from scratch. Written for an Arch-based launcher box (Omarchy or any Linux distro with Docker).

## Overview

- **Launcher box**: any Linux machine with Docker and `talosctl` installed
- **Target nodes**: bare-metal machines with NVMe drives
- **Cluster name**: `iva`
- **Control-plane IP**: `192.168.10.32` (static DHCP lease or pre-assigned)
- **Talos version**: `v1.12.5`
- **Kubernetes version**: `v1.35.2` (bundled with Talos v1.12.5)
- **CNI**: Cilium `v1.19.1`

---

## Current Cluster Status

Last updated: 2026-03-23

### Nodes

| Node | Role | IP | Hardware | Status |
|---|---|---|---|---|
| `talos-zzo-1sj` | control-plane | `192.168.10.32` | Dell OptiPlex 3080 Micro | Ready |
| `talos-shv-9v1` | worker | `192.168.10.11` | Dell OptiPlex 3080 Micro | Ready |
| `talos-d33-vyt` | worker | `192.168.10.43` | Dell OptiPlex 3080 Micro | Powered off |

### Software

| Component | Version |
|---|---|
| Talos Linux | v1.12.5 |
| Kubernetes | v1.35.2 |
| Cilium CNI | v1.19.1 |
| Container runtime | containerd v2.1.6 |
| Kernel | 6.18.15-talos |

### Launcher box

- **OS**: Omarchy (Arch Linux)
- **kubeconfig**: `~/talos-iva/kubeconfig` (also merged into `~/.kube/config`)
- **talosconfig**: `~/talos-iva/talosconfig`
- **kubectl context**: `admin@iva`

---

## Prerequisites

### On the launcher box

**Docker** must be installed and running:
```bash
docker info
```

**`talosctl`** — install if not present:
```bash
curl -sL https://talos.dev/install | sh
# verify
talosctl version --client
```

**`kubectl`** — install if not present:
```bash
# Arch/Omarchy
sudo pacman -S kubectl
# or via mise/asdf/direct binary
```

**`cilium` CLI** — install if not present:
```bash
CILIUM_CLI_VERSION=$(curl -s https://raw.githubusercontent.com/cilium/cilium-cli/main/stable.txt)
curl -L --remote-name-all \
  "https://github.com/cilium/cilium-cli/releases/download/${CILIUM_CLI_VERSION}/cilium-linux-amd64.tar.gz"
tar -C ~/.local/bin -xzf cilium-linux-amd64.tar.gz
rm cilium-linux-amd64.tar.gz
cilium version --client
```

**`zstd`** — for decompressing images:
```bash
# Arch/Omarchy
sudo pacman -S zstd
```

### Hardware notes (Dell OptiPlex 3080 Micro)

Before booting any node for the first time, configure the BIOS:

1. Power on the machine
2. Press **F2** repeatedly at the Dell splash screen to enter BIOS setup
3. Navigate to **Storage → SATA Operation** and set it to **AHCI** (from `RAID On` / `Intel RST`)
   - Without this, the NVMe is invisible to Linux
4. Navigate to **Boot Sequence** and ensure **HDD** (the NVMe) is first in the boot order
5. Disable **Secure Boot**
6. Confirm **Boot Mode** is set to **UEFI**
7. Save changes and restart (F10 or the Save & Exit option)

---

## Part 1 — Generate Cluster Config

All config generation happens on the launcher box. Create a working directory:

```bash
mkdir -p ~/talos-iva
```

Generate the cluster PKI, tokens, and machine configs:

```bash
talosctl gen config iva https://192.168.10.32:6443 \
  --install-disk /dev/nvme0n1 \
  --output-dir ~/talos-iva \
  --with-examples=false \
  --with-docs=false
```

This produces three files:

| File | Purpose |
|------|---------|
| `controlplane.yaml` | Machine config for the control-plane node |
| `worker.yaml` | Machine config for worker nodes |
| `talosconfig` | Client credentials for `talosctl` |

Verify the key values:
```bash
grep -E 'endpoint|disk:|clusterName' ~/talos-iva/controlplane.yaml
```

---

## Part 2 — Build the Control-Plane Image

Use the official Talos imager container to build a raw disk image with the control-plane config embedded. This means the node configures itself on first boot — no network apply step needed.

```bash
docker run --rm \
  --privileged \
  -v /dev:/dev \
  -v ~/talos-iva:/out \
  ghcr.io/siderolabs/imager:v1.12.5 \
    metal \
    --arch amd64 \
    --output /out \
    --output-kind image \
    --embedded-config-path /out/controlplane.yaml
```

The imager uses loop devices internally — the `--privileged` and `-v /dev:/dev` flags are required for this to work.

Output: `~/talos-iva/metal-amd64.raw.zst` (compressed, ~190 MB)

Decompress before flashing:
```bash
zstd -d ~/talos-iva/metal-amd64.raw.zst -o ~/talos-iva/metal-amd64.raw
# result: ~/talos-iva/metal-amd64.raw (~4.2 GB)
```

---

## Part 3 — Flash the Control-Plane Node

Connect the target NVMe to the launcher box (via USB enclosure or direct connection).

Identify the device:
```bash
lsblk -o NAME,SIZE,TYPE,TRAN,MODEL
# look for TRAN=usb or the correct NVMe — e.g. /dev/sdb
```

**This is destructive. Double-check the device before running.**

```bash
sudo dd if=~/talos-iva/metal-amd64.raw of=/dev/sdX bs=4M conv=fsync status=progress
sync
```

Replace `/dev/sdX` with the actual device. `dd` will show progress in bytes/s. For a 4.2 GB image over USB 3, expect 1–5 minutes.

---

## Part 4 — Boot and Bootstrap the Control-Plane Node

1. Reinstall the NVMe into the target machine
2. Ensure the machine will boot from the NVMe (check BIOS boot order)
3. Power on — Talos will boot and self-configure from the embedded config
4. Ensure `192.168.10.32` is assigned to this machine (static DHCP lease by MAC, or pre-configure on your switch/router)

### Verify the node is reachable

Point `talosctl` at the node:
```bash
talosctl config endpoint 192.168.10.32 --talosconfig ~/talos-iva/talosconfig
talosctl config node 192.168.10.32 --talosconfig ~/talos-iva/talosconfig
```

Check connectivity:
```bash
talosctl --talosconfig ~/talos-iva/talosconfig version
```

Expected output: both Client and Server show the same `Tag: v1.12.5`.

If the server returns `maintenance mode` — the embedded config wasn't picked up. See Troubleshooting below.

### Bootstrap etcd

Run this **once and only once** on a fresh cluster. Running it again on an existing cluster is a no-op.

```bash
talosctl --talosconfig ~/talos-iva/talosconfig bootstrap
```

Wait ~2 minutes for etcd and the Kubernetes API server to come up.

### Retrieve kubeconfig

```bash
talosctl --talosconfig ~/talos-iva/talosconfig \
  kubeconfig ~/talos-iva/kubeconfig --force
```

### Configure kubectl on the launcher box

```bash
mkdir -p ~/.kube

# If you have no existing ~/.kube/config:
cp ~/talos-iva/kubeconfig ~/.kube/config
chmod 600 ~/.kube/config

# If you already have a ~/.kube/config and want to merge:
KUBECONFIG=~/.kube/config:~/talos-iva/kubeconfig \
  kubectl config view --flatten > /tmp/kubeconfig-merged
mv /tmp/kubeconfig-merged ~/.kube/config
chmod 600 ~/.kube/config
```

Set the context:
```bash
kubectl config use-context admin@iva
kubectl get nodes
```

The node will show `NotReady` until CNI is installed — that is expected.

---

## Part 5 — Install Cilium CNI

The node stays `NotReady` until a CNI plugin handles pod networking. We use Cilium.

### Important: Talos-specific flags

Talos has a hardened security model that blocks Cilium's default deployment. The flags below are required:

- `cgroup.autoMount.enabled=false` + `cgroup.hostRoot=/sys/fs/cgroup` — Talos manages cgroups itself
- `securityContext.capabilities.*` — explicit capability grants required since Talos blocks ambient caps
- `k8sServicePort=6443` — point at the real API server port, not KubePrism (7445), which is only reachable from the node's loopback, not from pods

```bash
cilium install \
  --set ipam.mode=kubernetes \
  --set kubeProxyReplacement=false \
  --set securityContext.capabilities.ciliumAgent="{CHOWN,KILL,NET_ADMIN,NET_RAW,IPC_LOCK,SYS_ADMIN,SYS_RESOURCE,DAC_OVERRIDE,FOWNER,SETGID,SETUID}" \
  --set securityContext.capabilities.cleanCiliumState="{NET_ADMIN,SYS_ADMIN,SYS_RESOURCE}" \
  --set cgroup.autoMount.enabled=false \
  --set cgroup.hostRoot=/sys/fs/cgroup \
  --set k8sServiceHost=192.168.10.32 \
  --set k8sServicePort=6443
```

Wait for Cilium to come up (~2 minutes):
```bash
cilium status
kubectl get nodes
# node should now show Ready
```

---

## Part 6 — Add Worker Nodes

The worker image is built once and can be flashed to any number of identical worker machines.

### Build the worker image

```bash
docker run --rm \
  --privileged \
  -v /dev:/dev \
  -v ~/talos-iva:/out \
  ghcr.io/siderolabs/imager:v1.12.5 \
    metal \
    --arch amd64 \
    --output /out \
    --output-kind image \
    --embedded-config-path /out/worker.yaml
```

> Note: the imager writes to `/out/metal-amd64.raw.zst`. If you have a previous image there, remove it first:
> ```bash
> rm -f ~/talos-iva/metal-amd64.raw ~/talos-iva/metal-amd64.raw.zst
> ```

Decompress:
```bash
zstd -d ~/talos-iva/metal-amd64.raw.zst -o ~/talos-iva/metal-amd64.raw
```

### Flash each worker

Connect the worker NVMe to the launcher box, identify the device with `lsblk`, then:

```bash
# DESTRUCTIVE — replace /dev/sdX with the correct device
sudo dd if=~/talos-iva/metal-amd64.raw of=/dev/sdX bs=4M conv=fsync status=progress
sync
```

Reinstall the NVMe and boot the worker. It will automatically join the cluster using the token embedded in `worker.yaml` — no manual apply step needed.

### Verify the worker joined

Once the machine is up and has an IP (check your DHCP leases or the machine's console):

```bash
kubectl get nodes
# new node should appear, initially NotReady then Ready within ~60s
```

You can add as many workers as needed by repeating the flash-and-boot steps. The same image works for all identical hardware.

---

## File Reference

```
~/talos-iva/
├── controlplane.yaml   # Control-plane machine config (contains cluster PKI — keep safe)
├── worker.yaml         # Worker machine config (contains join token — keep safe)
├── talosconfig         # talosctl client credentials
├── kubeconfig          # kubectl credentials
├── metal-amd64.raw     # Decompressed disk image (safe to delete after flashing)
└── metal-amd64.raw.zst # Compressed image from imager (safe to delete after flashing)
```

> `controlplane.yaml` and `worker.yaml` contain private keys and tokens. Do not commit them to version control or share them publicly.

---

## Troubleshooting

### Node boots into maintenance mode (TLS cert says `maintenance-service.talos.dev`)

The embedded config wasn't loaded. Causes:
- Image was built without `--embedded-config-path`
- The machine booted from a different disk

Re-build the image with `--embedded-config-path` and re-flash.

### `no /dev/nvme0n1` on boot

The NVMe is not visible to the OS. On Dell OptiPlex 3080 Micro (and many Intel platforms):

1. Power on and press **F2** to enter BIOS
2. Go to **Storage → SATA Operation** and set to **AHCI** (from `RAID On` / `Intel RST`)
3. Save and restart

### Cilium pod stuck in `Init:Error` with `can't apply capabilities`

Cilium was installed without the Talos-specific security context flags. Uninstall and reinstall with the full set of `--set` flags from Part 5.

### Cilium `config` init container: `connection refused` on port 7445

Port 7445 (KubePrism) is only reachable from the node loopback, not from pods. Use `--set k8sServicePort=6443` when installing Cilium.

### `dd` appears stuck

`dd` with `status=progress` prints a live counter. If you see no output at all, it may be waiting for sudo. If the counter is frozen, the drive may be slow — a 4.2 GB image can take 5–10 minutes on a slow USB 2 enclosure. Do not interrupt it.

### Worker doesn't appear in `kubectl get nodes`

- Check the machine actually booted (console output)
- Verify DHCP gave it an IP (check your router)
- Check the worker image was built with `worker.yaml`, not `controlplane.yaml`
- Run `talosctl --talosconfig ~/talos-iva/talosconfig -e <worker-ip> -n <worker-ip> dmesg` to see what's happening on the node
