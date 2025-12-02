# Desafio 1 — Containers em Rede

## 📋 Descrição da Solução

Este projeto demonstra a comunicação entre dois containers Docker através de uma rede customizada. Um container executa um servidor web em Flask na porta 8080, enquanto outro container realiza requisições HTTP periódicas para o servidor, simulando um cliente que monitora o status do serviço.

## 🏗️ Arquitetura e Decisões Técnicas

### Componentes

1. **Servidor Web (servidor-web)**
   - Framework: Flask 3.0.0 (Python 3.11)
   - Imagem base: `python:3.11-slim`
   - Porta: 8080
   - Endpoints:
     - `GET /` - Retorna mensagem de status com timestamp
     - `GET /status` - Retorna JSON com status do serviço

2. **Cliente (cliente-requisicoes)**
   - Imagem base: `curlimages/curl:8.4.0`
   - Função: Fazer requisições HTTP periódicas (a cada 10 segundos)
   - Script shell para automação
   - Aguarda 5 segundos antes de iniciar requisições

3. **Rede Docker**
   - Nome: `rede-comunicacao`
   - Driver: bridge
   - Tipo: customizada
   - Propósito: Permitir comunicação entre containers por hostname (DNS automático)

### Decisões Técnicas

- **Flask**: Framework web leve e flexível, ideal para demonstrar endpoints dinâmicos com timestamps
- **Curl**: Cliente HTTP leve e eficiente, perfeito para testes de conectividade em containers
- **Docker Compose**: Orquestra os serviços e simplifica a configuração de rede em um único arquivo
- **Rede bridge customizada**: Permite que os containers se comuniquem por nome de serviço via DNS interno do Docker
- **depends_on**: Garante que o servidor inicia antes do cliente, evitando erros de conexão
- **Python 3.11-slim**: Imagem otimizada com tamanho reduzido e funcionalidades essenciais

## 🔄 Funcionamento Detalhado

### Fluxo de Comunicação

```
1. docker compose up é executado
2. Docker cria a rede 'rede-comunicacao' (bridge)
3. Container servidor-web inicia (Flask escutando em 0.0.0.0:8080)
4. Container cliente-requisicoes inicia (dependência satisfeita)
5. Cliente aguarda 5 segundos para garantir que o servidor está pronto
6. Cliente faz requisição HTTP: curl http://servidor-web:8080/
7. Servidor responde com timestamp atual
8. Cliente faz requisição HTTP: curl http://servidor-web:8080/status
9. Servidor responde com JSON contendo status e nome do serviço
10. Cliente aguarda 5 segundos
11. Ciclo se repete indefinidamente
```

## 🚀 Instruções de Execução

### Pré-requisitos

- Docker versão 20.10+
- Docker Compose integrado (comando `docker compose`)
- Linux/macOS ou Windows com WSL2

Verificar instalação:
```bash
docker --version
docker compose version
```

### Execução Passo a Passo

#### 1. Acessar o Diretório do Projeto

```bash
cd /desafio1
```

#### 2. Construir as Images

```bash
docker compose build
```

Isso construirá:
- `desafio1-servidor-web` (Python + Flask)
- `desafio1-cliente` (Curl + Script Shell)

#### 3. Iniciar os Containers

```bash
docker compose up
```

Para executar em background:
```bash
docker compose up -d
```

#### 4. Visualizar Logs em Tempo Real

```bash
docker compose logs -f
```

Saída esperada:
```
cliente-requisicoes  | ==========================================
cliente-requisicoes  | Requisição #1 - 2025-12-01 14:16:41
cliente-requisicoes  | ==========================================
cliente-requisicoes  | ✓ GET / - HTTP 200
cliente-requisicoes  | Servidor web ativo! Timestamp: 2025-12-01 14:16:41
cliente-requisicoes  | ✓ GET /status - HTTP 200
cliente-requisicoes  | {"servico":"servidor-web","status":"ok"}
cliente-requisicoes  | Estatísticas: Sucesso=1 | Falha=0
```

#### 5. Testar Manualmente em Outro Terminal

Enquanto os containers estão rodando:

```bash
# Testar endpoint raiz
curl http://localhost:8080/

# Testar endpoint de status
curl http://localhost:8080/status
```

Ou executar dentro do container cliente:
```bash
docker exec cliente-requisicoes curl http://servidor-web:8080/status
```

#### 6. Parar os Containers

```bash
docker compose down
```

Para remover volumes e networks também:
```bash
docker compose down -v
```

## 🔍 Verificação de Funcionamento

### Listar Containers em Execução

```bash
docker ps
```

Você deve ver:
- `servidor-web`
- `cliente-requisicoes`

### Inspecionar a Rede

```bash
docker network inspect desafio1_rede-comunicacao
```

Mostra os containers conectados e seus IPs internos.

### Testar Conectividade Entre Containers

```bash
docker exec cliente-requisicoes ping -c 2 servidor-web
```

Resposta esperada: pacotes enviados e recebidos com sucesso.

## 📝 Como o Projeto Funciona Tecnicamente

### Arquivo `docker-compose.yml`

Define dois serviços (`servidor-web` e `cliente`) na mesma rede bridge customizada. A chave `depends_on` garante ordem de inicialização.

### Arquivo `Dockerfile.servidor`

Cria uma imagem com Python 3.11, instala Flask via `requirements.txt` e executa a aplicação Flask.

### Arquivo `Dockerfile.cliente`

Cria uma imagem minimalista com Curl e executa o script shell que faz as requisições periódicas.

### Arquivo `servidor/app.py`

Aplicação Flask com dois endpoints:
- `/` retorna um timestamp em formato texto
- `/status` retorna um objeto JSON com informações do serviço

### Arquivo `cliente/script.sh`

Script shell que:
- Aguarda 5 segundos para o servidor ficar pronto
- Faz requisições HTTP usando Curl
- Monitora códigos HTTP e estatísticas de sucesso/falha
- Aguarda 10 segundos entre ciclos

### Arquivo `requirements.txt`

Define a dependência do Flask versão 3.0.0 para instalação durante o build.

### Resultados

#### 1. Logs:

![Logs](/desafio1/assets/Captura%20de%20tela%20de%202025-12-01%2013-32-31.png)

#### 2. Requisições:

![Requisições](/desafio1/assets/Captura%20de%20tela%20de%202025-12-01%2013-33-16.png)


## 🔗 Referências

- [Docker Networks Documentation](https://docs.docker.com/network/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Flask Official Documentation](https://flask.palletsprojects.com/)
- [Curl Manual](https://curl.se/docs/)