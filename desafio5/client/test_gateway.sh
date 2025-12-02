#!/bin/bash

# Cores para saída
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' 

GATEWAY_URL="http://api-gateway:5000"
RESULTADO=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}    TESTES DO API GATEWAY${NC}"
echo -e "${BLUE}========================================${NC}"

# Aguarda a disponibilidade do gateway
echo -e "\n${YELLOW}[*] Aguardando disponibilidade do gateway...${NC}"
for i in {1..30}; do
    if curl -s "$GATEWAY_URL/health" > /dev/null; then
        echo -e "${GREEN}[✓] Gateway está disponível${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# ============================================================================
# TESTES DE HEALTH CHECK
# ============================================================================

echo -e "\n${BLUE}\n[TEST] Health Check${NC}"
echo -e "${YELLOW}GET /health${NC}"
RESPONSE=$(curl -s "$GATEWAY_URL/health")
echo "$RESPONSE" | python3 -m json.tool
if echo "$RESPONSE" | grep -q "healthy\|degraded"; then
    echo -e "${GREEN}✓ Health check OK${NC}"
else
    echo -e "${RED}✗ Health check FALHOU${NC}"
    RESULTADO=1
fi

# ============================================================================
# TESTES DE USUÁRIOS
# ============================================================================

echo -e "\n${BLUE}\n[TEST] Listar Usuários${NC}"
echo -e "${YELLOW}GET /users${NC}"
curl -s "$GATEWAY_URL/users" | python3 -m json.tool

echo -e "\n${BLUE}\n[TEST] Obter Usuário Específico${NC}"
echo -e "${YELLOW}GET /users/1${NC}"
curl -s "$GATEWAY_URL/users/1" | python3 -m json.tool

echo -e "\n${BLUE}\n[TEST] Criar Novo Usuário${NC}"
echo -e "${YELLOW}POST /users${NC}"
NEW_USER=$(curl -s -X POST "$GATEWAY_URL/users" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Frank Wilson",
    "email": "frank@email.com",
    "perfil": "cliente",
    "ativo": true
  }')
echo "$NEW_USER" | python3 -m json.tool

# Extrai o ID do novo usuário
NEW_USER_ID=$(echo "$NEW_USER" | python3 -c "import sys, json; print(json.load(sys.stdin).get('usuario', {}).get('id', ''))" 2>/dev/null)

if [ -n "$NEW_USER_ID" ]; then
    echo -e "${GREEN}✓ Usuário criado com ID: $NEW_USER_ID${NC}"
    
    echo -e "\n${BLUE}\n[TEST] Atualizar Usuário${NC}"
    echo -e "${YELLOW}PUT /users/$NEW_USER_ID${NC}"
    curl -s -X PUT "$GATEWAY_URL/users/$NEW_USER_ID" \
      -H "Content-Type: application/json" \
      -d '{
        "nome": "Frank Wilson Updated",
        "perfil": "editor"
      }' | python3 -m json.tool
else
    echo -e "${YELLOW}[!] Não foi possível extrair ID do novo usuário${NC}"
fi

echo -e "\n${BLUE}\n[TEST] Filtrar Usuários Ativos${NC}"
echo -e "${YELLOW}GET /users?ativo=true${NC}"
curl -s "$GATEWAY_URL/users?ativo=true" | python3 -m json.tool

echo -e "\n${BLUE}\n[TEST] Filtrar Usuários por Perfil${NC}"
echo -e "${YELLOW}GET /users?perfil=editor${NC}"
curl -s "$GATEWAY_URL/users?perfil=editor" | python3 -m json.tool

echo -e "\n${BLUE}\n[TEST] Estatísticas de Usuários${NC}"
echo -e "${YELLOW}GET /users/stats${NC}"
curl -s "$GATEWAY_URL/users/stats" | python3 -m json.tool

# ============================================================================
# TESTES DE PEDIDOS
# ============================================================================

