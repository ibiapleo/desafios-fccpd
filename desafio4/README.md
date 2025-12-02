# Desafio 4 — Microsserviços Independentes

## 📋 Descrição da Solução

Este projeto demonstra a comunicação entre dois microsserviços independentes via HTTP:

- **Serviço A (Porta 5001)**: Microsserviço fornecedor de dados de usuários
  - Gerencia usuários (CRUD)
  - Fornece endpoints REST
  - Armazena dados em memória

- **Serviço B (Porta 5002)**: Microsserviço consumidor e analisador
  - Consome dados do Serviço A via HTTP
  - Formata e enriquece informações
  - Gera relatórios e análises

## 🏗️ Arquitetura

### Diagrama de Comunicação

```
┌─────────────────┐
│   Cliente       │
│   (testes)      │
└────────┬────────┘
         │
    ┌────┴─────┬──────────────┐
    │           │              │
    ▼           ▼              ▼
┌────────────┐ ┌──────────────┐
│ Serviço A  │ │ Serviço B    │
│ (5001)     │ │ (5002)       │
│            │◄─┤            │
│ Usuários   │  │ Análise    │
│ CRUD       │  │ Relatórios │
└────────────┘ └──────────────┘
```

### Componentes

#### 1. Serviço A — Gerenciamento de Usuários (Fornecedor)

**Porta**: 5001

**Endpoints**:

| Método | Endpoint | Descrição | Exemplo |
|--------|----------|-----------|---------|
| GET | `/health` | Health check | `http://localhost:5001/health` |
| GET | `/api/usuarios` | Lista todos os usuários | `http://localhost:5001/api/usuarios` |
| GET | `/api/usuarios?ativo=true` | Filtra por status | `http://localhost:5001/api/usuarios?ativo=true` |
| GET | `/api/usuarios?perfil=editor` | Filtra por perfil | `http://localhost:5001/api/usuarios?perfil=editor` |
| GET | `/api/usuarios/<id>` | Obtém usuário específico | `http://localhost:5001/api/usuarios/1` |
| POST | `/api/usuarios` | Cria novo usuário | `POST com JSON no body` |
| PUT | `/api/usuarios/<id>` | Atualiza usuário | `PUT com JSON no body` |
| DELETE | `/api/usuarios/<id>` | Deleta usuário | `http://localhost:5001/api/usuarios/1` |
| GET | `/api/usuarios/estatisticas/resumo` | Estatísticas dos usuários | `http://localhost:5001/api/usuarios/estatisticas/resumo` |

**Usuários Iniciais**:
- Alice Silva (Admin) - Ativo há 365 dias
- Bob Santos (Editor) - Ativo há 180 dias
- Carol Oliveira (Leitor) - Inativo há 90 dias
- David Costa (Editor) - Ativo há 30 dias
- Eva Martins (Leitor) - Ativo há 7 dias

**Resposta Exemplo** (GET `/api/usuarios`):
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
    },
    ...
  ],
  "timestamp": "2025-12-01T16:00:00.000000"
}
```

#### 2. Serviço B — Análise e Visualização (Consumidor)

**Porta**: 5002

**Comunicação com Serviço A**: Requisições HTTP para `http://servico-a:5001`

**Endpoints**:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Health check com status de Serviço A |
| GET | `/api/usuarios/formatados` | Usuários do Serviço A em formato legível |
| GET | `/api/usuarios/relatorio` | Relatório completo de usuários |
| GET | `/api/usuarios/<id>/detalhes` | Detalhes formatados de um usuário |
| GET | `/api/status-servicos` | Status de comunicação com Serviço A |

**Resposta Exemplo** (GET `/api/usuarios/formatados`):
```json
{
  "total": 5,
  "usuarios": [
    {
      "id": 1,
      "nome": "Alice Silva",
      "email": "alice@email.com",
      "status": "Ativo",
      "perfil": "Administrador",
      "cadastro": "365 dias atrás",
      "data_completa": "2024-12-01T10:00:00.000000"
    },
    ...
  ],
  "origem": "Serviço A",
  "timestamp": "2025-12-01T16:00:00.000000"
}
```

**Resposta Exemplo** (GET `/api/usuarios/relatorio`):
```json
{
  "titulo": "Relatório de Usuários",
  "resumo": {
    "total_usuarios": 5,
    "usuarios_ativos": 4,
    "usuarios_inativos": 1,
    "percentual_ativos": 80.0
  },
  "distribuicao_perfil": {
    "administrador": 1,
    "editor": 2,
    "leitor": 2
  },
  "usuarios_ativos": [
    {
      "nome": "Alice Silva",
      "email": "alice@email.com",
      "perfil": "ADMINISTRADOR",
      "ativo_a_dias": 365
    },
    ...
  ],
  "usuarios_inativos": [
    {
      "nome": "Carol Oliveira",
      "email": "carol@email.com",
      "perfil": "LEITOR"
    }
  ],
  "timestamp": "2025-12-01T16:00:00.000000"
}
```

## 🔄 Fluxo de Comunicação

### Exemplo 1: Usuário solicita Relatório (Serviço B)

```
1. Cliente faz GET /api/usuarios/relatorio (Serviço B)
2. Serviço B faz GET /api/usuarios (Serviço A)
3. Serviço A retorna lista de usuários
4. Serviço B faz GET /api/usuarios/estatisticas/resumo (Serviço A)
5. Serviço A retorna estatísticas
6. Serviço B processa e formata dados
7. Serviço B retorna relatório ao cliente
```

### Exemplo 2: Detalhes de um Usuário Específico

```
1. Cliente faz GET /api/usuarios/1/detalhes (Serviço B)
2. Serviço B faz GET /api/usuarios/1 (Serviço A)
3. Serviço A retorna dados do usuário
4. Serviço B calcula tempo de atividade
5. Serviço B formata e retorna ao cliente
```

