# Desafio 5 — Microsserviços com API Gateway

## 📋 Descrição da Solução

Este projeto implementa uma arquitetura moderna de microsserviços com **API Gateway como ponto único de entrada**, responsável por orquestrar e rotear requisições para dois microsserviços especializados:

- **Microsserviço de Usuários (Porta 5001)**: Gerencia dados e operações CRUD de usuários
- **Microsserviço de Pedidos (Porta 5002)**: Gerencia dados e operações CRUD de pedidos  
- **API Gateway (Porta 5000)**: Centraliza acesso, valida requisições e orquestra chamadas aos serviços

## 🏗️ Arquitetura

### Diagrama da Solução

```
┌──────────────────────────────────────────────────────────────────────┐
│                           CLIENTE/CONSUMIDOR                         │
└────────────────────┬─────────────────────────────────────────────────┘
                     │ HTTP Requests
                     ▼
         ┌───────────────────────────┐
         │    API GATEWAY (5000)     │
         │  ┌─────────────────────┐  │
         │  │ Roteamento          │  │
         │  │ Validação           │  │
         │  │ Orquestração        │  │
         │  │ Composição          │  │
         │  └─────────────────────┘  │
         │ GET /users                │
         │ POST /orders              │
         │ GET /dashboard            │
         │ GET /usuarios-com-pedidos │
         └───────────────────────────┘
                 │           │
        ┌────────┘           └────────┐
        │                             │
        ▼                             ▼
    ┌────────────────────┐    ┌────────────────────┐
    │  USUÁRIOS (5001)   │    │  PEDIDOS (5002)    │
    │ ┌────────────────┐ │    │ ┌────────────────┐ │
    │ │ GET /api/      │ │    │ │ GET /api/      │ │
    │ │   usuarios     │ │    │ │   pedidos      │ │
    │ │ POST /api/     │ │    │ │ POST /api/     │ │
    │ │   usuarios     │ │    │ │   pedidos      │ │
    │ │ PUT /api/      │ │    │ │ PUT /api/      │ │
    │ │   usuarios     │ │    │ │   pedidos      │ │
    │ │ DELETE /api/   │ │    │ │ DELETE /api/   │ │
    │ │   usuarios     │ │    │ │   pedidos      │ │
    │ └────────────────┘ │    │ └────────────────┘ │
    └────────────────────┘    └────────────────────┘
          Dados em Memória          Dados em Memória
```

### Componentes

#### 1. API Gateway (Porta 5000) — Ponto Único de Entrada

**Responsabilidades**:
- **Roteamento**: Direciona requisições aos microsserviços apropriados
- **Validação**: Valida formato de requisições
- **Orquestração**: Coordena chamadas a múltiplos serviços
- **Composição**: Combina dados de múltiplos serviços
- **Tratamento de Erros**: Trata falhas de serviços downstream

**Endpoints Principais**:

| Endpoint | Método | Descrição | Encaminha Para |
|----------|--------|-----------|-----------------|
| `/health` | GET | Health check do gateway | - |
| `/` | GET | Documentação da API | - |
| `/users` | GET | Lista usuários | Usuários |
| `/users/<id>` | GET | Obtém usuário | Usuários |
| `/users` | POST | Cria usuário | Usuários |
| `/users/<id>` | PUT | Atualiza usuário | Usuários |
| `/users/<id>` | DELETE | Deleta usuário | Usuários |
| `/users/stats` | GET | Estatísticas de usuários | Usuários |
| `/orders` | GET | Lista pedidos | Pedidos |
| `/orders/<id>` | GET | Obtém pedido | Pedidos |
| `/orders` | POST | Cria pedido | Pedidos |
| `/orders/<id>` | PUT | Atualiza pedido | Pedidos |
| `/orders/<id>` | DELETE | Cancela pedido | Pedidos |
| `/orders/user/<id>` | GET | Pedidos do usuário | Pedidos |
| `/orders/stats` | GET | Estatísticas de pedidos | Pedidos |
| `/dashboard` | GET | Dashboard consolidado | Ambos |
| `/usuarios-com-pedidos` | GET | Usuários com seus pedidos | Ambos |

#### 2. Microsserviço de Usuários (Porta 5001)

**Responsabilidades**:
- CRUD completo de usuários
- Filtros por status e perfil
- Estatísticas de usuários
- Health check

**Dados Iniciais**:
```
Alice Silva (admin, ativo)
Bob Santos (editor, ativo)
Carol Oliveira (leitor, inativo)
David Costa (vendedor, ativo)
Eva Martins (cliente, ativo)
```

