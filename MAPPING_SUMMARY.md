# GPU to RoCE Interface Mapping Summary

## CONFIRMED: All interfaces are 400G capable

### N/S vs E/W Classification:

**N/S (North/South) - Front-end interfaces:**
- `bond0` = 4×100G bonded = **400G total aggregate**
- Used for external/client traffic  
- Members: `mlx5_1`, `mlx5_2`, `mlx5_7`, `mlx5_8`

**E/W (East/West) - Backend interfaces:**
- Individual **400G RoCE interfaces**
- Used for inter-node GPU communication
- Members: `mlx5_0`, `mlx5_3`, `mlx5_4`, `mlx5_5`, `mlx5_6`, `mlx5_9`, `mlx5_10`, `mlx5_11`

## Complete Mapping Table

| NIC   | mlx5    | Interface      | Speed | Type | Status | GPU Affinity (PIX) | Purpose           |
|-------|---------|----------------|-------|------|--------|-------------------|-------------------|
| NIC0  | mlx5_0  | enp26s0np0     | 400G  | E/W  | ✅ Up   | GPU0              | Inter-node RDMA   |
| NIC1  | mlx5_1  | bond0          | 100G* | N/S  | ✅ Up   | GPU0              | Front-end (bonded)|
| NIC2  | mlx5_2  | bond0          | 100G* | N/S  | ✅ Up   | GPU0              | Front-end (bonded)|
| NIC3  | mlx5_3  | enp60s0np0     | 400G  | E/W  | ✅ Up   | GPU1              | Inter-node RDMA   |
| NIC4  | mlx5_4  | enp77s0np0     | 400G  | E/W  | ✅ Up   | GPU2              | Inter-node RDMA   |
| NIC5  | mlx5_5  | enp94s0np0     | 400G  | E/W  | ❌ Down | GPU3              | Inter-node RDMA   |
| NIC6  | mlx5_6  | enp156s0np0    | 400G  | E/W  | ✅ Up   | GPU4              | Inter-node RDMA   |
| NIC7  | mlx5_7  | bond0          | 100G* | N/S  | ✅ Up   | GPU4              | Front-end (bonded)|
| NIC8  | mlx5_8  | bond0          | 100G* | N/S  | ✅ Up   | GPU4              | Front-end (bonded)|
| NIC9  | mlx5_9  | enp188s0np0    | 400G  | E/W  | ✅ Up   | GPU5              | Inter-node RDMA   |
| NIC10 | mlx5_10 | enp204s0np0    | 400G  | E/W  | ✅ Up   | GPU6              | Inter-node RDMA   |
| NIC11 | mlx5_11 | enp220s0np0    | 400G  | E/W  | ✅ Up   | GPU7              | Inter-node RDMA   |

*bond0 members contribute 100G each to 400G total aggregate

## Key Insights

1. **All interfaces are 400G capable** ✅
2. **N/S (bond0)**: 4×100G = 400G aggregate for front-end traffic
3. **E/W interfaces**: 400G each for inter-node GPU communication  
4. **GPU0 & GPU4** have access to both N/S (bond0) and E/W (dedicated) interfaces
5. **GPU3** has a DOWN interface (mlx5_5) that needs investigation
6. **Optimal design** for separating front-end and backend traffic

## Configuration Examples

### Multi-node Training (E/W only):
```bash
export CUDA_VISIBLE_DEVICES=0,1,2,4,5,6,7
export NCCL_IB_HCA=mlx5_0,mlx5_3,mlx5_4,mlx5_6,mlx5_9,mlx5_10,mlx5_11
# Each GPU gets 400G dedicated E/W bandwidth
```

### Front-end Serving (N/S only):
```bash  
export CUDA_VISIBLE_DEVICES=0,4
export NCCL_IB_HCA=mlx5_1,mlx5_2,mlx5_7,mlx5_8
# Uses full 400G bond0 for front-end traffic
```

### Mixed Workload:
```bash
# E/W: Use dedicated 400G interfaces per GPU
# N/S: Use bond0 (400G shared between GPU0 and GPU4)
```