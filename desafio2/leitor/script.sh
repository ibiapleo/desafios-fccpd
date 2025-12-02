#!/bin/bash

echo "╔════════════════════════════════════════╗"
echo "║  Leitor - Verificando Persistência    ║"
echo "╚════════════════════════════════════════╝"
echo ""

echo "Aguardando aplicação iniciar..."
sleep 10

CONTADOR=0

while true; do
    CONTADOR=$((CONTADOR + 1))
    DATA=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "=========================================="
    echo "Leitura #$CONTADOR - $DATA"
    echo "=========================================="
    
    # Verificar status
    echo "📊 Status da aplicação:"
    curl -s http://app:5000/status
    echo -e "\n"
    
    # Listar usuários
    echo "👥 Usuários no banco:"
    curl -s http://app:5000/usuarios
    echo -e "\n"
    
    # Listar logs
    echo "📝 Logs da aplicação:"
    curl -s http://app:5000/logs
    echo -e "\n"
    
    sleep 15
done