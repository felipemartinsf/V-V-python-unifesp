import pytest
from datetime import datetime, timedelta
from calcular_ponto import calcular_horas_trabalhadas, calcular_atraso, calcular_horas_extras, calcular_adicional_noturno
from unittest.mock import patch
from main import main 

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

def test_atraso_fora_da_tolerancia():
    esperado_entrada = datetime(2023, 10, 1, 8, 0)
    realizado_entrada = datetime(2023, 10, 1, 8, 15)
    
    atraso = calcular_atraso(esperado_entrada, realizado_entrada)
    assert atraso.total_seconds() == 15 * 60  # 15 minutos em segundos deve retornar atraso


def test_saida_antecipada_gera_horas_devedoras():
    esperado_saida = datetime(2023, 10, 1, 17, 0)
    realizado_saida = datetime(2023, 10, 1, 16, 30)
    
    atraso = calcular_atraso(esperado_saida, realizado_saida, is_saida=True)
    assert atraso.total_seconds() == 30 * 60 # esperando o atraso alto


# TESTES DE EXTRAS

def test_calculo_hora_extras_simples():
    # Jornada de 1h extra
    entradas_saidas = [
        datetime(2023, 10, 1, 8, 0),
        datetime(2023, 10, 1, 12, 0),
        datetime(2023, 10, 1, 13, 0),
        datetime(2023, 10, 1, 18, 0)
    ]    
    horas_totais = calcular_horas_trabalhadas(entradas_saidas)
    carga_diaria = timedelta(hours=8) #padrao clt
    extras = calcular_horas_extras(entradas_saidas)
    assert extras.total_seconds() == 1 * 3600


def  test_trabalho_em_dia_de_folga():
    entradas_saidas = [
        datetime(2023, 10, 1, 8, 0), # isso eh um domingo
        datetime(2023, 10, 1, 12, 0)
    ]
    horas = calcular_horas_trabalhadas(entradas_saidas)
    carga_diaria = timedelta(hours=8) #padrao clt
    extras = calcular_horas_extras(horas, carga_diaria)
    assert extras.total_seconds() == 4  * 3600 # tudo tem que ser extra em domingo

# TESTE NOTURNO

def test_jornada_sem_adicional(): # teste de limite
    entradas_saidas = [
        datetime(2023, 10, 1, 14, 0),
        datetime(2023, 10, 1, 22, 0) # encerra no limite da hora extra noturna
    ]
    horas_noturnas = calcular_adicional_noturno(entradas_saidas)
    assert horas_noturnas.total_seconds() == 0

    return


def test_adicional_noturno_integral_atravessando_meia_noite():
    entradas_saidas = [
        datetime(2023, 10, 1, 22, 0),
        datetime(2023, 10, 2, 6, 0)
    ]
    horas_noturnas = calcular_adicional_noturno(entradas_saidas) # 7 horas noturnas, das 22h ate as 5.
    assert horas_noturnas.total_seconds() == 7 * 3600




@patch('main.datetime') # duble relógio do sistema
@patch('builtins.input') # duble para o usuário digitando no teclado
def test_fluxo_bater_ponto_e_sair(mock_input, mock_datetime, capsys):
    data_falsa = datetime(2023, 10, 25, 8, 0, 0)
    mock_datetime.now.return_value = data_falsa # mockando o horario pra uma hora falsa
    
    mock_input.side_effect = ['1', '3'] # usuario batendo ponto
    
    main() # rodar o main para ele testar com o mockado
    
    tela_do_terminal = capsys.readouterr().out # pegar o que foi cuspido do main()
    
    assert "Ponto registrado: 2023-10-25 08:00:00" in tela_do_terminal 
    assert "Encerrando o sistema..." in tela_do_terminal



@patch('main.datetime')
@patch('builtins.input')
def test_exibir_espelho_sem_pontos(mock_input, mock_datetime, capsys):
    mock_input.side_effect = ['2', '3'] # sem nenhum ponto
    
    main()
    
    tela_do_terminal = capsys.readouterr().out
    assert "Nenhum ponto registrado hoje." in tela_do_terminal
