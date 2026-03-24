# OS Install Strategy

Flash Talos Linux raw disk images to the NVMe of each Dell OptiPlex 3080 Micro. Each image has its machine config embedded, so the node self-configures on first boot with no manual intervention.

## How it works

1. **Build the image** — Use the Talos imager container to produce a raw disk image with the node's machine config baked in.
2. **Decompress** — The imager outputs a compressed image; decompress it before flashing.
3. **Flash via `dd`** — Pull the NVMe from the node, connect it through a USB enclosure, and write the image with `dd`.
4. **Reinstall and boot** — Put the NVMe back in the node and power on. Talos picks up the embedded config and joins the cluster automatically.

## BIOS prerequisites (Dell OptiPlex 3080 Micro)

Before first boot, set the following in BIOS:

- **SATA mode** — set to AHCI (not RAID)
- **Boot mode** — UEFI
- **Secure Boot** — Disabled

## Comparison with the previous Ubuntu approach

| | Ubuntu (manual/PXE) | Talos (raw image) |
|---|---|---|
| Install method | USB installer wizard or PXE + autoinstall | `dd` a raw image to NVMe |
| Post-install config | SSH + Ansible or manual setup | None — config is embedded in the image |
| Reproducibility | Requires automation tooling (Ansible, preseed) | Deterministic by construction |
| Re-image a node | Re-run installer or PXE boot | Flash a new image, boot |
| Time per node | ~10-15 min (installer) | ~2-3 min (`dd` + reassemble) |

The Ubuntu approach required either walking through the installer on each node or standing up a PXE server with autoinstall configs, followed by Ansible for post-install configuration. Talos eliminates all of that: the image is the entire OS plus config, and no SSH or post-install tooling exists on the node.

## Full procedure

See [RUNBOOK.md](RUNBOOK.md) for the step-by-step instructions (image build, flash, BIOS setup, cluster bootstrap).
