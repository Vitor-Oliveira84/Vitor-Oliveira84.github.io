#!/bin/bash
# Port Scan Parallelizado - Usa masscan + nmap em paralelo para reconhecimento rápido
#
# Uso:
#   ./port-scan-parallel.sh -t 192.168.0.0/24
#   ./port-scan-parallel.sh -t example.com -p 80,443,22,3389
#   ./port-scan-parallel.sh -l targets.txt --aggressive
#   ./port-scan-parallel.sh -t 10.0.0.0/16 --service-detection

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Default values
TARGET=""
PORTS="1-65535"
THREADS=500
AGGRESSIVE=0
SERVICE_DETECTION=0
OUTPUT_DIR="scan_results_$(date +%s)"

usage() {
    echo -e "${CYAN}Port Scan Parallelizado${NC}"
    echo "Uso: $0 -t <target> [opções]"
    echo ""
    echo "Opções:"
    echo "  -t, --target <CIDR/IP/domain>    Alvo (obrigatório)"
    echo "  -l, --list <file>                Lista de alvos"
    echo "  -p, --ports <ports>              Portas (default: 1-65535)"
    echo "  --threads <N>                    Threads (default: 500)"
    echo "  --aggressive                     Modo agressivo (scan completo)"
    echo "  --service-detection              Detecta serviços (nmap -sV)"
    echo "  -o, --output <dir>               Diretório de saída"
    echo ""
    echo "Exemplos:"
    echo "  $0 -t 192.168.1.0/24"
    echo "  $0 -t 10.0.0.0/16 -p 22,80,443,3389 --aggressive"
    echo "  $0 -l targets.txt --service-detection"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--target) TARGET="$2"; shift 2 ;;
        -l|--list) LIST_FILE="$2"; shift 2 ;;
        -p|--ports) PORTS="$2"; shift 2 ;;
        --threads) THREADS="$2"; shift 2 ;;
        --aggressive) AGGRESSIVE=1; shift ;;
        --service-detection) SERVICE_DETECTION=1; shift ;;
        -o|--output) OUTPUT_DIR="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Opção desconhecida: $1"; usage; exit 1 ;;
    esac
done

# Validação
if [[ -z "$TARGET" && -z "$LIST_FILE" ]]; then
    echo -e "${RED}[!] Erro: -t ou -l é obrigatório${NC}"
    usage
    exit 1
fi

# Criar diretório de saída
mkdir -p "$OUTPUT_DIR"

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}🔍 Port Scan Parallelizado${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Checklist de ferramentas
check_tools() {
    echo -e "${YELLOW}[*] Verificando ferramentas...${NC}"

    for tool in masscan nmap; do
        if command -v $tool &> /dev/null; then
            echo -e "${GREEN}  ✓ $tool${NC}"
        else
            echo -e "${RED}  ✗ $tool (instalar: apt-get install $tool)${NC}"
            exit 1
        fi
    done
}

# Scan com masscan (rápido)
masscan_scan() {
    local target=$1
    echo -e "\n${CYAN}[1/3] Masscan (descoberta rápida)${NC}"
    echo "[*] Alvo: $target"
    echo "[*] Porta: $PORTS"
    echo "[*] Threads: $THREADS"

    masscan $target \
        -p $PORTS \
        --max-rate=$THREADS \
        -oX "$OUTPUT_DIR/masscan_$target.xml" \
        2>/dev/null || true

    # Parse masscan output
    grep "portid" "$OUTPUT_DIR/masscan_$target.xml" 2>/dev/null | \
        sed -n 's/.*portid="\([^"]*\)".*/\1/p' > "$OUTPUT_DIR/open_ports_$target.txt" || true

    local open_count=$(wc -l < "$OUTPUT_DIR/open_ports_$target.txt" 2>/dev/null || echo 0)
    echo -e "${GREEN}[+] $open_count portas abertas${NC}"
}

# Scan detalhado com nmap
nmap_detailed_scan() {
    local target=$1
    echo -e "\n${CYAN}[2/3] Nmap (scan detalhado)${NC}"

    if [[ ! -f "$OUTPUT_DIR/open_ports_$target.txt" ]]; then
        echo "[!] Nenhuma porta aberta encontrada"
        return
    fi

    # Converter para formato nmap (-p p1,p2,p3...)
    ports=$(tr '\n' ',' < "$OUTPUT_DIR/open_ports_$target.txt" | sed 's/,$//')

    if [[ -z "$ports" ]]; then
        echo "[!] Lista de portas vazia"
        return
    fi

    # Opções do nmap
    local nmap_opts="-sV --script=default,vuln -oX $OUTPUT_DIR/nmap_$target.xml"

    if [[ $AGGRESSIVE -eq 1 ]]; then
        nmap_opts="$nmap_opts -A -O"
    fi

    echo "[*] Portas: $ports"
    echo "[*] Opcões: $nmap_opts"

    nmap -p $ports $nmap_opts $target 2>/dev/null || true
}

# Detecção de serviço
service_detection() {
    local target=$1

    if [[ $SERVICE_DETECTION -eq 0 ]]; then
        return
    fi

    echo -e "\n${CYAN}[3/3] Detecção de Serviços${NC}"

    if [[ ! -f "$OUTPUT_DIR/open_ports_$target.txt" ]]; then
        return
    fi

    ports=$(tr '\n' ',' < "$OUTPUT_DIR/open_ports_$target.txt" | sed 's/,$//')

    nmap -p $ports -sV -O \
        -oX "$OUTPUT_DIR/services_$target.xml" \
        $target 2>/dev/null || true

    echo -e "${GREEN}[+] Detecção completa${NC}"
}

# Gerar relatório
generate_report() {
    echo -e "\n${CYAN}[+] Gerando relatório...${NC}"

    {
        echo "Port Scan Report - $(date)"
        echo "========================================"
        echo ""

        for file in "$OUTPUT_DIR/open_ports"*; do
            if [[ -f "$file" ]]; then
                target=$(basename "$file" | sed 's/open_ports_//' | sed 's/.txt//')
                count=$(wc -l < "$file" 2>/dev/null || echo 0)
                echo "Target: $target"
                echo "Open ports: $count"
                echo "Portas:"
                cat "$file" | sed 's/^/  /'
                echo ""
            fi
        done
    } > "$OUTPUT_DIR/REPORT.txt"

    echo -e "${GREEN}[+] Relatório: $OUTPUT_DIR/REPORT.txt${NC}"
}

# === MAIN ===
check_tools

if [[ -n "$LIST_FILE" ]]; then
    # Processar lista
    echo "[*] Lendo alvos de: $LIST_FILE"
    while IFS= read -r target; do
        [[ -z "$target" ]] && continue
        masscan_scan "$target"
        nmap_detailed_scan "$target"
        service_detection "$target"
    done < "$LIST_FILE"
else
    # Alvo único
    masscan_scan "$TARGET"
    nmap_detailed_scan "$TARGET"
    service_detection "$TARGET"
fi

generate_report

echo -e "\n${GREEN}[✓] Scan concluído!${NC}"
echo -e "${YELLOW}[*] Resultados em: $OUTPUT_DIR/${NC}"