echo -e "\n${BLUE}\n[TEST] Listar Pedidos${NC}"
echo -e "${YELLOW}GET /orders${NC}"
curl -s "$GATEWAY_URL/orders" | python3 -m json.tool

echo -e "\n${BLUE}\n[TEST] Obter Pedido Específico${NC}"
echo -e "${YELLOW}GET /orders/101${NC}"
curl -s "$GATEWAY_URL/orders/101" | python3 -m json.tool

echo -e "\n${BLUE}\n[TEST] Listar Pedidos de um Usuário${NC}"
echo -e "${YELLOW}GET /orders/user/1${NC}"
curl -s "$GATEWAY_URL/orders/user/1" | python3 -m json.tool

echo -e "\n${BLUE}\n[TEST] Criar Novo Pedido${NC}"
echo -e "${YELLOW}POST /orders${NC}"
NEW_ORDER=$(curl -s -X POST "$GATEWAY_URL/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": 2,
    "itens": [
      {
        "produto": "Webcam",
        "quantidade": 1,
        "preco": 79.99
      }
    ]
  }')
echo "$NEW_ORDER" | python3 -m json.tool

# Extrai o ID do novo pedido
NEW_ORDER_ID=$(echo "$NEW_ORDER" | python3 -c "import sys, json; print(json.load(sys.stdin).get('pedido', {}).get('id', ''))" 2>/dev/null)

if [ -n "$NEW_ORDER_ID" ]; then
    echo -e "${GREEN}✓ Pedido criado com ID: $NEW_ORDER_ID${NC}"
    
    echo -e "\n${BLUE}\n[TEST] Atualizar Status do Pedido${NC}"
    echo -e "${YELLOW}PUT /orders/$NEW_ORDER_ID${NC}"
    curl -s -X PUT "$GATEWAY_URL/orders/$NEW_ORDER_ID" \
      -H "Content-Type: application/json" \
      -d '{"status": "processando"}' | python3 -m json.tool
else
    echo -e "${YELLOW}[!] Não foi possível extrair ID do novo pedido${NC}"
fi

echo -e "\n${BLUE}\n[TEST] Filtrar Pedidos por Status${NC}"
echo -e "${YELLOW}GET /orders?status=entregue${NC}"
curl -s "$GATEWAY_URL/orders?status=entregue" | python3 -m json.tool

echo -e "\n${BLUE}\n[TEST] Estatísticas de Pedidos${NC}"
echo -e "${YELLOW}GET /orders/stats${NC}"
curl -s "$GATEWAY_URL/orders/stats" | python3 -m json.tool

# ============================================================================
# TESTES DE COMPOSIÇÃO/ORQUESTRAÇÃO
# ============================================================================

echo -e "\n${BLUE}\n[TEST] Dashboard Consolidado${NC}"
echo -e "${YELLOW}GET /dashboard${NC}"
curl -s "$GATEWAY_URL/dashboard" | python3 -m json.tool

echo -e "\n${BLUE}\n[TEST] Usuários com Pedidos${NC}"
echo -e "${YELLOW}GET /usuarios-com-pedidos${NC}"
curl -s "$GATEWAY_URL/usuarios-com-pedidos" | python3 -m json.tool | head -100
echo "..."

# ============================================================================
# TESTES DE DOCUMENTAÇÃO
# ============================================================================

echo -e "\n${BLUE}\n[TEST] Documentação da API${NC}"
echo -e "${YELLOW}GET /{{NC}"
curl -s "$GATEWAY_URL/" | python3 -m json.tool

# ============================================================================
# RESUMO
# ============================================================================

echo -e "\n${BLUE}========================================${NC}"
if [ $RESULTADO -eq 0 ]; then
    echo -e "${GREEN}    TESTES CONCLUÍDOS COM SUCESSO${NC}"
else
    echo -e "${RED}    ALGUNS TESTES FALHARAM${NC}"
fi
echo -e "${BLUE}========================================${NC}"

exit $RESULTADO
