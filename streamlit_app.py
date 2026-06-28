from pathlib import Path
import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(
    page_title="Análise de Dados Enamed",
    page_icon="👋",
    layout="wide"
)

workspace = Path(__file__).resolve().parent

@st.cache_data 
def ler_dados_csv():
    pasta = workspace / 'data' / 'questionario_contextual'
    if not pasta.exists():
        return None, None
        
    contagem_sexo = None
    contagem_idade = None
    
    # Varre todos os arquivos para preencher os dados de cada tipo
    for arquivo in os.listdir(pasta):
        if arquivo.endswith('.txt'):
            tabela = pd.read_csv(pasta / arquivo, sep=';')
            
            if "NU_ANO" in tabela.columns:
                tabela.drop(columns="NU_ANO", inplace=True)
                
            nomes_para_correcao = {'9': 'Indefinido', 'F': 'Feminino', 'M': 'Masculino', '.': 'Indefinido'}
            tabela.replace(to_replace=nomes_para_correcao, inplace=True)
            
            # Alimenta as variáveis sem interromper o loop com return precoce
            if 'TP_SEXO' in tabela.columns:
                contagem_sexo = tabela['TP_SEXO'].value_counts()
            if 'NU_IDADE' in tabela.columns:
                # Ordena o índice numérico da idade para o gráfico de barras ficar alinhado crescentemente
                contagem_idade = tabela['NU_IDADE'].value_counts().sort_index()
                
    return contagem_sexo, contagem_idade

def gerar_grafico_pizza(serie_dados):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(serie_dados.values, labels=serie_dados.index, autopct="%1.1f%%", startangle=90)
    ax.axis('equal')
    return fig

def gerar_grafico_barra(serie_dados, color_palette=None):
    fig, ax = plt.subplots(figsize=(12, 12))
    
    if color_palette is None:
        color_palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    if len(serie_dados) <= len(color_palette):
        cores = color_palette[:len(serie_dados)]
    else:
        cores = color_palette[0] 
        
    eixo_x = [str(idx) for idx in serie_dados.index]
    valores = serie_dados.values

    if len(serie_dados) > 5:
        bars = ax.barh(eixo_x, valores, color=cores)
        ax.bar_label(bars, padding=3)
        ax.invert_yaxis()  
    else:
        bars = ax.bar(eixo_x, valores, color=cores)
        ax.bar_label(bars, padding=3)
        
    return fig

caminho_logo_enamed = workspace / 'logo.png'
if caminho_logo_enamed.exists():
    st.image(str(caminho_logo_enamed), width=150)
    
st.title("Análise de Dados Enamed - 2025")

tab1, tab2, tab3 = st.tabs([
    "Questionário do Estudante Enamed",
    "Questionário Contextual Enamed",
    "Questionário de Percepção de Prova Enamed"
])

with tab2:
    st.subheader("Análise de Dados das Perguntas do Questionário Contextual")
    
    caminho_questionario_pdf = workspace / 'data' / 'questionario_contextual' / 'Questionário Contextual Enamed 2025.pdf'
    if caminho_questionario_pdf.exists():
        st.download_button("Baixar o questionário", data=caminho_questionario_pdf.read_bytes(), file_name="Questionário Contextual Enamed 2025.pdf", mime="application/pdf")
    
    st.divider()
    
    contagem_sexo, contagem_idade = ler_dados_csv()
    
    if contagem_sexo is not None:
        total_participantes = int(contagem_sexo.sum())
        total_feminino = int(contagem_sexo.get('Feminino', 0))
        total_masculino = int(contagem_sexo.get('Masculino', 0))

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Quantidade de Participantes", value=f"{total_participantes:,}".replace(",", "."))
        with col2:
            st.metric("Participantes do Sexo Feminino", value=f"{total_feminino:,}".replace(",", "."))
        with col3:
            st.metric("Participantes do Sexo Masculino", value=f"{total_masculino:,}".replace(",", "."))
            
        st.divider()
        
        st.write("### Distribuição por Sexo")
        col_grafico1, col_grafico2 = st.columns(2)
        
        with col_grafico1:
            fig_pizza = gerar_grafico_pizza(contagem_sexo)
            st.pyplot(fig_pizza)
            
        with col_grafico2:
            fig_barra = gerar_grafico_barra(contagem_sexo)
            st.pyplot(fig_barra)
    else:
        st.warning("Dados da coluna 'TP_SEXO' não encontrados na pasta.")

    st.divider()

    if contagem_idade is not None:
        st.write("### Distribuição por Idade")
        
        col_idade1, col_idade2 = st.columns(2)
        with col_idade1:
            fig_barra_idade = gerar_grafico_barra(contagem_idade, color_palette=['#2ca02c'])
            st.pyplot(fig_barra_idade)
        with col_idade2:
            st.write("#### Tabela de Frequência de Idades")
            st.dataframe(contagem_idade.rename("Total de Alunos"), use_container_width=True)
    else:
        st.warning("Dados da coluna 'NU_IDADE' não encontrados na pasta.")
