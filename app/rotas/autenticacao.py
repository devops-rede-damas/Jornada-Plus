"""
Rotas de autenticação: login, logout, reset e troca de senha.
"""
from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
from flask_login import login_user, logout_user, login_required
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from app.banco import obter_conexao
from app.modelos import Usuario

autenticacao = Blueprint('autenticacao', __name__)


@autenticacao.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login com chapa e senha."""
    if request.method == 'POST':
        chapa = request.form['chapa']
        senha = request.form['senha']

        conexao = obter_conexao()
        try:
            with conexao.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE chapa = %s AND status = 1", (chapa,))
                dados_usuario = cursor.fetchone()
        finally:
            conexao.close()

        if dados_usuario and check_password_hash(dados_usuario['senha_hash'], senha):
            usuario = Usuario.criar_de_dicionario(dados_usuario)
            login_user(usuario)
            flash('Login efetuado com sucesso!', 'success')

            if usuario.nivel in (1, 2):
                return redirect(url_for('painel.painel_admin'))
            return redirect(url_for('solicitacoes.listar_solicitacoes'))
        else:
            flash('Dados inválidos.', 'danger')

    return render_template('login.html')


@autenticacao.route('/logout')
@login_required
def logout():
    """Encerra a sessão do usuário."""
    logout_user()
    flash('Sessão encerrada com sucesso.', 'success')
    return redirect(url_for('principal.inicio'))


@autenticacao.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    """Envia link de recuperação de senha por email."""
    if request.method == 'POST':
        email = request.form['email']

        conexao = obter_conexao()
        try:
            with conexao.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s AND status = 1", (email,))
                usuario = cursor.fetchone()
        finally:
            conexao.close()

        if usuario:
            from app import mail
            s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = s.dumps(email, salt='email-reset')

            msg = Message(
                'Solicitação de alteração de senha',
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[email]
            )
            link = url_for('autenticacao.alterar_senha', token=token, _external=True)
            msg.body = f'Para redefinir sua senha, clique no link a seguir: {link}'
            mail.send(msg)

            flash('Um email foi enviado com instruções para redefinir sua senha.', 'info')
            return redirect(url_for('autenticacao.login'))
        else:
            flash('Nenhuma conta encontrada com este email.', 'danger')

    return render_template('reset_password.html')


@autenticacao.route('/alterar_senha/<token>', methods=['GET', 'POST'])
def alterar_senha(token):
    """Formulário para definir nova senha a partir do token enviado por email."""
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    try:
        email = s.loads(token, salt='email-reset', max_age=3600)
    except SignatureExpired:
        flash('O link de redefinição de senha expirou.', 'danger')
        return redirect(url_for('autenticacao.recuperar_senha'))

    if request.method == 'POST':
        nova_senha = request.form['senha']
        hash_senha = generate_password_hash(nova_senha)

        conexao = obter_conexao()
        try:
            with conexao.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET senha_hash = %s WHERE email = %s",
                    (hash_senha, email)
                )
            conexao.commit()
        finally:
            conexao.close()

        flash('Sua senha foi atualizada com sucesso!', 'success')
        return redirect(url_for('autenticacao.login'))

    return render_template('change_password.html')
