"""
Fábrica da aplicação Flask (Application Factory).
Centraliza a criação e configuração do app.
"""
import pymysql
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail

from app.config import Configuracao
from app.banco import obter_conexao
from app.modelos import Usuario

# Extensões globais (inicializadas sem app)
login_manager = LoginManager()
mail = Mail()


def criar_app():
    """Cria e configura a aplicação Flask."""
    app = Flask(__name__)
    app.config.from_object(Configuracao)

    # Configurações extras que o Flask precisa em app.config
    app.config['UPLOAD_FOLDER'] = Configuracao.PASTA_UPLOAD

    # Inicializa PyMySQL como substituto do MySQLdb
    pymysql.install_as_MySQLdb()

    # --- Inicializa extensões ---
    login_manager.init_app(app)
    login_manager.login_view = 'autenticacao.login'
    login_manager.login_message = 'Faça login para acessar esta página.'
    login_manager.login_message_category = 'warning'

    mail.init_app(app)

    # --- Carrega usuário para sessão (Flask-Login) ---
    @login_manager.user_loader
    def carregar_usuario(user_id):
        conexao = obter_conexao()
        try:
            with conexao.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s AND status = 1", (user_id,))
                dados = cursor.fetchone()
        finally:
            conexao.close()
        return Usuario.criar_de_dicionario(dados)

    # --- Registra os Blueprints (rotas) ---
    from app.rotas.principal import principal
    from app.rotas.autenticacao import autenticacao
    from app.rotas.solicitacoes import solicitacoes
    from app.rotas.painel import painel
    from app.rotas.perfil import perfil_bp
    from app.rotas.aniversariantes import aniversariantes
    from app.rotas.massagem import massagem
    from app.rotas.usuarios import usuarios

    app.register_blueprint(principal)
    app.register_blueprint(autenticacao)
    app.register_blueprint(solicitacoes)
    app.register_blueprint(painel)
    app.register_blueprint(perfil_bp)
    app.register_blueprint(aniversariantes)
    app.register_blueprint(massagem)
    app.register_blueprint(usuarios)

    return app
