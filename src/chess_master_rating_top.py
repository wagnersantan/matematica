import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from openpyxl import Workbook, load_workbook
from openpyxl.drawing.image import Image
import xlsxwriter
from pymongo import MongoClient  # Importar a biblioteca pymongo

# Conectar ao MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Endereço e porta do MongoDB
db = client["enxadristas_db"]  # Nome do banco de dados
collection = db["enxadristas"]  # Nome da coleção

RATING_INICIAL = 1600  # Constantes para o cálculo do rating Elo
K = 32  # Fator de ajuste do rating Elo

# Função para calcular a pontuação por medalha
def calcular_pontuacao(medalhas_ouro, medalhas_prata, medalhas_bronze):
    return (medalhas_ouro * 3) + (medalhas_prata * 2) + (medalhas_bronze * 1)

# Função para atualizar o rating após um confronto
def atualizar_rating(rating_atual, resultado, expectativa):
    return round(rating_atual + K * (resultado - expectativa))

# Função para calcular a expectativa de vitória
def expectativa_vitoria(rating_jogador, rating_oponente):
    return 1 / (1 + 10 ** ((rating_oponente - rating_jogador) / 400))

# Função para cadastrar um novo enxadrista
def cadastrar_enxadrista():
    nome = entry_nome.get().strip()
    ultimo_torneio = entry_torneio.get().strip()
    ouro = int(entry_ouro.get())
    prata = int(entry_prata.get())
    bronze = int(entry_bronze.get())
    partidas = int(entry_partidas.get())
    pontuacao = calcular_pontuacao(ouro, prata, bronze)
    media_pontos = pontuacao / partidas if partidas > 0 else 0
    
    # Criar um dicionário para o enxadrista
    enxadrista = {
        'nome': nome,
        'rating': RATING_INICIAL,
        'ouro': ouro,
        'prata': prata,
        'bronze': bronze,
        'último_torneio': ultimo_torneio,
        "Pontuação": pontuacao,
        "Média de Pontos": media_pontos,
        "Partidas": partidas
    }
    
    # Inserir no MongoDB
    collection.insert_one(enxadrista)  # Inserir o enxadrista na coleção
    atualizar_tabela()
    messagebox.showinfo("Sucesso", "Enxadrista cadastrado com sucesso!")

# Função para registrar confrontos
def registrar_confronto():
    nome1 = entry_jogador1.get().strip()
    nome2 = entry_jogador2.get().strip()
    resultado = float(entry_resultado.get())
    
    jogador1 = collection.find_one({'nome': nome1})  # Consultar jogador no MongoDB
    jogador2 = collection.find_one({'nome': nome2})  # Consultar jogador no MongoDB
    
    if jogador1 and jogador2:
        expectativa1 = expectativa_vitoria(jogador1['rating'], jogador2['rating'])
        expectativa2 = expectativa_vitoria(jogador2['rating'], jogador1['rating'])
        novo_rating1 = atualizar_rating(jogador1['rating'], resultado, expectativa1)
        novo_rating2 = atualizar_rating(jogador2['rating'], 1 - resultado, expectativa2)
        
        # Atualizar os ratings no MongoDB
        collection.update_one({'nome': nome1}, {'$set': {'rating': novo_rating1}})
        collection.update_one({'nome': nome2}, {'$set': {'rating': novo_rating2}})
        
        atualizar_tabela()
        messagebox.showinfo("Sucesso", "Confronto registrado com sucesso!")
    else:
        messagebox.showerror("Erro", "Jogador não encontrado!")

# Função para atualizar a exibição da tabela na interface gráfica.
def atualizar_tabela():
    global enxadristas  # Usar a lista global
    enxadristas = list(collection.find())  # Buscar todos os enxadristas do MongoDB
    
    # Ordenar enxadristas pela média de pontos
    enxadristas_ordenados = sorted(enxadristas, key=lambda x: x['Média de Pontos'], reverse=True)
    
    for row in tree.get_children():
        tree.delete(row)
    
    for i, enxadrista in enumerate(enxadristas_ordenados, start=1):
        tree.insert("", "end", values=(i, enxadrista['nome'], enxadrista['rating'], enxadrista['ouro'], enxadrista['prata'], enxadrista['bronze'], enxadrista['último_torneio'], enxadrista['Pontuação'], enxadrista['Média de Pontos'], enxadrista['Partidas']))

# Função para gerar o relatório em formato Excel.
def gerar_relatorio():
    # Ordenar enxadristas pela média de pontos
    enxadristas_ordenados = sorted(enxadristas, key=lambda x: x['Média de Pontos'], reverse=True)
    
    # Adicionar posição ao DataFrame
    df = pd.DataFrame(enxadristas_ordenados)
    df.insert(0, 'Posição', range(1, len(df) + 1))
    
    df.to_excel("ranking_enxadristas.xlsx", index=False)
    messagebox.showinfo("Sucesso", "Relatório gerado com sucesso!")

