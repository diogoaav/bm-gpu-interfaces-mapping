# GPU to RoCE Interface Mapping Guide

This guide provides comprehensive methods to check GPU to RoCE (RDMA over Converged Ethernet) interface mapping on your system.

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

### 1. Comprehensive Analysis Tool
```bash
# Run full analysis
python3 gpu_roce_mapping.py

# Get JSON output for scripting
python3 gpu_roce_mapping.py --json

# Check specific GPU
python3 gpu_roce_mapping.py --gpu 0
```

### 2. Quick Check Script
```bash
# Show everything
./quick_gpu_roce_check.sh

# Show specific information
./quick_gpu_roce_check.sh topo      # Topology only
./quick_gpu_roce_check.sh rdma      # RDMA devices only
./quick_gpu_roce_check.sh roce      # RoCE capabilities
./quick_gpu_roce_check.sh optimal   # Recommendations
```

## Best Practices for GPU-RoCE Mapping

### 1. Performance Considerations
- **Use PIX connections**: Minimize PCIe hops between GPU and NIC
- **Consider NUMA affinity**: Match GPU and NIC on same NUMA node
- **Load balancing**: Distribute traffic across multiple RoCE interfaces

### 2. Application Configuration
```bash
# Set CUDA device and corresponding RoCE interface
export CUDA_VISIBLE_DEVICES=0
export NCCL_IB_HCA=mlx5_0,mlx5_1,mlx5_2  # Use GPUs with PIX connections

# For multi-GPU applications
export NCCL_TOPO_FILE=/path/to/topology.xml  # Custom topology if needed
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

## Hardware-Specific Notes

Your system appears to be a high-performance GPU cluster with:
- 8x NVIDIA H100 GPUs with NVLink
- 12x Mellanox ConnectX RDMA-capable NICs
- Multi-NUMA architecture

This configuration is optimized for:
- Large-scale distributed training
- High-throughput computing
- Multi-node RDMA communication

For optimal performance, ensure your applications are configured to use the recommended GPU-RoCE mappings identified by the analysis tools.