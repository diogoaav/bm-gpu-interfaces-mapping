# GPU to RoCE Interface Mapping Guide

This guide provides comprehensive methods to check GPU to RoCE (RDMA over Converged Ethernet) interface mapping on your system, including both single-node analysis and multi-node cluster communication mapping.

## 🛠️ Available Tools

| Tool | Purpose | Output Example |
|------|---------|----------------|
| `intra_node_gpu_mapping.py` | Single-node GPU-RoCE analysis | [`intra_node_output_example.txt`](intra_node_output_example.txt) |
| `inter_node_gpu_mapping.py` | Multi-node cluster analysis | [`inter_node_output_example.txt`](inter_node_output_example.txt) |

## 🚀 Quick Start

```bash
# Intra-node (single-node) analysis
python3 intra_node_gpu_mapping.py

# Inter-node (multi-node) analysis - specify remote node hostname/IP
python3 inter_node_gpu_mapping.py <remote_node>

# Examples:
python3 inter_node_gpu_mapping.py am4g2r32bm1
python3 inter_node_gpu_mapping.py 10.45.170.79
python3 inter_node_gpu_mapping.py node2.cluster.local

# Test SSH connectivity first (optional)
python3 inter_node_gpu_mapping.py <remote_node> --test-ssh
```

## Quick Reference Commands

### 1. Basic GPU Topology
```bash
# Show GPU topology matrix with NIC connections
nvidia-smi topo -m

# Show GPU details with PCI information
nvidia-smi --query-gpu=index,name,pci.bus_id,pci.domain,pci.bus,pci.device --format=csv,noheader
```

### 2. RDMA Device Mapping
```bash
# Map RDMA devices to network interfaces  
ibdev2netdev

# Show detailed RDMA device information
ibv_devinfo

# Check RoCE capabilities for specific device
ibv_devinfo -d mlx5_0
```

### 3. Network Interface Information
```bash
# List all network interfaces
ip link show

# Show interfaces with RDMA capabilities
ls /sys/class/infiniband/

# Check interface statistics
cat /proc/net/dev
```

### 4. NUMA Affinity Checking
```bash
# Check GPU NUMA node affinity
for i in {0..7}; do 
  echo -n "GPU$i: "
  cat /sys/class/drm/card$i/device/numa_node 2>/dev/null || echo "N/A"
done

# Check NIC NUMA affinity
for nic in /sys/class/net/enp*; do
  echo "$(basename $nic): $(cat $nic/device/numa_node 2>/dev/null || echo N/A)"
done
```

## Understanding the Topology Matrix

From your system's `nvidia-smi topo -m` output:

### Connection Types (Performance Order):
- **NV#**: NVLink connections (best for GPU-GPU)
- **PIX**: Single PCIe bridge (excellent for GPU-NIC)
- **PXB**: Multiple PCIe bridges (good)
- **PHB**: PCIe Host Bridge (fair)
- **NODE**: Cross-NUMA node (poor)
- **SYS**: Cross-NUMA with SMP interconnect (poorest)

### Your System Configuration:
Based on the topology analysis, your system has:
- 8 GPUs (GPU0-GPU7) with NVLink interconnects  
- 12 NICs (NIC0-NIC11) mapped to mlx5_0 through mlx5_11
- **ALL interfaces are 400G capable** (confirmed via ethtool)
- Mixed N/S (front-end) and E/W (backend) interface architecture

**INTERFACE CLASSIFICATION**:
- **N/S (North/South)**: bond0 = 4x100G bonded = 400G aggregate for front-end traffic
  - Members: mlx5_1, mlx5_2, mlx5_7, mlx5_8
- **E/W (East/West)**: Individual 400G RoCE interfaces for inter-node GPU communication  
  - Members: mlx5_0, mlx5_3, mlx5_4, mlx5_5, mlx5_6, mlx5_9, mlx5_10, mlx5_11

