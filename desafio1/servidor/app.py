from flask import Flask
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def inicio():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Servidor web ativo! Timestamp: {timestamp}\n"

@app.route('/status')
def status():
    return {"status": "ok", "servico": "servidor-web"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)