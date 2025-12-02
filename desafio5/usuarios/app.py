from flask import Flask, jsonify, request
from datetime import datetime, timedelta

app = Flask(__name__)

# Dados em memória
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
        "perfil": "vendedor"
    },
    {
        "id": 5,
        "nome": "Eva Martins",
        "email": "eva@email.com",
        "ativo": True,
        "data_cadastro": (datetime.now() - timedelta(days=7)).isoformat(),
        "perfil": "cliente"
    }
]

@app.route('/health', methods=['GET'])
def health():
    """Health check do microsserviço de usuários"""
    return jsonify({
        "status": "healthy",
        "servico": "Microsserviço de Usuários",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/api/usuarios', methods=['GET'])
def listar_usuarios():
    """
    Lista todos os usuários
    Query params opcionais:
    - ativo: true/false (filtrar por status)
    - perfil: administrador/editor/leitor/vendedor/cliente (filtrar por perfil)
    """
    try:
        usuarios = USUARIOS.copy()
        
        ativo = request.args.get('ativo')
        if ativo:
            ativo_bool = ativo.lower() == 'true'
            usuarios = [u for u in usuarios if u['ativo'] == ativo_bool]
        
        perfil = request.args.get('perfil')
        if perfil:
            usuarios = [u for u in usuarios if u['perfil'].lower() == perfil.lower()]
        
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
        
        if not dados or 'nome' not in dados or 'email' not in dados:
            return jsonify({"erro": "Nome e email são obrigatórios"}), 400
        
        if any(u['email'] == dados['email'] for u in USUARIOS):
            return jsonify({"erro": "Email já cadastrado"}), 409
        
        novo_id = max([u['id'] for u in USUARIOS]) + 1
        
        novo_usuario = {
            "id": novo_id,
            "nome": dados['nome'],
            "email": dados['email'],
            "ativo": dados.get('ativo', True),
            "data_cadastro": datetime.now().isoformat(),
            "perfil": dados.get('perfil', 'cliente')
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
        
        if 'nome' in dados:
            usuario['nome'] = dados['nome']
        if 'email' in dados:
            if any(u['id'] != usuario_id and u['email'] == dados['email'] for u in USUARIOS):
                return jsonify({"erro": "Email já cadastrado"}), 409
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
def estatisticas_usuarios():
    """Retorna estatísticas sobre os usuários"""
    try:
        total = len(USUARIOS)
        ativos = len([u for u in USUARIOS if u['ativo']])
        inativos = total - ativos
        
        perfis = {}
        for usuario in USUARIOS:
            perfil = usuario['perfil']
            perfis[perfil] = perfis.get(perfil, 0) + 1
        
        return jsonify({
            "total_usuarios": total,
            "usuarios_ativos": ativos,
            "usuarios_inativos": inativos,
            "percentual_ativos": round((ativos / total * 100) if total > 0 else 0, 2),
            "distribuicao_perfil": perfis,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
