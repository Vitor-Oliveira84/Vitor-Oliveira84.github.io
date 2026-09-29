#!/bin/bash
# SSL Certificate Analyzer - Extrai dados de certificados SSL/TLS
#
# Uso:
#   ./ssl-cert-analyzer.sh -d example.com
#   ./ssl-cert-analyzer.sh -d example.com -p 443
#   ./ssl-cert-analyzer.sh -l domains.txt --batch
#   ./ssl-cert-analyzer.sh -d example.com --ct-logs

set -e

DOMAIN=""
PORT=443
TIMEOUT=10

usage() {
    echo "SSL Certificate Analyzer"
    echo "Uso: $0 -d <domain> [opções]"
    echo ""
    echo "Opções:"
    echo "  -d, --domain <domain>    Domínio alvo"
    echo "  -p, --port <PORT>        Porta (default: 443)"
    echo "  -l, --list <file>        Lista de domínios"
    echo "  --ct-logs                Extrai CT logs"
    echo "  --batch                  Modo batch"
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--domain) DOMAIN="$2"; shift 2 ;;
        -p|--port) PORT="$2"; shift 2 ;;
        -l|--list) LIST_FILE="$2"; shift 2 ;;
        --ct-logs) CT_LOGS=1; shift ;;
        --batch) BATCH=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Opção desconhecida: $1"; shift ;;
    esac
done

if [[ -z "$DOMAIN" && -z "$LIST_FILE" ]]; then
    echo "[!] Erro: -d ou -l é obrigatório"
    usage
    exit 1
fi

echo "=========================================="
echo "📜 SSL Certificate Analyzer"
echo "=========================================="

analyze_cert() {
    local domain=$1
    local port=${2:-443}

    echo ""
    echo "[*] Analisando: $domain:$port"

    # Extrair certificado
    cert_data=$(echo | openssl s_client -servername $domain -connect $domain:$port -showcerts 2>/dev/null | head -100)

    if [[ -z "$cert_data" ]]; then
        echo "[!] Erro ao conectar"
        return
    fi

    # Salvar certificado
    echo "-----BEGIN CERTIFICATE-----" > "/tmp/$domain.crt"
    echo "$cert_data" | sed -n '/-----BEGIN CERTIFICATE-----/,/-----END CERTIFICATE-----/p' | head -n -1 >> "/tmp/$domain.crt"

    # Analisar com openssl
    echo "[+] Informações do Certificado:"

    openssl x509 -in "/tmp/$domain.crt" -text -noout 2>/dev/null | grep -E "Subject:|Issuer:|Not Before:|Not After:" | sed 's/^/    /'

    # Extrair SANs (Subject Alternative Names)
    echo "[+] Subdomínios (SANs):"
    openssl x509 -in "/tmp/$domain.crt" -text -noout 2>/dev/null | grep -A1 "Subject Alternative Name" | tail -1 | tr ',' '\n' | sed 's/^/    /'

    # Check expiration
    exp_date=$(openssl x509 -in "/tmp/$domain.crt" -noout -enddate 2>/dev/null | cut -d= -f2)
    exp_seconds=$(date -d "$exp_date" +%s 2>/dev/null || echo 0)
    now_seconds=$(date +%s)
    days_left=$(( ($exp_seconds - $now_seconds) / 86400 ))

    if [[ $days_left -lt 0 ]]; then
        echo "[!] Certificado EXPIRADO! (há $((0 - $days_left)) dias)"
    elif [[ $days_left -lt 30 ]]; then
        echo "[!] Certificado VENCE EM $days_left dias!"
    else
        echo "[+] Certificado válido por mais $days_left dias"
    fi

    # Issuer
    issuer=$(openssl x509 -in "/tmp/$domain.crt" -noout -issuer 2>/dev/null)
    echo "[+] Issuer: $issuer"

    rm -f "/tmp/$domain.crt"
}

# Main
if [[ -n "$LIST_FILE" ]]; then
    while IFS= read -r domain; do
        [[ -z "$domain" ]] && continue
        analyze_cert "$domain" "$PORT"
    done < "$LIST_FILE"
else
    analyze_cert "$DOMAIN" "$PORT"
fi

# CT Logs
if [[ $CT_LOGS -eq 1 ]]; then
    echo ""
    echo "[*] Extratando CT Logs..."

    domain=${DOMAIN:-$LIST_FILE}
    curl -s "https://crt.sh/?q=%.${domain}&output=json" | \
        jq -r '.[] | .name_value' | sort -u | \
        sed 's/^/    /'
fi

echo ""
echo "[✓] Análise completa!"