**COMPLETE NIC MAPPING**:
```
NIC0  -> mlx5_0  -> enp26s0np0     (400G E/W)
NIC1  -> mlx5_1  -> bond0          (100G* N/S, bonded)  
NIC2  -> mlx5_2  -> bond0          (100G* N/S, bonded)
NIC3  -> mlx5_3  -> enp60s0np0     (400G E/W)
NIC4  -> mlx5_4  -> enp77s0np0     (400G E/W)
NIC5  -> mlx5_5  -> enp94s0np0     (400G E/W, DOWN)
NIC6  -> mlx5_6  -> enp156s0np0    (400G E/W)
NIC7  -> mlx5_7  -> bond0          (100G* N/S, bonded)
NIC8  -> mlx5_8  -> bond0          (100G* N/S, bonded)  
NIC9  -> mlx5_9  -> enp188s0np0    (400G E/W)
NIC10 -> mlx5_10 -> enp204s0np0    (400G E/W)
NIC11 -> mlx5_11 -> enp220s0np0    (400G E/W)
```
*bond0 members contribute 100G each to 400G total aggregate

## How to Read the GPU-RoCE Mapping

### Step 1: Understand the Topology Matrix
The `nvidia-smi topo -m` output shows connection quality between GPUs and NICs:
- **PIX** = Optimal (single PCIe bridge)
- **SYS** = Poor (cross-NUMA with overhead)

### Step 2: Map NIC Numbers to RDMA Devices
From the NIC Legend:
- NIC0 → mlx5_0 → enp26s0np0
- NIC1 → mlx5_1 → bond0 (RoCE-capable!)
- NIC2 → mlx5_2 → bond0 (RoCE-capable!)
- NIC3 → mlx5_3 → enp60s0np0
- etc.

### Step 3: Identify Optimal GPU-RoCE Pairings
**KEY INSIGHT**: bond0 is made of 4 RoCE-capable interfaces, NOT regular Ethernet!

From your topology analysis:
- **GPU0** has PIX (optimal) connections to:
  - mlx5_0 (enp26s0np0) - Individual RoCE interface
  - mlx5_1 (bond0) - Bonded RoCE interfaces  
  - mlx5_2 (bond0) - Bonded RoCE interfaces

- **GPU1** has PIX connection to:
  - mlx5_3 (enp60s0np0) - Individual RoCE interface

- **GPU2** has PIX connection to:
  - mlx5_4 (enp77s0np0) - Individual RoCE interface

- **GPU3** has PIX connection to:
  - mlx5_5 (enp94s0np0) - Individual RoCE interface (currently DOWN)

- **GPU4** has PIX connections to:
  - mlx5_6 (enp156s0np0) - Individual RoCE interface
  - mlx5_7 (bond0) - Bonded RoCE interfaces
  - mlx5_8 (bond0) - Bonded RoCE interfaces

- **GPU5** has PIX connection to:
  - mlx5_9 (enp188s0np0) - Individual RoCE interface

- **GPU6** has PIX connection to:
  - mlx5_10 (enp204s0np0) - Individual RoCE interface

- **GPU7** has PIX connection to:
  - mlx5_11 (enp220s0np0) - Individual RoCE interface

## Using the Provided Tools

### 1. Intra-Node (Single-Node) GPU-RoCE Analysis
```bash
# Complete single-node analysis with N/S vs E/W classification
python3 intra_node_gpu_mapping.py

# Shows:
# - Complete NIC mapping table with GPU assignments
# - N/S (front-end) vs E/W (backend) interface classification  
# - Optimal GPU-RoCE pairings for different use cases
# - NCCL configuration examples
# - See example output: intra_node_output_example.txt
```

### 2. Inter-Node (Multi-Node) GPU Communication Analysis
```bash
# Complete inter-node GPU-to-GPU communication mapping
python3 inter_node_gpu_mapping.py <remote_node>

# Examples:
python3 inter_node_gpu_mapping.py am4g2r32bm1          # By hostname
python3 inter_node_gpu_mapping.py 10.45.170.79        # By IP address
python3 inter_node_gpu_mapping.py node2 --test-ssh    # Test SSH first

# Shows:
# - Inter-node GPU communication paths (Node1 GPU ↔ Node2 GPU)
# - Remote node connectivity via SSH
# - Distributed training configuration with NCCL settings
# - Bandwidth analysis and connectivity testing commands
# - Status indicators for working/failed connections
# - See example output: inter_node_output_example.txt
```