**Endpoints**:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Health check |
| GET | `/api/usuarios` | Lista usuários (filtros: ativo, perfil) |
| GET | `/api/usuarios/<id>` | Obtém usuário específico |
| POST | `/api/usuarios` | Cria novo usuário |
| PUT | `/api/usuarios/<id>` | Atualiza usuário |
| DELETE | `/api/usuarios/<id>` | Deleta usuário |
| GET | `/api/usuarios/estatisticas/resumo` | Estatísticas |

**Exemplo de Resposta** (GET `/api/usuarios`):
```json
{
  "total": 5,
  "usuarios": [
    {
      "id": 1,
      "nome": "Alice Silva",
      "email": "alice@email.com",
      "ativo": true,
      "data_cadastro": "2024-12-01T10:00:00.000000",
      "perfil": "administrador"
    }
  ],
  "timestamp": "2025-12-02T16:00:00.000000"
}
```

#### 3. Microsserviço de Pedidos (Porta 5002)

**Responsabilidades**:
- CRUD completo de pedidos
- Filtros por status e usuário
- Cálculo de totais
- Estatísticas de pedidos
- Health check

**Dados Iniciais**:
```
101 - Alice Silva - Laptop ($299.90) - Entregue
102 - Bob Santos - Mouse ($89.50) - Processando
103 - David Costa - Teclado ($150.00) - Entregue
104 - Eva Martins - Headset ($49.99) - Enviado
105 - Alice Silva - Monitor ($199.99) - Pendente
```

**Endpoints**:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Health check |
| GET | `/api/pedidos` | Lista pedidos (filtros: usuario_id, status) |
| GET | `/api/pedidos/<id>` | Obtém pedido específico |
| GET | `/api/pedidos/usuario/<id>` | Pedidos de um usuário |
| POST | `/api/pedidos` | Cria novo pedido |
| PUT | `/api/pedidos/<id>` | Atualiza pedido (status) |
| DELETE | `/api/pedidos/<id>` | Cancela pedido |
| GET | `/api/pedidos/estatisticas/resumo` | Estatísticas |

**Exemplo de Resposta** (GET `/api/pedidos`):
```json
{
  "total": 5,
  "pedidos": [
    {
      "id": 101,
      "usuario_id": 1,
      "data_pedido": "2024-11-02T10:00:00.000000",
      "status": "entregue",
      "total": 299.90,
      "itens": [
        {
          "produto": "Laptop",
          "quantidade": 1,
          "preco": 299.90
        }
      ]
    }
  ],
  "timestamp": "2025-12-02T16:00:00.000000"
}
```

## 🚀 Como Executar

### Pré-requisitos

- Docker
- Docker Compose

### Passo 1: Clonar o Repositório

```bash
cd /desafio5
```

### Passo 2: Iniciar os Serviços

```bash
docker-compose up --build
```

Isso vai:
1. Construir as imagens Docker para os 4 serviços
2. Criar a rede compartilhada `gateway-network`
3. Iniciar o microsserviço de usuários (porta 5001)
4. Iniciar o microsserviço de pedidos (porta 5002)
5. Iniciar o API Gateway (porta 5000)
6. Executar o cliente de testes
7. Exibir os logs de todos os serviços

### Passo 3: Acessar a API

**Documentação e Health Check**:
```bash
curl http://localhost:5000/
curl http://localhost:5000/health
```

**Listar Usuários**:
```bash
curl http://localhost:5000/users
```

**Listar Pedidos**:
```bash
curl http://localhost:5000/orders
```

**Dashboard Consolidado**:
```bash
curl http://localhost:5000/dashboard
```

## 📝 Exemplos de Uso

### 1. Listar Usuários

```bash
curl -X GET http://localhost:5000/users
```

**Resposta**:
```json
{
  "total": 5,
  "usuarios": [
    {
      "id": 1,
      "nome": "Alice Silva",
      "email": "alice@email.com",
      "ativo": true,
      "data_cadastro": "2024-12-01T10:00:00.000000",
      "perfil": "administrador"
    }
  ],
  "timestamp": "2025-12-02T16:00:00.000000"
}
```

### 2. Filtrar Usuários Ativos

```bash
curl http://localhost:5000/users?ativo=true
```

### 3. Filtrar Usuários por Perfil

```bash
curl http://localhost:5000/users?perfil=editor
```

### 4. Criar Novo Usuário

```bash
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Grace Harper",
    "email": "grace@email.com",
    "perfil": "vendedor",
    "ativo": true
  }'
```

