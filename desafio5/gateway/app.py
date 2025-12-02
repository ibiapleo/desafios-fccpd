from flask import Flask, jsonify, request
from functools import wraps
import requests
from datetime import datetime
import os

app = Flask(__name__)

USUARIOS_SERVICE_URL = os.getenv('USUARIOS_SERVICE_URL', 'http://localhost:5001')
PEDIDOS_SERVICE_URL = os.getenv('PEDIDOS_SERVICE_URL', 'http://localhost:5002')
REQUEST_TIMEOUT = 5

def fazer_requisicao(metodo, url, dados=None, params=None):
    """
    Faz uma requisição HTTP ao serviço especificado
    
    Args:
        metodo: GET, POST, PUT, DELETE
        url: URL completa do serviço
        dados: dados para POST/PUT (JSON)
        params: parâmetros de query
    
    Returns:
        tuple: (resposta_json, status_code) ou (erro, status_code)
    """
    try:
        if metodo == 'GET':
            resposta = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        elif metodo == 'POST':
            resposta = requests.post(url, json=dados, timeout=REQUEST_TIMEOUT)
        elif metodo == 'PUT':
            resposta = requests.put(url, json=dados, timeout=REQUEST_TIMEOUT)
        elif metodo == 'DELETE':
            resposta = requests.delete(url, timeout=REQUEST_TIMEOUT)
        else:
            return {"erro": "Método HTTP não suportado"}, 400
        
        if resposta.status_code == 204:
            return {}, 204
        
        try:
            dados_resposta = resposta.json()
        except:
            dados_resposta = {"mensagem": resposta.text}
        
        return dados_resposta, resposta.status_code
    
    except requests.exceptions.Timeout:
        return {"erro": f"Timeout ao conectar com o serviço: {url}"}, 504
    except requests.exceptions.ConnectionError:
        return {"erro": f"Erro ao conectar com o serviço: {url}"}, 503
    except Exception as e:
        return {"erro": f"Erro na requisição: {str(e)}"}, 500

