#!/bin/bash

echo "╔════════════════════════════════════════╗"
echo "║  Cliente - Requisições ao Servidor     ║"
echo "╚════════════════════════════════════════╝"
echo ""

echo "Cliente iniciado. Aguardando servidor em http://servidor-web:8080..."
sleep 5

CONTADOR=0
SUCESSO=0
FALHA=0

while true; do
    CONTADOR=$((CONTADOR + 1))
    DATA=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "=========================================="
    echo "Requisição #$CONTADOR - $DATA"
    echo "=========================================="
    
    # Requisição 1: GET /
    if RESPOSTA=$(curl -s -w "\n%{http_code}" http://servidor-web:8080/); then
        HTTP_CODE=$(echo "$RESPOSTA" | tail -n1)
        BODY=$(echo "$RESPOSTA" | head -n-1)
        
        if [ "$HTTP_CODE" = "200" ]; then
            echo "✓ GET / - HTTP $HTTP_CODE"
            echo "$BODY"
            SUCESSO=$((SUCESSO + 1))
        else
            echo "✗ GET / - HTTP $HTTP_CODE"
            FALHA=$((FALHA + 1))
        fi
    else
        echo "✗ Erro ao conectar em servidor-web:8080"
        FALHA=$((FALHA + 1))
    fi
    
    echo ""
    
    # Requisição 2: GET /status
    if RESPOSTA=$(curl -s -w "\n%{http_code}" http://servidor-web:8080/status); then
        HTTP_CODE=$(echo "$RESPOSTA" | tail -n1)
        BODY=$(echo "$RESPOSTA" | head -n-1)
        
        if [ "$HTTP_CODE" = "200" ]; then
            echo "✓ GET /status - HTTP $HTTP_CODE"
            echo "$BODY" | python -m json.tool 2>/dev/null || echo "$BODY"
        else
            echo "✗ GET /status - HTTP $HTTP_CODE"
        fi
    fi
    
    echo ""
    echo "Estatísticas: Sucesso=$SUCESSO | Falha=$FALHA"
    echo ""
    
    sleep 10
done