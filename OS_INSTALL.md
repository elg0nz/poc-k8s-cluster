# OS Install Strategy

Bare minimum Ubuntu Server install on 20 Dell OptiPlex 3080 Micro nodes. Each box gets a default password. No post-install configuration (handled separately).

## Assumptions

- 20 nodes total
- Download rate: ~35 MB/s
- Ubuntu Server ISO: ~2 GB
- Goal: bootable Ubuntu with SSH access and a default password

## Option A: Manual USB Install (4 nodes at a time)

Plug in USB, walk through the installer, repeat.

| Step                          | Time        |
|-------------------------------|-------------|
| Boot USB + installer wizard   | ~10-15 min  |
| OS writes to disk             | ~8-10 min   |
| **Per batch (4 nodes)**       | **~20-25 min** |
| **5 batches (20 nodes)**      | **~2 hours**   |

**Total: ~2 hours hands-on**

## Option B: PXE + Ansible (all 20 nodes in parallel)

PXE server serves the installer over the network. Autoinstall/preseed handles unattended config (hostname, default password, SSH). All nodes boot and install simultaneously.

| Step                                  | Time           |
|---------------------------------------|----------------|
| One-time setup (PXE server, autoinstall config) | ~2-4 hours |
| PXE boot + unattended install (20 nodes parallel) | ~10-15 min |
| **Total after setup**                 | **~10-15 min** |

**Total: ~2-4 hours upfront, then ~15 min per deployment**

## Comparison

| | Manual (4 at a time) | PXE + Ansible |
|---|---|---|
| First deployment | ~2 hours | ~2-4 hours |
| Each re-deployment | ~2 hours | ~15 min |
| Breaks even after | - | 2-3 re-deployments |
| Reproducible | No | Yes |
| Hands-on required | Every node | Power on only |

## Recommendation

For a one-time install, manual at 4-at-a-time is fine (~2 hours). PXE + Ansible pays off if we expect to re-image nodes for OS upgrades, config drift, or testing fresh installs.