def verificar_servicos():
    """Verifica se os microsserviços estão disponíveis"""
    try:
        resp_usuarios = requests.get(f"{USUARIOS_SERVICE_URL}/health", timeout=REQUEST_TIMEOUT)
        resp_pedidos = requests.get(f"{PEDIDOS_SERVICE_URL}/health", timeout=REQUEST_TIMEOUT)
        
        return {
            "usuarios": resp_usuarios.status_code == 200,
            "pedidos": resp_pedidos.status_code == 200
        }
    except:
        return {
            "usuarios": False,
            "pedidos": False
        }

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check do API Gateway"""
    servicos = verificar_servicos()
    status = "healthy" if all(servicos.values()) else "degraded"
    
    return jsonify({
        "status": status,
        "servico": "API Gateway",
        "servicos": servicos,
        "timestamp": datetime.now().isoformat()
    }), 200

# ============================================================================
# ENDPOINTS DE USUÁRIOS - Gateway expõe /users
# ============================================================================

@app.route('/users', methods=['GET'])
def gateway_listar_usuarios():
    """
    GET /users
    Lista todos os usuários
    Query params: ativo, perfil
    Encaminha para: GET /api/usuarios
    """
    params = {}
    if request.args.get('ativo'):
        params['ativo'] = request.args.get('ativo')
    if request.args.get('perfil'):
        params['perfil'] = request.args.get('perfil')
    
    dados, status_code = fazer_requisicao(
        'GET',
        f"{USUARIOS_SERVICE_URL}/api/usuarios",
        params=params
    )
    
    return jsonify(dados), status_code

@app.route('/users/<int:usuario_id>', methods=['GET'])
def gateway_obter_usuario(usuario_id):
    """
    GET /users/<id>
    Obtém detalhes de um usuário específico
    Encaminha para: GET /api/usuarios/<id>
    """
    dados, status_code = fazer_requisicao(
        'GET',
        f"{USUARIOS_SERVICE_URL}/api/usuarios/{usuario_id}"
    )
    
    return jsonify(dados), status_code

@app.route('/users', methods=['POST'])
def gateway_criar_usuario():
    """
    POST /users
    Cria um novo usuário
    Body: { nome, email, ativo (opcional), perfil (opcional) }
    Encaminha para: POST /api/usuarios
    """
    dados_entrada = request.get_json()
    
    dados, status_code = fazer_requisicao(
        'POST',
        f"{USUARIOS_SERVICE_URL}/api/usuarios",
        dados=dados_entrada
    )
    
    return jsonify(dados), status_code

@app.route('/users/<int:usuario_id>', methods=['PUT'])
def gateway_atualizar_usuario(usuario_id):
    """
    PUT /users/<id>
    Atualiza um usuário existente
    Encaminha para: PUT /api/usuarios/<id>
    """
    dados_entrada = request.get_json()
    
    dados, status_code = fazer_requisicao(
        'PUT',
        f"{USUARIOS_SERVICE_URL}/api/usuarios/{usuario_id}",
        dados=dados_entrada
    )
    
    return jsonify(dados), status_code

@app.route('/users/<int:usuario_id>', methods=['DELETE'])
def gateway_deletar_usuario(usuario_id):
    """
    DELETE /users/<id>
    Deleta um usuário
    Encaminha para: DELETE /api/usuarios/<id>
    """
    dados, status_code = fazer_requisicao(
        'DELETE',
        f"{USUARIOS_SERVICE_URL}/api/usuarios/{usuario_id}"
    )
    
    return jsonify(dados), status_code

@app.route('/users/stats', methods=['GET'])
def gateway_stats_usuarios():
    """
    GET /users/stats
    Retorna estatísticas dos usuários
    Encaminha para: GET /api/usuarios/estatisticas/resumo
    """
    dados, status_code = fazer_requisicao(
        'GET',
        f"{USUARIOS_SERVICE_URL}/api/usuarios/estatisticas/resumo"
    )
    
    return jsonify(dados), status_code

# ============================================================================
# ENDPOINTS DE PEDIDOS - Gateway expõe /orders
# ============================================================================

@app.route('/orders', methods=['GET'])
def gateway_listar_pedidos():
    """
    GET /orders
    Lista todos os pedidos
    Query params: usuario_id, status
    Encaminha para: GET /api/pedidos
    """
    params = {}
    if request.args.get('usuario_id'):
        params['usuario_id'] = request.args.get('usuario_id')
    if request.args.get('status'):
        params['status'] = request.args.get('status')
    
    dados, status_code = fazer_requisicao(
        'GET',
        f"{PEDIDOS_SERVICE_URL}/api/pedidos",
        params=params
    )
    
    return jsonify(dados), status_code

@app.route('/orders/<int:pedido_id>', methods=['GET'])
def gateway_obter_pedido(pedido_id):
    """
    GET /orders/<id>
    Obtém detalhes de um pedido específico
    Encaminha para: GET /api/pedidos/<id>
    """
    dados, status_code = fazer_requisicao(
        'GET',
        f"{PEDIDOS_SERVICE_URL}/api/pedidos/{pedido_id}"
    )
    
    return jsonify(dados), status_code

@app.route('/orders', methods=['POST'])
def gateway_criar_pedido():
    """
    POST /orders
    Cria um novo pedido
    Body: { usuario_id, itens }
    Encaminha para: POST /api/pedidos
    """
    dados_entrada = request.get_json()
    
    dados, status_code = fazer_requisicao(
        'POST',
        f"{PEDIDOS_SERVICE_URL}/api/pedidos",
        dados=dados_entrada
    )
    
    return jsonify(dados), status_code

@app.route('/orders/<int:pedido_id>', methods=['PUT'])
def gateway_atualizar_pedido(pedido_id):
    """
    PUT /orders/<id>
    Atualiza um pedido existente (principalmente status)
    Encaminha para: PUT /api/pedidos/<id>
    """
    dados_entrada = request.get_json()
    
    dados, status_code = fazer_requisicao(
        'PUT',
        f"{PEDIDOS_SERVICE_URL}/api/pedidos/{pedido_id}",
        dados=dados_entrada
    )
    
    return jsonify(dados), status_code

@app.route('/orders/<int:pedido_id>', methods=['DELETE'])
def gateway_deletar_pedido(pedido_id):
    """
    DELETE /orders/<id>
    Cancela um pedido
    Encaminha para: DELETE /api/pedidos/<id>
    """
    dados, status_code = fazer_requisicao(
        'DELETE',
        f"{PEDIDOS_SERVICE_URL}/api/pedidos/{pedido_id}"
    )
    
    return jsonify(dados), status_code

@app.route('/orders/user/<int:usuario_id>', methods=['GET'])
def gateway_pedidos_usuario(usuario_id):
    """
    GET /orders/user/<id>
    Lista todos os pedidos de um usuário
    Encaminha para: GET /api/pedidos/usuario/<id>
    """
    dados, status_code = fazer_requisicao(
        'GET',
        f"{PEDIDOS_SERVICE_URL}/api/pedidos/usuario/{usuario_id}"
    )
    
    return jsonify(dados), status_code

@app.route('/orders/stats', methods=['GET'])
def gateway_stats_pedidos():
    """
    GET /orders/stats
    Retorna estatísticas dos pedidos
    Encaminha para: GET /api/pedidos/estatisticas/resumo
    """
    dados, status_code = fazer_requisicao(
        'GET',
        f"{PEDIDOS_SERVICE_URL}/api/pedidos/estatisticas/resumo"
    )
    
    return jsonify(dados), status_code

# ============================================================================
# ENDPOINTS DE COMPOSIÇÃO - Orquestra os dois serviços
# ============================================================================

@app.route('/dashboard', methods=['GET'])
def gateway_dashboard():
    """
    GET /dashboard
    Dashboard consolidado com informações de usuários e pedidos
    Orquestra chamadas aos dois serviços
    """
    usuarios_resp, usuarios_status = fazer_requisicao(
        'GET',
        f"{USUARIOS_SERVICE_URL}/api/usuarios/estatisticas/resumo"
    )
    
    pedidos_resp, pedidos_status = fazer_requisicao(
        'GET',
        f"{PEDIDOS_SERVICE_URL}/api/pedidos/estatisticas/resumo"
    )
    
    if usuarios_status != 200 or pedidos_status != 200:
        return jsonify({
            "erro": "Erro ao obter dados dos serviços",
            "usuarios_status": usuarios_status,
            "pedidos_status": pedidos_status
        }), 503
    
    return jsonify({
        "titulo": "Dashboard de Usuários e Pedidos",
        "usuarios": usuarios_resp,
        "pedidos": pedidos_resp,
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/usuarios-com-pedidos', methods=['GET'])
def gateway_usuarios_com_pedidos():
    """
    GET /usuarios-com-pedidos
    Retorna lista de usuários com seus respectivos pedidos
    Orquestra chamadas aos dois serviços
    """
    try:
        usuarios_resp, usuarios_status = fazer_requisicao(
            'GET',
            f"{USUARIOS_SERVICE_URL}/api/usuarios"
        )
        
        if usuarios_status != 200:
            return jsonify({"erro": "Erro ao obter usuários"}), usuarios_status
        
        usuarios = usuarios_resp.get('usuarios', [])
        resultado = []
        
        for usuario in usuarios:
            usuario_id = usuario['id']
            pedidos_resp, pedidos_status = fazer_requisicao(
                'GET',
                f"{PEDIDOS_SERVICE_URL}/api/pedidos/usuario/{usuario_id}"
            )
            
            usuario_com_pedidos = {
                "usuario": usuario,
                "pedidos": pedidos_resp.get('pedidos', []) if pedidos_status == 200 else [],
                "total_pedidos": pedidos_resp.get('total_pedidos', 0) if pedidos_status == 200 else 0,
                "valor_total_pedidos": pedidos_resp.get('valor_total', 0) if pedidos_status == 200 else 0
            }
            resultado.append(usuario_com_pedidos)
        
        return jsonify({
            "total_usuarios": len(usuarios),
            "usuarios_com_pedidos": resultado,
            "timestamp": datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ============================================================================
# ROTA RAIZ E DOCUMENTAÇÃO
# ============================================================================

@app.route('/', methods=['GET'])
def documentacao():
    """Retorna documentação da API Gateway"""
    return jsonify({
        "titulo": "API Gateway - Arquitetura de Microsserviços",
        "versao": "1.0.0",
        "descricao": "Gateway centralizando acesso a microsserviços de usuários e pedidos",
        "endpoints": {
            "saude": {
                "GET /health": "Health check do gateway e seus serviços"
            },
            "usuarios": {
                "GET /users": "Lista todos os usuários",
                "GET /users/<id>": "Obtém detalhes de um usuário",
                "POST /users": "Cria novo usuário",
                "PUT /users/<id>": "Atualiza usuário",
                "DELETE /users/<id>": "Deleta usuário",
                "GET /users/stats": "Estatísticas de usuários"
            },
            "pedidos": {
                "GET /orders": "Lista todos os pedidos",
                "GET /orders/<id>": "Obtém detalhes de um pedido",
                "GET /orders/user/<usuario_id>": "Lista pedidos de um usuário",
                "POST /orders": "Cria novo pedido",
                "PUT /orders/<id>": "Atualiza pedido",
                "DELETE /orders/<id>": "Cancela pedido",
                "GET /orders/stats": "Estatísticas de pedidos"
            },
            "composicao": {
                "GET /dashboard": "Dashboard consolidado",
                "GET /usuarios-com-pedidos": "Usuários com seus pedidos"
            }
        },
        "servicos_internos": {
            "usuarios_service": USUARIOS_SERVICE_URL,
            "pedidos_service": PEDIDOS_SERVICE_URL
        }
    }), 200

@app.errorhandler(404)
def nao_encontrado(error):
    """Tratamento para rotas não encontradas"""
    return jsonify({
        "erro": "Rota não encontrada",
        "mensagem": "Visite GET / para documentação",
        "timestamp": datetime.now().isoformat()
    }), 404

@app.errorhandler(405)
def metodo_nao_permitido(error):
    """Tratamento para métodos não permitidos"""
    return jsonify({
        "erro": "Método não permitido",
        "timestamp": datetime.now().isoformat()
    }), 405

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
