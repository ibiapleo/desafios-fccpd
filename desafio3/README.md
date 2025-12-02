# Desafio 3 — Docker Compose Orquestrando Serviços

## 📋 Descrição da Solução

Este projeto demonstra a orquestração de múltiplos serviços interdependentes usando Docker Compose. A aplicação consiste em:
- **Web**: Aplicação Flask que fornece uma API REST
- **Database**: PostgreSQL para persistência de dados
- **Cache**: Redis para cache em memória

Os três serviços trabalham em conjunto para criar uma aplicação completa com comunicação entre containers.

## 🏗️ Arquitetura e Decisões Técnicas

### Componentes

#### 1. Serviço Web (Flask API)
- **Imagem base**: `python:3.11-slim`
- **Porta**: 5000
- **Função**: Fornece endpoints REST para interagir com DB e Cache
- **Dependências**: PostgreSQL, Redis
- **Endpoints**:
  - `GET /health` - Health check
  - `GET /status` - Status de conexão com DB e Cache
  - `GET /api/posts` - Lista posts do banco
  - `POST /api/posts` - Cria novo post
  - `GET /api/posts/cache` - Lista posts com cache
  - `GET /api/contador` - Contador armazenado no Redis
  - `GET /api/stats` - Estatísticas gerais

#### 2. Serviço Database (PostgreSQL)
- **Imagem base**: `postgres:15-alpine`
- **Porta**: 5432
- **Função**: Armazenar dados persistentes
- **Tabelas**: `posts` (id, titulo, conteudo, autor, data_criacao)
- **Volume**: `dados_postgres` para persistência

#### 3. Serviço Cache (Redis)
- **Imagem base**: `redis:7-alpine`
- **Porta**: 6379
- **Função**: Cache em memória e armazenamento de contadores
- **Dados armazenados**:
  - `posts_cache` - Cache de posts (TTL 60s)
  - `contador_requisicoes` - Contador de requisições HTTP

#### 4. Cliente de Teste
- **Imagem base**: `python:3.11-slim`
- **Função**: Testa comunicação entre todos os serviços
- **Intervalo**: Faz requisições a cada 15 segundos

### Decisões Técnicas

| Decisão | Motivo |
|---------|--------|
| **Alpine em imagens base** | Menor tamanho, melhor performance |
| **depends_on com healthcheck** | Garante ordem correta de inicialização |
| **Rede bridge personalizada** | Comunicação interna via hostname |
| **Volume para PostgreSQL** | Dados persistem após parada do container |
| **Redis para cache** | Melhora performance com TTL |
| **Health checks** | Detecta e reinicia containers problemáticos |
| **Variáveis de ambiente** | Configuração flexível e segura |

## 🔄 Funcionamento Detalhado

### Ordem de Inicialização

```
1. Docker Compose inicia os serviços em paralelo
2. Database inicia e executa init.sql
3. Cache inicia e fica pronto
4. Web aguarda healthchecks de DB e Cache
5. Web inicia e conecta aos dois serviços
6. Client inicia e começa a fazer requisições
```

### Fluxo de Comunicação

```
Cliente HTTP → Web (Flask)
                 ├→ PostgreSQL (dados)
                 ├→ Redis (cache)
                 └→ Responde com dados
```

### Exemplo de Requisição

```
1. Cliente faz: GET /api/posts/cache
2. Web verifica Redis (cache)
3. Se cache vazio: busca PostgreSQL
4. Armazena em Redis com TTL 60s
5. Retorna dados ao cliente
6. Próxima requisição (dentro de 60s): vem do Redis
```

## 🚀 Instruções de Execução

### Pré-requisitos

- Docker 20.10+
- Docker Compose integrado
- Linux/macOS ou Windows com WSL2

Verificar instalação:
```bash
docker --version
docker compose version
```

### Execução Passo a Passo

#### 1. Acessar o Diretório

```bash
cd /desafio3
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
docker compose logs -f web
docker compose logs -f db
docker compose logs -f cache
docker compose logs -f client
```

#### 4. Testar a Comunicação (em outro terminal)

**Health Check (Web)**:
```bash
curl http://localhost:5000/health
```

Resposta esperada:
```json
{"status": "healthy"}
```

**Status de Conexão (DB + Cache)**:
```bash
curl http://localhost:5000/status
```

Resposta esperada:
```json
{
  "banco_dados": "conectado",
  "cache": "conectado",
  "status": "ok",
  "timestamp": "2025-12-01T15:30:00.123456"
}
```

**Listar Posts (Database)**:
```bash
curl http://localhost:5000/api/posts
```

**Criar Novo Post (Database)**:
```bash
curl -X POST http://localhost:5000/api/posts \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Novo Post",
    "conteudo": "Conteúdo aqui",
    "autor": "Você"
  }'
```

**Listar Posts com Cache**:
```bash
curl http://localhost:5000/api/posts/cache
```

