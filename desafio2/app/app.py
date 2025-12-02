from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os

app = Flask(__name__)

# Configuração do banco de dados
DB_HOST = os.getenv('DB_HOST', 'db')
DB_USER = os.getenv('DB_USER', 'usuario')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'senha123')
DB_NAME = os.getenv('DB_NAME', 'aplicacao')
DB_PORT = os.getenv('DB_PORT', '5432')

def conectar_db():
    """Conecta ao banco de dados PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return None

@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    """Lista todos os usuários do banco"""
    conn = conectar_db()
    if not conn:
        return jsonify({"erro": "Conexão com banco falhou"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM usuarios ORDER BY id;")
        usuarios = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify([dict(u) for u in usuarios])
    except Exception as e:
        conn.close()
        return jsonify({"erro": str(e)}), 500

@app.route('/usuarios', methods=['POST'])
def criar_usuario():
    """Cria um novo usuário"""
    conn = conectar_db()
    if not conn:
        return jsonify({"erro": "Conexão com banco falhou"}), 500
    
    try:
        dados = request.get_json()
        nome = dados.get('nome')
        email = dados.get('email')
        
        if not nome or not email:
            return jsonify({"erro": "Nome e email são obrigatórios"}), 400
        
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, email) VALUES (%s, %s) RETURNING id, nome, email, data_criacao;",
            (nome, email)
        )
        novo_usuario = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "id": novo_usuario[0],
            "nome": novo_usuario[1],
            "email": novo_usuario[2],
            "data_criacao": novo_usuario[3].isoformat()
        }), 201
    except Exception as e:
        conn.close()
        return jsonify({"erro": str(e)}), 500

@app.route('/logs', methods=['GET'])
def listar_logs():
    """Lista todos os logs"""
    conn = conectar_db()
    if not conn:
        return jsonify({"erro": "Conexão com banco falhou"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM logs ORDER BY data_log DESC;")
        logs = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify([dict(l) for l in logs])
    except Exception as e:
        conn.close()
        return jsonify({"erro": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Verifica status da aplicação"""
    conn = conectar_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM usuarios;")
            total_usuarios = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            return jsonify({
                "status": "ok",
                "banco": "conectado",
                "total_usuarios": total_usuarios,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            conn.close()
            return jsonify({
                "status": "erro",
                "banco": "erro na consulta",
                "erro": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    else:
        return jsonify({
            "status": "erro",
            "banco": "desconectado",
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)