## 🚀 Instruções de Execução

### Pré-requisitos

- Docker 20.10+
- Docker Compose integrado
- Linux/macOS ou Windows com WSL2

### Execução Passo a Passo

#### 1. Acessar o Diretório

```bash
cd /desafio4
```

#### 2. Construir e Iniciar

```bash
docker compose up --build
```

Para executar em background:
```bash
docker compose up -d
```

#### 3. Visualizar Logs

Todos os logs:
```bash
docker compose logs -f
```

Logs específicos:
```bash
docker compose logs -f servico-a
docker compose logs -f servico-b
docker compose logs -f client
```

#### 4. Testar em Outro Terminal

**Testar Serviço A Diretamente**:

Health check:
```bash
curl http://localhost:5001/health
```

Listar usuários:
```bash
curl http://localhost:5001/api/usuarios
```

Criar usuário:
```bash
curl -X POST http://localhost:5001/api/usuarios \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Frank Lima",
    "email": "frank@email.com",
    "perfil": "leitor"
  }'
```

Filtrar por status:
```bash
curl http://localhost:5001/api/usuarios?ativo=true
```

Filtrar por perfil:
```bash
curl http://localhost:5001/api/usuarios?perfil=editor
```

**Testar Serviço B (Consumidor)**:

Health check:
```bash
curl http://localhost:5002/health
```

Usuários formatados:
```bash
curl http://localhost:5002/api/usuarios/formatados
```

Relatório completo:
```bash
curl http://localhost:5002/api/usuarios/relatorio | python3 -m json.tool
```

Detalhes de um usuário:
```bash
curl http://localhost:5002/api/usuarios/1/detalhes
```

Status de comunicação:
```bash
curl http://localhost:5002/api/status-servicos
```

#### 5. Parar os Serviços

```bash
docker compose down
```

## 🔍 Verificação de Funcionamento

### Listar Containers

```bash
docker ps
```

Você deve ver:
- `servico-a-usuarios`
- `servico-b-analise`
- `client-teste` (se estiver rodando)

### Verificar Rede Interna

```bash
docker network inspect desafio4_rede-microsservicos
```

### Testar Conectividade

De dentro de um container:
```bash
docker exec servico-b-analise curl http://servico-a:5001/health
```

### Verificar Health Status

```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

Ambos devem estar com status `healthy`.

## 🧪 Demonstração de Funcionalidade

### Teste 1: Comunicação Básica

```bash
# Serviço A fornece dados
curl http://localhost:5001/api/usuarios

# Serviço B consome e formata
curl http://localhost:5002/api/usuarios/formatados
```

**Esperado**: Serviço B retorna dados do Serviço A em formato diferente.

### Teste 2: Criar Usuário e Ver em Relatório

```bash
# Criar novo usuário no Serviço A
curl -X POST http://localhost:5001/api/usuarios \
  -H "Content-Type: application/json" \
  -d '{"nome": "George Wilson", "email": "george@email.com", "perfil": "editor"}'

# Ver relatório no Serviço B (deve incluir novo usuário)
curl http://localhost:5002/api/usuarios/relatorio
```

**Esperado**: Total de usuários aumenta em 1, novo usuário aparece no relatório.

### Teste 3: Desativar Serviço A

```bash
# Parar Serviço A
docker stop servico-a-usuarios

# Tentar acessar Serviço B
curl http://localhost:5002/api/usuarios/formatados
```

**Esperado**: Serviço B retorna erro 503 (Serviço Indisponível).

### Teste 4: Verificar Tempo de Resposta

```bash
# Verificar quanto tempo leva para Serviço B conectar em A
curl http://localhost:5002/api/status-servicos | python3 -m json.tool
```

**Esperado**: Campo `tempo_resposta_ms` mostra latência entre serviços.

## 📊 Decisões de Design

| Decisão | Motivo |
|---------|--------|
| **Microsserviços em portas diferentes** | Isolamento total, simula ambiente real |
| **Serviço A em memória** | Simplicidade, foco na comunicação |
| **Serviço B consome HTTP** | Padrão real de microsserviços |
| **Health checks** | Garante inicialização correta |
| **Tratamento de erros** | Serviço B lida com indisponibilidade de A |
| **Dados em JSON** | Padrão REST comum |
| **Formatação no B** | Demonstra processamento de dados consumidos |

## 🔗 Tecnologias Utilizadas

| Componente | Tecnologia | Versão | Propósito |
|-----------|-----------|--------|----------|
| Serviço A | Python + Flask | 3.11 / 3.0.0 | Fornecedor de dados |
| Serviço B | Python + Flask + Requests | 3.11 / 3.0.0 / 2.31.0 | Consumidor e análise |
| Orquestração | Docker Compose | integrado | Gerenciar microsserviços |
| Comunicação | HTTP | REST | Entre microsserviços |

## Resultados

#### 1. Logs:

![Logs](/desafio4/assets/Captura%20de%20tela%20de%202025-12-01%2023-16-04.png)

#### 2. Comunicação básica com os serviços:

![Serviço-A](/desafio4/assets/Captura%20de%20tela%20de%202025-12-01%2023-22-55.png)

![Serviço-B](/desafio4/assets/Captura%20de%20tela%20de%202025-12-01%2023-25-50.png)

#### 3. Fluxo de criar usuário e ver relatório:

![Criar](/desafio4/assets/Captura%20de%20tela%20de%202025-12-01%2023-27-39.png)

![Relatório](/desafio4/assets/Captura%20de%20tela%20de%202025-12-01%2023-28-59.png)



## 🔗 Referências

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [RESTful API Design](https://restfulapi.net/)
- [Microservices Architecture](https://microservices.io/)   