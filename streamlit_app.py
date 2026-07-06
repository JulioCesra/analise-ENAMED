from pathlib import Path
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(
    page_title="Análise de Dados Enamed",
    page_icon="👋",
    layout="wide"
)

workspace = Path(__file__).resolve().parent

PASTAS_DADOS = {
    'contextual': workspace / 'data' / 'questionario_contextual',
    'perfil_estudante': workspace / 'data' / 'perfil_estudante',
    'questionario_estudante': workspace / 'data' / 'questionario_estudante',
    'percepcao_prova': workspace / 'data' / 'questionario_percepcao_prova',
}

COLUNAS_POR_TIPO = {
    'perfil_estudante': ['TP_SEXO', 'NU_IDADE', 'ANO_FIM_EM', 'ANO_IN_GRAD', 'CO_TURNO_GRADUACAO'],
    'questionario_estudante': ['QE_'],
    'percepcao_prova': ['CO_RS_I'],
}

def ordenar_coluna_questionario(nome_coluna):
    numeros = re.findall(r'\d+', nome_coluna)
    if numeros:
        return int(numeros[-1])
    return 0

def montar_retorno_dados(pasta, arquivos_lidos, contagens):
    total_registros = 0
    if contagens:
        primeira_coluna = next(iter(contagens.values()))
        total_registros = int(primeira_coluna.sum())

    return {
        'pasta': pasta,
        'arquivos_lidos': arquivos_lidos,
        'total_arquivos': len(arquivos_lidos),
        'total_colunas': len(contagens),
        'total_registros': total_registros,
        'contagens': contagens,
    }

@st.cache_data 
def ler_dados_csv(tipo_dado='contextual'):
    pasta = PASTAS_DADOS.get(tipo_dado, PASTAS_DADOS['contextual'])
    if not pasta.exists():
        if tipo_dado == 'contextual':
            return None, None
        return montar_retorno_dados(pasta, [], {})
        
    contagem_sexo = None
    contagem_idade = None
    contagens = {}
    arquivos_lidos = []
    
    # Varre todos os arquivos para preencher os dados de cada tipo
    for arquivo in sorted(os.listdir(pasta)):
        if arquivo.endswith('.txt'):
            arquivos_lidos.append(arquivo)
            tabela = pd.read_csv(pasta / arquivo, sep=';', dtype=str)
            
            if "NU_ANO" in tabela.columns:
                tabela.drop(columns="NU_ANO", inplace=True)
                
            nomes_para_correcao = {'9': 'Indefinido', 'F': 'Feminino', 'M': 'Masculino', '.': 'Indefinido'}
            if 'TP_SEXO' in tabela.columns:
                tabela['TP_SEXO'] = tabela['TP_SEXO'].replace(to_replace=nomes_para_correcao)
            
            if tipo_dado != 'contextual':
                colunas_tipo = COLUNAS_POR_TIPO.get(tipo_dado, [])
                for coluna in tabela.columns:
                    if coluna in colunas_tipo or any(coluna.startswith(prefixo) for prefixo in colunas_tipo):
                        contagens[coluna] = tabela[coluna].value_counts().sort_index()
                continue
            
            # Alimenta as variáveis sem interromper o loop com return precoce
            if 'TP_SEXO' in tabela.columns:
                contagem_sexo = tabela['TP_SEXO'].value_counts()
            if 'NU_IDADE' in tabela.columns:
                # Ordena o índice numérico da idade para o gráfico de barras ficar alinhado crescentemente
                contagem_idade = tabela['NU_IDADE'].value_counts().sort_index()
    
    if tipo_dado != 'contextual':
        contagens = dict(sorted(contagens.items(), key=lambda item: ordenar_coluna_questionario(item[0])))
        return montar_retorno_dados(pasta, arquivos_lidos, contagens)
    
    return contagem_sexo, contagem_idade

@st.cache_data
def ler_perguntas_questionario_estudante():
    caminho_perguntas = PASTAS_DADOS['questionario_estudante'] / 'perguntas_questionario_estudante.csv'
    if not caminho_perguntas.exists():
        return {}

    perguntas = pd.read_csv(caminho_perguntas, sep=';')
    return {
        linha['codigo']: {
            'pergunta': linha['pergunta'],
            'categorias': linha['categorias']
        }
        for _, linha in perguntas.iterrows()
    }

@st.cache_data
def ler_alternativas_questionario_estudante():
    caminho_alternativas = PASTAS_DADOS['questionario_estudante'] / 'alternativas_questionario_estudante.csv'
    if not caminho_alternativas.exists():
        return {}

    alternativas = pd.read_csv(caminho_alternativas, sep=';', dtype=str)
    return {
        (linha['codigo'], linha['resposta']): linha['descricao']
        for _, linha in alternativas.iterrows()
    }

def descrever_resposta_questionario(codigo_pergunta, resposta, alternativas):
    resposta = str(resposta)
    if ',' not in resposta:
        return alternativas.get((codigo_pergunta, resposta), resposta)

    descricoes = []
    for item in resposta.split(','):
        item = item.strip()
        descricao = alternativas.get((codigo_pergunta, item), item)
        descricoes.append(f"{item} - {descricao}")
    return "; ".join(descricoes)

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

with tab1:
    st.subheader("Análise de Dados das Perguntas do Questionário do Estudante")

    dados_questionario_estudante = ler_dados_csv('questionario_estudante')
    perguntas_questionario_estudante = ler_perguntas_questionario_estudante()
    alternativas_questionario_estudante = ler_alternativas_questionario_estudante()

    if dados_questionario_estudante['contagens']:
        total_perguntas = dados_questionario_estudante['total_colunas']
        total_respostas = dados_questionario_estudante['total_registros']
        total_arquivos = dados_questionario_estudante['total_arquivos']

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Quantidade de Perguntas", value=total_perguntas)
        with col2:
            st.metric("Quantidade de Respostas", value=f"{total_respostas:,}".replace(",", "."))
        with col3:
            st.metric("Arquivos Analisados", value=total_arquivos)

        st.divider()

        pergunta_escolhida = st.selectbox(
            "Escolha a pergunta para visualizar",
            list(dados_questionario_estudante['contagens'].keys()),
            format_func=lambda codigo: f"{codigo} - {perguntas_questionario_estudante.get(codigo, {}).get('pergunta', codigo)}"
        )

        contagem_pergunta = dados_questionario_estudante['contagens'][pergunta_escolhida]
        texto_pergunta = perguntas_questionario_estudante.get(pergunta_escolhida, {}).get('pergunta', pergunta_escolhida)

        st.write(f"### {pergunta_escolhida}")
        st.write(texto_pergunta)
        col_grafico1, col_grafico2 = st.columns(2)

        with col_grafico1:
            fig_barra = gerar_grafico_barra(contagem_pergunta)
            st.pyplot(fig_barra)

        with col_grafico2:
            st.write("#### Tabela de Frequência")
            tabela_frequencia = contagem_pergunta.rename_axis("Código da Resposta").reset_index(name="Total de Respostas")
            tabela_frequencia["Resposta"] = tabela_frequencia["Código da Resposta"].map(
                lambda resposta: descrever_resposta_questionario(
                    pergunta_escolhida,
                    resposta,
                    alternativas_questionario_estudante
                )
            )
            tabela_frequencia = tabela_frequencia[["Código da Resposta", "Resposta", "Total de Respostas"]]
            st.dataframe(tabela_frequencia, use_container_width=True)
    else:
        st.warning("Dados do Questionário do Estudante não encontrados na pasta.")

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