### 5. Atualizar Usuário

```bash
curl -X PUT http://localhost:5000/users/6 \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Grace Harper Updated",
    "perfil": "admin"
  }'
```

### 6. Listar Pedidos de um Usuário

```bash
curl http://localhost:5000/orders/user/1
```

**Resposta**:
```json
{
  "usuario_id": 1,
  "total_pedidos": 2,
  "valor_total": 499.89,
  "pedidos": [
    {
      "id": 101,
      "usuario_id": 1,
      "data_pedido": "2024-11-02T10:00:00.000000",
      "status": "entregue",
      "total": 299.90,
      "itens": [{"produto": "Laptop", "quantidade": 1, "preco": 299.90}]
    },
    {
      "id": 105,
      "usuario_id": 1,
      "data_pedido": "2025-12-02T15:30:00.000000",
      "status": "pendente",
      "total": 199.99,
      "itens": [{"produto": "Monitor 27\"", "quantidade": 1, "preco": 199.99}]
    }
  ],
  "timestamp": "2025-12-02T16:00:00.000000"
}
```

### 7. Criar Novo Pedido

```bash
curl -X POST http://localhost:5000/orders \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": 2,
    "itens": [
      {
        "produto": "SSD 1TB",
        "quantidade": 1,
        "preco": 120.00
      },
      {
        "produto": "Cabo HDMI",
        "quantidade": 2,
        "preco": 15.00
      }
    ]
  }'
```

### 8. Atualizar Status do Pedido

```bash
curl -X PUT http://localhost:5000/orders/102 \
  -H "Content-Type: application/json" \
  -d '{"status": "enviado"}'
```

### 9. Dashboard Consolidado

```bash
curl http://localhost:5000/dashboard
```

**Resposta**:
```json
{
  "titulo": "Dashboard de Usuários e Pedidos",
  "usuarios": {
    "total_usuarios": 5,
    "usuarios_ativos": 4,
    "usuarios_inativos": 1,
    "percentual_ativos": 80.0,
    "distribuicao_perfil": {
      "administrador": 1,
      "editor": 1,
      "leitor": 1,
      "vendedor": 1,
      "cliente": 1
    },
    "timestamp": "2025-12-02T16:00:00.000000"
  },
  "pedidos": {
    "total_pedidos": 5,
    "valor_total": 788.38,
    "valor_medio": 157.676,
    "distribuicao_status": {
      "entregue": 2,
      "processando": 1,
      "enviado": 1,
      "pendente": 1
    },
    "timestamp": "2025-12-02T16:00:00.000000"
  },
  "timestamp": "2025-12-02T16:00:00.000000"
}
```

### 10. Usuários com Seus Pedidos

```bash
curl http://localhost:5000/usuarios-com-pedidos
```

**Resposta**:
```json
{
  "total_usuarios": 5,
  "usuarios_com_pedidos": [
    {
      "usuario": {
        "id": 1,
        "nome": "Alice Silva",
        "email": "alice@email.com",
        "ativo": true,
        "data_cadastro": "2024-12-01T10:00:00.000000",
        "perfil": "administrador"
      },
      "pedidos": [
        {
          "id": 101,
          "usuario_id": 1,
          "data_pedido": "2024-11-02T10:00:00.000000",
          "status": "entregue",
          "total": 299.90,
          "itens": [{"produto": "Laptop", "quantidade": 1, "preco": 299.90}]
        },
        {
          "id": 105,
          "usuario_id": 1,
          "data_pedido": "2025-12-02T15:30:00.000000",
          "status": "pendente",
          "total": 199.99,
          "itens": [{"produto": "Monitor 27\"", "quantidade": 1, "preco": 199.99}]
        }
      ],
      "total_pedidos": 2,
      "valor_total_pedidos": 499.89
    }
  ],
  "timestamp": "2025-12-02T16:00:00.000000"
}
```

## 🧪 Testes Automatizados

O arquivo `client/test_gateway.sh` contém uma suite completa de testes que valida:

1. Health check do gateway
2. Listagem de usuários
3. Obtenção de usuário específico
4. Criação de novo usuário
5. Atualização de usuário
6. Filtros de usuários
7. Estatísticas de usuários
8. Listagem de pedidos
9. Obtenção de pedido específico
10. Criação de novo pedido
11. Atualização de pedido
12. Filtros de pedidos
13. Estatísticas de pedidos
14. Dashboard consolidado
15. Usuários com pedidos

**Executar testes manualmente**:

