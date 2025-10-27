#!/usr/bin/env python3
"""
Complete GPU to RoCE Interface Mapping with N/S vs E/W Classification
"""

def print_complete_mapping():
    print("=" * 100)
    print("COMPLETE GPU to RoCE Interface Mapping - N/S vs E/W Classification")
    print("=" * 100)
    
    print("\n🌐 INTERFACE CLASSIFICATION:")
    print("-" * 60)
    print("📡 N/S (North/South) - Front-end interfaces:")
    print("   • bond0 = 4x100G bonded = 400G total aggregate")
    print("   • Used for external/client traffic")
    print("   • Members: mlx5_1, mlx5_2, mlx5_7, mlx5_8")
    print()
    print("🔄 E/W (East/West) - Backend/Inter-node interfaces:")
    print("   • Individual 400G RoCE interfaces")
    print("   • Used for GPU-to-GPU communication between nodes")
    print("   • Members: mlx5_0, mlx5_3, mlx5_4, mlx5_5, mlx5_6, mlx5_9, mlx5_10, mlx5_11")
    
    print("\n📊 COMPLETE NIC MAPPING TABLE:")
    print("-" * 110)
    print(f"{'NIC':<6} {'mlx5':<8} {'Interface':<20} {'Speed':<12} {'Type':<8} {'GPU':<6} {'Status':<8} {'Purpose'}")
    print("-" * 110)
    
    mappings = [
        ("NIC0", "mlx5_0", "enp26s0np0", "400G", "E/W", "GPU0", "Up", "Inter-node RDMA"),
        ("NIC1", "mlx5_1", "bond0", "100G*", "N/S", "GPU0", "Up", "Front-end (bonded)"),
        ("NIC2", "mlx5_2", "bond0", "100G*", "N/S", "GPU0", "Up", "Front-end (bonded)"),
        ("NIC3", "mlx5_3", "enp60s0np0", "400G", "E/W", "GPU1", "Up", "Inter-node RDMA"),
        ("NIC4", "mlx5_4", "enp77s0np0", "400G", "E/W", "GPU2", "Up", "Inter-node RDMA"),
        ("NIC5", "mlx5_5", "enp94s0np0", "400G", "E/W", "GPU3", "Down", "Inter-node RDMA"),
        ("NIC6", "mlx5_6", "enp156s0np0", "400G", "E/W", "GPU4", "Up", "Inter-node RDMA"),
        ("NIC7", "mlx5_7", "bond0", "100G*", "N/S", "GPU4", "Up", "Front-end (bonded)"),
        ("NIC8", "mlx5_8", "bond0", "100G*", "N/S", "GPU4", "Up", "Front-end (bonded)"),
        ("NIC9", "mlx5_9", "enp188s0np0", "400G", "E/W", "GPU5", "Up", "Inter-node RDMA"),
        ("NIC10", "mlx5_10", "enp204s0np0", "400G", "E/W", "GPU6", "Up", "Inter-node RDMA"),
        ("NIC11", "mlx5_11", "enp220s0np0", "400G", "E/W", "GPU7", "Up", "Inter-node RDMA"),
    ]
    
    for mapping in mappings:
        nic, mlx5, interface, speed, type_str, gpu, status, purpose = mapping
        status_icon = "✅" if status == "Up" else "❌"
        print(f"{nic:<6} {mlx5:<8} {interface:<20} {speed:<12} {type_str:<8} {gpu:<6} {status_icon} {status:<6} {purpose}")
    
    print("\n* bond0 members contribute 100G each to 400G total aggregate")
    
    print(f"\n🎯 OPTIMAL GPU-RoCE MAPPINGS by Use Case:")
    print("-" * 60)
    
    print("\n📡 FOR FRONT-END/CLIENT TRAFFIC (N/S):")
    print("GPU0 -> bond0 (mlx5_1,mlx5_2) = 200G of 400G bond")
    print("GPU4 -> bond0 (mlx5_7,mlx5_8) = 200G of 400G bond")
    print("Note: GPU0 and GPU4 share the 400G bond0 interface")
    
    print("\n🔄 FOR INTER-NODE GPU COMMUNICATION (E/W):")
    print("GPU0 -> NIC0  -> mlx5_0 (enp26s0np0) = 400G dedicated")
    print("GPU1 -> NIC3  -> mlx5_3 (enp60s0np0) = 400G dedicated")
    print("GPU2 -> NIC4  -> mlx5_4 (enp77s0np0) = 400G dedicated")
    print("GPU3 -> NIC5  -> mlx5_5 (enp94s0np0) = 400G dedicated (DOWN)")
    print("GPU4 -> NIC6  -> mlx5_6 (enp156s0np0) = 400G dedicated")
    print("GPU5 -> NIC9  -> mlx5_9 (enp188s0np0) = 400G dedicated")
    print("GPU6 -> NIC10 -> mlx5_10 (enp204s0np0) = 400G dedicated")
    print("GPU7 -> NIC11 -> mlx5_11 (enp220s0np0) = 400G dedicated")
    
    print(f"\n🚀 CONFIGURATION EXAMPLES:")
    print("-" * 60)
    
    print("\n# Multi-node training (E/W communication):")
    print("export CUDA_VISIBLE_DEVICES=0,1,2,4,5,6,7")
    print("export NCCL_IB_HCA=mlx5_0,mlx5_3,mlx5_4,mlx5_6,mlx5_9,mlx5_10,mlx5_11")
    print("# Each GPU gets 400G dedicated E/W bandwidth")
    
    print("\n# Front-end serving with GPU0 and GPU4:")
    print("export CUDA_VISIBLE_DEVICES=0,4")
    print("export NCCL_IB_HCA=mlx5_1,mlx5_2,mlx5_7,mlx5_8")
    print("# Uses full 400G bond0 for front-end traffic")
    
    print("\n# Mixed workload (E/W + N/S):")
    print("# GPU0: E/W communication")
    print("export NCCL_IB_HCA=mlx5_0  # 400G E/W")
    print("# Separate process for front-end on same GPU0:")
    print("# Use mlx5_1,mlx5_2 for N/S traffic (200G of bond)")
    
    print(f"\n⚠️  IMPORTANT NOTES:")
    print("-" * 60)
    print("1. ALL interfaces are 400G capable (confirmed)")
    print("2. bond0 = 4x100G = 400G aggregate for N/S traffic")
    print("3. E/W interfaces are 400G each for inter-node GPU communication")
    print("4. GPU3's interface (mlx5_5) is DOWN - needs investigation")
    print("5. GPU0 and GPU4 have both N/S (bond0) and E/W (dedicated) access")
    print("6. For maximum performance, separate N/S and E/W traffic")

if __name__ == "__main__":
    print_complete_mapping()