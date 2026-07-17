"""
Rotas de solicitações: listar, criar, editar, excluir e atualizar status.
"""
import os
from datetime import datetime
from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.banco import obter_conexao
from app.utilidades import arquivo_permitido, garantir_pasta_upload

solicitacoes = Blueprint('solicitacoes', __name__)


# --- Query reutilizável para calcular saldo de horas ---
QUERY_SALDO = """
    SELECT IFNULL(
        TIME_FORMAT(
            SEC_TO_TIME(
                SUM(
                    CASE
                        WHEN LOWER(tipo) = 'horas extra'
                            THEN TIME_TO_SEC(STR_TO_DATE(horas, '%%H:%%i'))
                        WHEN LOWER(tipo) IN ('saida antecipada', 'compensacao')
                            THEN -TIME_TO_SEC(STR_TO_DATE(horas, '%%H:%%i'))
                        ELSE 0
                    END
                )
            ),
            '%%H:%%i'
        ),
        '00:00'
    ) AS qtd
    FROM solicitacoes
    WHERE pessoa_id = %s
  AND status = 'Aprovado';
"""

QUERY_SALDO_PENDENTE = """
    SELECT IFNULL(
        TIME_FORMAT(
            SEC_TO_TIME(
                SUM(
                    CASE
                        WHEN LOWER(tipo) = 'horas extra'
                            THEN TIME_TO_SEC(STR_TO_DATE(horas, '%%H:%%i'))
                        WHEN LOWER(tipo) IN ('saida antecipada', 'compensacao')
                            THEN -TIME_TO_SEC(STR_TO_DATE(horas, '%%H:%%i'))
                        ELSE 0
                    END
                )
            ),
            '%%H:%%i'
        ),
        '00:00'
    ) AS qtd
    FROM solicitacoes
    WHERE pessoa_id = %s
  AND status IN ('Aprovado', 'pendente');
"""

@solicitacoes.route('/solicitacoes', methods=['GET', 'POST'])
@login_required
def listar_solicitacoes():
    """Lista as solicitações do usuário logado e permite criar/editar."""
    if request.method == 'POST':
        _salvar_solicitacao()
        return redirect(url_for('solicitacoes.listar_solicitacoes'))

    # Busca solicitações do usuário
    conexao = obter_conexao()
    try:
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT *,
                    DATE_FORMAT(dia_acontecimento, '%%d/%%m/%%Y') AS dia_acontecimento_fmt,
                    DATE_FORMAT(created_at, '%%d/%%m/%%Y') AS created_at_fmt
                FROM solicitacoes
                WHERE pessoa_id = %s
                ORDER BY created_at DESC
            """, (current_user.id,))
            lista_solicitacoes = cursor.fetchall()

            # Calcula saldo de horas aprovadas
            cursor.execute(QUERY_SALDO, (current_user.id,))
            saldo = cursor.fetchone()

            # Calcula saldo de horas pendentes
            cursor.execute(QUERY_SALDO_PENDENTE, (current_user.id,))
            saldo_pendente = cursor.fetchone()
    finally:
        conexao.close()

    return render_template(
        'solicitacoes.html',
        solicitacoes=lista_solicitacoes,
        saldo=saldo,
        saldo_pendente=saldo_pendente
    )


@solicitacoes.route('/nova_solicitacao', methods=['GET'])
@solicitacoes.route('/nova_solicitacao/<int:solicitacao_id>', methods=['GET'])
@login_required
def nova_solicitacao(solicitacao_id=None):
    """Formulário de nova solicitação ou edição de uma existente."""
    solicitacao = None

    if solicitacao_id:
        conexao = obter_conexao()
        try:
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM solicitacoes WHERE id = %s",
                    (solicitacao_id,)
                )
                solicitacao = cursor.fetchone()
        finally:
            conexao.close()

    return render_template('nova_solicitacao.html', solicitacao=solicitacao)


@solicitacoes.route('/excluir_solicitacao/<int:solicitacao_id>', methods=['GET'])
@login_required
def excluir_solicitacao(solicitacao_id):
    """Remove uma solicitação pelo ID."""
    conexao = obter_conexao()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                "DELETE FROM solicitacoes WHERE id = %s AND pessoa_id = %s",
                (solicitacao_id, current_user.id)
            )
        conexao.commit()
    finally:
        conexao.close()

    flash('Solicitação deletada com sucesso!', 'success')
    return redirect(url_for('solicitacoes.listar_solicitacoes'))


@solicitacoes.route('/atualizar_status', methods=['POST'])
@login_required
def atualizar_status():
    """Atualiza o status de uma solicitação (aprovado/rejeitado/pendente)."""
    dados = request.get_json()
    solicitacao_id = dados['solicitacao_id']
    novo_status = dados['status']

    conexao = obter_conexao()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                "UPDATE solicitacoes SET status = %s WHERE id = %s",
                (novo_status, solicitacao_id)
            )
        conexao.commit()
    finally:
        conexao.close()

    return jsonify({'success': True}), 200


# --- Função auxiliar interna ---

def _salvar_solicitacao():
    """Cria ou atualiza uma solicitação a partir dos dados do formulário."""
    tipo = request.form['tipo']
    justificativa = request.form['justificativa']
    horas = request.form['horas']
    data_acontecimento = request.form['data_acontecimento']
    pessoa_id = current_user.id

    # Processa arquivos enviados
    links_evidencias = []
    if 'arquivos' in request.files:
        pasta = garantir_pasta_upload()
        arquivos = request.files.getlist('arquivos')
        for arquivo in arquivos:
            if arquivo and arquivo_permitido(arquivo.filename):
                nome_seguro = secure_filename(arquivo.filename)
                nome_final = f"{datetime.now().strftime('%H%M%S')}_{nome_seguro}"
                arquivo.save(os.path.join(pasta, nome_final))
                links_evidencias.append(nome_final)

    links_str = ','.join(links_evidencias)

    conexao = obter_conexao()
    try:
        with conexao.cursor() as cursor:
            # Verifica se é edição ou criação
            if 'solicitacao_id' in request.form and request.form['solicitacao_id']:
                solicitacao_id = request.form['solicitacao_id']
                cursor.execute("""
                    UPDATE solicitacoes
                    SET tipo = %s, justificativa = %s, horas = %s,
                        dia_acontecimento = %s, links_evidencias = %s, status = 'pendente'
                    WHERE id = %s AND pessoa_id = %s
                """, (tipo, justificativa, horas, data_acontecimento,
                      links_str, solicitacao_id, pessoa_id))
                flash('Solicitação atualizada com sucesso!', 'success')
            else:
                cursor.execute("""
                    INSERT INTO solicitacoes
                        (pessoa_id, created_at, tipo, justificativa, horas,
                         dia_acontecimento, links_evidencias, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'pendente')
                """, (pessoa_id, datetime.now(), tipo, justificativa,
                      horas, data_acontecimento, links_str))
                flash('Solicitação cadastrada com sucesso!', 'success')
        conexao.commit()
    finally:
        conexao.close()
