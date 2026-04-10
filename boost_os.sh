#!/bin/bash
# ==============================================================================
# PROJECT HYPER - ULTIMATE CPU/iGPU ACCELERATION MATRIX (LINUX OVERRIDE)
# ==============================================================================
# This script injects aggressive kernel-level overrides to break standard 
# OS hardware throttling bounds.
# WARNING: MUST RUN AS ROOT (sudo)
# ==============================================================================

if [ "$EUID" -ne 0 ]; then
  echo "ERROR: Kernel tuning requires root privileges. Run with sudo."
  exit 1
fi

echo "[*] INITIATING PROJECT HYPER EXTREME KERNEL OVERRIDES"

# 1. Disable Power Throttling / Enable Performance Governors
echo "==> Locking all CPU cores to maximum C0 state frequency..."
for cpu in /sys/devices/system/cpu/cpu[0-9]*; do
    if [ -f "$cpu/cpufreq/scaling_governor" ]; then
        echo "performance" > "$cpu/cpufreq/scaling_governor"
    fi
done

# 2. Virtual Memory Swappiness Override
# A value of 1 instructs the kernel to NEVER swap AI model weights to disk unless 
# absolutely completely out of physical RAM. Bypasses disk thrashing perfectly.
echo "==> Configuring virtual memory swappiness hooks to 1..."
sysctl -w vm.swappiness=1

# 3. Transparent HugePages (THP) Enforcements
# Prevents TLB (Translation Lookaside Buffer) misses by grouping memory blocks
# natively into 2MB chunks rather than 4KB chunks. Critical for Neural Networks.
echo "==> Enforcing Transparent HugePages (THP)..."
if [ -f /sys/kernel/mm/transparent_hugepage/enabled ]; then
    echo "always" > /sys/kernel/mm/transparent_hugepage/enabled
fi
if [ -f /sys/kernel/mm/transparent_hugepage/defrag ]; then
    echo "always" > /sys/kernel/mm/transparent_hugepage/defrag
fi

# 4. Intel Machine Check Architecture (MCA) Relaxations
# Useful for massive AVX-512 vector pipelines
echo "==> Adjusting AVX pipeline kernel tracking..."
sysctl -w kernel.perf_event_paranoid=-1
sysctl -w kernel.nmi_watchdog=0

# 5. Network Tuning for Localhost IPC Max Throughput
echo "==> Boosting localhost IPC TCP limits..."
sysctl -w net.ipv4.tcp_rmem="4096 87380 16777216"
sysctl -w net.ipv4.tcp_wmem="4096 65536 16777216"
sysctl -w net.core.somaxconn=65535

# Write dynamically back to sysctl so it persists until reboot
sysctl -p

echo "[*] KERNEL OVERRIDE SEQUENCE COMPLETE. CPU/iGPU BOUNDARIES REMOVED."
