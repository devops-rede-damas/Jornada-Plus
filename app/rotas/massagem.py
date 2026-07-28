"""
Rotas da página de fila de massagem.
Fila persistente e rotativa: ao concluir, o usuário vai para o fim da fila.
Usuários inativos e os IDs 2 e 4 não participam nem enxergam a fila.
"""
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required

from app.banco import obter_conexao
from app.utilidades import massagem_permitido, USUARIOS_FORA_DA_FILA

massagem = Blueprint('massagem', __name__)


# Query da fila: todos os ativos, exceto os IDs que não participam da fila.
# A ordem segue a coluna `ordem`; quem ainda não está na tabela vai para o fim.
QUERY_FILA = """
    SELECT
        u.id,
        CONCAT(u.nome, ' ', u.sobrenome) AS nome,
        u.img_url,
        f.ordem,
        COALESCE(f.ferias, 0) AS ferias
    FROM users u
    LEFT JOIN fila_massagem f ON f.id_func = u.id
    WHERE u.status = 1
      AND u.id NOT IN ({placeholders})
    ORDER BY (f.ordem IS NULL) ASC, f.ordem ASC, u.id ASC
""".format(placeholders=', '.join(['%s'] * len(USUARIOS_FORA_DA_FILA)))


def _garantir_todos_na_fila(cursor):
    """Insere no fim da fila os usuários ativos elegíveis que ainda não estão nela.

    Sem isso, um usuário fora da tabela cai no LEFT JOIN como ordem = NULL e
    fica preso no fim da lista, sem rotacionar.
    """
    placeholders = ', '.join(['%s'] * len(USUARIOS_FORA_DA_FILA))
    cursor.execute(
        f"""
        SELECT u.id
        FROM users u
        LEFT JOIN fila_massagem f ON f.id_func = u.id
        WHERE u.status = 1
          AND u.id NOT IN ({placeholders})
          AND f.id_func IS NULL
        ORDER BY u.id
        """,
        USUARIOS_FORA_DA_FILA
    )
    faltantes = cursor.fetchall()
    if not faltantes:
        return

    cursor.execute("SELECT COALESCE(MAX(ordem), 0) AS m FROM fila_massagem")
    proxima_ordem = cursor.fetchone()['m']
    for linha in faltantes:
        proxima_ordem += 1
        cursor.execute(
            "INSERT INTO fila_massagem (id_func, ordem) VALUES (%s, %s)",
            (linha['id'], proxima_ordem)
        )


@massagem.route('/massagem', methods=['GET'])
@login_required
@massagem_permitido
def fila_massagem():
    """Exibe a fila de massagem: próximo no topo e os demais em ordem."""
    conexao = obter_conexao()
    try:
        with conexao.cursor() as cursor:
            _garantir_todos_na_fila(cursor)
            conexao.commit()

            cursor.execute(QUERY_FILA, USUARIOS_FORA_DA_FILA)
            fila = cursor.fetchall()
    finally:
        conexao.close()

    # O próximo da vez é o primeiro que NÃO está de férias.
    # Quem está de férias é pulado, mas mantém a posição (coluna `ordem`).
    indice_proximo = next(
        (i for i, pessoa in enumerate(fila) if not pessoa['ferias']),
        None
    )
    if indice_proximo is None:
        proximo = None
        restante = fila
    else:
        proximo = fila[indice_proximo]
        restante = fila[:indice_proximo] + fila[indice_proximo + 1:]

    return render_template(
        'massagem.html',
        proximo=proximo,
        restante=restante
    )


@massagem.route('/massagem/concluir/<int:usuario_id>', methods=['POST'])
@login_required
@massagem_permitido
def concluir_massagem(usuario_id):
    """Marca a massagem como concluída: o usuário vai para o fim da fila."""
    if usuario_id in USUARIOS_FORA_DA_FILA:
        flash('Usuário não participa da fila.', 'danger')
        return redirect(url_for('massagem.fila_massagem'))

    conexao = obter_conexao()
    try:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT COALESCE(MAX(ordem), 0) AS m FROM fila_massagem")
            nova_ordem = cursor.fetchone()['m'] + 1

            cursor.execute(
                """
                INSERT INTO fila_massagem (id_func, ordem, vezes, ultima_vez)
                VALUES (%s, %s, 1, NOW())
                ON DUPLICATE KEY UPDATE
                    ordem = %s,
                    vezes = vezes + 1,
                    ultima_vez = NOW()
                """,
                (usuario_id, nova_ordem, nova_ordem)
            )
        conexao.commit()
    finally:
        conexao.close()

    flash('Massagem concluída! Próximo da fila.', 'success')
    return redirect(url_for('massagem.fila_massagem'))


@massagem.route('/massagem/ferias/<int:usuario_id>', methods=['POST'])
@login_required
@massagem_permitido
def alternar_ferias(usuario_id):
    """Alterna o status de férias de um usuário.

    De férias: é pulado na escolha do próximo, mas mantém a posição na fila.
    """
    if usuario_id in USUARIOS_FORA_DA_FILA:
        flash('Usuário não participa da fila.', 'danger')
        return redirect(url_for('massagem.fila_massagem'))

    conexao = obter_conexao()
    try:
        with conexao.cursor() as cursor:
            # Garante que o usuário exista na fila antes de alternar.
            cursor.execute(
                "SELECT ferias FROM fila_massagem WHERE id_func = %s",
                (usuario_id,)
            )
            linha = cursor.fetchone()
            if linha is None:
                cursor.execute(
                    "SELECT COALESCE(MAX(ordem), 0) AS m FROM fila_massagem"
                )
                nova_ordem = cursor.fetchone()['m'] + 1
                cursor.execute(
                    "INSERT INTO fila_massagem (id_func, ordem, ferias) "
                    "VALUES (%s, %s, 1)",
                    (usuario_id, nova_ordem)
                )
            else:
                cursor.execute(
                    "UPDATE fila_massagem SET ferias = NOT ferias "
                    "WHERE id_func = %s",
                    (usuario_id,)
                )
        conexao.commit()
    finally:
        conexao.close()

    flash('Status de férias atualizado.', 'success')
    return redirect(url_for('massagem.fila_massagem'))
