"""
Configurações da aplicação.
Todas as credenciais são carregadas do arquivo .env
"""
import os
from dotenv import load_dotenv

# Carrega o arquivo .env da raiz do projeto
load_dotenv()


class Configuracao:
    """Configurações gerais da aplicação."""

    # --- Flask ---
    SECRET_KEY = os.getenv('CHAVE_SECRETA', 'chave-padrao-trocar-em-producao')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    FLASK_PORTA = int(os.getenv('FLASK_PORTA', 5001))

    # --- Banco de Dados MySQL ---
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USUARIO', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_SENHA', '')
    MYSQL_DB = os.getenv('MYSQL_BANCO', 'app_pontointerno')

    # --- Email (SMTP) ---
    MAIL_SERVER = os.getenv('EMAIL_SERVIDOR', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('EMAIL_PORTA', 587))
    MAIL_USE_TLS = os.getenv('EMAIL_USAR_TLS', 'true').lower() == 'true'
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('EMAIL_USUARIO', '')
    MAIL_PASSWORD = os.getenv('EMAIL_SENHA', '')
    MAIL_DEFAULT_SENDER = os.getenv('EMAIL_REMETENTE', '')

    # --- Upload de Arquivos ---
    PASTA_UPLOAD = os.path.join(os.path.dirname(__file__), 'static', 'arquivos')
    EXTENSOES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