# Função para gerar o gráfico de pizza no Excel
def gerar_grafico():
    df = pd.DataFrame(enxadristas)

    # Ordenar enxadristas pela média de pontos
    enxadristas_ordenados = sorted(enxadristas, key=lambda x: x['Média de Pontos'], reverse=True)
    
    # Criar DataFrame com os enxadristas ordenados
    df = pd.DataFrame(enxadristas_ordenados)
    
    # Adicionar a coluna "Posição" ao DataFrame
    df.insert(0, 'Posição', range(1, len(df) + 1))
    
    if df.empty:
        messagebox.showerror("Erro", "Nenhum dado disponível para gerar gráfico.")
        return
    
    # Criar gráfico de pizza
    try:
        fig, ax = plt.subplots()
        # Gerar o gráfico de pizza com os nomes dos enxadristas como rótulos
        wedges, texts, autotexts = ax.pie(
            df["rating"],
            labels=df["nome"],  # Nomes dos enxadristas como rótulos
            autopct="%1.1f%%",  # Porcentagem no gráfico
            startangle=90,       # Ângulo inicial
            colors=plt.cm.viridis(range(len(df))),  # Cores únicas para cada enxadrista
            textprops={'fontsize': 8}  # Tamanho da fonte dos rótulos
        )
        
        # Adicionar legenda
        ax.legend(
            wedges, df["nome"],  # Elementos da legenda (cores e nomes)
            title="Enxadristas",  # Título da legenda
            loc="center left",    # Posição da legenda
            bbox_to_anchor=(1, 0, 0.5, 1)  # Ajustar posição fora do gráfico
        )
        
        plt.title("Distribuição de Rating dos Enxadristas")
        plt.savefig("grafico_pizza.png", bbox_inches="tight")  # Salva o gráfico com ajustes de layout
        
        # Criar planilha e inserir imagem
        writer = pd.ExcelWriter("ranking_enxadristas.xlsx", engine="openpyxl")
        df.to_excel(writer, sheet_name="Ranking", index=False)
        writer.close()  # Fecha para poder editar com openpyxl
        
        # Inserir imagem com openpyxl
        wb = load_workbook("ranking_enxadristas.xlsx")
        ws = wb["Ranking"]
        img = Image("grafico_pizza.png")
        ws.add_image(img, "K1")  # Insere o gráfico na célula J2
        wb.save("ranking_enxadristas.xlsx")
        
        messagebox.showinfo("Sucesso", "Gráfico gerado e salvo no arquivo Excel!")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao gerar gráfico: {e}")

# Interface gráfica
root = tk.Tk()
root.title("Gerenciador de Enxadristas")
root.geometry("900x600")

# Cadastro de enxadristas
frame_cadastro = ttk.LabelFrame(root, text="Cadastro de Enxadrista")
frame_cadastro.pack(fill="x", padx=10, pady=5)

entry_nome = ttk.Entry(frame_cadastro, width=20)
entry_torneio = ttk.Entry(frame_cadastro, width=10)
entry_ouro = ttk.Entry(frame_cadastro, width=5)
entry_prata = ttk.Entry(frame_cadastro, width=5)
entry_bronze = ttk.Entry(frame_cadastro, width=5)
entry_partidas = ttk.Entry(frame_cadastro, width=5)

ttk.Label(frame_cadastro, text="Nome:").pack(side="left")
entry_nome.pack(side="left", padx=5)
ttk.Label(frame_cadastro, text="Último Torneio:").pack(side="left")
entry_torneio.pack(side="left", padx=5)
ttk.Label(frame_cadastro, text="Ouro:").pack(side="left")
entry_ouro.pack(side="left", padx=5)
ttk.Label(frame_cadastro, text="Prata:").pack(side="left")
entry_prata.pack(side="left", padx=5)
ttk.Label(frame_cadastro, text="Bronze:").pack(side="left")
entry_bronze.pack(side="left", padx=5)
ttk.Label(frame_cadastro, text="Partidas:").pack(side="left")
entry_partidas.pack(side="left", padx=5)

btn_cadastrar = ttk.Button(frame_cadastro, text="Cadastrar", command=cadastrar_enxadrista)
btn_cadastrar.pack(side="left", padx=5)

# Registro de confronto
frame_confronto = ttk.LabelFrame(root, text="Registrar Confronto")
frame_confronto.pack(fill="x", padx=10, pady=5)

entry_jogador1 = ttk.Entry(frame_confronto, width=20)
entry_jogador2 = ttk.Entry(frame_confronto, width=20)
entry_resultado = ttk.Entry(frame_confronto, width=5)

ttk.Label(frame_confronto, text="Jogador 1:").pack(side="left")
entry_jogador1.pack(side="left", padx=5)
ttk.Label(frame_confronto, text="Jogador 2:").pack(side="left")
entry_jogador2.pack(side="left", padx=5)
ttk.Label(frame_confronto, text="Resultado:").pack(side="left")
entry_resultado.pack(side="left", padx=5)

btn_confronto = ttk.Button(frame_confronto, text="Registrar", command=registrar_confronto)
btn_confronto.pack(side="left", padx=5)

# Tabela de enxadristas
tree = ttk.Treeview(root, columns=("Posição", "Nome", "Rating", "Ouro", "Prata", "Bronze", "Último Torneio", "Pontuação", "Média de Pontos", "Partidas"), show="headings")
for col in ("Posição", "Nome", "Rating", "Ouro", "Prata", "Bronze", "Último Torneio", "Pontuação", "Média de Pontos", "Partidas"):
    tree.heading(col, text=col)
    tree.column(col, width=100)
tree.pack(fill="both", expand=True, padx=10, pady=5)

# Botões extras
frame_botoes = ttk.Frame(root)
frame_botoes.pack(fill="x", padx=10, pady=5)
btn_relatorio = ttk.Button(frame_botoes, text="Gerar Relatório", command=gerar_relatorio)
btn_relatorio.pack(side="left", padx=5)
btn_grafico = ttk.Button(frame_botoes, text="Gerar Gráfico", command=gerar_grafico)
btn_grafico.pack(side="left", padx=5)

root.mainloop()