# Desafio 2 — Volumes e Persistência

## 📋 Descrição da Solução

Este projeto demonstra a persistência de dados usando volumes Docker. A aplicação usa PostgreSQL para armazenar dados em um volume, garantindo que os dados persistam mesmo após a remoção e recriação dos containers.

## 🏗️ Arquitetura e Decisões Técnicas

### Componentes

1. **Banco de Dados (db-postgres)**
   - DBMS: PostgreSQL 15 Alpine
   - Volume: `dados_postgres` montado em `/var/lib/postgresql/data`
   - Porta: 5432
   - Tabelas: `usuarios` e `logs`

2. **Aplicação (app-flask)**
   - Framework: Flask 3.0.0 (Python 3.11)
   - Biblioteca: psycopg2 (driver PostgreSQL)
   - Porta: 5000
   - Endpoints:
     - `GET /usuarios` - Lista usuários
     - `POST /usuarios` - Cria novo usuário
     - `GET /logs` - Lista logs
     - `GET /status` - Status da aplicação

3. **Leitor (leitor-dados)**
   - Imagem: curlimages/curl:8.4.0
   - Função: Fazer leitura dos dados persistidos
   - Script shell para automação

### Decisões Técnicas

- **PostgreSQL**: Banco de dados robusto com suporte a transações ACID
- **Volume Docker**: Armazena dados fora do container em `dados_postgres`
- **Health Check**: Garante que o banco está pronto antes da aplicação conectar
- **Alpine**: Imagens otimizadas para tamanho e performance
- **Rede Bridge**: Comunicação interna entre containers
- **psycopg2**: Driver PostgreSQL mais confiável para Python

### Persistência de Dados

O volume `dados_postgres` mapeia o diretório `/var/lib/postgresql/data` dentro do container para um volume gerenciado pelo Docker. Isso significa:
- Dados sobrevivem à remoção do container
- Dados sobrevivem à recriação do container
- Dados são isolados em um volume específico
- Dados podem ser inspecionados e gerenciados pelo Docker

## 🔄 Funcionamento Detalhado

### Fluxo de Execução

```
1. docker compose up é executado
2. Volume 'dados_postgres' é criado (se não existir)
3. Container db-postgres inicia PostgreSQL
4. Health check verifica se PostgreSQL está pronto
5. Container app-flask inicia e conecta ao banco
6. Dados iniciais são inseridos (init.sql)
7. Container leitor-dados inicia e faz leituras periódicas
8. Dados persistem no volume mesmo após parar/remover containers
```

### Tecnologias Utilizadas

| Componente | Versão | Propósito |
|-----------|--------|----------|
| Docker | 20.10+ | Containerização |
| Docker Compose | Integrado | Orquestração |
| PostgreSQL | 15-alpine | Banco de dados |
| Python | 3.11-slim | Runtime |
| Flask | 3.0.0 | Framework web |
| psycopg2 | 2.9.9 | Driver PostgreSQL |
| Curl | 8.4.0 | Cliente HTTP |

## 🚀 Instruções de Execução

### Pré-requisitos

- Docker 20.10+
- Docker Compose integrado
- Linux/macOS ou Windows com WSL2

### Execução Passo a Passo

#### 1. Acessar o Diretório

```bash
cd /desafio2
```

#### 2. Construir e Iniciar

```bash
docker compose up --build
```

#### 3. Testar a Aplicação (em outro terminal)

Criar um novo usuário:
```bash
curl -X POST http://localhost:5000/usuarios \
  -H "Content-Type: application/json" \
  -d '{"nome": "Ana Costa", "email": "ana@example.com"}'
```

Listar usuários:
```bash
curl http://localhost:5000/usuarios
```

Verificar status:
```bash
curl http://localhost:5000/status
```

#### 4. Testar Persistência

Parar os containers:
```bash
docker compose down
```

Verificar que o volume ainda existe:
```bash
docker volume ls | grep dados_postgres
```

Reiniciar:
```bash
docker compose up
```

Os dados estarão lá! Verifique:
```bash
curl http://localhost:5000/usuarios
```

#### 5. Parar Tudo

```bash
docker compose down
```

Remover volume (CUIDADO - deleta dados):
```bash
docker compose down -v
```

## 🔍 Verificação de Funcionamento

### Listar Volumes

```bash
docker volume ls
```

### Inspecionar Volume

```bash
docker volume inspect desafio2_dados_postgres
```

### Conectar ao Banco Diretamente

```bash
docker exec -it db-postgres psql -U usuario -d aplicacao
```

Dentro do psql:
```sql
SELECT * FROM usuarios;
SELECT * FROM logs;
```

### Verificar Dados Persistidos

Após parar e reiniciar:
```bash
docker compose down
docker compose up -d
sleep 5
curl http://localhost:5000/usuarios
```

Os dados criados anteriormente devem estar lá!

## 📊 Resultados Esperados

### Primeira Execução

Dados iniciais do `init.sql`:
- 3 usuários criados
- 2 logs registrados

### Após Criar Novo Usuário

```json
[
  {
    "id": 1,
    "nome": "João Silva",
    "email": "joao@example.com",
    "data_criacao": "2025-12-01T14:30:00"
  },
  {
    "id": 2,
    "nome": "Maria Santos",
    "email": "maria@example.com",
    "data_criacao": "2025-12-01T14:30:00"
  },
  {
    "id": 3,
    "nome": "Pedro Oliveira",
    "email": "pedro@example.com",
    "data_criacao": "2025-12-01T14:30:00"
  },
  {
    "id": 4,
    "nome": "Ana Costa",
    "email": "ana@example.com",
    "data_criacao": "2025-12-01T14:35:22"
  }
]
```

### Após Remover e Reiniciar

Os mesmos dados aparecerão, comprovando persistência!

### Resultados

#### 1. Logs:

![Logs](/desafio2/assets/Captura%20de%20tela%20de%202025-12-01%2012-29-24.png)

#### 2. Inserção de Dados:

![Requisição POST](/desafio2/assets/Captura%20de%20tela%20de%202025-12-01%2012-30-23.png)

#### 3. Retorno dos Dados:

![Requisição GET](/desafio2/assets/Captura%20de%20tela%20de%202025-12-01%2012-30-54.png)

#### 4. Persistência:

![Persistência](/desafio2/assets/Captura%20de%20tela%20de%202025-12-01%2012-35-02.png)

## 🔗 Referências

- [Docker Volumes](https://docs.docker.com/storage/volumes/)
- [Docker Compose](https://docs.docker.com/compose/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [psycopg2 Documentation](https://www.psycopg.org/)