## Best Practices for GPU-RoCE Mapping

### 1. Performance Considerations
- **Use PIX connections**: Minimize PCIe hops between GPU and NIC
- **Consider NUMA affinity**: Match GPU and NIC on same NUMA node
- **Load balancing**: Distribute traffic across multiple RoCE interfaces

### 2. Application Configuration

#### Single-Node Training:
```bash
# Use E/W interfaces for maximum bandwidth
export CUDA_VISIBLE_DEVICES=0,1,2,4,5,6,7  # Skip GPU3 (interface DOWN)
export NCCL_IB_HCA=mlx5_0,mlx5_3,mlx5_4,mlx5_6,mlx5_9,mlx5_10,mlx5_11
```

#### Multi-Node Distributed Training:
```bash
# Node 1 configuration:
export CUDA_VISIBLE_DEVICES=0,1,2,4,5,6,7
export NCCL_IB_HCA=mlx5_0,mlx5_3,mlx5_4,mlx5_6,mlx5_9,mlx5_10,mlx5_11
export NCCL_SOCKET_IFNAME=bond0
export MASTER_ADDR=10.45.170.76
export WORLD_SIZE=14  # Total working GPUs across nodes
export RANK=0

# Node 2 configuration:
export CUDA_VISIBLE_DEVICES=0,1,2,4,5,6,7
export NCCL_IB_HCA=mlx5_0,mlx5_3,mlx5_4,mlx5_6,mlx5_9,mlx5_10,mlx5_11
export NCCL_SOCKET_IFNAME=bond0
export MASTER_ADDR=10.45.170.76
export WORLD_SIZE=14
export RANK=7
```

#### Front-End Serving (N/S Traffic):
```bash
# Use bond0 for high-bandwidth front-end traffic
export CUDA_VISIBLE_DEVICES=0,4  # GPUs with bond0 access
export NCCL_IB_HCA=mlx5_1,mlx5_2,mlx5_7,mlx5_8  # Full 400G bond
```

### 3. Monitoring and Validation
```bash
# Monitor RoCE interface utilization
ibstat

# Check interface counters
cat /sys/class/infiniband/mlx5_0/ports/1/counters/*

# Monitor GPU memory and utilization
nvidia-smi -l 1
```

## Troubleshooting

### Common Issues:
1. **NIC shows "Down"**: Check physical connections and interface configuration
2. **No RoCE capabilities**: Verify driver installation and firmware
3. **Poor performance**: Check for SYS/NODE connections instead of PIX

### Diagnostic Commands:
```bash
# Check RDMA subsystem
systemctl status rdma-hw
systemctl status rdma-load-modules

# Verify RoCE is enabled
ibv_devinfo -d mlx5_0 | grep transport

# Test connectivity
ibping -S -C mlx5_0    # Server side
ibping -c 10 -C mlx5_1 <server_ip>  # Client side
```

## Multi-Node Cluster Configuration

### Inter-Node GPU Communication Paths
This toolkit supports mapping GPU-to-GPU communication paths between cluster nodes. The inter-node analysis tools automatically discover and map:

- **Direct E/W connections** between corresponding GPUs on different nodes
- **SSH-based remote node discovery** for automatic topology mapping
- **Bandwidth analysis** showing total inter-node communication capacity
- **NCCL configuration** for distributed training across nodes

### Example Multi-Node Setup
```bash
# Analyze inter-node connectivity (specify remote node)
python3 inter_node_gpu_mapping.py am4g2r32bm1

# Test connectivity first if needed
python3 inter_node_gpu_mapping.py 10.45.170.79 --test-ssh
```

**Typical Output:**
```
🟢 Node1 GPU0 - NIC0 - mlx5_0 (enp26s0np0) >>>>> Node2 GPU0 - NIC0 - mlx5_0 (enp26s0np0)
🟢 Node1 GPU1 - NIC3 - mlx5_3 (enp60s0np0) >>>>> Node2 GPU1 - NIC3 - mlx5_3 (enp60s0np0)
...
🔴 Node1 GPU3 - NIC5 - mlx5_5 (enp94s0np0) >>>>> Node2 GPU3 - NIC5 - mlx5_5 (enp94s0np0)
```

