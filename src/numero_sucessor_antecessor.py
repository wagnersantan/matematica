import pandas as pd
from bson import ObjectId
import matplotlib.pyplot as plt
from pymongo import MongoClient
import io
import streamlit as st

# Conectar ao MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["enxadristas_db"]
collection = db["enxadristas"]

RATING_INICIAL = 1600
K = 32

# Funções para cálculo e manipulação de dados
def calcular_pontuacao(medalhas_ouro, medalhas_prata, medalhas_bronze):
    return (medalhas_ouro * 3) + (medalhas_prata * 2) + (medalhas_bronze * 1)

def atualizar_rating(rating_atual, resultado, expectativa):
    return round(rating_atual + K * (resultado - expectativa))

def expectativa_vitoria(rating_jogador, rating_oponente):
    return 1 / (1 + 10 ** ((rating_oponente - rating_jogador) / 400))

def cadastrar_enxadrista(nome, ultimo_torneio, ouro, prata, bronze, partidas):
    pontuacao = calcular_pontuacao(ouro, prata, bronze)
    media_pontos = pontuacao / partidas if partidas > 0 else 0
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
    collection.insert_one(enxadrista)
    return f"Enxadrista {nome} cadastrado com sucesso!"

def registrar_confronto(nome1, nome2, resultado):
    jogador1 = collection.find_one({'nome': nome1})
    jogador2 = collection.find_one({'nome': nome2})
    
    if jogador1 and jogador2:
        expectativa1 = expectativa_vitoria(jogador1['rating'], jogador2['rating'])
        expectativa2 = expectativa_vitoria(jogador2['rating'], jogador1['rating'])
        novo_rating1 = atualizar_rating(jogador1['rating'], resultado, expectativa1)
        novo_rating2 = atualizar_rating(jogador2['rating'], 1 - resultado, expectativa2)

        collection.update_one({'nome': nome1}, {'$set': {'rating': novo_rating1}})
        collection.update_one({'nome': nome2}, {'$set': {'rating': novo_rating2}})
        return "Confronto registrado com sucesso!"
    else:
        return "Jogador não encontrado!"

def gerar_relatorio():
    enxadristas = list(collection.find())
    df = pd.DataFrame(enxadristas)
    df.insert(0, 'Posição', range(1, len(df) + 1))
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return output

def gerar_grafico():
    enxadristas = list(collection.find())
    df = pd.DataFrame(enxadristas)
    
    if df.empty:
        return None
    
    plt.figure(figsize=(8, 6))
    wedges, texts, autotexts = plt.pie(
        df["rating"],
        labels=df["nome"],
        autopct="%1.1f%%",
        startangle=90,
        colors=plt.cm.viridis(range(len(df))),
        textprops={'fontsize': 12}
    )
    plt.title("Distribuição de Rating dos Enxadristas")
    return plt

def remover_duplicados():
    nomes = collection.distinct('nome')
    for nome in nomes:
        duplicados = list(collection.find({'nome': nome}))
        if len(duplicados) > 1:
            ids_para_excluir = [str(enxadrista['_id']) for enxadrista in duplicados[1:]]
            collection.delete_many({'_id': {'$in': [ObjectId(id) for id in ids_para_excluir]}})
    return "Duplicados removidos com sucesso!"

def remover_enxadrista(nome):
    resultado = collection.delete_one({'nome': nome})
    if resultado.deleted_count > 0:
        return f"Enxadrista {nome} removido com sucesso!"
    else:
        return f"Enxadrista {nome} não encontrado."

# Interface do Streamlit
st.set_page_config(
    page_title="Chess Master Rating",
    layout="wide",
    initial_sidebar_state="collapsed"  # Sidebar inicia fechada
)

# Inicializa o tema na session state
if "tema" not in st.session_state:
    st.session_state.tema = "Escuro"  # Tema padrão

