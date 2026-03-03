# How to Add GPU Inference to the Cluster

**Version:** 0.0.3 · [Changelog](CHANGELOG.md)

The OptiPlex 3080 Micro has no PCIe slot — it cannot take a discrete GPU. This doc covers the two paths to add GPU inference: external GPU nodes and eGPU via Thunderbolt.

---

## Option A — Dedicated GPU Nodes (recommended)

Add one or more GPU-capable machines to the existing k3s cluster as dedicated inference workers. These run alongside the OptiPlex nodes — the cluster scheduler directs inference workloads to GPU nodes via node selectors.

### Hardware to consider

| Option | GPU | VRAM | Form factor | Est. cost | Notes |
|---|---|---|---|---|---|
| Used workstation (Dell T3660, HP Z4) | RTX 3090 | 24 GB | Tower | $800–1,200 | Best value for VRAM |
| Mini PC (ASUS NUC 14 Pro+) | Arc A770M (integrated) | 16 GB | Mini | $700–900 | Compact, lower power |
| NVIDIA Jetson AGX Orin | Ampere 2048-core | 32 GB unified | Edge | $2,000 | ARM, good for edge inference |
| Used cloud-decom server | A100 40GB / A10G | 40 GB | 1–2U rack | $3,000–8,000 | Fastest option |

**Recommendation for Phase 2:** One used workstation with an RTX 3090 (24GB VRAM) gives you full Llama 3.1 70B at Q4 (~40 GB fits in 24GB VRAM with offload), ~300–500 tok/sec, for ~$1,000–1,200 all-in.

### Add a GPU node to the cluster

1. **Install Ubuntu 22.04 + NVIDIA drivers:**
```bash
# Install NVIDIA drivers
sudo apt install nvidia-driver-535 -y
sudo reboot

# Verify
nvidia-smi
```

2. **Join the node to k3s:**
```bash
curl -sfL https://get.k3s.io | K3S_URL=https://10.0.1.10:6443 \
  K3S_TOKEN=<NODE_TOKEN> sh -
```

3. **Install NVIDIA device plugin:**
```bash
helm repo add nvdp https://nvidia.github.io/k8s-device-plugin
helm install nvdp nvdp/nvidia-device-plugin \
  --namespace nvidia-device-plugin \
  --create-namespace \
  --set failOnInitError=false
```

4. **Label the node:**
```bash
kubectl label node <gpu-node-name> accelerator=nvidia-gpu
kubectl label node <gpu-node-name> node-role=inference
```

5. **Verify GPU is visible to k3s:**
```bash
kubectl describe node <gpu-node-name> | grep nvidia
# Should show: nvidia.com/gpu: 1
```

### Deploy an inference workload

Use `ollama` or `vllm` as the inference server. Example with ollama:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama
  namespace: inference
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ollama
  template:
    metadata:
      labels:
        app: ollama
    spec:
      nodeSelector:
        accelerator: nvidia-gpu        # pin to GPU node
      containers:
        - name: ollama
          image: ollama/ollama:latest
          resources:
            limits:
              nvidia.com/gpu: 1        # request the GPU
            requests:
              memory: "16Gi"
              cpu: "4"
          volumeMounts:
            - name: ollama-models
              mountPath: /root/.ollama
      volumes:
        - name: ollama-models
          hostPath:
            path: /data/ollama-models  # local NVMe on GPU node
            type: DirectoryOrCreate
---
apiVersion: v1
kind: Service
metadata:
  name: ollama
  namespace: inference
spec:
  selector:
    app: ollama
  ports:
    - port: 11434
      targetPort: 11434
```

Pull a model and test:
```bash
kubectl exec -it deploy/ollama -n inference -- ollama pull llama3.1:8b
kubectl exec -it deploy/ollama -n inference -- ollama run llama3.1:8b "Hello"
```

---

## Option B — eGPU via Thunderbolt (limited)

The OptiPlex 3080 Micro has a Thunderbolt 3 port. An eGPU enclosure (Razer Core X, Sonnet Breakaway Box) can attach a full-size GPU.

**Caveats:**
- Thunderbolt 3 = PCIe x4 bandwidth (~16 GB/s) vs native PCIe x16 (~32 GB/s) — ~30–40% inference throughput penalty
- NVIDIA drivers on Linux with eGPU require manual setup (no plug-and-play)
- Not hot-swappable — node must be rebooted to attach/detach
- One eGPU per node maximum

**When to use:** If you already have a GPU and an enclosure, this is a zero-hardware-cost path to test GPU inference on the existing nodes. Not recommended for production.

```bash
# Check Thunderbolt controller
lspci | grep -i thunderbolt

# Authorize the eGPU device (if security level requires it)
echo 1 > /sys/bus/thunderbolt/devices/0-1/authorized
```

---

## GPU Inference Performance (reference)

| GPU | VRAM | Model | Quantization | Tok/sec |
|---|---|---|---|---|
| RTX 3090 | 24 GB | Llama 3.1 70B | Q4_K_M | 25–40 |
| RTX 3090 | 24 GB | Llama 3.1 8B | Q8 | 200–300 |
| RTX 3090 | 24 GB | Mistral 7B | Q4_K_M | 250–350 |
| A100 40GB | 40 GB | Llama 3.1 70B | Q4_K_M | 80–120 |
| A100 40GB | 40 GB | Llama 3.1 8B | FP16 | 600–900 |
| RTX 4090 | 24 GB | Llama 3.1 8B | Q8 | 400–600 |

Compare: CPU-only on i5-10500T → Llama 3.1 8B Q4 = 6–12 tok/sec.
A single RTX 3090 is ~25–40× faster than one OptiPlex node for inference.

---

## Recommended Phase 2 Plan

1. Procure one used workstation with RTX 3090 (~$1,000–1,200)
2. Join it to the existing k3s cluster as a labeled inference node
3. Install NVIDIA device plugin (30 min)
4. Deploy ollama with GPU resource request
5. Move LLM inference workloads from the 3 CPU inference nodes → GPU node
6. Repurpose the 3 freed CPU nodes as general workers

**Result:** ~300–500 tok/sec inference (vs 18–36 tok/sec CPU), 3 more general workers, same cluster management overhead.

---

*See `COMPUTE_CAPACITY.md` for current CPU-only inference estimates.*