```bash
# Dentro do container cliente
docker exec client-gateway-test bash /app/test_gateway.sh

# Ou após iniciar os serviços, em outro terminal
bash desafio5/client/test_gateway.sh
```

## 🔍 Explicação da Arquitetura

### Por que um API Gateway?

Um API Gateway é um componente essencial em arquiteturas de microsserviços:

1. **Ponto Único de Entrada**: Clientes não precisam conhecer os detalhes dos serviços
2. **Roteamento Inteligente**: Direciona requisições automaticamente
3. **Composição de Dados**: Combina dados de múltiplos serviços (ex: `/usuarios-com-pedidos`)
4. **Tratamento de Falhas**: Oferece fallbacks quando serviços falham
5. **Validação Centralizada**: Valida requisições uma única vez
6. **Logging e Monitoramento**: Centraliza observabilidade

### Fluxo de uma Requisição

**Exemplo: GET /users**

```
1. Cliente → GET /users
2. Gateway recebe requisição
3. Gateway encaminha → GET /api/usuarios (Serviço 1)
4. Serviço 1 retorna dados
5. Gateway formata resposta
6. Gateway → Cliente com dados formatados
```

**Exemplo: GET /usuarios-com-pedidos (Orquestração)**

```
1. Cliente → GET /usuarios-com-pedidos
2. Gateway recebe requisição
3. Gateway → GET /api/usuarios (Serviço 1)
4. Serviço 1 retorna lista de usuários
5. Para cada usuário:
   a. Gateway → GET /api/pedidos/usuario/<id> (Serviço 2)
   b. Serviço 2 retorna pedidos do usuário
6. Gateway agrega dados
7. Gateway → Cliente com usuários + pedidos
```

### Tratamento de Erros

```python
# Se um serviço está indisponível:
try:
    resposta = requests.get(url, timeout=5)
except requests.exceptions.Timeout:
    return {"erro": "Timeout do serviço"}, 504
except requests.exceptions.ConnectionError:
    return {"erro": "Serviço indisponível"}, 503
```

## 📊 Estrutura de Pastas

```
desafio5/
├── docker-compose.yml          # Orquestração de containers
├── Dockerfile.gateway           # Imagem do Gateway
├── Dockerfile.usuarios          # Imagem do Microsserviço de Usuários
├── Dockerfile.pedidos           # Imagem do Microsserviço de Pedidos
├── Dockerfile.client            # Imagem do Cliente de Testes
│
├── gateway/
│   ├── app.py                  # API Gateway (roteamento, orquestração)
│   └── requirements.txt         # Dependências Python
│
├── usuarios/
│   ├── app.py                  # Microsserviço de Usuários
│   └── requirements.txt         # Dependências Python
│
├── pedidos/
│   ├── app.py                  # Microsserviço de Pedidos
│   └── requirements.txt         # Dependências Python
│
├── client/
│   ├── test_gateway.sh         # Suite de testes
│   └── requirements.txt         # Dependências Python
│
└── README.md                    # Este arquivo
```

## 🛠️ Tecnologias Utilizadas

- **Python 3.11**: Linguagem de programação
- **Flask**: Framework web minimalista
- **Docker**: Containerização
- **Docker Compose**: Orquestração de containers
- **Requests**: Cliente HTTP para chamadas entre serviços

## 🔌 Comunicação Entre Serviços

### Network Docker

Os serviços se comunicam através da rede compartilhada `gateway-network`:

```yaml
networks:
  gateway-network:
    driver: bridge
```

### URLs de Comunicação

- Gateway → Usuários: `http://usuarios-service:5001`
- Gateway → Pedidos: `http://pedidos-service:5002`

Os nomes de domínio são automaticamente resolvidos pelo Docker.


## Resultados


#### 1. Gateway

![Logs](/desafio5/assets/image.png)

![Gateway-Routes](/desafio5/assets/image%20copy.png)

![Gateway-Healthcheck](/desafio5/assets/image%20copy%202.png)

![Dashboard](/desafio5/assets/image%20copy%205.png)

#### 2. Serviço Usuários

![Usuários](/desafio5/assets/image%20copy%203.png)

#### 3. Serviço Pedidos

![Pedidos](/desafio5/assets/image%20copy%204.png)



## 📚 Referências de Padrões

- **API Gateway Pattern**: Padrão de arquitetura para microsserviços
- **Service Discovery**: Integrado via Docker networking
- **Health Checks**: Todos os serviços implementam `/health`
- **Retry Logic**: Poderia ser implementado no gateway