# Função para aplicar o tema
def aplicar_tema(tema):
    if tema == "Escuro":
        st.markdown(
            """
            <style>
            .reportview-container {
                background-color: #1E1E1E;
                color: white;
            }
            .sidebar .sidebar-content {
                background-color: #1E1E1E;
                color: white;
            }
            .stButton button {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
            .reportview-container {
                background-color: white;
                color: black;
            }
            .sidebar .sidebar-content {
                background-color: white;
                color: black;
            }
            .stButton button {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

# Aplica o tema atual
aplicar_tema(st.session_state.tema)

# Título e Descrição
st.markdown(
    """
    <h1 style='text-align: center; color: #DAA520;'>
        Chess Master Rating 🏆
    </h1>
    <h3 style='text-align: center; color: #4CAF50;'>
        Acompanhe o desempenho dos enxadristas e seus ratings!
    </h3>
    """,
    unsafe_allow_html=True
)

# Sidebar Personalizada
with st.sidebar:
    st.header("ℹ️ Sobre o Projeto")
    st.markdown(
        """
        **Chess Master Rating** é um aplicativo para gerenciar e acompanhar o desempenho de enxadristas.
        
        - **Objetivo:** Facilitar o cálculo de ratings e a visualização de estatísticas.
        - **Tecnologias:** Streamlit, MongoDB, Python.
        """
    )

    st.markdown("---")  # Linha divisória

    st.header("🔗 Links do GitHub dos Devs")
    st.markdown("[Dev Marcelo](https://github.com/maasj1)")
    st.markdown("[Dev Wagner](https://github.com/wagnersantan)")

# Adicionando abas para melhor organização
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Cadastro e Registro", "Relatórios e Gráficos", "Manutenção de Dados", "Emparceiramento Suíço", "Resultados"])

# Inicializa a estrutura para armazenar resultados das rodadas
if "resultados_rodadas" not in st.session_state:
    st.session_state.resultados_rodadas = []

with tab1:
    with st.expander("Cadastro de Enxadrista", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            with st.form("cadastro_form"):
                nome = st.text_input("Nome:")
                ultimo_torneio = st.text_input("Último Torneio:")
                ouro = st.number_input("🥇 Ouro:", min_value=0)
                prata = st.number_input("🥈 Prata:", min_value=0)
                bronze = st.number_input("🥉 Bronze:", min_value=0)
                partidas = st.number_input("Partidas:", min_value=0)
                submitted = st.form_submit_button("Cadastrar")
                if submitted:
                    result = cadastrar_enxadrista(nome, ultimo_torneio, ouro, prata, bronze, partidas)
                    st.success(result)

        with col2:
            with st.form("confronto_form"):
                nome1 = st.text_input("Jogador 1:")
                nome2 = st.text_input("Jogador 2:")
                resultado = st.number_input("Resultado (0 a 1):", min_value=0, max_value=1, step=1)
                submitted = st.form_submit_button("Registrar Confronto")
                if submitted:
                    result = registrar_confronto(nome1, nome2, resultado)
                    st.success(result)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Gerar Relatório"):
            relatorio = gerar_relatorio()
            st.download_button("Baixar Relatório", relatorio, "ranking_enxadristas.xlsx")

    with col2:
        if st.button("Gerar Gráfico"):
            fig = gerar_grafico()
            if fig:
                st.pyplot(fig)
            else:
                st.warning("Nenhum dado disponível para gerar gráfico.")

with tab3:
    if st.button("Remover Duplicados"):
        result = remover_duplicados()
        st.success(result)

    st.header("Remover Enxadrista")
    nome_remover = st.selectbox("Selecione o Enxadrista:", [enxadrista['nome'] for enxadrista in collection.find()])
    if st.button("Remover Enxadrista"):
        result = remover_enxadrista(nome_remover)
        st.success(result)

with tab4:
    st.header("Emparceiramento Suíço")
    num_rodadas = st.number_input("Número de Rodadas:", min_value=1, value=1)
    
    # Adiciona um controle para selecionar a rodada atual
    if "rodada_atual" not in st.session_state:
        st.session_state.rodada_atual = 1

    st.write(f"Rodada Atual: {st.session_state.rodada_atual}/{num_rodadas}")

    if st.button("Gerar Emparceiramento"):
        enxadristas = list(collection.find())
        if not enxadristas:
            st.warning("Nenhum enxadrista cadastrado.")
        else:
            # Ordena os enxadristas por rating
            df = pd.DataFrame(enxadristas)
            df = df.sort_values(by='rating', ascending=False)

            # Cria listas para jogos
            partidas = []
            for i in range(0, len(df), 2):
                if i + 1 < len(df):  # Verifica se há um par
                    jogador1 = df.iloc[i]
                    jogador2 = df.iloc[i + 1]
                    partidas.append((jogador1['nome'], jogador2['nome']))

            # Armazena partidas no session state para uso posterior
            st.session_state.partidas = partidas

            # Exibe as partidas
            if partidas:
                st.subheader("Partidas Geradas:")
                for partida in partidas:
                    st.write(f"{partida[0]} vs {partida[1]}")
                st.success("Emparceiramento gerado com sucesso!")
            else:
                st.warning("Número insuficiente de jogadores para emparceiramento.")

# Adicionar seção para registrar resultados
if 'partidas' in st.session_state:
    st.subheader("Registrar Resultados das Partidas")
    resultados = {}
    for partida in st.session_state.partidas:
        col1, col2 = st.columns(2)
        with col1:
            resultado_jogador1 = st.selectbox(
                f"Resultado de {partida[0]}:",
                options=[0.0, 0.5, 1.0],
                key=f"{partida[0]}_resultado"
            )
            resultados[partida[0]] = resultado_jogador1  # Armazena resultado para o jogador 1
            if st.button(f"Registrar resultado para {partida[0]} vs {partida[1]}", key=f"registrar_{partida[0]}"):
                registrar_confronto(partida[0], partida[1], resultado_jogador1)
                st.success(f"Resultado registrado para {partida[0]} vs {partida[1]}.")

        with col2:
            resultado_jogador2 = st.selectbox(
                f"Resultado de {partida[1]}:",
                options=[0.0, 0.5, 1.0],
                key=f"{partida[1]}_resultado"
            )
            resultados[partida[1]] = resultado_jogador2  # Armazena resultado para o jogador 2
            if st.button(f"Registrar resultado para {partida[1]} vs {partida[0]}", key=f"registrar_{partida[1]}"):
                registrar_confronto(partida[1], partida[0], 1 - resultado_jogador2)  # Inverte o resultado
                st.success(f"Resultado registrado para {partida[1]} vs {partida[0]}.")


        # Botão para avançar para a próxima rodada
        if st.button("Avançar para a Próxima Rodada"):
            if all(res in resultados for partida in st.session_state.partidas for res in [partida[0], partida[1]]):
                # Armazena os resultados da rodada atual
                st.session_state.resultados_rodadas.append(resultados)
                st.session_state.rodada_atual += 1
                st.success(f"Avançou para a rodada {st.session_state.rodada_atual}.")
                del st.session_state.partidas  # Limpa as partidas após avançar
            else:
                st.warning("Por favor, registre todos os resultados antes de avançar.")

with tab5:
    st.header("Tabela de Resultados entre Jogadores")
    if st.session_state.resultados_rodadas:
        # Cria um DataFrame para exibir todos os resultados armazenados
        resultados_list = []
        for idx, rodada in enumerate(st.session_state.resultados_rodadas, start=1):
            for partida in rodada.items():
                resultados_list.append({
                    "Rodada": idx,
                    "Jogador 1": partida[0],
                    "Resultado Jogador 1": partida[1],  # Obtemos o resultado do jogador 1
                    "Jogador 2": partida[0],
                    "Resultado Jogador 2": 1 - partida[1]  # Inverte o resultado
                })

        resultados_df = pd.DataFrame(resultados_list)
        st.dataframe(resultados_df)
    else:
        st.warning("Nenhum resultado registrado ainda.")

# Exibir tabela de enxadristas
st.header("Tabela de Enxadristas")
enxadristas = list(collection.find())
if enxadristas:
    df = pd.DataFrame(enxadristas)

    # Adiciona ícones às colunas de medalhas
    df["Ouro"] = "🥇 " + df["ouro"].astype(str)
    df["Prata"] = "🥈 " + df["prata"].astype(str)
    df["Bronze"] = "🥉 " + df["bronze"].astype(str)

    # Converter todas as colunas que contêm ObjectId para string
    for column in df.columns:
        if df[column].dtype == 'object':
            df[column] = df[column].apply(lambda x: str(x) if isinstance(x, ObjectId) else x)

    st.dataframe(df)
else:
    st.warning("Nenhum enxadrista cadastrado.")