from flask import Flask, jsonify, request
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os
import time
import json

app = Flask(__name__)

# Configurações
DB_HOST = os.getenv('DB_HOST', 'db')
DB_USER = os.getenv('DB_USER', 'usuario')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'senha123')
DB_NAME = os.getenv('DB_NAME', 'aplicacao')
DB_PORT = os.getenv('DB_PORT', '5432')

REDIS_HOST = os.getenv('REDIS_HOST', 'cache')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

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
        print(f"Erro ao conectar ao DB: {e}")
        return None

def conectar_redis():
    """Conecta ao Redis"""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        r.ping()
        return r
    except Exception as e:
        print(f"Erro ao conectar ao Redis: {e}")
        return None

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({"status": "healthy"}), 200

@app.route('/status', methods=['GET'])
def status():
    """Status de conexão dos serviços"""
    db_status = "conectado" if conectar_db() else "desconectado"
    redis_status = "conectado" if conectar_redis() else "desconectado"
    
    return jsonify({
        "status": "ok",
        "banco_dados": db_status,
        "cache": redis_status,
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/api/posts', methods=['GET'])
def listar_posts():
    """Lista posts do banco de dados"""
    conn = conectar_db()
    if not conn:
        return jsonify({"erro": "Conexão com banco falhou"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM posts ORDER BY id DESC;")
        posts = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify([dict(p) for p in posts])
    except Exception as e:
        conn.close()
        return jsonify({"erro": str(e)}), 500

@app.route('/api/posts', methods=['POST'])
def criar_post():
    """Cria novo post"""
    conn = conectar_db()
    if not conn:
        return jsonify({"erro": "Conexão com banco falhou"}), 500
    
    try:
        dados = request.get_json()
        titulo = dados.get('titulo')
        conteudo = dados.get('conteudo')
        autor = dados.get('autor', 'Anônimo')
        
        if not titulo or not conteudo:
            return jsonify({"erro": "Título e conteúdo são obrigatórios"}), 400
        
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO posts (titulo, conteudo, autor) VALUES (%s, %s, %s) RETURNING id, titulo, conteudo, autor, data_criacao;",
            (titulo, conteudo, autor)
        )
        novo_post = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        # Invalidar cache
        r = conectar_redis()
        if r:
            r.delete('posts_cache')
        
        return jsonify({
            "id": novo_post[0],
            "titulo": novo_post[1],
            "conteudo": novo_post[2],
            "autor": novo_post[3],
            "data_criacao": novo_post[4].isoformat()
        }), 201
    except Exception as e:
        conn.close()
        return jsonify({"erro": str(e)}), 500

@app.route('/api/posts/cache', methods=['GET'])
def listar_posts_cache():
    """Lista posts com cache"""
    r = conectar_redis()
    
    # Tentar obter do cache
    if r:
        cached = r.get('posts_cache')
        if cached:
            return jsonify({
                "fonte": "cache",
                "dados": json.loads(cached),
                "timestamp": datetime.now().isoformat()
            }), 200
    
    # Se não está em cache, buscar do banco
    conn = conectar_db()
    if not conn:
        return jsonify({"erro": "Conexão com banco falhou"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM posts ORDER BY id DESC;")
        posts = cursor.fetchall()
        cursor.close()
        conn.close()
        
        posts_dict = [dict(p) for p in posts]
        
        # Armazenar em cache por 60 segundos
        if r:
            r.setex('posts_cache', 60, json.dumps(posts_dict, default=str))
        
        return jsonify({
            "fonte": "banco_de_dados",
            "dados": posts_dict,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        conn.close()
        return jsonify({"erro": str(e)}), 500

@app.route('/api/contador', methods=['GET'])
def contador():
    """Contador armazenado no Redis"""
    r = conectar_redis()
    if not r:
        return jsonify({"erro": "Cache não disponível"}), 500
    
    try:
        contador_atual = r.incr('contador_requisicoes')
        return jsonify({
            "contador": contador_atual,
            "mensagem": f"Requisição número {contador_atual}",
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def stats():
    """Estatísticas gerais"""
    conn = conectar_db()
    r = conectar_redis()
    
    total_posts = 0
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM posts;")
            total_posts = cursor.fetchone()[0]
            cursor.close()
            conn.close()
        except:
            pass
    
    total_requisicoes = 0
    if r:
        try:
            total_requisicoes = int(r.get('contador_requisicoes') or 0)
        except:
            pass
    
    return jsonify({
        "total_posts": total_posts,
        "total_requisicoes": total_requisicoes,
        "timestamp": datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)