**Contador (Cache/Redis)**:
```bash
curl http://localhost:5000/api/contador
```

**Estatísticas Gerais**:
```bash
curl http://localhost:5000/api/stats
```

#### 5. Parar os Serviços

```bash
docker compose down
```

Para remover volumes (CUIDADO - deleta dados):
```bash
docker compose down -v
```

## 🔍 Verificação de Funcionamento

### Listar Containers em Execução

```bash
docker ps
```

Você deve ver:
- `web-flask`
- `db-postgresql`
- `cache-redis`
- `client-teste`

### Verificar a Rede Interna

```bash
docker network inspect desafio3_rede-aplicacao
```

Mostra todos os containers conectados e seus IPs internos.

### Testar Conectividade Interna

```bash
# De dentro do container web, testar conexão com db
docker exec web-flask ping db

# De dentro do container web, testar conexão com cache
docker exec web-flask redis-cli -h cache ping
```

### Inspecionar Dados do PostgreSQL

```bash
docker exec -it db-postgresql psql -U usuario -d aplicacao
```

Dentro do PostgreSQL:
```sql
SELECT * FROM posts;
SELECT COUNT(*) FROM posts;
```

### Inspecionar Dados do Redis

```bash
docker exec -it cache-redis redis-cli
```

Dentro do Redis:
```
KEYS *
GET posts_cache
GET contador_requisicoes
```

### Verificar Health Status

```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

Todos devem estar `Up` com health `healthy`.

## 🧪 Demonstração de Funcionalidade

### Teste 1: Comunicação Web ↔ Database

```bash
# Verificar posts iniciais
curl http://localhost:5000/api/posts

# Criar novo post
curl -X POST http://localhost:5000/api/posts \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Test", "conteudo": "Testando"}'

# Verificar que foi criado
curl http://localhost:5000/api/posts
```

**Esperado**: Novo post aparece na lista.

### Teste 2: Comunicação Web ↔ Cache

```bash
# Primeira requisição (vai no DB)
curl http://localhost:5000/api/posts/cache

# Segunda requisição (vai no cache, mais rápida)
curl http://localhost:5000/api/posts/cache

# Esperar 61 segundos e fazer novamente (volta ao DB)
sleep 61
curl http://localhost:5000/api/posts/cache
```

**Esperado**: Campo `fonte` muda de `banco_de_dados` para `cache` e volta.

### Teste 3: Contador (Redis)

```bash
# Fazer várias requisições
for i in {1..5}; do
  curl http://localhost:5000/api/contador
  echo ""
done
```

**Esperado**: Contador aumenta: 1, 2, 3, 4, 5...

### Teste 4: Estatísticas Globais

```bash
curl http://localhost:5000/api/stats
```

**Esperado**: 
- `total_posts`: 3 (posts iniciais) + posts criados
- `total_requisicoes`: número de requisições feitas

## 📐 Estrutura de Arquivos

```
/desafio3
├── docker-compose.yml          # Orquestração principal
├── Dockerfile.web              # Construir web
├── Dockerfile.db               # Construir database
├── Dockerfile.cache            # Construir cache
├── Dockerfile.client           # Construir cliente
├── web/
│   ├── app.py                  # Aplicação Flask
│   └── requirements.txt         # Dependências Python
├── db/
│   └── init.sql                # Script de inicialização
├── client/
│   └── test_comunicacao.sh      # Script de teste
├── .gitignore                  # Arquivos ignorados
└── README.md                   # Este arquivo
```

## 🔗 Tecnologias Utilizadas

| Serviço | Tecnologia | Versão | Propósito |
|---------|-----------|--------|----------|
| Web | Python + Flask | 3.11 / 3.0.0 | API REST |
| Database | PostgreSQL | 15-alpine | Persistência |
| Cache | Redis | 7-alpine | Cache em memória |
| Orquestração | Docker Compose | integrado | Gerenciar serviços |

## Resultados

#### 1. Logs:

![Logs](/desafio3/assets/Captura%20de%20tela%20de%202025-12-01%2013-56-49.png)

#### 2. Requisições:

![Requisição POST](/desafio3/assets/Captura%20de%20tela%20de%202025-12-01%2013-57-47.png)


![Requisição GET](/desafio3/assets/Captura%20de%20tela%20de%202025-12-01%2014-08-34.png)

#### cache

![Requisição GET](/desafio3/assets/Captura%20de%20tela%20de%202025-12-01%2014-11-59.png)

![Contador](/desafio3/assets/Captura%20de%20tela%20de%202025-12-01%2014-20-43.png)

#### 3. Status Gerais:

![Status Gerais](/desafio3/assets/Captura%20de%20tela%20de%202025-12-01%2014-22-23.png)


## 🔗 Referências

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Redis Docker Image](https://hub.docker.com/_/redis)
- [Docker Networks](https://docs.docker.com/network/)