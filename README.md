# GPU Delegater based on KubeAI

This repository stores the `An Improved Design of NVIDIA GPU Dynamic LLM Task Scheduling Architecture Based on KubeAI` paper source code.

## Environment

### GPU Delegater

- Ubuntu 22.04.3 LTS
- Python 3.10.12

### Kubernetes

The Kubernetes cluster has one master node and two worker nodes.

#### Master Node

- Hardware:
  - CPU: Intel Core i7 7700 4C/8T
  - Memory: 32GB
  - Disk: 2.5" 1TB SATA3 SSD
- Software:
  - Ubuntu 22.04.3 LTS
  - Kubernetes 1.31.3
  - containerd 1.7.24

#### Worker Node 1

- Hardware:
  - CPU: Intel Core i7 7700 4C/8T
  - Memory: 32GB DDR4
  - Disk: 2.5" 1TB SATA3 SSD
  - GPU: 1 x NVIDIA GeForce RTX 3070 Ti 8GB
- Software:
  - Ubuntu 22.04.3 LTS
  - Kubernetes 1.31.3
  - containerd 1.7.24
  - NVIDIA Driver 550.54.15
  - CUDA 12.4
  - cuDNN 9.1.70
  - NVIDIA Container Toolkit 1.17.2
  - NVIDIA GPU Operator 24.9.1
  - KubeAI 0.11.0

#### Worker Node 2

- Hardware:
  - CPU: Intel Core i7 13700 16C/24T
  - Memory: 128GB DDR4
  - Disk: 2.5" 1TB SATA3 SSD
  - GPU: 2 x NVIDIA GeForce RTX 4070 12GB
- Software:
  - Ubuntu 22.04.3 LTS
  - Kubernetes 1.31.3
  - containerd 1.7.24
  - NVIDIA Driver 535.129.03
  - CUDA 12.2
  - cuDNN 9.1.70
  - NVIDIA Container Toolkit 1.17.2
  - NVIDIA GPU Operator 24.9.1
  - KubeAI 0.11.0
