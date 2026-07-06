"""
Regras de negócio do sistema de ponto.

Convenções adotadas (definidas para fechar os testes de test_ponto.py,
tests_boundary.py e test_mcdc_coberture.py):

- Tolerância de atraso na entrada: 10 minutos (>10min conta o atraso cheio).
- Carga diária padrão: 8 horas.
- Adicional noturno: janela das 22:00 às 05:00 (limites exclusivos:
  bater ponto exatamente às 22:00 ou às 05:00 NÃO conta como noturno,
  só a partir de 1 segundo depois).
- Dia de descanso (domingo ou feriado): todo tempo trabalhado é hora extra.
"""

from datetime import timedelta

TOLERANCIA_ATRASO = timedelta(minutes=10)
CARGA_DIARIA_PADRAO = timedelta(hours=8)
HORA_INICIO_NOTURNO = 22
HORA_FIM_NOTURNO = 5


def calcular_horas_trabalhadas(marcacoes):
    """Recebe uma lista de marcações [entrada, saida, entrada, saida, ...]
    e retorna o total trabalhado como timedelta."""
    if len(marcacoes) % 2 != 0:
        raise ValueError("Número ímpar de marcações")

    total = timedelta()
    for i in range(0, len(marcacoes), 2):
        entrada, saida = marcacoes[i], marcacoes[i + 1]
        total += saida - entrada
    return total


def calcular_atraso(esperado, realizado, is_saida=False):
    """Calcula atraso na entrada (com tolerância de 10 min) ou
    horas devedoras por saída antecipada (sem tolerância)."""
    if is_saida:
        diferenca = esperado - realizado
        return diferenca if diferenca.total_seconds() > 0 else timedelta()

    diferenca = realizado - esperado
    if diferenca <= TOLERANCIA_ATRASO:
        return timedelta()
    return diferenca


def calcular_horas_extras(entrada_ou_horas, carga_diaria=None, is_dia_de_descanso=False):
    """Aceita tanto uma lista de marcações quanto um timedelta já calculado
    de horas trabalhadas. Se is_dia_de_descanso=True, todo tempo trabalhado
    é considerado extra (ex.: trabalho em domingo/feriado)."""
    if isinstance(entrada_ou_horas, list):
        horas_trabalhadas = calcular_horas_trabalhadas(entrada_ou_horas)
    else:
        horas_trabalhadas = entrada_ou_horas

    if carga_diaria is None:
        carga_diaria = CARGA_DIARIA_PADRAO

    if is_dia_de_descanso:
        return horas_trabalhadas

    extras = horas_trabalhadas - carga_diaria
    return extras if extras.total_seconds() > 0 else timedelta()


def _overlap(inicio_a, fim_a, inicio_b, fim_b):
    inicio = max(inicio_a, inicio_b)
    fim = min(fim_a, fim_b)
    return fim - inicio if fim > inicio else timedelta()


def calcular_adicional_noturno(marcacoes):
    """Soma o tempo trabalhado que cai dentro da janela 22:00-05:00,
    considerando que a janela pode atravessar a virada do dia."""
    if len(marcacoes) % 2 != 0:
        raise ValueError("Número ímpar de marcações")

    total_noturno = timedelta()
    for i in range(0, len(marcacoes), 2):
        entrada, saida = marcacoes[i], marcacoes[i + 1]
        dia_base = entrada.replace(hour=0, minute=0, second=0, microsecond=0)

        # janela que começa às 22h do dia_base e termina às 05h do dia seguinte
        janela_atual_inicio = dia_base.replace(hour=HORA_INICIO_NOTURNO)
        janela_atual_fim = dia_base.replace(hour=HORA_FIM_NOTURNO) + timedelta(days=1)
        total_noturno += _overlap(entrada, saida, janela_atual_inicio, janela_atual_fim)

        # janela que começou às 22h do dia anterior e termina às 05h do dia_base
        # (cobre o caso de a marcação já começar de madrugada, ex.: 00:00-05:00)
        janela_anterior_inicio = (dia_base - timedelta(days=1)).replace(hour=HORA_INICIO_NOTURNO)
        janela_anterior_fim = dia_base.replace(hour=HORA_FIM_NOTURNO)
        total_noturno += _overlap(entrada, saida, janela_anterior_inicio, janela_anterior_fim)

    return total_noturno


def verify_dia_descanso(data, is_feriado=False):
    """Condição A: is_domingo | Condição B: is_feriado -> MC/DC nos testes."""
    is_domingo = data.weekday() == 6  # segunda=0 ... domingo=6
    return is_domingo or is_feriado
