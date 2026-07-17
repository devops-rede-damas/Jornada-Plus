"""
Módulo de conexão com o banco de dados MySQL.
Centraliza a criação e o fechamento de conexões.
"""
import pymysql
from flask import current_app


def obter_conexao():
    """
    Cria e retorna uma conexão com o banco de dados MySQL.
    Usa as configurações da aplicação Flask ativa.
    """
    return pymysql.connect(
        host=current_app.config['MYSQL_HOST'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD'],
        db=current_app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )
