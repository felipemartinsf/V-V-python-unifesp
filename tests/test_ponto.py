# test_ponto.py
import pytest
from datetime import datetime
from calcular_ponto import calcular_horas_trabalhadas 
def test_calculo_jornada_normal_sem_atraso():
    # 1. Preparação (Arrange)
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