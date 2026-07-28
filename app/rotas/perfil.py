"""
Rotas do perfil do usuário.
"""
import os
import shutil
from datetime import datetime
from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.banco import obter_conexao
from app.utilidades import arquivo_permitido

perfil_bp = Blueprint('perfil', __name__)


@perfil_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """Exibe e permite editar o perfil do usuário (presentes de aniversário)."""
    if request.method == 'POST':
        presente1 = request.form.get('presente1', '')
        presente2 = request.form.get('presente2', '')

        # Processa imagem de perfil se enviada
        nova_img = None
        if 'foto_perfil' in request.files:
            arquivo = request.files['foto_perfil']
            if arquivo and arquivo.filename and arquivo_permitido(arquivo.filename):
                pasta_img = os.path.join(current_app.root_path, 'static', 'img')
                pasta_backup = os.path.join(pasta_img, 'backup')
                os.makedirs(pasta_backup, exist_ok=True)

                # Busca imagem atual para backup
                conexao = obter_conexao()
                try:
                    with conexao.cursor() as cursor:
                        cursor.execute("SELECT img_url FROM users WHERE id = %s", (current_user.id,))
                        atual = cursor.fetchone()
                finally:
                    conexao.close()

                if atual and atual['img_url'] and atual['img_url'] != 'default.png':
                    img_atual_path = os.path.join(pasta_img, atual['img_url'])
                    if os.path.exists(img_atual_path):
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        nome_backup = f"{timestamp}_{atual['img_url']}"
                        shutil.copy2(img_atual_path, os.path.join(pasta_backup, nome_backup))

                # Salva nova imagem
                nome_seguro = secure_filename(arquivo.filename)
                extensao = nome_seguro.rsplit('.', 1)[1].lower()
                nova_img = f"user_{current_user.id}.{extensao}"
                arquivo.save(os.path.join(pasta_img, nova_img))

        conexao = obter_conexao()
        try:
            with conexao.cursor() as cursor:
                if nova_img:
                    cursor.execute(
                        "UPDATE users SET presente1 = %s, presente2 = %s, img_url = %s WHERE id = %s",
                        (presente1, presente2, nova_img, current_user.id)
                    )
                else:
                    cursor.execute(
                        "UPDATE users SET presente1 = %s, presente2 = %s WHERE id = %s",
                        (presente1, presente2, current_user.id)
                    )
            conexao.commit()
        finally:
            conexao.close()

        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('perfil.perfil'))

    conexao = obter_conexao()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT u.*, n.nivel AS nivel_nome "
                "FROM users u "
                "LEFT JOIN nivel n ON n.id = u.nivel "
                "WHERE u.id = %s",
                (current_user.id,)
            )
            dados_perfil = cursor.fetchone()
    finally:
        conexao.close()

    return render_template('perfil.html', perfil=dados_perfil)
