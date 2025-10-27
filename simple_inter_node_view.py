#!/usr/bin/env python3
"""
Simplified Inter-Node GPU Communication Visualization
"""

def print_simple_inter_node_mapping():
    print("=" * 80)
    print("INTER-NODE GPU-to-GPU COMMUNICATION PATHS")
    print("=" * 80)
    
    print("\n🔗 Direct GPU-to-GPU Communication (E/W):")
    print("-" * 80)
    
    # Define the mappings based on the analysis
    mappings = [
        ("GPU0", "NIC0", "mlx5_0", "enp26s0np0", "✅", "GPU0", "NIC0", "mlx5_0", "enp26s0np0", "✅"),
        ("GPU1", "NIC3", "mlx5_3", "enp60s0np0", "✅", "GPU1", "NIC3", "mlx5_3", "enp60s0np0", "✅"),
        ("GPU2", "NIC4", "mlx5_4", "enp77s0np0", "✅", "GPU2", "NIC4", "mlx5_4", "enp77s0np0", "✅"),
        ("GPU3", "NIC5", "mlx5_5", "enp94s0np0", "❌", "GPU3", "NIC5", "mlx5_5", "enp94s0np0", "✅"),
        ("GPU4", "NIC6", "mlx5_6", "enp156s0np0", "✅", "GPU4", "NIC6", "mlx5_6", "enp156s0np0", "✅"),
        ("GPU5", "NIC9", "mlx5_9", "enp188s0np0", "✅", "GPU5", "NIC9", "mlx5_9", "enp188s0np0", "✅"),
        ("GPU6", "NIC10", "mlx5_10", "enp204s0np0", "✅", "GPU6", "NIC10", "mlx5_10", "enp204s0np0", "✅"),
        ("GPU7", "NIC11", "mlx5_11", "enp220s0np0", "✅", "GPU7", "NIC11", "mlx5_11", "enp220s0np0", "✅"),
    ]
    
    for local_gpu, local_nic, local_mlx5, local_iface, local_status, remote_gpu, remote_nic, remote_mlx5, remote_iface, remote_status in mappings:
        # Create the connection string
        connection_status = "🟢" if local_status == "✅" and remote_status == "✅" else "🔴"
        
        print(f"{connection_status} Node1 {local_gpu} - {local_nic} - {local_mlx5} ({local_iface}) >>>>> Node2 {remote_gpu} - {remote_nic} - {remote_mlx5} ({remote_iface})")
    
    print(f"\n📈 SUMMARY:")
    print("-" * 40)
    print("🟢 Working connections: 7/8 (2.8TB/s total bandwidth)")
    print("🔴 Failed connections: 1/8 (GPU3 local interface DOWN)")
    print("💡 Each connection: 400G bidirectional RoCE")
    print("🌐 Network: 10.45.170.0/24 (bond0 for control plane)")
    
    print(f"\n⚡ QUICK DISTRIBUTED TRAINING SETUP:")
    print("-" * 40)
    print("# Use 7 working GPU pairs (skip GPU3)")
    print("# Total: 14 GPUs across 2 nodes")
    print("# Bandwidth: 2.8TB/s inter-node communication")

if __name__ == "__main__":
    print_simple_inter_node_mapping()