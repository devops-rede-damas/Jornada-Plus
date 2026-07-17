"""
Ponto de entrada da aplicação.
Uso: python run.py
"""
from app import criar_app

aplicacao = criar_app()

if __name__ == '__main__':
    aplicacao.run(
        host='0.0.0.0',
        port=aplicacao.config['FLASK_PORTA'],
        debug=aplicacao.config['FLASK_DEBUG']
    )
