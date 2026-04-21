# Multi-Tenant OpenClaw with ArgoCD and SOPS

!!! warning "Work in Progress"
    This document is actively being written. The architecture is proposed but not yet implemented on our cluster.

This design runs one isolated [OpenClaw](https://github.com/anthropics/openclaw) instance per tenant on our bare-metal Talos cluster, stores configuration in Git, and keeps secrets encrypted with [SOPS](https://github.com/getsops/sops) so [ArgoCD](https://argo-cd.readthedocs.io/en/stable/) can deploy them safely during sync. It is meant for backend engineers who want a predictable "edit YAML, open PR, ship" workflow without having to think like platform engineers.

This is the secrets management and multi-tenancy strategy referenced in our [public-beta-1.0.0 access model](next-steps.md#access-model), where each AI floor citizen brings their own API token and gets an isolated OpenClaw environment deployed via [NemoClaw](https://github.com/NVIDIA/NemoClaw).

---

## Why This Setup

The core idea is simple: each tenant gets its own namespace, its own OpenClaw deployment, its own persistent storage, and its own secrets. That gives clean tenant boundaries without asking us to build a complicated shared control plane first. For more on Kubernetes multi-tenancy patterns, see [Red Hat's multi-tenant SaaS guide](https://developers.redhat.com/articles/2022/08/12/implement-multitenant-saas-kubernetes).

ArgoCD is the delivery engine: it watches this repo, renders the tenant manifests, and applies them to the cluster. SOPS handles secret encryption so sensitive values (like API keys from our [BYOT model](next-steps.md#access-model)) can live in Git without being stored in plaintext. See [ArgoCD multi-tenancy patterns](https://oneuptime.com/blog/post/2026-01-27-argocd-multi-tenancy/view) for background on this approach.

---

## How It Works

Each tenant lives in its own directory in Git, with normal Kubernetes YAML for things like the Deployment, Service, PVC, and NetworkPolicy, plus one encrypted `secret.sops.yaml` file for credentials. ArgoCD reads that directory, decrypts the secret during manifest generation, and deploys the resulting resources into that tenant's namespace. For a walkthrough of this pattern, see [Red Hat's guide to GitOps and secret management with ArgoCD and SOPS](https://www.redhat.com/en/blog/a-guide-to-gitops-and-secret-management-with-argocd-operator-and-sops).

At runtime, OpenClaw runs as a normal Kubernetes workload — one instance per tenant. The pod reads tenant-specific secrets from Kubernetes Secrets and keeps its local working state on a PVC so tenants do not share filesystems or config.

---

## Secret Model

The GPG model is the most important part to understand. SOPS encrypts a file to one or more **public keys**, and any matching **private key** can decrypt it. That means one tenant secret can be encrypted to both the tenant admin's public key and a separate ArgoCD deployment public key at the same time. See the [SOPS documentation](https://github.com/getsops/sops) for full details on how this works.

This is what "bring your own key" means in practice:

- A developer generates a GPG keypair locally
- They share only the **public key** and fingerprint with the platform team
- Their **private key** stays on their machine and is never uploaded to the cluster
- ArgoCD uses a separate deployment private key that belongs to the platform, not to any individual engineer (see [this walkthrough on ArgoCD + SOPS key management](https://juanjo.garciaamaya.com/posts/k8s/k8s-addons/))

That split is what keeps the model safe. Backend engineers can still decrypt and edit their own tenant secrets locally, while ArgoCD can still deploy them automatically, but nobody needs to hand over a personal private key.

---

## Developer Workflow

From a backend engineer's point of view, the workflow is intentionally boring:

1. Copy the tenant template directory
2. Update the non-secret config in YAML
3. Edit the encrypted secret with `sops` using your own GPG key
4. Open a pull request
5. Merge, and let ArgoCD sync it

See the [ArgoCD secret management docs](https://argo-cd.readthedocs.io/en/stable/operator-manual/secret-management/) for how ArgoCD handles decryption during sync.

The important part is what developers do **not** do:

- They do not commit plaintext API keys to Git
- They do not upload personal private keys to the platform
- They do not deploy directly from a laptop into production

---

## Security Boundaries

GPG helps by separating public and private keys, but it does not magically make private keys unstealable. If ArgoCD is going to decrypt secrets in-cluster, then some private key must exist in or be reachable by ArgoCD, and that key must be treated as sensitive infrastructure material.

So the real protection comes from architecture and process:

- Personal user private keys never enter the cluster
- Only a dedicated ArgoCD deployment key is stored for in-cluster decryption
- Tenant workloads are isolated by namespace and fenced with quotas and [NetworkPolicies](https://kubernetes.io/docs/concepts/services-networking/network-policies/) enforced by our [Cilium](https://docs.cilium.io/en/stable/security/policy/) CNI
- Git remains the source of truth, and changes flow through review instead of ad hoc cluster edits

This gives a setup that is simple enough for backend teams to use, while still preserving the right security boundaries for multi-tenant OpenClaw on our cluster.

---

## References

| Topic | Link |
|-------|------|
| SOPS — secrets encryption tool | [github.com/getsops/sops](https://github.com/getsops/sops) |
| ArgoCD — GitOps continuous delivery | [argo-cd.readthedocs.io](https://argo-cd.readthedocs.io/en/stable/) |
| ArgoCD secret management | [argo-cd.readthedocs.io/secret-management](https://argo-cd.readthedocs.io/en/stable/operator-manual/secret-management/) |
| ArgoCD + SOPS guide (Red Hat) | [redhat.com/blog](https://www.redhat.com/en/blog/a-guide-to-gitops-and-secret-management-with-argocd-operator-and-sops) |
| Multi-tenant SaaS on Kubernetes (Red Hat) | [developers.redhat.com](https://developers.redhat.com/articles/2022/08/12/implement-multitenant-saas-kubernetes) |
| ArgoCD multi-tenancy patterns | [oneuptime.com/blog](https://oneuptime.com/blog/post/2026-01-27-argocd-multi-tenancy/view) |
| ArgoCD + SOPS key management walkthrough | [juanjo.garciaamaya.com](https://juanjo.garciaamaya.com/posts/k8s/k8s-addons/) |
| Multi-tenant ArgoCD with Application Projects | [codefresh.io/blog](https://codefresh.io/blog/multi-tenant-argocd-with-application-projects/) |
| Kubernetes NetworkPolicies | [kubernetes.io/docs](https://kubernetes.io/docs/concepts/services-networking/network-policies/) |
| Cilium network policy | [docs.cilium.io](https://docs.cilium.io/en/stable/security/policy/) |
| OpenClaw | [github.com/anthropics/openclaw](https://github.com/anthropics/openclaw) |
| NemoClaw | [github.com/NVIDIA/NemoClaw](https://github.com/NVIDIA/NemoClaw) |
