from flask import Flask, jsonify, request
from datetime import datetime, timedelta
import random

app = Flask(__name__)
# Dados em memória
PEDIDOS = [
    {
        "id": 101,
        "usuario_id": 1,
        "data_pedido": (datetime.now() - timedelta(days=30)).isoformat(),
        "status": "entregue",
        "total": 299.90,
        "itens": [
            {"produto": "Laptop", "quantidade": 1, "preco": 299.90}
        ]
    },
    {
        "id": 102,
        "usuario_id": 2,
        "data_pedido": (datetime.now() - timedelta(days=15)).isoformat(),
        "status": "processando",
        "total": 89.50,
        "itens": [
            {"produto": "Mouse", "quantidade": 2, "preco": 44.75}
        ]
    },
    {
        "id": 103,
        "usuario_id": 4,
        "data_pedido": (datetime.now() - timedelta(days=5)).isoformat(),
        "status": "entregue",
        "total": 150.00,
        "itens": [
            {"produto": "Teclado", "quantidade": 1, "preco": 150.00}
        ]
    },
    {
        "id": 104,
        "usuario_id": 5,
        "data_pedido": (datetime.now() - timedelta(days=2)).isoformat(),
        "status": "enviado",
        "total": 49.99,
        "itens": [
            {"produto": "Headset", "quantidade": 1, "preco": 49.99}
        ]
    },
    {
        "id": 105,
        "usuario_id": 1,
        "data_pedido": datetime.now().isoformat(),
        "status": "pendente",
        "total": 199.99,
        "itens": [
            {"produto": "Monitor 27\"", "quantidade": 1, "preco": 199.99}
        ]
    }
]

@app.route('/health', methods=['GET'])
def health():
    """Health check do microsserviço de pedidos"""
    return jsonify({
        "status": "healthy",
        "servico": "Microsserviço de Pedidos",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/api/pedidos', methods=['GET'])
def listar_pedidos():
    """
    Lista todos os pedidos
    Query params opcionais:
    - usuario_id: ID do usuário para filtrar pedidos
    - status: status do pedido (pendente/processando/enviado/entregue)
    """
    try:
        pedidos = PEDIDOS.copy()
        
        usuario_id = request.args.get('usuario_id')
        if usuario_id:
            try:
                usuario_id_int = int(usuario_id)
                pedidos = [p for p in pedidos if p['usuario_id'] == usuario_id_int]
            except ValueError:
                return jsonify({"erro": "usuario_id deve ser um número"}), 400
        
        status = request.args.get('status')
        if status:
            pedidos = [p for p in pedidos if p['status'].lower() == status.lower()]
        
        return jsonify({
            "total": len(pedidos),
            "pedidos": pedidos,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/pedidos/<int:pedido_id>', methods=['GET'])
def obter_pedido(pedido_id):
    """Obtém detalhes de um pedido específico"""
    try:
        pedido = next((p for p in PEDIDOS if p['id'] == pedido_id), None)
        if not pedido:
            return jsonify({"erro": f"Pedido {pedido_id} não encontrado"}), 404
        
        return jsonify({
            "pedido": pedido,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/pedidos', methods=['POST'])
def criar_pedido():
    """Cria um novo pedido"""
    try:
        dados = request.get_json()
        
        if not dados or 'usuario_id' not in dados or 'itens' not in dados:
            return jsonify({"erro": "usuario_id e itens são obrigatórios"}), 400
        
        if not isinstance(dados['itens'], list) or len(dados['itens']) == 0:
            return jsonify({"erro": "itens deve ser uma lista não vazia"}), 400
        
        novo_id = max([p['id'] for p in PEDIDOS]) + 1
        
        total = sum(item.get('quantidade', 1) * item.get('preco', 0) for item in dados['itens'])
        
        novo_pedido = {
            "id": novo_id,
            "usuario_id": dados['usuario_id'],
            "data_pedido": datetime.now().isoformat(),
            "status": "pendente",
            "total": round(total, 2),
            "itens": dados['itens']
        }
        
        PEDIDOS.append(novo_pedido)
        
        return jsonify({
            "mensagem": "Pedido criado com sucesso",
            "pedido": novo_pedido,
            "timestamp": datetime.now().isoformat()
        }), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/pedidos/<int:pedido_id>', methods=['PUT'])
def atualizar_pedido(pedido_id):
    """Atualiza um pedido existente"""
    try:
        pedido = next((p for p in PEDIDOS if p['id'] == pedido_id), None)
        if not pedido:
            return jsonify({"erro": f"Pedido {pedido_id} não encontrado"}), 404
        
        dados = request.get_json()
        
        if 'status' in dados:
            status_validos = ['pendente', 'processando', 'enviado', 'entregue', 'cancelado']
            if dados['status'] not in status_validos:
                return jsonify({"erro": f"Status inválido. Válidos: {status_validos}"}), 400
            pedido['status'] = dados['status']
        
        return jsonify({
            "mensagem": "Pedido atualizado com sucesso",
            "pedido": pedido,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/pedidos/<int:pedido_id>', methods=['DELETE'])
def cancelar_pedido(pedido_id):
    """Cancela um pedido"""
    try:
        pedido = next((p for p in PEDIDOS if p['id'] == pedido_id), None)
        if not pedido:
            return jsonify({"erro": f"Pedido {pedido_id} não encontrado"}), 404
        
        if pedido['status'] == 'entregue':
            return jsonify({"erro": "Não é possível cancelar pedido entregue"}), 409
        
        pedido['status'] = 'cancelado'
        
        return jsonify({
            "mensagem": f"Pedido {pedido_id} cancelado com sucesso",
            "pedido": pedido,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/pedidos/usuario/<int:usuario_id>', methods=['GET'])
def listar_pedidos_usuario(usuario_id):
    """Lista todos os pedidos de um usuário específico"""
    try:
        pedidos = [p for p in PEDIDOS if p['usuario_id'] == usuario_id]
        
        return jsonify({
            "usuario_id": usuario_id,
            "total_pedidos": len(pedidos),
            "pedidos": pedidos,
            "valor_total": round(sum(p['total'] for p in pedidos), 2),
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/pedidos/estatisticas/resumo', methods=['GET'])
def estatisticas_pedidos():
    """Retorna estatísticas sobre os pedidos"""
    try:
        total = len(PEDIDOS)
        valor_total = sum(p['total'] for p in PEDIDOS)
        
        status_dist = {}
        for pedido in PEDIDOS:
            s = pedido['status']
            status_dist[s] = status_dist.get(s, 0) + 1
        
        return jsonify({
            "total_pedidos": total,
            "valor_total": round(valor_total, 2),
            "valor_medio": round(valor_total / total, 2) if total > 0 else 0,
            "distribuicao_status": status_dist,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)
