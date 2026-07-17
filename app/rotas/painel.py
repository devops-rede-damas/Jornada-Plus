"""
Rotas do painel administrativo (dashboard).
"""
import os
import hashlib
import zipfile
from datetime import datetime
from flask import Blueprint, render_template, url_for, current_app
from flask_login import login_required, current_user

from app.banco import obter_conexao
from app.utilidades import admin_obrigatorio

painel = Blueprint('painel', __name__)


# --- Query base para listar colaboradores com saldo de horas ---
QUERY_COLABORADORES = """
    SELECT
        id,
        img_url,
        CONCAT(nome, ' ', sobrenome) AS nome,
        chapa,
        (
            SELECT IFNULL(
                TIME_FORMAT(
                    SEC_TO_TIME(
                        SUM(
                            CASE
                                WHEN LOWER(tipo) = 'horas extra'
                                    THEN TIME_TO_SEC(STR_TO_DATE(horas, '%H:%i'))
                                WHEN LOWER(tipo) IN ('saida antecipada', 'compensacao')
                                    THEN -TIME_TO_SEC(STR_TO_DATE(horas, '%H:%i'))
                                ELSE 0
                            END
                        )
                    ),
                    '%H:%i'
                ),
                '00:00'
            )
            FROM solicitacoes
            WHERE pessoa_id = users.id
            AND status = 'Aprovado'
        ) AS qtd,
        presente1,
        presente2,
        DATE_FORMAT(data_nascimento, '%d/%m') AS data_nascimento,
        (
            SELECT EXISTS(
                SELECT 1
                FROM solicitacoes
                WHERE pessoa_id = users.id
                AND status = 'pendente'
            )
        ) AS pendente
    FROM users
    WHERE {filtro}
    AND status = 1
    ORDER BY nome;
"""


@painel.route('/painel')
@login_required
@admin_obrigatorio
def painel_admin():
    """Dashboard com lista de colaboradores, saldos e gráfico."""
    # Define o filtro de acordo com o administrador logado
    if current_user.id == 3:
        filtro = "id <> 3"
    elif current_user.id == 4:
        filtro = "id NOT IN (1, 2, 3, 4, 10)"
    elif current_user.id == 34:
        filtro = "1 = 1"
    else:
        filtro = "id IN (1, 10)"
        

    query = QUERY_COLABORADORES.format(filtro=filtro)

    conexao = obter_conexao()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(query)
            colaboradores = cursor.fetchall()
    finally:
        conexao.close()

    return render_template('dash.html', colabs=colaboradores)


@painel.route('/tabela_solicitacoes/<int:colab_id>', methods=['GET'])
@login_required
@admin_obrigatorio
def tabela_solicitacoes(colab_id):
    """Exibe as solicitações de um colaborador específico (visão do admin)."""
    conexao = obter_conexao()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM solicitacoes WHERE pessoa_id = %s ORDER BY created_at DESC",
                (colab_id,)
            )
            lista_solicitacoes = cursor.fetchall()
    finally:
        conexao.close()

    # Prepara links de download para evidências
    for solicitacao in lista_solicitacoes:
        evidencias = (
            solicitacao['links_evidencias'].split(',')
            if solicitacao['links_evidencias'] else []
        )
        evidencias = [e.strip() for e in evidencias if e.strip()]

        if len(evidencias) == 1:
            solicitacao['download_url'] = url_for(
                'static', filename=f'arquivos/{evidencias[0]}'
            )
            solicitacao['download_name'] = evidencias[0]
            solicitacao['is_zip'] = False
        elif len(evidencias) > 1:
            pasta_arquivos = current_app.config['PASTA_UPLOAD']
            nome_zip = (
                f"{solicitacao['id']}_"
                f"{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}.zip"
            )
            caminho_zip = os.path.join(pasta_arquivos, nome_zip)
            os.makedirs(pasta_arquivos, exist_ok=True)

            with zipfile.ZipFile(caminho_zip, 'w') as zipf:
                for evidencia in evidencias:
                    caminho_arquivo = os.path.join(pasta_arquivos, evidencia)
                    if os.path.exists(caminho_arquivo):
                        zipf.write(caminho_arquivo, arcname=evidencia)

            solicitacao['download_url'] = url_for(
                'static', filename=f'arquivos/{nome_zip}'
            )
            solicitacao['download_name'] = 'arquivos.zip'
            solicitacao['is_zip'] = True
        else:
            solicitacao['download_url'] = None

    return render_template('tabela_solicitacoes.html', solicitacoes=lista_solicitacoes)
