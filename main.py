from datetime import datetime, timedelta
from calculador_ponto import (
    calcular_horas_trabalhadas,
    calcular_atraso,
    calcular_horas_extras,
    calcular_adicional_noturno
)

def main():
    marcacoes = []
    carga_diaria = timedelta(hours=8)
    esperado_entrada = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    
    while True:
        print("\n--- Sistema de Registro de Ponto ---")
        print("1. Bater Ponto (Horário Atual)")
        print("2. Fechar Dia e Exibir Espelho")
        print("3. Sair")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == '1':
            agora = datetime.now()
            marcacoes.append(agora)
            print(f"Ponto registrado: {agora.strftime('%Y-%m-%d %H:%M:%S')}")
                
        elif opcao == '2':
            if not marcacoes:
                print("Nenhum ponto registrado hoje.")
                continue
            
            print("\n--- Espelho de Ponto Diário ---")
            for i, marcacao in enumerate(marcacoes):
                tipo = "Entrada" if i % 2 == 0 else "Saída" # se for par ou impar eh um estado
                print(f"{tipo} {i//2 + 1}: {marcacao.strftime('%H:%M:%S')}")
                
            try:
                total_horas = calcular_horas_trabalhadas(marcacoes)
                print(f"\nTotal Trabalhado: {total_horas}")
                
                atraso = calcular_atraso(esperado_entrada, marcacoes[0])
                if atraso.total_seconds() > 0:
                    print(f"Atraso Registrado: {atraso}")
                
                extras = calcular_horas_extras(total_horas, carga_diaria)
                if extras.total_seconds() > 0:
                    print(f"Horas Extras: {extras}")
                
                noturno = calcular_adicional_noturno(marcacoes)
                if noturno.total_seconds() > 0:
                    print(f"Adicional Noturno: {noturno}")
                    
            except ValueError as e:
                print(f"Erro: {e}")
            except Exception as e:
                print(f"Erro ao calcular espelho de ponto: {e}")
                
        elif opcao == '3':
            print("Encerrando o sistema...")
            break
            
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()