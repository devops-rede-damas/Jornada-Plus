"""
Rotas de administração de usuários (somente Administrador — nível 1).

Permite listar (Todos / Ativos / Inativos), criar e editar usuários, incluindo
troca de nome, email, senha, imagem, nível e coordenador responsável.
"""
import os
from flask import (
    Blueprint, render_template, flash, redirect, url_for, request, current_app
)
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import pymysql

from app.banco import obter_conexao
from app.utilidades import admin_estrito, arquivo_permitido

usuarios = Blueprint('usuarios', __name__)


def _salvar_imagem(arquivo, user_id):
    """Salva a foto do usuário como user_<id>.<ext> e retorna o nome do arquivo."""
    if not (arquivo and arquivo.filename and arquivo_permitido(arquivo.filename)):
        return None
    pasta_img = os.path.join(current_app.root_path, 'static', 'img')
    os.makedirs(pasta_img, exist_ok=True)
    nome_seguro = secure_filename(arquivo.filename)
    extensao = nome_seguro.rsplit('.', 1)[1].lower()
    nome = f"user_{user_id}.{extensao}"
    arquivo.save(os.path.join(pasta_img, nome))
    return nome


def _definir_coordenador(cursor, func_id, coord_id, autor_id):
    """Define o coordenador responsável de um usuário na tabela coord_func.

    Desativa quaisquer vínculos ativos anteriores e ativa (ou cria) o vínculo
    com o coordenador escolhido. Se coord_id for vazio, apenas remove os vínculos.
    """
    cursor.execute(
        "UPDATE coord_func SET status = 0, modificado_por = %s "
        "WHERE id_func = %s AND status = 1",
        (autor_id, func_id)
    )
    if coord_id:
        cursor.execute(
            """
            INSERT INTO coord_func (id_func, id_coord, status, criado_por)
            VALUES (%s, %s, 1, %s)
            ON DUPLICATE KEY UPDATE status = 1, modificado_por = %s
            """,
            (func_id, coord_id, autor_id, autor_id)
        )


def _carregar_apoio(cursor):
    """Carrega listas de níveis e de coordenadores para os formulários."""
    cursor.execute("SELECT id, nivel FROM nivel WHERE status = 1 ORDER BY id")
    niveis = cursor.fetchall()
    cursor.execute(
        "SELECT id, CONCAT(nome, ' ', sobrenome) AS nome "
        "FROM users WHERE status = 1 AND nivel = 2 ORDER BY nome"
    )
    coordenadores = cursor.fetchall()
    return niveis, coordenadores


@usuarios.route('/admin/usuarios')
@login_required
@admin_estrito
def listar_usuarios():
    """Lista todos os usuários com abas Todos / Ativos / Inativos."""
    conexao = obter_conexao()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    u.id, u.chapa, u.nome, u.sobrenome, u.email,
                    u.nivel, u.status, u.img_url,
                    DATE_FORMAT(u.data_nascimento, '%Y-%m-%d') AS data_nascimento,
                    n.nivel AS nivel_nome,
                    (
                        SELECT id_coord FROM coord_func
                        WHERE id_func = u.id AND status = 1 LIMIT 1
                    ) AS coordenador_id
                FROM users u
                LEFT JOIN nivel n ON n.id = u.nivel
                ORDER BY u.nome
                """
            )
            lista = cursor.fetchall()
            niveis, coordenadores = _carregar_apoio(cursor)
    finally:
        conexao.close()

    return render_template(
        'usuarios.html',
        usuarios=lista,
        niveis=niveis,
        coordenadores=coordenadores
    )


@usuarios.route('/admin/usuarios/criar', methods=['POST'])
@login_required
@admin_estrito
def criar_usuario():
    """Cria um novo usuário."""
    chapa = request.form.get('chapa', '').strip()
    nome = request.form.get('nome', '').strip()
    sobrenome = request.form.get('sobrenome', '').strip()
    email = request.form.get('email', '').strip()
    senha = request.form.get('senha', '')
    nivel = request.form.get('nivel') or 3
    status = 1 if request.form.get('status', '1') == '1' else 0
    data_nascimento = request.form.get('data_nascimento') or None
    coordenador_id = request.form.get('coordenador') or None

    if not chapa or not nome or not email or not senha:
        flash('Chapa, nome, email e senha são obrigatórios.', 'danger')
        return redirect(url_for('usuarios.listar_usuarios'))

    conexao = obter_conexao()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users
                    (chapa, nome, sobrenome, email, senha_hash, nivel, status, data_nascimento)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (chapa, nome, sobrenome, email, generate_password_hash(senha),
                 nivel, status, data_nascimento)
            )
            novo_id = cursor.lastrowid

            nova_img = _salvar_imagem(request.files.get('foto_perfil'), novo_id)
            if nova_img:
                cursor.execute(
                    "UPDATE users SET img_url = %s WHERE id = %s", (nova_img, novo_id)
                )

            _definir_coordenador(cursor, novo_id, coordenador_id, current_user.id)
        conexao.commit()
        flash('Usuário criado com sucesso!', 'success')
    except pymysql.err.IntegrityError:
        conexao.rollback()
        flash('Já existe um usuário com essa chapa ou email.', 'danger')
    finally:
        conexao.close()

    return redirect(url_for('usuarios.listar_usuarios'))


@usuarios.route('/admin/usuarios/<int:usuario_id>/editar', methods=['POST'])
@login_required
@admin_estrito
def editar_usuario(usuario_id):
    """Edita um usuário existente."""
    chapa = request.form.get('chapa', '').strip()
    nome = request.form.get('nome', '').strip()
    sobrenome = request.form.get('sobrenome', '').strip()
    email = request.form.get('email', '').strip()
    senha = request.form.get('senha', '')
    nivel = request.form.get('nivel') or 3
    status = 1 if request.form.get('status', '1') == '1' else 0
    data_nascimento = request.form.get('data_nascimento') or None
    coordenador_id = request.form.get('coordenador') or None

    if not chapa or not nome or not email:
        flash('Chapa, nome e email são obrigatórios.', 'danger')
        return redirect(url_for('usuarios.listar_usuarios'))

    conexao = obter_conexao()
    try:
        with conexao.cursor() as cursor:
            nova_img = _salvar_imagem(request.files.get('foto_perfil'), usuario_id)
            remover_img = request.form.get('remover_img') == '1'

            campos = [
                "chapa = %s", "nome = %s", "sobrenome = %s", "email = %s",
                "nivel = %s", "status = %s", "data_nascimento = %s"
            ]
            valores = [chapa, nome, sobrenome, email, nivel, status, data_nascimento]

            if senha:
                campos.append("senha_hash = %s")
                valores.append(generate_password_hash(senha))
            if nova_img:
                campos.append("img_url = %s")
                valores.append(nova_img)
            elif remover_img:
                campos.append("img_url = %s")
                valores.append('default.png')

            valores.append(usuario_id)
            cursor.execute(
                f"UPDATE users SET {', '.join(campos)} WHERE id = %s", valores
            )

            _definir_coordenador(cursor, usuario_id, coordenador_id, current_user.id)
        conexao.commit()
        flash('Usuário atualizado com sucesso!', 'success')
    except pymysql.err.IntegrityError:
        conexao.rollback()
        flash('Já existe um usuário com essa chapa ou email.', 'danger')
    finally:
        conexao.close()

    return redirect(url_for('usuarios.listar_usuarios'))
