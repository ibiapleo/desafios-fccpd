#!/bin/bash

echo "╔════════════════════════════════════════════╗"
echo "║  Cliente                                   ║"
echo "║  Testando Web, DB e Cache                  ║"
echo "╚════════════════════════════════════════════╝"
echo ""

sleep 15

CONTADOR=0

while true; do
    CONTADOR=$((CONTADOR + 1))
    DATA=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "=========================================="
    echo "Teste #$CONTADOR - $DATA"
    echo "=========================================="
    
    # Teste de Health Check
    echo "🏥 Health Check (Web):"
    curl -s http://web:5000/health
    echo -e "\n"
    
    # Teste de Status dos Serviços
    echo "📊 Status de Conexão (DB + Cache):"
    curl -s http://web:5000/status | python3 -m json.tool 2>/dev/null || curl -s http://web:5000/status
    echo -e "\n"
    
    # Listar Posts
    echo "📝 Posts no Banco de Dados:"
    curl -s http://web:5000/api/posts | python3 -m json.tool 2>/dev/null || curl -s http://web:5000/api/posts
    echo -e "\n"
    
    # Listar Posts com Cache
    echo "💾 Posts com Cache:"
    curl -s http://web:5000/api/posts/cache | python3 -m json.tool 2>/dev/null || curl -s http://web:5000/api/posts/cache
    echo -e "\n"
    
    # Contador (Redis)
    echo "📈 Contador de Requisições (Redis):"
    curl -s http://web:5000/api/contador | python3 -m json.tool 2>/dev/null || curl -s http://web:5000/api/contador
    echo -e "\n"
    
    # Estatísticas
    echo "📊 Estatísticas Gerais:"
    curl -s http://web:5000/api/stats | python3 -m json.tool 2>/dev/null || curl -s http://web:5000/api/stats
    echo -e "\n"
    
    sleep 15
done