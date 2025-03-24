import matplotlib.pyplot as plt  # type: ignore

enxadristas = []

while True:
    # Dicionário para armazenar os dados de um enxadrista
    enxadrista = {}
    enxadrista['nome'] = input('Nome do enxadrista: ').strip()
    
    while True:
        try:
            # Solicita o número de partidas jogadas
            tot = int(input(f'Quantas partidas {enxadrista["nome"]} jogou?: '))
            if tot < 0:
                raise ValueError  # Garante que o número de partidas não seja negativo
            break
        except ValueError:
            print("Erro! Digite um número inteiro válido.")

    # Lista para armazenar os pontos de cada partida
    partidas = []
    for c in range(tot):
        while True:
            try:
                # Solicita os pontos obtidos em cada partida
                pontos = int(input(f'Quantos pontos na partida {c + 1}? '))
                partidas.append(pontos)
                break
            except ValueError:
                print("Erro! Digite um número inteiro válido.")

    # Armazena os pontos e a soma total no dicionário do enxadrista
    enxadrista['medalhas'] = partidas
    enxadrista['Total'] = sum(partidas)

    # Entrada para medalhas com validação
    for medalha in ['ouro', 'prata', 'bronze']:
        while True:
            try:
                # Solicita a quantidade de medalhas do enxadrista
                enxadrista[medalha] = int(input(f'Quantas medalhas de {medalha} {enxadrista["nome"]} possui? '))
                if enxadrista[medalha] < 0:
                    raise ValueError  # Garante que o número de medalhas não seja negativo
                break
            except ValueError:
                print("Erro! Digite um número inteiro válido.")

    # Adiciona o enxadrista à lista de enxadristas
    enxadristas.append(enxadrista)

    while True:
        # Pergunta se deseja cadastrar outro enxadrista
        resp = input('Deseja cadastrar outro enxadrista? [S/N] ').strip().upper()
        if resp in 'SN':
            break
        print('Erro! Responda apenas S ou N.')

    if resp == 'N':
        break  # Encerra o loop de cadastro

# Verifica se há enxadristas cadastrados antes de exibir os dados
if enxadristas:
    print('-=' * 30)
    print(f'{"cod":<5}{"Nome":<15}{"Total":<10}{"Ouro":<6}{"Prata":<6}{"Bronze":<6}')
    print('-=' * 30)

    # Exibe os dados de cada enxadrista
    for k, v in enumerate(enxadristas):
        print(f'{k:<5}{v["nome"]:<15}{v["Total"]:<10}{v["ouro"]:<6}{v["prata"]:<6}{v["bronze"]:<6}')
    
    print('-=' * 30)

    # Criar gráfico de barras
    nomes = [v['nome'] for v in enxadristas]
    medalhas_ouro = [v['ouro'] for v in enxadristas]
    medalhas_prata = [v['prata'] for v in enxadristas]
    medalhas_bronze = [v['bronze'] for v in enxadristas]

    bar_width = 0.25
    index = range(len(nomes))

    plt.bar(index, medalhas_ouro, width=bar_width, label='Ouro', color='gold')
    plt.bar([i + bar_width for i in index], medalhas_prata, width=bar_width, label='Prata', color='silver')
    plt.bar([i + bar_width * 2 for i in index], medalhas_bronze, width=bar_width, label='Bronze', color='#cd7f32')

    plt.xlabel('Enxadristas')
    plt.ylabel('Número de Medalhas')
    plt.title('Medalhas dos Enxadristas')
    plt.xticks([i + bar_width for i in index], nomes)
    plt.legend()
    plt.tight_layout()
    plt.show()

    while True:
        try:
            # Permite buscar os detalhes de um enxadrista pelo índice
            busca = int(input('Mostrar dados de qual enxadrista? (999 para parar): '))
            if busca == 999:
                break  # Encerra a busca
            if 0 <= busca < len(enxadristas):
                print(f'--- LEVANTAMENTO DO ENXADRISTA {enxadristas[busca]["nome"]}')
                print(f'Medalhas: Ouro: {enxadristas[busca]["ouro"]}, Prata: {enxadristas[busca]["prata"]}, Bronze: {enxadristas[busca]["bronze"]}')
                print(f'Partidas jogadas: {len(enxadristas[busca]["medalhas"])}')
                print('-=' * 30)
            else:
                print(f'ERRO! Não existe enxadrista com código {busca}.')
        except ValueError:
            print("Erro! Digite um número inteiro válido.")

    # Determina os enxadristas com mais medalhas de cada tipo
    campeao_ouro = max(enxadristas, key=lambda x: x["ouro"])['nome']
    campeao_prata = max(enxadristas, key=lambda x: x["prata"])['nome']
    campeao_bronze = max(enxadristas, key=lambda x: x["bronze"])['nome']

    # Exibe os campeões em cada categoria de medalha
    print(f'O enxadrista com mais medalhas de ouro é: {campeao_ouro}')
    print(f'O enxadrista com mais medalhas de prata é: {campeao_prata}')
    print(f'O enxadrista com mais medalhas de bronze é: {campeao_bronze}')

print('<< Volte sempre >>')