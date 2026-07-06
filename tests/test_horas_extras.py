from datetime import timedelta
from calcular_ponto import calcular_horas_extras

def test_sem_hora_extra_quando_trabalha_8h():
    assert calcular_horas_extras(timedelta(hours=8)) == timedelta()

def test_hora_extra_quando_trabalha_9h30():
    assert calcular_horas_extras(timedelta(hours=9, minutes=30)) == timedelta(hours=1, minutes=30)

def test_dia_descanso_tudo_e_extra():
    assert calcular_horas_extras(
        timedelta(hours=6),
        is_dia_de_descanso=True
    ) == timedelta(hours=6)