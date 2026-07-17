"""
Rotas da página de aniversariantes.
"""
from datetime import datetime
from flask import Blueprint, render_template

from app.banco import obter_conexao

aniversariantes = Blueprint('aniversariantes', __name__)

MESES_PT = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}


@aniversariantes.route('/aniversariantes', methods=['GET'])
def listar_aniversariantes():
    """Lista os aniversariantes do mês atual."""
    mes_atual = datetime.now().month
    nome_mes = MESES_PT.get(mes_atual, '')

    conexao = obter_conexao()
    try:
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT
                    nome,
                    CONCAT('./static/img/', img_url) AS img,
                    DATE_FORMAT(data_nascimento, '%%d/%%m') AS data,
                    presente1, presente2
                FROM users
                WHERE MONTH(data_nascimento) = %s
                  AND status = 1
                ORDER BY DAY(data_nascimento)
            """, (mes_atual,))
            lista = cursor.fetchall()
    finally:
        conexao.close()

    return render_template(
        'aniversariantes.html',
        aniversariantes=lista,
        nome_mes=nome_mes
    )
