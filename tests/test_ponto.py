# test_ponto.py
import pytest
from datetime import datetime
from calcular_ponto import calcular_horas_trabalhadas, calcular_atraso
def test_calculo_jornada_normal_sem_atraso():

    entradas_saidas = [
        datetime(2023, 10, 1, 8, 0),   # first entrada
        datetime(2023, 10, 1, 12, 0),  # saida almoco
        datetime(2023, 10, 1, 13, 0),  # volta almoco
        datetime(2023, 10, 1, 17, 0)   # saida do trabalho
    ]
    
    # calcular com base na saida e entrada com almoco quanto foi as horas
    total_horas = calcular_horas_trabalhadas(entradas_saidas)
    
    # deve dar 8horas de trabalho em segundos
    assert total_horas.total_seconds() == 8 * 3600


def test_calculo_jornada_com_marcacao_impar_gera_erro():
    entradas_saidas = [
        datetime(2023, 10, 1, 8, 0),
        datetime(2023, 10, 1, 12, 0),
        datetime(2023, 10, 1, 13, 0)
        # faltou a saida
    ]
    with pytest.raises(ValueError, match="Número ímpar de marcações"): # deve retornar erro
        calcular_horas_trabalhadas(entradas_saidas)


def test_atraso_dentro_da_tolerancia():
    # tolerancia de no maximo 10 min
    esperado_entrada = datetime(2023, 10, 1, 8, 0)
    realizado_entrada = datetime(2023, 10, 1, 8, 9)
    
    atraso = calcular_atraso(esperado_entrada, realizado_entrada)
    assert atraso.total_seconds() == 0 # se for menos que 10 min, nao tem atraso
