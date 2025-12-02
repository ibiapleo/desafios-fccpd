from flask import Flask, jsonify
import requests
from datetime import datetime
import time

app = Flask(__name__)

SERVICO_A_URL = "http://servico-a:5001"

def obter_usuarios_servico_a():
    """Faz requisição ao Serviço A para obter usuários"""
    try:
        resposta = requests.get(f"{SERVICO_A_URL}/api/usuarios", timeout=5)
        if resposta.status_code == 200:
            return resposta.json()
        else:
            return None
    except Exception as e:
        print(f"Erro ao conectar ao Serviço A: {e}")
        return None

def obter_usuario_servico_a(usuario_id):
    """Faz requisição ao Serviço A para obter usuário específico"""
    try:
        resposta = requests.get(f"{SERVICO_A_URL}/api/usuarios/{usuario_id}", timeout=5)
        if resposta.status_code == 200:
            return resposta.json()
        else:
            return None
    except Exception as e:
        print(f"Erro ao conectar ao Serviço A: {e}")
        return None

def obter_estatisticas_servico_a():
    """Faz requisição ao Serviço A para obter estatísticas"""
    try:
        resposta = requests.get(f"{SERVICO_A_URL}/api/usuarios/estatisticas/resumo", timeout=5)
        if resposta.status_code == 200:
            return resposta.json()
        else:
            return None
    except Exception as e:
        print(f"Erro ao conectar ao Serviço A: {e}")
        return None

@app.route('/health', methods=['GET'])
def health():
    """Health check do serviço B"""
    try:
        resposta = requests.get(f"{SERVICO_A_URL}/health", timeout=2)
        servico_a_status = "disponível" if resposta.status_code == 200 else "indisponível"
    except:
        servico_a_status = "indisponível"
    
    return jsonify({
        "status": "healthy",
        "servico": "Serviço B - Análise e Visualização",
        "servico_a": servico_a_status,
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/api/usuarios/formatados', methods=['GET'])
def usuarios_formatados():
    """
    Consome Serviço A e retorna usuários com informações formatadas
    Mostra: nome, email, status, tempo desde cadastro, perfil
    """
    try:
        dados = obter_usuarios_servico_a()
        
        if not dados:
            return jsonify({
                "erro": "Não foi possível conectar ao Serviço A",
                "servico_a_url": SERVICO_A_URL
            }), 503
        
        usuarios = dados.get('usuarios', [])
        
        usuarios_formatados = []
        for u in usuarios:
            data_cadastro = datetime.fromisoformat(u['data_cadastro'])
            dias_cadastro = (datetime.now() - data_cadastro).days
            
            usuarios_formatados.append({
                "id": u['id'],
                "nome": u['nome'],
                "email": u['email'],
                "status": "Ativo" if u['ativo'] else "Inativo",
                "perfil": u['perfil'].capitalize(),
                "cadastro": f"{dias_cadastro} dias atrás" if dias_cadastro > 0 else "Hoje",
                "data_completa": u['data_cadastro']
            })
        
        return jsonify({
            "total": len(usuarios_formatados),
            "usuarios": usuarios_formatados,
            "origem": "Serviço A",
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/usuarios/relatorio', methods=['GET'])
def usuarios_relatorio():
    """
    Cria um relatório detalhado consumindo dados do Serviço A
    Inclui: resumo, usuários ativos/inativos, breakdown por perfil
    """
    try:
        dados_usuarios = obter_usuarios_servico_a()
        dados_stats = obter_estatisticas_servico_a()
        
        if not dados_usuarios or not dados_stats:
            return jsonify({
                "erro": "Não foi possível conectar ao Serviço A"
            }), 503
        
        usuarios = dados_usuarios.get('usuarios', [])
        stats = dados_stats
        
        ativos = [u for u in usuarios if u['ativo']]
        inativos = [u for u in usuarios if not u['ativo']]
        
        ativos_formatados = []
        for u in ativos:
            data_cadastro = datetime.fromisoformat(u['data_cadastro'])
            dias = (datetime.now() - data_cadastro).days
            ativos_formatados.append({
                "nome": u['nome'],
                "email": u['email'],
                "perfil": u['perfil'].upper(),
                "ativo_a_dias": dias
            })
        
        inativos_formatados = []
        for u in inativos:
            inativos_formatados.append({
                "nome": u['nome'],
                "email": u['email'],
                "perfil": u['perfil'].upper()
            })
        
        relatorio = {
            "titulo": "Relatório de Usuários",
            "resumo": {
                "total_usuarios": stats['total_usuarios'],
                "usuarios_ativos": stats['ativos'],
                "usuarios_inativos": stats['inativos'],
                "percentual_ativos": round((stats['ativos'] / stats['total_usuarios'] * 100), 2) if stats['total_usuarios'] > 0 else 0
            },
            "distribuicao_perfil": stats['por_perfil'],
            "usuarios_ativos": ativos_formatados,
            "usuarios_inativos": inativos_formatados,
            "origem": "Consumido do Serviço A",
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(relatorio), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/usuarios/<int:usuario_id>/detalhes', methods=['GET'])
def usuario_detalhes(usuario_id):
    """
    Consome Serviço A para obter detalhes de um usuário específico
    Adiciona informações calculadas como tempo de atividade
    """
    try:
        dados = obter_usuario_servico_a(usuario_id)
        
        if not dados:
            return jsonify({
                "erro": f"Usuário {usuario_id} não encontrado"
            }), 404
        
        usuario = dados.get('usuario')
        data_cadastro = datetime.fromisoformat(usuario['data_cadastro'])
        dias_cadastro = (datetime.now() - data_cadastro).days
        horas_cadastro = (datetime.now() - data_cadastro).seconds // 3600
        
        detalhes = {
            "id": usuario['id'],
            "nome": usuario['nome'],
            "email": usuario['email'],
            "perfil": usuario['perfil'].upper(),
            "status": {
                "ativo": usuario['ativo'],
                "label": "Ativo" if usuario['ativo'] else "Inativo"
            },
            "tempo_inscricao": {
                "dias": dias_cadastro,
                "horas": horas_cadastro,
                "formatado": f"{dias_cadastro} dias e {horas_cadastro} horas"
            },
            "data_cadastro_completa": usuario['data_cadastro'],
            "origem": "Consumido do Serviço A",
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(detalhes), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/status-servicos', methods=['GET'])
def status_servicos():
    """
    Verifica o status de conectividade com o Serviço A
    Útil para debugging
    """
    try:
        inicio = time.time()
        resposta = requests.get(f"{SERVICO_A_URL}/health", timeout=5)
        tempo_resposta = (time.time() - inicio) * 1000
        
        if resposta.status_code == 200:
            servico_a_info = resposta.json()
            status = "disponível"
        else:
            servico_a_info = {"erro": "Status não 200"}
            status = "indisponível"
    except Exception as e:
        servico_a_info = {"erro": str(e)}
        tempo_resposta = None
        status = "indisponível"
    
    return jsonify({
        "servico_b": {
            "status": "healthy",
            "porta": 5002
        },
        "servico_a": {
            "url": SERVICO_A_URL,
            "status": status,
            "tempo_resposta_ms": tempo_resposta,
            "info": servico_a_info
        },
        "timestamp": datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)