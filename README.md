# poc-k8s-cluster

Bare-metal Kubernetes cluster on Talos Linux v1.12.5 with Dell OptiPlex 3080 Micro nodes.

**Current version:** alpha-0.0.2 | **Next:** alpha-0.1.0

**[Browse the docs site](https://elg0nz.github.io/poc-k8s-cluster/)**

## Documentation

Docs are published to **GitHub Pages** automatically on push to `main`.

This project uses [MkDocs](https://www.mkdocs.org/) with the [Material](https://squidfundamentals.com/mkdocs-material/) theme.

### Setup

GitHub Pages must be enabled once in the repo settings:

1. Go to **Settings > Pages**
2. Under **Source**, select **GitHub Actions**
3. Push to `main` — the workflow at `.github/workflows/deploy-docs.yml` builds and deploys the site

### Browse locally

```bash
pip install mkdocs-material
mkdocs serve
```

Then open [http://localhost:8000](http://localhost:8000).

## Contents

All documentation lives in `docs/`:

| Document | Description |
|---|---|
| [Home](docs/index.md) | Landing page and version overview |
| [Cluster Plan](docs/plan.md) | Architecture, network topology, software stack |
| [Runbook](docs/runbook.md) | Bootstrapping and operating the Talos cluster |
| [Compute Capacity](docs/compute-capacity.md) | CPU, RAM, storage, workload estimates |
| [Inference Capacity](docs/inference-capacity.md) | LLM inference speed across hardware tiers |
| [GPU Inference](docs/gpu-inference.md) | Adding GPU nodes for inference |
| [OS Install](docs/os-install.md) | Talos raw-image flashing strategy |
| [Next Steps](docs/next-steps.md) | Roadmap for alpha-0.1.0 and public-beta-1.0.0 |
| [Changelog](docs/changelog.md) | Version history |
