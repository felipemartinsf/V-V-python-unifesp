import pytest
from datetime import datetime, timedelta
from calcular_ponto import calcular_horas_trabalhadas, calcular_atraso, calcular_horas_extras, calcular_adicional_noturno
from unittest.mock import patch
from main import main 


# BOUNDARY TESTS
def test_atraso_limite_exato_tolerancia():
    esperado_entrada = datetime(2023, 10, 1, 8, 0, 0)
    realizado_entrada = datetime(2023, 10, 1, 8, 10, 0)
    
    atraso = calcular_atraso(esperado_entrada, realizado_entrada)
    assert atraso.total_seconds() == 0

def test_atraso_limite_estourado_por_um_segundo():
    esperado_entrada = datetime(2023, 10, 1, 8, 0, 0)
    realizado_entrada = datetime(2023, 10, 1, 8, 10, 1)
    
    atraso = calcular_atraso(esperado_entrada, realizado_entrada)
    assert atraso.total_seconds() == 601

def test_adicional_noturno_limite_inferior_exato():
    entradas_saidas = [
        datetime(2023, 10, 1, 18, 0, 0),
        datetime(2023, 10, 1, 22, 0, 0)
    ]
    
    horas_noturnas = calcular_adicional_noturno(entradas_saidas)
    assert horas_noturnas.total_seconds() == 0

def test_adicional_noturno_limite_superior_exato():
    entradas_saidas = [
        datetime(2023, 10, 1, 5, 0, 0),
        datetime(2023, 10, 1, 12, 0, 0)
    ]
    
    horas_noturnas = calcular_adicional_noturno(entradas_saidas)
    assert horas_noturnas.total_seconds() == 0

def test_adicional_noturno_iniciado_um_segundo_apos_limite():
    entradas_saidas = [
        datetime(2023, 10, 1, 18, 0, 0),
        datetime(2023, 10, 1, 22, 0, 1)
    ]
    
    horas_noturnas = calcular_adicional_noturno(entradas_saidas)
    assert horas_noturnas.total_seconds() == 1