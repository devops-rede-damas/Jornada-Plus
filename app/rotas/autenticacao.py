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


def _montar_email_recuperacao(link, nome=''):
    """Monta o corpo HTML (card clean) do email de recuperação de senha."""
    saudacao = f'Olá, {nome.split()[0]}!' if nome else 'Olá!'
    return f"""\
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background-color:#f8fafc;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f8fafc;padding:32px 12px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
               style="max-width:480px;background-color:#ffffff;border:1px solid #e5e7eb;border-radius:16px;overflow:hidden;font-family:'Segoe UI',Roboto,Helvetica,Arial,sans-serif;box-shadow:0 4px 6px -1px rgba(0,0,0,.08);">
          <tr>
            <td style="background:linear-gradient(135deg,#4f46e5,#3730a3);padding:28px 32px;">
              <p style="margin:0;color:#ffffff;font-size:18px;font-weight:700;letter-spacing:.2px;">Sistema de Aprovação</p>
            </td>
          </tr>
          <tr>
            <td style="padding:32px;">
              <p style="margin:0 0 8px;color:#111827;font-size:20px;font-weight:600;">Redefinição de senha</p>
              <p style="margin:0 0 20px;color:#4b5563;font-size:15px;line-height:1.6;">
                {saudacao} Recebemos uma solicitação para redefinir a senha da sua conta.
                Clique no botão abaixo para criar uma nova senha.
              </p>
              <table role="presentation" cellpadding="0" cellspacing="0" style="margin:8px 0 24px;">
                <tr>
                  <td style="border-radius:10px;background-color:#4f46e5;">
                    <a href="{link}" target="_blank"
                       style="display:inline-block;padding:13px 28px;color:#ffffff;font-size:15px;font-weight:600;text-decoration:none;border-radius:10px;">
                      Redefinir minha senha
                    </a>
                  </td>
                </tr>
              </table>
              <p style="margin:0 0 6px;color:#6b7280;font-size:13px;line-height:1.6;">
                Ou copie e cole este link no navegador:
              </p>
              <p style="margin:0 0 24px;word-break:break-all;">
                <a href="{link}" target="_blank" style="color:#4f46e5;font-size:13px;text-decoration:none;">{link}</a>
              </p>
              <div style="border-top:1px solid #e5e7eb;padding-top:16px;">
                <p style="margin:0;color:#9ca3af;font-size:12px;line-height:1.6;">
                  Este link é válido por <strong>1 hora</strong>. Se você não solicitou esta alteração,
                  ignore este email &mdash; sua senha permanecerá a mesma.
                </p>
              </div>
            </td>
          </tr>
          <tr>
            <td style="background-color:#f9fafb;padding:16px 32px;border-top:1px solid #e5e7eb;">
              <p style="margin:0;color:#9ca3af;font-size:12px;text-align:center;">
                Mensagem automática &middot; Sistema de Aprovação
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


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
                'Redefinição de senha — Sistema de Aprovação',
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[email]
            )
            link = url_for('autenticacao.alterar_senha', token=token, _external=True)
            nome_usuario = usuario.get('nome') or usuario.get('name') or ''
            msg.body = (
                'Recebemos uma solicitação para redefinir a sua senha.\n\n'
                f'Acesse o link a seguir para criar uma nova senha (válido por 1 hora):\n{link}\n\n'
                'Se você não solicitou esta alteração, ignore este email.'
            )
            msg.html = _montar_email_recuperacao(link, nome_usuario)
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
