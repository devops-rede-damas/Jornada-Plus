"""
Funções auxiliares usadas em várias partes da aplicação.
"""
import os
from functools import wraps
from urllib.parse import urlparse
from flask import flash, redirect, url_for, current_app, request
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
        if not current_user.is_authenticated or current_user.nivel not in (1, 2):
            flash('Acesso negado. Apenas administradores podem acessar esta página.', 'danger')
            return redirect(url_for('principal.inicio'))
        return funcao(*args, **kwargs)
    return funcao_decorada


# Usuários bloqueados de ver/acessar a página de massagem.
USUARIOS_SEM_ACESSO_MASSAGEM = (2, 4)

# Usuários que não participam da fila (não aparecem na lista),
# mesmo que possam ver a página (ex.: o ID 12 vê, mas não entra na fila).
USUARIOS_FORA_DA_FILA = (2, 4, 12)


def _pagina_anterior_segura():
    """Retorna a última página do usuário (referrer) se for segura.

    Evita open redirect (só aceita o mesmo host) e evita loop, ignorando
    qualquer referrer que aponte para a própria área de massagem.
    Cai para a página inicial quando não há referrer confiável.
    """
    referrer = request.referrer
    if referrer:
        alvo = urlparse(referrer)
        atual = urlparse(request.host_url)
        mesmo_host = (not alvo.netloc) or (alvo.netloc == atual.netloc)
        if mesmo_host and '/massagem' not in alvo.path:
            return referrer
    return url_for('principal.inicio')


def massagem_permitido(funcao):
    """Decorador que bloqueia o acesso dos usuários sem permissão (IDs 2 e 4).

    Além de o link não aparecer no menu, se um desses usuários acessar a rota
    diretamente pela URL, ele é barrado e devolvido à última página em que estava.
    """
    @wraps(funcao)
    def funcao_decorada(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Faça login para acessar esta página.', 'warning')
            return redirect(url_for('autenticacao.login'))
        if current_user.id in USUARIOS_SEM_ACESSO_MASSAGEM:
            flash('Acesso negado.', 'danger')
            return redirect(_pagina_anterior_segura())
        return funcao(*args, **kwargs)
    return funcao_decorada


def garantir_pasta_upload():
    """Cria a pasta de upload se não existir."""
    pasta = current_app.config['PASTA_UPLOAD']
    if not os.path.exists(pasta):
        os.makedirs(pasta)
    return pasta
