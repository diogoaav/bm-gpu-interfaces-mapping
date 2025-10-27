#!/usr/bin/env python3
"""
Inter-Node GPU-to-GPU Communication Mapping Script

This script maps GPU-to-GPU communication paths between two nodes in a cluster,
showing the complete E/W (East/West) RDMA connectivity for distributed training.
"""

import subprocess
import json
import sys
from collections import defaultdict

class InterNodeGPUMapper:
    def __init__(self, local_node="am4g2r31bm1", remote_node="am4g2r32bm1"):
        self.local_node = local_node
        self.remote_node = remote_node
        
    def get_local_node_info(self):
        """Get local node GPU-RoCE mapping"""
        # Based on our previous analysis
        local_mapping = {
            'node_name': self.local_node,
            'gpu_nic_mapping': {
                'GPU0': {'nic': 'NIC0', 'mlx5': 'mlx5_0', 'interface': 'enp26s0np0', 'type': 'E/W', 'speed': '400G'},
                'GPU1': {'nic': 'NIC3', 'mlx5': 'mlx5_3', 'interface': 'enp60s0np0', 'type': 'E/W', 'speed': '400G'},
                'GPU2': {'nic': 'NIC4', 'mlx5': 'mlx5_4', 'interface': 'enp77s0np0', 'type': 'E/W', 'speed': '400G'},
                'GPU3': {'nic': 'NIC5', 'mlx5': 'mlx5_5', 'interface': 'enp94s0np0', 'type': 'E/W', 'speed': '400G', 'status': 'DOWN'},
                'GPU4': {'nic': 'NIC6', 'mlx5': 'mlx5_6', 'interface': 'enp156s0np0', 'type': 'E/W', 'speed': '400G'},
                'GPU5': {'nic': 'NIC9', 'mlx5': 'mlx5_9', 'interface': 'enp188s0np0', 'type': 'E/W', 'speed': '400G'},
                'GPU6': {'nic': 'NIC10', 'mlx5': 'mlx5_10', 'interface': 'enp204s0np0', 'type': 'E/W', 'speed': '400G'},
                'GPU7': {'nic': 'NIC11', 'mlx5': 'mlx5_11', 'interface': 'enp220s0np0', 'type': 'E/W', 'speed': '400G'},
            }
        }
        return local_mapping
    
    def get_remote_node_info(self):
        """Get remote node GPU-RoCE mapping via SSH"""
        try:
            # Get RDMA device mapping
            result = subprocess.run(['ssh', self.remote_node, 'ibdev2netdev'], 
                                  capture_output=True, text=True, check=True)
            
            rdma_mapping = {}
            for line in result.stdout.strip().split('\n'):
                if 'port' in line and '==>' in line:
                    parts = line.split('==>')
                    if len(parts) == 2:
                        left = parts[0].strip()
                        right = parts[1].strip()
                        
                        device_parts = left.split()
                        if len(device_parts) >= 1:
                            device = device_parts[0]
                            
                            interface_parts = right.split()
                            if len(interface_parts) >= 1:
                                interface = interface_parts[0]
                                status = 'Up' if 'Up' in right else 'Down'
                                rdma_mapping[device] = {
                                    'interface': interface,
                                    'status': status
                                }
            
            # Get GPU topology (assumed same as local based on identical hardware)
            # In a real scenario, you'd run nvidia-smi topo -m on remote node
            remote_mapping = {
                'node_name': self.remote_node,
                'gpu_nic_mapping': {
                    'GPU0': {'nic': 'NIC0', 'mlx5': 'mlx5_0', 'interface': rdma_mapping.get('mlx5_0', {}).get('interface', 'enp26s0np0'), 'type': 'E/W', 'speed': '400G', 'status': rdma_mapping.get('mlx5_0', {}).get('status', 'Unknown')},
                    'GPU1': {'nic': 'NIC3', 'mlx5': 'mlx5_3', 'interface': rdma_mapping.get('mlx5_3', {}).get('interface', 'enp60s0np0'), 'type': 'E/W', 'speed': '400G', 'status': rdma_mapping.get('mlx5_3', {}).get('status', 'Unknown')},
                    'GPU2': {'nic': 'NIC4', 'mlx5': 'mlx5_4', 'interface': rdma_mapping.get('mlx5_4', {}).get('interface', 'enp77s0np0'), 'type': 'E/W', 'speed': '400G', 'status': rdma_mapping.get('mlx5_4', {}).get('status', 'Unknown')},
                    'GPU3': {'nic': 'NIC5', 'mlx5': 'mlx5_5', 'interface': rdma_mapping.get('mlx5_5', {}).get('interface', 'enp94s0np0'), 'type': 'E/W', 'speed': '400G', 'status': rdma_mapping.get('mlx5_5', {}).get('status', 'Unknown')},
                    'GPU4': {'nic': 'NIC6', 'mlx5': 'mlx5_6', 'interface': rdma_mapping.get('mlx5_6', {}).get('interface', 'enp156s0np0'), 'type': 'E/W', 'speed': '400G', 'status': rdma_mapping.get('mlx5_6', {}).get('status', 'Unknown')},
                    'GPU5': {'nic': 'NIC9', 'mlx5': 'mlx5_9', 'interface': rdma_mapping.get('mlx5_9', {}).get('interface', 'enp188s0np0'), 'type': 'E/W', 'speed': '400G', 'status': rdma_mapping.get('mlx5_9', {}).get('status', 'Unknown')},
                    'GPU6': {'nic': 'NIC10', 'mlx5': 'mlx5_10', 'interface': rdma_mapping.get('mlx5_10', {}).get('interface', 'enp204s0np0'), 'type': 'E/W', 'speed': '400G', 'status': rdma_mapping.get('mlx5_10', {}).get('status', 'Unknown')},
                    'GPU7': {'nic': 'NIC11', 'mlx5': 'mlx5_11', 'interface': rdma_mapping.get('mlx5_11', {}).get('interface', 'enp220s0np0'), 'type': 'E/W', 'speed': '400G', 'status': rdma_mapping.get('mlx5_11', {}).get('status', 'Unknown')},
                }
            }
            
            return remote_mapping
            
        except subprocess.CalledProcessError as e:
            print(f"Error connecting to remote node {self.remote_node}: {e}")
            return None
    
    def get_network_connectivity(self):
        """Get network connectivity information between nodes"""
        try:
            # Get local IPs
            local_result = subprocess.run(['ip', 'addr', 'show'], 
                                        capture_output=True, text=True, check=True)
            
            # Get remote IPs
            remote_result = subprocess.run(['ssh', self.remote_node, 'ip addr show'], 
                                         capture_output=True, text=True, check=True)
            
            # Extract relevant network info (simplified)
            connectivity = {
                'local_bond0': '10.45.170.76/24',  # From previous check
                'remote_bond0': '10.45.170.79/24', # From previous check
                'network': '10.45.170.0/24'
            }
            
            return connectivity
            
        except subprocess.CalledProcessError as e:
            print(f"Error getting network connectivity: {e}")
            return None
    
    def print_inter_node_mapping(self):
        """Print comprehensive inter-node GPU-to-GPU communication mapping"""
        print("=" * 120)
        print("INTER-NODE GPU-to-GPU COMMUNICATION MAPPING")
        print("=" * 120)
        
        local_info = self.get_local_node_info()
        remote_info = self.get_remote_node_info()
        connectivity = self.get_network_connectivity()
        
        if not remote_info:
            print("❌ Could not connect to remote node")
            return
        
        print(f"\n🌐 CLUSTER OVERVIEW:")
        print("-" * 60)
        print(f"Local Node:  {local_info['node_name']}")
        print(f"Remote Node: {remote_info['node_name']}")
        if connectivity:
            print(f"Network:     {connectivity['network']}")
            print(f"Local IP:    {connectivity['local_bond0']}")
            print(f"Remote IP:   {connectivity['remote_bond0']}")
        
        print(f"\n📊 INTER-NODE GPU COMMUNICATION PATHS (E/W):")
        print("-" * 120)
        print(f"{'Local GPU':<10} {'Local NIC':<10} {'Local mlx5':<12} {'Local Interface':<18} {'Status':<8} {'>>>':<5} {'Remote GPU':<12} {'Remote NIC':<12} {'Remote mlx5':<14} {'Remote Interface':<18} {'Status'}")
        print("-" * 120)
        
        # Map each local GPU to corresponding remote GPU for E/W communication
        for gpu_id in range(8):
            local_gpu = f'GPU{gpu_id}'
            remote_gpu = f'GPU{gpu_id}'  # Assume 1:1 mapping for distributed training
            
            if local_gpu in local_info['gpu_nic_mapping'] and remote_gpu in remote_info['gpu_nic_mapping']:
                local_data = local_info['gpu_nic_mapping'][local_gpu]
                remote_data = remote_info['gpu_nic_mapping'][remote_gpu]
                
                # Status icons
                local_status = local_data.get('status', 'Up')
                remote_status = remote_data.get('status', 'Up')
                local_icon = "✅" if local_status == 'Up' else "❌"
                remote_icon = "✅" if remote_status == 'Up' else "❌"
                
                print(f"{local_gpu:<10} {local_data['nic']:<10} {local_data['mlx5']:<12} {local_data['interface']:<18} {local_icon} {local_status:<6} {'>>>>>':<5} {remote_gpu:<12} {remote_data['nic']:<12} {remote_data['mlx5']:<14} {remote_data['interface']:<18} {remote_icon} {remote_status}")
        
        print(f"\n🚀 DISTRIBUTED TRAINING CONFIGURATION:")
        print("-" * 60)
        
        # Generate NCCL configuration for multi-node training
        local_interfaces = []
        remote_interfaces = []
        working_gpus = []
        
        for gpu_id in range(8):
            local_gpu = f'GPU{gpu_id}'
            if local_gpu in local_info['gpu_nic_mapping']:
                local_data = local_info['gpu_nic_mapping'][local_gpu]
                local_status = local_data.get('status', 'Up')
                
                if local_gpu in remote_info['gpu_nic_mapping']:
                    remote_data = remote_info['gpu_nic_mapping'][local_gpu]
                    remote_status = remote_data.get('status', 'Up')
                    
                    if local_status == 'Up' and remote_status == 'Up':
                        working_gpus.append(str(gpu_id))
                        local_interfaces.append(local_data['mlx5'])
                        remote_interfaces.append(remote_data['mlx5'])
        
        print(f"# Multi-node training with {len(working_gpus)} GPU pairs")
        print(f"# Node 1 ({local_info['node_name']}):")
        print(f"export CUDA_VISIBLE_DEVICES={','.join(working_gpus)}")
        print(f"export NCCL_IB_HCA={','.join(local_interfaces)}")
        print(f"export NCCL_SOCKET_IFNAME=bond0")
        print(f"export MASTER_ADDR={connectivity['local_bond0'].split('/')[0] if connectivity else '10.45.170.76'}")
        print(f"export MASTER_PORT=29500")
        print(f"export WORLD_SIZE=16  # Total GPUs across both nodes")
        print(f"export RANK=0")
        print()
        print(f"# Node 2 ({remote_info['node_name']}):")
        print(f"export CUDA_VISIBLE_DEVICES={','.join(working_gpus)}")
        print(f"export NCCL_IB_HCA={','.join(remote_interfaces)}")
        print(f"export NCCL_SOCKET_IFNAME=bond0")
        print(f"export MASTER_ADDR={connectivity['local_bond0'].split('/')[0] if connectivity else '10.45.170.76'}")
        print(f"export MASTER_PORT=29500")
        print(f"export WORLD_SIZE=16")
        print(f"export RANK=8")
        
        print(f"\n💡 COMMUNICATION PATTERN ANALYSIS:")
        print("-" * 60)
        
        # Count working connections
        working_pairs = len(working_gpus)
        total_bandwidth = working_pairs * 400  # 400G per connection
        
        print(f"✅ Working GPU pairs: {working_pairs}/8")
        print(f"✅ Total E/W bandwidth: {total_bandwidth}G ({working_pairs} × 400G)")
        print(f"✅ RDMA Protocol: RoCE v2 (InfiniBand over Ethernet)")
        print(f"✅ Network Topology: Direct E/W connections for GPU-GPU communication")
        
        if working_pairs < 8:
            failed_gpus = []
            for gpu_id in range(8):
                local_gpu = f'GPU{gpu_id}'
                if local_gpu in local_info['gpu_nic_mapping']:
                    local_status = local_info['gpu_nic_mapping'][local_gpu].get('status', 'Up')
                    remote_status = remote_info['gpu_nic_mapping'].get(local_gpu, {}).get('status', 'Up')
                    
                    if local_status != 'Up' or remote_status != 'Up':
                        failed_gpus.append(f"{local_gpu} ({local_status}/{remote_status})")
            
            if failed_gpus:
                print(f"⚠️  Issues detected: {', '.join(failed_gpus)}")
        
        print(f"\n🔧 TESTING INTER-NODE CONNECTIVITY:")
        print("-" * 60)
        print(f"# Test RDMA connectivity between nodes:")
        print(f"# On {local_info['node_name']}:")
        print(f"ibv_rc_pingpong -d mlx5_0 -g 0")
        print(f"# On {remote_info['node_name']}:")
        print(f"ibv_rc_pingpong -d mlx5_0 -g 0 {connectivity['local_bond0'].split('/')[0] if connectivity else '10.45.170.76'}")

def main():
    mapper = InterNodeGPUMapper()
    mapper.print_inter_node_mapping()

if __name__ == '__main__':
    main()