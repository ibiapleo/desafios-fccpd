#!/bin/bash

echo "╔════════════════════════════════════════════════════════╗"
echo "║  Cliente - Testador de Microsserviços                  ║"
echo "║  Serviço A: Fornecedor de Dados                        ║"
echo "║  Serviço B: Consumidor e Análise                       ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

sleep 15

CONTADOR=0

while true; do
    CONTADOR=$((CONTADOR + 1))
    DATA=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "=========================================="
    echo "Teste #$CONTADOR - $DATA"
    echo "=========================================="
    
    # Health Check Serviço A
    echo "🏥 Health Check (Serviço A):"
    curl -s http://servico-a:5001/health | python3 -m json.tool 2>/dev/null || curl -s http://servico-a:5001/health
    echo ""
    
    # Health Check Serviço B
    echo "🏥 Health Check (Serviço B):"
    curl -s http://servico-b:5002/health | python3 -m json.tool 2>/dev/null || curl -s http://servico-b:5002/health
    echo ""
    
    # Listar usuários brutos do Serviço A
    echo "📊 Usuários Brutos (Serviço A):"
    curl -s http://servico-a:5001/api/usuarios | python3 -m json.tool 2>/dev/null || curl -s http://servico-a:5001/api/usuarios
    echo ""
    
    # Usuários formatados pelo Serviço B
    echo "📝 Usuários Formatados (Serviço B consome A):"
    curl -s http://servico-b:5002/api/usuarios/formatados | python3 -m json.tool 2>/dev/null || curl -s http://servico-b:5002/api/usuarios/formatados
    echo ""
    
    # Relatório completo do Serviço B
    echo "📈 Relatório Completo (Serviço B):"
    curl -s http://servico-b:5002/api/usuarios/relatorio | python3 -m json.tool 2>/dev/null || curl -s http://servico-b:5002/api/usuarios/relatorio
    echo ""
    
    # Status dos serviços
    echo "🔍 Status de Comunicação:"
    curl -s http://servico-b:5002/api/status-servicos | python3 -m json.tool 2>/dev/null || curl -s http://servico-b:5002/api/status-servicos
    echo ""
    
    sleep 20
done