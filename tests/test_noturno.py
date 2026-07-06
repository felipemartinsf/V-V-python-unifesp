from datetime import datetime, timedelta
from calcular_ponto import calcular_adicional_noturno

def test_noturno_22h_exato_nao_conta():
    marcacoes = [
        datetime(2026, 7, 6, 22, 0),
        datetime(2026, 7, 6, 23, 0),
    ]

    assert calcular_adicional_noturno(marcacoes) == timedelta(hours=1)

def test_noturno_madrugada():
    marcacoes = [
        datetime(2026, 7, 6, 0, 0),
        datetime(2026, 7, 6, 5, 0),
    ]

    assert calcular_adicional_noturno(marcacoes) == timedelta(hours=5)