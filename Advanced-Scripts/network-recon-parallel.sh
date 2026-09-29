#!/bin/bash
# Network Reconnaissance Parallelizado
# Uso: ./network-recon-parallel.sh -t 192.168.1.0/24

TARGETS=""
THREADS=10

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--targets) TARGETS="$2"; shift 2 ;;
        --threads) THREADS="$2"; shift 2 ;;
        *) shift ;;
    esac
done

echo "[*] Network Reconnaissance Parallelizado"
echo "[*] Alvo: $TARGETS"

# ARP scan
echo "[*] ARP scanning..."
arp-scan -l | grep -v "Interface\|Packets\|Ending\|^--" > arp_results.txt &

# Ping sweep
echo "[*] Ping sweep..."
for ip in $(echo $TARGETS | tr '/' '\n'); do
    ping -c 1 $ip &
done
wait

# Port scan consolidado
echo "[*] Port scanning (top 1000)..."
nmap -p- --top-ports 1000 -T4 -sS $TARGETS -oX scan_results.xml &

wait

echo "[+] Reconhecimento completo!"
echo "[*] Resultados: scan_results.xml, arp_results.txt"