### Performance Characteristics
- **Working GPU pairs**: 7/8 (one interface DOWN on local node)
- **Total inter-node bandwidth**: 2.8TB/s (7 × 400G bidirectional)
- **Protocol**: RoCE v2 over 400G Ethernet
- **Network separation**: E/W (GPU traffic) vs N/S (control/management)

## Hardware-Specific Notes

Your system appears to be a high-performance GPU cluster with:
- **8x NVIDIA H100 GPUs** with NVLink interconnects
- **12x Mellanox ConnectX RDMA-capable NICs** (400G each)
- **Multi-NUMA architecture** with optimal GPU-NIC affinity
- **Bonded front-end interfaces** (4×100G = 400G aggregate)
- **Dedicated E/W interfaces** (400G each for inter-node communication)

This configuration is optimized for:
- **Large-scale distributed training** across multiple nodes
- **High-throughput computing** with dedicated RDMA paths  
- **Separated traffic patterns** (N/S front-end vs E/W backend)
- **Fault tolerance** with multiple interface options per GPU

### Prerequisites for Multi-Node Analysis
- **SSH access** to remote nodes (passwordless recommended)
- **Consistent hardware** topology across nodes
- **RDMA drivers** installed on all nodes (`rdma-core`, `ibverbs`)
- **Network connectivity** on both management (bond0) and RDMA (E/W) networks

For optimal performance, ensure your applications are configured to use the recommended GPU-RoCE mappings identified by the analysis tools.

## 📋 Output Examples

This repository includes real output examples from both tools:

- **[`intra_node_output_example.txt`](intra_node_output_example.txt)**: Complete single-node GPU-RoCE mapping output
  - Shows the complete NIC mapping table with GPU assignments
  - N/S vs E/W interface classification
  - Configuration examples for different use cases

- **[`inter_node_output_example.txt`](inter_node_output_example.txt)**: Multi-node GPU communication mapping output
  - Inter-node GPU communication paths (GPU0 ↔ GPU0, GPU1 ↔ GPU1, etc.)
  - NCCL configuration for distributed training
  - Bandwidth analysis and connectivity status

These examples demonstrate the tools' output format and help you understand what to expect when running them on your own cluster.

## 🔗 Understanding GPU-to-NIC Mapping

### **Important: Optimal Paths vs Communication Flexibility**

The GPU-to-NIC mappings shown by these tools represent **optimal network paths based on hardware topology**, not communication restrictions. Here's what this means for your applications:

**✅ What the mapping shows:**
- **Optimal performance paths**: Each GPU has preferred RDMA interfaces based on PCIe topology (PIX connections)
- **NUMA affinity**: GPUs and NICs on the same NUMA node provide best latency and bandwidth
- **Load distribution recommendations**: Spread network traffic across multiple interfaces for maximum throughput

**🌐 Actual communication capability:**
- **Any GPU can communicate with any other GPU** across nodes through the RDMA network
- **All RDMA interfaces are shared resources** that any GPU can utilize
- **NCCL/MPI libraries handle routing** and automatically select the best available network paths
- **Multiple interfaces can be used simultaneously** for higher aggregate bandwidth

### **Practical Example:**

```
Mapping shows: GPU0 → mlx5_0 (optimal) ↔ GPU0 → mlx5_0 (optimal)
Reality: GPU0 on Node1 can send data to ANY GPU on Node2 through ANY available RDMA interface
```

**Use the mappings to:**
1. **Configure NCCL_IB_HCA** with optimal interfaces for each GPU
2. **Balance network load** by distributing traffic across different interfaces  
3. **Achieve best performance** by following NUMA-aware GPU-NIC pairings
4. **Plan capacity** by understanding which GPUs share network resources

The tools help you optimize network performance, but your distributed applications have full flexibility to communicate between any GPUs across the cluster.