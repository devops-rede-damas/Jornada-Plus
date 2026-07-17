"""
Rotas principais: página inicial, movidesk e envio de email ao líder.
"""
from datetime import datetime
from flask import Blueprint, render_template, jsonify, current_app
from flask_mail import Message
from app.banco import obter_conexao

principal = Blueprint('principal', __name__)


@principal.route('/')
def inicio():
    """Página inicial com regras e botão de notificação."""
    conexao = obter_conexao()
    try:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT ultima_notificacao FROM notificacao")
            resultado = cursor.fetchone()

        ultima_data = resultado['ultima_notificacao'].strftime('%d/%m/%y às %H:%M')
    finally:
        conexao.close()

    return render_template('index.html', last_data=ultima_data)


@principal.route('/enviar_email_lider', methods=['GET'])
def enviar_email_lider():
    """Envia email de notificação aos líderes e atualiza a data da última notificação."""
    from app import mail

    msg = Message(
        'Notificação de Aprovação',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[
            'edilson.souza@rededamas.com.br',
            'paula.araujo@rededamas.com.br'
        ]
    )
    msg.body = (
        'Olá Edilson Jr, seus funcionários solicitaram aprovações '
        'no sistema de ponto interno. Acesse o sistema para aprovar ou rejeitar.'
    )
    mail.send(msg)

    conexao = obter_conexao()
    try:
        with conexao.cursor() as cursor:
            agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            linhas = cursor.execute(
                "UPDATE notificacao SET ultima_notificacao = %s", (agora,)
            )
        conexao.commit()
    finally:
        conexao.close()

    if linhas:
        return jsonify({"message": "Email enviado e notificação atualizada com sucesso!"}), 200

    return jsonify({"message": "Erro ao atualizar notificação."}), 500


@principal.route('/movidesk')
def gv_movidesk():
    """Página de gestão à vista do Movidesk."""
    return render_template('gv_movidesk.html')
