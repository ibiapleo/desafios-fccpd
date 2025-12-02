from flask import Flask, jsonify, request
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# Banco de dados em memória simulado
USUARIOS = [
    {
        "id": 1,
        "nome": "Alice Silva",
        "email": "alice@email.com",
        "ativo": True,
        "data_cadastro": (datetime.now() - timedelta(days=365)).isoformat(),
        "perfil": "administrador"
    },
    {
        "id": 2,
        "nome": "Bob Santos",
        "email": "bob@email.com",
        "ativo": True,
        "data_cadastro": (datetime.now() - timedelta(days=180)).isoformat(),
        "perfil": "editor"
    },
    {
        "id": 3,
        "nome": "Carol Oliveira",
        "email": "carol@email.com",
        "ativo": False,
        "data_cadastro": (datetime.now() - timedelta(days=90)).isoformat(),
        "perfil": "leitor"
    },
    {
        "id": 4,
        "nome": "David Costa",
        "email": "david@email.com",
        "ativo": True,
        "data_cadastro": (datetime.now() - timedelta(days=30)).isoformat(),
        "perfil": "editor"
    },
    {
        "id": 5,
        "nome": "Eva Martins",
        "email": "eva@email.com",
        "ativo": True,
        "data_cadastro": (datetime.now() - timedelta(days=7)).isoformat(),
        "perfil": "leitor"
    }
]

@app.route('/health', methods=['GET'])
def health():
    """Health check do serviço A"""
    return jsonify({
        "status": "healthy",
        "servico": "Serviço A - Gerenciamento de Usuários",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/api/usuarios', methods=['GET'])
def listar_usuarios():
    """
    Lista todos os usuários
    Query params opcionais:
    - ativo: true/false (filtrar por status)
    - perfil: administrador/editor/leitor (filtrar por perfil)
    """
    try:
        usuarios = USUARIOS.copy()
        
        # Filtro por status ativo
        ativo = request.args.get('ativo')
        if ativo:
            ativo_bool = ativo.lower() == 'true'
            usuarios = [u for u in usuarios if u['ativo'] == ativo_bool]
        
        # Filtro por perfil
        perfil = request.args.get('perfil')
        if perfil:
            usuarios = [u for u in usuarios if u['perfil'] == perfil]
        
        return jsonify({
            "total": len(usuarios),
            "usuarios": usuarios,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/usuarios/<int:usuario_id>', methods=['GET'])
def obter_usuario(usuario_id):
    """Obtém detalhes de um usuário específico"""
    try:
        usuario = next((u for u in USUARIOS if u['id'] == usuario_id), None)
        if not usuario:
            return jsonify({"erro": f"Usuário {usuario_id} não encontrado"}), 404
        
        return jsonify({
            "usuario": usuario,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/usuarios', methods=['POST'])
def criar_usuario():
    """Cria um novo usuário"""
    try:
        dados = request.get_json()
        
        # Validação
        if not dados.get('nome') or not dados.get('email'):
            return jsonify({"erro": "Nome e email são obrigatórios"}), 400
        
        # Novo usuário
        novo_id = max(u['id'] for u in USUARIOS) + 1
        novo_usuario = {
            "id": novo_id,
            "nome": dados.get('nome'),
            "email": dados.get('email'),
            "ativo": dados.get('ativo', True),
            "data_cadastro": datetime.now().isoformat(),
            "perfil": dados.get('perfil', 'leitor')
        }
        
        USUARIOS.append(novo_usuario)
        
        return jsonify({
            "mensagem": "Usuário criado com sucesso",
            "usuario": novo_usuario,
            "timestamp": datetime.now().isoformat()
        }), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/usuarios/<int:usuario_id>', methods=['PUT'])
def atualizar_usuario(usuario_id):
    """Atualiza um usuário existente"""
    try:
        usuario = next((u for u in USUARIOS if u['id'] == usuario_id), None)
        if not usuario:
            return jsonify({"erro": f"Usuário {usuario_id} não encontrado"}), 404
        
        dados = request.get_json()
        
        # Atualizar campos
        if 'nome' in dados:
            usuario['nome'] = dados['nome']
        if 'email' in dados:
            usuario['email'] = dados['email']
        if 'ativo' in dados:
            usuario['ativo'] = dados['ativo']
        if 'perfil' in dados:
            usuario['perfil'] = dados['perfil']
        
        return jsonify({
            "mensagem": "Usuário atualizado com sucesso",
            "usuario": usuario,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/usuarios/<int:usuario_id>', methods=['DELETE'])
def deletar_usuario(usuario_id):
    """Deleta um usuário"""
    try:
        usuario = next((u for u in USUARIOS if u['id'] == usuario_id), None)
        if not usuario:
            return jsonify({"erro": f"Usuário {usuario_id} não encontrado"}), 404
        
        USUARIOS.remove(usuario)
        
        return jsonify({
            "mensagem": f"Usuário {usuario_id} deletado com sucesso",
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/usuarios/estatisticas/resumo', methods=['GET'])
def estatisticas():
    """Retorna estatísticas dos usuários"""
    total = len(USUARIOS)
    ativos = len([u for u in USUARIOS if u['ativo']])
    inativos = total - ativos
    
    perfis = {}
    for u in USUARIOS:
        perfil = u['perfil']
        perfis[perfil] = perfis.get(perfil, 0) + 1
    
    return jsonify({
        "total_usuarios": total,
        "ativos": ativos,
        "inativos": inativos,
        "por_perfil": perfis,
        "timestamp": datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)