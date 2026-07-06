import pytest
from datetime import datetime, timedelta
from calcular_ponto import calcular_horas_trabalhadas, calcular_atraso, calcular_horas_extras, calcular_adicional_noturno, verify_dia_descanso
from unittest.mock import patch
from main import main 

def test_mcdc_domingo_nao_feriado():
    data = datetime(2023, 10, 1)  # eh domingo mas nao eh feriado
    assert verify_dia_descanso(data, is_feriado=False) is True

def test_mcdc_dia_util_feriado():
    data = datetime(2023, 10, 2)  # nao eh domingo mas eh feriado
    assert verify_dia_descanso(data, is_feriado=True) is True

def test_mcdc_dia_util_nao_feriado():
    data = datetime(2023, 10, 2)  # nem feriado nem domingo
    assert verify_dia_descanso(data, is_feriado=False) is False