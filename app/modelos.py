"""
Modelo de usuário para autenticação com Flask-Login.
"""
from flask_login import UserMixin
from werkzeug.security import check_password_hash


class Usuario(UserMixin):
    """Representa um usuário do sistema."""

    def __init__(self, id, chapa, nome, sobrenome, email, senha_hash,
                 perfil, data_nascimento, presente1, presente2, img_url):
        self.id = id
        self.chapa = chapa
        self.nome = nome
        self.sobrenome = sobrenome
        self.email = email
        self.senha_hash = senha_hash
        self.perfil = perfil
        self.data_nascimento = data_nascimento
        self.presente1 = presente1
        self.presente2 = presente2
        self.img_url = img_url

    def verificar_senha(self, senha):
        """Compara a senha informada com o hash armazenado."""
        return check_password_hash(self.senha_hash, senha)

    @staticmethod
    def criar_de_dicionario(dados):
        """Cria uma instância de Usuario a partir de um dicionário do banco."""
        if not dados:
            return None
        return Usuario(
            id=dados['id'],
            chapa=dados['chapa'],
            nome=dados['nome'],
            sobrenome=dados['sobrenome'],
            email=dados['email'],
            senha_hash=dados['senha_hash'],
            perfil=dados['perfil'],
            data_nascimento=dados['data_nascimento'],
            presente1=dados['presente1'],
            presente2=dados['presente2'],
            img_url=dados['img_url'],
        )
