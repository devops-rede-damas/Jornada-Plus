"""
Funções auxiliares usadas em várias partes da aplicação.
"""
import os
from functools import wraps
from flask import flash, redirect, url_for, current_app
from flask_login import current_user


def arquivo_permitido(nome_arquivo):
    """Verifica se a extensão do arquivo é permitida."""
    extensoes = current_app.config['EXTENSOES_PERMITIDAS']
    return '.' in nome_arquivo and \
        nome_arquivo.rsplit('.', 1)[1].lower() in extensoes


def admin_obrigatorio(funcao):
    """Decorador que restringe acesso apenas a administradores."""
    @wraps(funcao)
    def funcao_decorada(*args, **kwargs):
        if not current_user.is_authenticated or current_user.perfil != 'admin':
            flash('Acesso negado. Apenas administradores podem acessar esta página.', 'danger')
            return redirect(url_for('principal.inicio'))
        return funcao(*args, **kwargs)
    return funcao_decorada


def garantir_pasta_upload():
    """Cria a pasta de upload se não existir."""
    pasta = current_app.config['PASTA_UPLOAD']
    if not os.path.exists(pasta):
        os.makedirs(pasta)
    return pasta
