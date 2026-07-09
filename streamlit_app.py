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

PERGUNTAS_CONTEXTUAIS = {
    'NU_QUESTAO_01': 'Qual o seu estado civil?',
    'NU_QUESTAO_02': 'Você tem filhos?',
    'NU_QUESTAO_03': 'Qual é a sua cor ou raça?',
    'NU_QUESTAO_04': 'Você tem alguma deficiência, transtorno global do desenvolvimento ou altas habilidades?',
    'NU_QUESTAO_05': 'Qual a renda total de sua família, incluindo seus rendimentos?',
    'NU_QUESTAO_06': 'Há quanto tempo você concluiu o curso de medicina?',
    'NU_QUESTAO_07': 'Você está trabalhando atualmente?',
    'NU_QUESTAO_08': 'Há quanto tempo você atua profissionalmente como médico?',
    'NU_QUESTAO_09': 'Qual sua carga horária atual de trabalho semanal como médico?',
    'NU_QUESTAO_10': 'A partir da obtenção de especialidade médico-profissional, em quais esferas profissionais pretende inserir-se?',
}

ALTERNATIVAS_CONTEXTUAIS = {
    'NU_QUESTAO_01': {
        'A': 'Solteiro(a)',
        'B': 'Casado (a) ou vivendo em união estável',
        'C': 'Separado(a) judicialmente/divorciado(a)',
        'D': 'Viúvo(a)',
        'E': 'Outro',
    },
    'NU_QUESTAO_02': {
        'A': 'Não',
        'B': 'Sim, 1 filho',
        'C': 'Sim, 2 filhos',
        'D': 'Sim, 3 filhos ou mais',
    },
    'NU_QUESTAO_03': {
        'A': 'Branca',
        'B': 'Preta',
        'C': 'Amarela',
        'D': 'Parda',
        'E': 'Indígena',
        'F': 'Não quero declarar',
    },
    'NU_QUESTAO_04': {
        'A': 'Não possuo',
        'B': 'Cegueira',
        'C': 'Baixa Visão',
        'D': 'Surdez',
        'E': 'Deficiência Auditiva',
        'F': 'Deficiência Física',
        'G': 'Transtorno do Espectro Autista (TEA)',
        'H': 'Altas habilidades/superdotação',
        'I': 'Deficiência Intelectual',
        'J': 'Transtorno do Déficit de Atenção com Hiperatividade (TDAH)',
        'K': 'Dislexia',
        'L': 'Outras/outros',
        'M': 'Não quero declarar',
    },
    'NU_QUESTAO_05': {
        'A': 'Até 1,5 salário mínimo (até R$ 2.277,00)',
        'B': 'De 1,5 a 3 salários mínimos (R$ 2.277,00 a R$ 4.554,00)',
        'C': 'De 3 a 4,5 salários mínimos (R$ 4.554,00 a R$ 6.831,00)',
        'D': 'De 4,5 a 6 salários mínimos (R$ 6.831,00 a R$ 9.108,00)',
        'E': 'De 6 a 10 salários mínimos (R$ 9.108,00 a R$ 15.180,00)',
        'F': 'De 10 a 30 salários mínimos (R$ 15.180,00 a R$ 45.540,00)',
        'G': 'Acima de 30 salários mínimos (mais de R$ 45.540,00)',
    },
    'NU_QUESTAO_06': {
        'A': 'Menos de 1 ano',
        'B': 'Entre 1 e 2 anos',
        'C': 'Entre 3 e 5 anos',
        'D': 'Entre 6 e 10 anos',
        'E': 'Mais de 10 anos',
        'F': 'Não conclui',
    },
    'NU_QUESTAO_07': {
        'A': 'Não',
        'B': 'Sim, mas não na minha área de formação',
        'C': 'Sim, na minha área de formação',
    },
    'NU_QUESTAO_08': {
        'A': 'Nunca atuei como médico',
        'B': 'Menos de 1 ano',
        'C': 'Entre 1 e 2 anos',
        'D': 'Entre 3 e 5 anos',
        'E': 'Entre 6 e 10 anos',
        'F': 'Mais de 10 anos',
    },
    'NU_QUESTAO_09': {
        'A': 'Não estou trabalhando atualmente como médico',
        'B': '20 horas semanais ou menos',
        'C': '30 horas semanais',
        'D': '40 horas semanais',
        'E': 'Mais de 40 horas semanais',
    },
    'NU_QUESTAO_10': {
        'A': 'Prestação de serviço no Sistema Único de Saúde (SUS)',
        'B': 'Prestação de serviço na rede hospitalar privada',
        'C': 'Pesquisa aplicada no setor privado',
        'D': 'Pesquisa e Ensino na área da formação médica',
        'E': 'Outras',
    },
}

PERGUNTAS_PERCEPCAO_PROVA = {
    'CO_RS_I1': 'Qual o grau de dificuldade das questões?',
    'CO_RS_I2': 'Qual foi o tempo gasto por você para concluir a prova?',
    'CO_RS_I3': 'Em relação ao tempo total de aplicação, você considera que a prova foi',
    'CO_RS_I4': 'Os enunciados das questões estavam claros e objetivos?',
    'CO_RS_I5': 'As informações/instruções fornecidas para a resolução das questões foram suficientes para resolvê-las?',
    'CO_RS_I6': 'Você se deparou com alguma dificuldade ao responder à prova? Qual?',
    'CO_RS_I7': 'Considerando as questões da prova, você percebeu que',
    'CO_RS_I8': 'Como você avalia a sequência das questões na prova?',
    'CO_RS_I9': 'As atividades práticas desenvolvidas ao longo do seu curso contribuíram para a resolução das questões dessa prova?',
}

ALTERNATIVAS_PERCEPCAO_PROVA = {
    'CO_RS_I1': {
        'A': 'Muito fácil',
        'B': 'Fácil',
        'C': 'Médio',
        'D': 'Difícil',
        'E': 'Muito difícil',
    },
    'CO_RS_I2': {
        'A': 'Menos de uma hora',
        'B': 'Entre uma e duas horas',
        'C': 'Entre três e quatro horas',
        'D': 'Entre quatro e cinco horas',
        'E': 'Cinco horas, e não consegui terminar',
    },
    'CO_RS_I3': {
        'A': 'Muito longa',
        'B': 'Longa',
        'C': 'Adequada',
        'D': 'Curta',
        'E': 'Muito curta',
    },
    'CO_RS_I4': {
        'A': 'Sim, todos',
        'B': 'Sim, a maioria',
        'C': 'Apenas cerca da metade',
        'D': 'Poucos',
        'E': 'Não, nenhum',
    },
    'CO_RS_I5': {
        'A': 'Sim, até excessivas',
        'B': 'Sim, em todas elas',
        'C': 'Sim, na maioria delas',
        'D': 'Sim, somente em algumas',
        'E': 'Não, em nenhuma delas',
    },
    'CO_RS_I6': {
        'A': 'Desconhecimento do conteúdo',
        'B': 'Forma diferente de abordagem do conteúdo',
        'C': 'Espaço insuficiente para responder às questões',
        'D': 'Falta de motivação para fazer a prova',
        'E': 'Não tive qualquer tipo de dificuldade para responder à prova',
    },
    'CO_RS_I7': {
        'A': 'Não estudou ainda a maioria desses conteúdos',
        'B': 'Estudou alguns desses conteúdos, mas não os aprendeu',
        'C': 'Estudou a maioria desses conteúdos, mas não os aprendeu',
        'D': 'Estudou e aprendeu muitos desses conteúdos',
        'E': 'Estudou e aprendeu todos esses conteúdos',
    },
    'CO_RS_I8': {
        'A': 'A sequência não interferiu nas minhas respostas',
        'B': 'Preferiria a sequência por área',
        'C': 'Preferiria a sequência por grau de dificuldade',
        'D': 'A sequência dificultou meu raciocínio durante a prova',
        'E': 'A sequência facilitou minha organização e resolução da prova',
    },
    'CO_RS_I9': {
        'A': 'Sim',
        'B': 'Não',
    },
}

MAPA_SEXO = {'9': 'Indefinido', 'F': 'Feminino', 'M': 'Masculino', '.': 'Indefinido'}
MAPA_REGIAO = {'1': 'Norte', '2': 'Nordeste', '3': 'Sudeste', '4': 'Sul', '5': 'Centro-Oeste'}
MAPA_TURNO = {'1': 'Matutino', '2': 'Vespertino', '3': 'Integral', '4': 'Noturno'}

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
                
            if 'TP_SEXO' in tabela.columns:
                tabela['TP_SEXO'] = tabela['TP_SEXO'].replace(to_replace=MAPA_SEXO)
            
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
def ler_perfil_estudante():
    pasta = PASTAS_DADOS['perfil_estudante']
    if not pasta.exists():
        return pd.DataFrame()

    arquivos_colunas = {
        'microdados_enade_2025_arq1.txt': ['CO_CURSO', 'CO_UF_CURSO', 'CO_REGIAO_CURSO'],
        'microdados_enade_2025_arq2.txt': ['ANO_FIM_EM', 'ANO_IN_GRAD', 'CO_TURNO_GRADUACAO'],
        'microdados_enade_2025_arq5.txt': ['TP_SEXO'],
        'microdados_enade_2025_arq6.txt': ['NU_IDADE'],
    }

    perfil = pd.DataFrame()
    for arquivo, colunas in arquivos_colunas.items():
        caminho_arquivo = pasta / arquivo
        if caminho_arquivo.exists():
            tabela = pd.read_csv(caminho_arquivo, sep=';', dtype=str, usecols=colunas)
            for coluna in tabela.columns:
                perfil[coluna] = tabela[coluna]

    if perfil.empty:
        return perfil

    if 'TP_SEXO' in perfil.columns:
        perfil['TP_SEXO'] = perfil['TP_SEXO'].replace(to_replace=MAPA_SEXO).fillna('Indefinido')

    if 'CO_REGIAO_CURSO' in perfil.columns:
        perfil['CO_REGIAO_CURSO'] = perfil['CO_REGIAO_CURSO'].replace(to_replace=MAPA_REGIAO)

    if 'CO_TURNO_GRADUACAO' in perfil.columns:
        perfil['CO_TURNO_GRADUACAO'] = perfil['CO_TURNO_GRADUACAO'].replace(to_replace=MAPA_TURNO).fillna('Indefinido')

    if 'NU_IDADE' in perfil.columns:
        idade_numerica = pd.to_numeric(perfil['NU_IDADE'], errors='coerce')
        perfil['FAIXA_IDADE'] = pd.cut(
            idade_numerica,
            bins=[0, 24, 29, 34, 39, 200],
            labels=['Até 24 anos', '25 a 29 anos', '30 a 34 anos', '35 a 39 anos', '40 anos ou mais']
        ).astype(str).replace('nan', 'Indefinido')

    return perfil

def aplicar_filtros_perfil(perfil, sexo, faixa_idade, regiao, turno):
    mascara = pd.Series(True, index=perfil.index)

    if sexo != 'Todos' and 'TP_SEXO' in perfil.columns:
        mascara &= perfil['TP_SEXO'] == sexo
    if faixa_idade != 'Todos' and 'FAIXA_IDADE' in perfil.columns:
        mascara &= perfil['FAIXA_IDADE'] == faixa_idade
    if regiao != 'Todos' and 'CO_REGIAO_CURSO' in perfil.columns:
        mascara &= perfil['CO_REGIAO_CURSO'] == regiao
    if turno != 'Todos' and 'CO_TURNO_GRADUACAO' in perfil.columns:
        mascara &= perfil['CO_TURNO_GRADUACAO'] == turno

    return mascara

def ler_questionario_estudante_filtrado(mascara_perfil):
    pasta = PASTAS_DADOS['questionario_estudante']
    if not pasta.exists():
        return montar_retorno_dados(pasta, [], {})

    contagens = {}
    arquivos_lidos = []

    for arquivo in sorted(os.listdir(pasta)):
        if arquivo.endswith('.txt'):
            arquivos_lidos.append(arquivo)
            tabela = pd.read_csv(pasta / arquivo, sep=';', dtype=str)
            if len(tabela) != len(mascara_perfil):
                continue

            tabela = tabela.loc[mascara_perfil.values]
            for coluna in tabela.columns:
                if coluna.startswith('QE_'):
                    contagens[coluna] = tabela[coluna].value_counts().sort_index()

    contagens = dict(sorted(contagens.items(), key=lambda item: ordenar_coluna_questionario(item[0])))
    return montar_retorno_dados(pasta, arquivos_lidos, contagens)

@st.cache_data
def ler_questionario_contextual():
    pasta = PASTAS_DADOS['contextual']
    if not pasta.exists():
        return montar_retorno_dados(pasta, [], {})

    contagens = {}
    arquivos_lidos = []

    for arquivo in sorted(os.listdir(pasta)):
        if arquivo.endswith('.txt'):
            tabela = pd.read_csv(pasta / arquivo, sep=';', dtype=str)
            colunas_questionario = [coluna for coluna in tabela.columns if coluna.startswith('NU_QUESTAO_')]

            if colunas_questionario:
                arquivos_lidos.append(arquivo)

            for coluna in colunas_questionario:
                contagens[coluna] = tabela[coluna].value_counts().sort_index()

    contagens = dict(sorted(contagens.items(), key=lambda item: ordenar_coluna_questionario(item[0])))
    return montar_retorno_dados(pasta, arquivos_lidos, contagens)

@st.cache_data
def ler_perfil_contextual():
    pasta = PASTAS_DADOS['contextual']
    if not pasta.exists():
        return pd.DataFrame()

    caminho_sexo = pasta / 'microdados_demais_part_2025_arq2.txt'
    caminho_idade = pasta / 'microdados_demais_part_2025_arq3.txt'

    if not caminho_sexo.exists() or not caminho_idade.exists():
        return pd.DataFrame()

    perfil = pd.DataFrame()
    perfil['TP_SEXO'] = pd.read_csv(caminho_sexo, sep=';', dtype=str, usecols=['TP_SEXO'])['TP_SEXO']
    perfil['NU_IDADE'] = pd.read_csv(caminho_idade, sep=';', dtype=str, usecols=['NU_IDADE'])['NU_IDADE']
    perfil['TP_SEXO'] = perfil['TP_SEXO'].replace(to_replace=MAPA_SEXO).fillna('Indefinido')

    idade_numerica = pd.to_numeric(perfil['NU_IDADE'], errors='coerce')
    perfil['FAIXA_IDADE'] = pd.cut(
        idade_numerica,
        bins=[0, 24, 29, 34, 39, 200],
        labels=['Até 24 anos', '25 a 29 anos', '30 a 34 anos', '35 a 39 anos', '40 anos ou mais']
    ).astype(str).replace('nan', 'Indefinido')

    return perfil

def aplicar_filtros_contextual(perfil, sexo, faixa_idade):
    mascara = pd.Series(True, index=perfil.index)

    if sexo != 'Todos' and 'TP_SEXO' in perfil.columns:
        mascara &= perfil['TP_SEXO'] == sexo
    if faixa_idade != 'Todos' and 'FAIXA_IDADE' in perfil.columns:
        mascara &= perfil['FAIXA_IDADE'] == faixa_idade

    return mascara

def ler_questionario_contextual_filtrado(mascara_perfil):
    pasta = PASTAS_DADOS['contextual']
    if not pasta.exists():
        return montar_retorno_dados(pasta, [], {})

    contagens = {}
    arquivos_lidos = []

    for arquivo in sorted(os.listdir(pasta)):
        if arquivo.endswith('.txt'):
            tabela = pd.read_csv(pasta / arquivo, sep=';', dtype=str)
            if len(tabela) != len(mascara_perfil):
                continue

            tabela = tabela.loc[mascara_perfil.values]
            colunas_questionario = [coluna for coluna in tabela.columns if coluna.startswith('NU_QUESTAO_')]

            if colunas_questionario:
                arquivos_lidos.append(arquivo)

            for coluna in colunas_questionario:
                contagens[coluna] = tabela[coluna].value_counts().sort_index()

    contagens = dict(sorted(contagens.items(), key=lambda item: ordenar_coluna_questionario(item[0])))
    return montar_retorno_dados(pasta, arquivos_lidos, contagens)

def ler_percepcao_prova_filtrada(mascara_perfil):
    pasta = PASTAS_DADOS['percepcao_prova']
    if not pasta.exists():
        return montar_retorno_dados(pasta, [], {})

    contagens = {}
    arquivos_lidos = []

    for arquivo in sorted(os.listdir(pasta)):
        if arquivo.endswith('.txt'):
            tabela = pd.read_csv(pasta / arquivo, sep=';', dtype=str)
            if len(tabela) != len(mascara_perfil):
                continue

            tabela = tabela.loc[mascara_perfil.values]
            arquivos_lidos.append(arquivo)

            for coluna in tabela.columns:
                if coluna.startswith('CO_RS_I'):
                    contagens[coluna] = tabela[coluna].value_counts().sort_index()

    contagens = dict(sorted(contagens.items(), key=lambda item: ordenar_coluna_questionario(item[0])))
    return montar_retorno_dados(pasta, arquivos_lidos, contagens)

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

def descrever_resposta_contextual(codigo_pergunta, resposta):
    resposta = str(resposta)
    alternativas = ALTERNATIVAS_CONTEXTUAIS.get(codigo_pergunta, {})

    if resposta == '.':
        return 'Sem resposta'
    if ',' not in resposta:
        return alternativas.get(resposta, resposta)

    descricoes = []
    for item in resposta.split(','):
        item = item.strip()
        descricao = alternativas.get(item, item)
        descricoes.append(f"{item} - {descricao}")
    return "; ".join(descricoes)

def descrever_resposta_percepcao(codigo_pergunta, resposta):
    resposta = str(resposta)
    alternativas = ALTERNATIVAS_PERCEPCAO_PROVA.get(codigo_pergunta, {})

    if resposta in ['.', '*']:
        return 'Sem resposta'
    return alternativas.get(resposta, resposta)

def gerar_grafico_pizza(serie_dados):
    def formatar_percentual(percentual):
        if percentual < 3:
            return ""
        return f"{percentual:.1f}%"

    fig, ax = plt.subplots(figsize=(9, 6))
    wedges, _, autotexts = ax.pie(
        serie_dados.values,
        labels=None,
        autopct=formatar_percentual,
        startangle=90,
        pctdistance=0.68,
        wedgeprops={'linewidth': 1, 'edgecolor': 'white'}
    )

    for texto in autotexts:
        texto.set_fontsize(9)
        texto.set_color('#263238')

    ax.legend(
        wedges,
        [str(indice) for indice in serie_dados.index],
        title="Respostas",
        loc="center left",
        bbox_to_anchor=(1.08, 0.5),
        frameon=False,
        labelspacing=1.1
    )
    ax.axis('equal')
    fig.tight_layout()
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


def limpar_filtros(*chaves):
    for chave in chaves:
        st.session_state[chave] = 'Todos'


tab1, tab2, tab3 = st.tabs([
    "Questionário do Estudante Enamed",
    "Questionário Contextual Enamed",
    "Questionário de Percepção de Prova Enamed"
])

with tab1:
    st.subheader("Análise de Dados das Perguntas do Questionário do Estudante")

    caminho_questionario_estudante_pdf = workspace / 'data' / 'questionario_estudante' / 'Questionário do Estudante Enamed 2025.pdf'
    if caminho_questionario_estudante_pdf.exists():
        st.download_button(
            "Baixar o questionário",
            data=caminho_questionario_estudante_pdf.read_bytes(),
            file_name="Questionário do Estudante Enamed 2025.pdf",
            mime="application/pdf"
        )

    perfil_estudante = ler_perfil_estudante()
    perguntas_questionario_estudante = ler_perguntas_questionario_estudante()
    alternativas_questionario_estudante = ler_alternativas_questionario_estudante()

    if not perfil_estudante.empty:
        st.write("### Filtros por Perfil")

        opcoes_sexo = ['Todos'] + sorted(perfil_estudante['TP_SEXO'].dropna().unique().tolist())
        opcoes_faixa_idade = ['Todos'] + [
            faixa for faixa in ['Até 24 anos', '25 a 29 anos', '30 a 34 anos', '35 a 39 anos', '40 anos ou mais', 'Indefinido']
            if faixa in perfil_estudante['FAIXA_IDADE'].dropna().unique().tolist()
        ]
        opcoes_regiao = ['Todos'] + sorted(perfil_estudante['CO_REGIAO_CURSO'].dropna().unique().tolist())
        opcoes_turno = ['Todos'] + sorted(perfil_estudante['CO_TURNO_GRADUACAO'].dropna().unique().tolist())

        filtro1, filtro2, filtro3, filtro4 = st.columns(4)
        with filtro1:
            sexo_escolhido = st.selectbox("Sexo", opcoes_sexo, key='filtro_sexo_estudante')
        with filtro2:
            faixa_idade_escolhida = st.selectbox("Faixa etária", opcoes_faixa_idade, key='filtro_faixa_idade_estudante')
        with filtro3:
            regiao_escolhida = st.selectbox("Região do curso", opcoes_regiao, key='filtro_regiao_estudante')
        with filtro4:
            turno_escolhido = st.selectbox("Turno", opcoes_turno, key='filtro_turno_estudante')

        st.button(
            "Limpar filtros",
            key='limpar_filtros_estudante',
            on_click=limpar_filtros,
            args=(
                'filtro_sexo_estudante',
                'filtro_faixa_idade_estudante',
                'filtro_regiao_estudante',
                'filtro_turno_estudante'
            )
        )


        mascara_perfil = aplicar_filtros_perfil(
            perfil_estudante,
            sexo_escolhido,
            faixa_idade_escolhida,
            regiao_escolhida,
            turno_escolhido
        )
        dados_questionario_estudante = ler_questionario_estudante_filtrado(mascara_perfil)
    else:
        st.warning("Dados de perfil do estudante não encontrados. A análise será exibida sem filtros.")
        dados_questionario_estudante = ler_dados_csv('questionario_estudante')

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
            total_respostas_pergunta = tabela_frequencia["Total de Respostas"].sum()
            tabela_frequencia["Percentual"] = (
                tabela_frequencia["Total de Respostas"] / total_respostas_pergunta * 100
            ).round(2)
            tabela_frequencia = tabela_frequencia[["Código da Resposta", "Resposta", "Total de Respostas", "Percentual"]]
            st.dataframe(tabela_frequencia, use_container_width=True)
    else:
        st.warning("Dados do Questionário do Estudante não encontrados na pasta.")

with tab2:
    st.subheader("Análise de Dados das Perguntas do Questionário Contextual")
    
    caminho_questionario_pdf = workspace / 'data' / 'questionario_contextual' / 'Questionário Contextual Enamed 2025.pdf'
    if caminho_questionario_pdf.exists():
        st.download_button("Baixar o questionário", data=caminho_questionario_pdf.read_bytes(), file_name="Questionário Contextual Enamed 2025.pdf", mime="application/pdf")
    
    st.divider()
    st.write("### Perguntas do Questionário Contextual")

    perfil_contextual = ler_perfil_contextual()

    if not perfil_contextual.empty:
        st.write("#### Filtros")

        opcoes_sexo_contextual = ['Todos'] + sorted(perfil_contextual['TP_SEXO'].dropna().unique().tolist())
        opcoes_faixa_contextual = ['Todos'] + [
            faixa for faixa in ['Até 24 anos', '25 a 29 anos', '30 a 34 anos', '35 a 39 anos', '40 anos ou mais', 'Indefinido']
            if faixa in perfil_contextual['FAIXA_IDADE'].dropna().unique().tolist()
        ]


        filtro_contextual1, filtro_contextual2 = st.columns(2)
        with filtro_contextual1:
            sexo_contextual = st.selectbox("Sexo", opcoes_sexo_contextual, key='filtro_sexo_contextual')
        with filtro_contextual2:
            faixa_contextual = st.selectbox("Faixa etária", opcoes_faixa_contextual, key='filtro_faixa_idade_contextual')

        st.button(
            "Limpar filtros",
            key='limpar_filtros_contextual',
            on_click=limpar_filtros,
            args=(
                'filtro_sexo_contextual',
                'filtro_faixa_idade_contextual'
            )
        )

        mascara_contextual = aplicar_filtros_contextual(
            perfil_contextual,
            sexo_contextual,
            faixa_contextual
        )
        dados_questionario_contextual = ler_questionario_contextual_filtrado(mascara_contextual)
    else:
        st.warning("Dados de perfil contextual não encontrados. A análise será exibida sem filtros.")
        dados_questionario_contextual = ler_questionario_contextual()

    if dados_questionario_contextual['contagens']:
        pergunta_contextual_escolhida = st.selectbox(
            "Escolha a pergunta contextual para visualizar",
            list(dados_questionario_contextual['contagens'].keys()),
            format_func=lambda codigo: f"{codigo} - {PERGUNTAS_CONTEXTUAIS.get(codigo, codigo)}"
        )

        contagem_contextual = dados_questionario_contextual['contagens'][pergunta_contextual_escolhida]
        texto_pergunta_contextual = PERGUNTAS_CONTEXTUAIS.get(pergunta_contextual_escolhida, pergunta_contextual_escolhida)

        st.write(f"### {pergunta_contextual_escolhida}")
        st.write(texto_pergunta_contextual)

        total_contextual = int(contagem_contextual.sum())
        total_sem_resposta = int(contagem_contextual.get('.', 0))
        total_respostas_validas = total_contextual - total_sem_resposta
        percentual_sem_resposta = (total_sem_resposta / total_contextual * 100) if total_contextual else 0

        contagem_validas = contagem_contextual.drop(labels='.', errors='ignore')
        if not contagem_validas.empty:
            codigo_mais_frequente = contagem_validas.idxmax()
            total_mais_frequente = int(contagem_validas.max())
            percentual_mais_frequente = (total_mais_frequente / total_respostas_validas * 100) if total_respostas_validas else 0
            resposta_mais_frequente = descrever_resposta_contextual(pergunta_contextual_escolhida, codigo_mais_frequente)
        else:
            codigo_mais_frequente = '-'
            total_mais_frequente = 0
            percentual_mais_frequente = 0
            resposta_mais_frequente = 'Sem respostas válidas'

        info1, info2, info3, info4 = st.columns(4)
        with info1:
            st.metric("Total de respostas", value=f"{total_contextual:,}".replace(",", "."))
        with info2:
            st.metric("Respostas válidas", value=f"{total_respostas_validas:,}".replace(",", "."))
        with info3:
            st.metric("Sem resposta", value=f"{total_sem_resposta:,}".replace(",", "."), delta=f"{percentual_sem_resposta:.2f}%")
        with info4:
            st.metric("Alternativas marcadas", value=len(contagem_validas))

        total_mais_frequente_formatado = f"{total_mais_frequente:,}".replace(",", ".")
        st.info(
            f"Resposta mais frequente: {codigo_mais_frequente} - {resposta_mais_frequente} "
            f"({total_mais_frequente_formatado} respostas; {percentual_mais_frequente:.2f}% das respostas válidas)."
        )

        st.write("### Distribuição das Respostas")
        col_contextual1, col_contextual2 = st.columns(2)

        with col_contextual1:
            fig_pizza_contextual = gerar_grafico_pizza(contagem_contextual)
            st.pyplot(fig_pizza_contextual)

        with col_contextual2:
            fig_barra_contextual = gerar_grafico_barra(contagem_contextual)
            st.pyplot(fig_barra_contextual)

        st.write("#### Tabela de Frequência")
        tabela_contextual = contagem_contextual.rename_axis("Código da Resposta").reset_index(name="Total de Respostas")
        tabela_contextual["Resposta"] = tabela_contextual["Código da Resposta"].map(
            lambda resposta: descrever_resposta_contextual(pergunta_contextual_escolhida, resposta)
        )
        tabela_contextual["Percentual"] = (
            tabela_contextual["Total de Respostas"] / total_contextual * 100
        ).round(2)
        tabela_contextual = tabela_contextual[["Código da Resposta", "Resposta", "Total de Respostas", "Percentual"]]
        st.dataframe(tabela_contextual, use_container_width=True)
    else:
        st.warning("Dados das perguntas contextuais não encontrados na pasta.")

with tab3:
    st.subheader("Análise de Dados das Perguntas do Questionário de Percepção de Prova")

    caminho_percepcao_pdf = workspace / 'data' / 'questionario_percepcao_prova' / 'Questionário de Percepção de Prova Enamed 2025.pdf'
    if caminho_percepcao_pdf.exists():
        st.download_button(
            "Baixar o questionário",
            data=caminho_percepcao_pdf.read_bytes(),
            file_name="Questionário de Percepção de Prova Enamed 2025.pdf",
            mime="application/pdf"
        )

    st.divider()

    perfil_percepcao = ler_perfil_estudante()

    if not perfil_percepcao.empty:
        st.write("### Filtros por Perfil")

        opcoes_sexo_percepcao = ['Todos'] + sorted(perfil_percepcao['TP_SEXO'].dropna().unique().tolist())
        opcoes_faixa_idade_percepcao = ['Todos'] + [
            faixa for faixa in ['Até 24 anos', '25 a 29 anos', '30 a 34 anos', '35 a 39 anos', '40 anos ou mais', 'Indefinido']
            if faixa in perfil_percepcao['FAIXA_IDADE'].dropna().unique().tolist()
        ]
        opcoes_regiao_percepcao = ['Todos'] + sorted(perfil_percepcao['CO_REGIAO_CURSO'].dropna().unique().tolist())
        opcoes_turno_percepcao = ['Todos'] + sorted(perfil_percepcao['CO_TURNO_GRADUACAO'].dropna().unique().tolist())


        filtro_percepcao1, filtro_percepcao2, filtro_percepcao3, filtro_percepcao4 = st.columns(4)
        with filtro_percepcao1:
            sexo_percepcao = st.selectbox("Sexo", opcoes_sexo_percepcao, key='filtro_sexo_percepcao')
        with filtro_percepcao2:
            faixa_idade_percepcao = st.selectbox("Faixa etária", opcoes_faixa_idade_percepcao, key='filtro_faixa_idade_percepcao')
        with filtro_percepcao3:
            regiao_percepcao = st.selectbox("Região do curso", opcoes_regiao_percepcao, key='filtro_regiao_percepcao')
        with filtro_percepcao4:
            turno_percepcao = st.selectbox("Turno", opcoes_turno_percepcao, key='filtro_turno_percepcao')

        st.button(
            "Limpar filtros",
            key='limpar_filtros_percepcao',
            on_click=limpar_filtros,
            args=(
                'filtro_sexo_percepcao',
                'filtro_faixa_idade_percepcao',
                'filtro_regiao_percepcao',
                'filtro_turno_percepcao'
            )
        )

        mascara_percepcao = aplicar_filtros_perfil(
            perfil_percepcao,
            sexo_percepcao,
            faixa_idade_percepcao,
            regiao_percepcao,
            turno_percepcao
        )
        dados_percepcao_prova = ler_percepcao_prova_filtrada(mascara_percepcao)
    else:
        st.warning("Dados de perfil do estudante não encontrados. A análise será exibida sem filtros.")
        dados_percepcao_prova = ler_dados_csv('percepcao_prova')

    if dados_percepcao_prova['contagens']:
        pergunta_percepcao_escolhida = st.selectbox(
            "Escolha a pergunta de percepção de prova para visualizar",
            list(dados_percepcao_prova['contagens'].keys()),
            format_func=lambda codigo: f"{codigo} - {PERGUNTAS_PERCEPCAO_PROVA.get(codigo, codigo)}"
        )

        contagem_percepcao = dados_percepcao_prova['contagens'][pergunta_percepcao_escolhida]
        texto_pergunta_percepcao = PERGUNTAS_PERCEPCAO_PROVA.get(pergunta_percepcao_escolhida, pergunta_percepcao_escolhida)

        st.write(f"### {pergunta_percepcao_escolhida}")
        st.write(texto_pergunta_percepcao)

        total_percepcao = int(contagem_percepcao.sum())
        total_sem_resposta_percepcao = int(contagem_percepcao.get('.', 0)) + int(contagem_percepcao.get('*', 0))
        total_respostas_validas_percepcao = total_percepcao - total_sem_resposta_percepcao
        percentual_sem_resposta_percepcao = (total_sem_resposta_percepcao / total_percepcao * 100) if total_percepcao else 0

        contagem_validas_percepcao = contagem_percepcao.drop(labels=['.', '*'], errors='ignore')
        if not contagem_validas_percepcao.empty:
            codigo_mais_frequente_percepcao = contagem_validas_percepcao.idxmax()
            total_mais_frequente_percepcao = int(contagem_validas_percepcao.max())
            percentual_mais_frequente_percepcao = (
                total_mais_frequente_percepcao / total_respostas_validas_percepcao * 100
            ) if total_respostas_validas_percepcao else 0
            resposta_mais_frequente_percepcao = descrever_resposta_percepcao(
                pergunta_percepcao_escolhida,
                codigo_mais_frequente_percepcao
            )
        else:
            codigo_mais_frequente_percepcao = '-'
            total_mais_frequente_percepcao = 0
            percentual_mais_frequente_percepcao = 0
            resposta_mais_frequente_percepcao = 'Sem respostas válidas'

        info1, info2, info3, info4 = st.columns(4)
        with info1:
            st.metric("Total de respostas", value=f"{total_percepcao:,}".replace(",", "."))
        with info2:
            st.metric("Respostas válidas", value=f"{total_respostas_validas_percepcao:,}".replace(",", "."))
        with info3:
            st.metric(
                "Sem resposta",
                value=f"{total_sem_resposta_percepcao:,}".replace(",", "."),
                delta=f"{percentual_sem_resposta_percepcao:.2f}%"
            )
        with info4:
            st.metric("Alternativas marcadas", value=len(contagem_validas_percepcao))

        total_mais_frequente_percepcao_formatado = f"{total_mais_frequente_percepcao:,}".replace(",", ".")
        st.info(
            f"Resposta mais frequente: {codigo_mais_frequente_percepcao} - {resposta_mais_frequente_percepcao} "
            f"({total_mais_frequente_percepcao_formatado} respostas; "
            f"{percentual_mais_frequente_percepcao:.2f}% das respostas válidas)."
        )

        st.write("### Distribuição das Respostas")
        col_percepcao1, col_percepcao2 = st.columns(2)

        with col_percepcao1:
            fig_pizza_percepcao = gerar_grafico_pizza(contagem_percepcao)
            st.pyplot(fig_pizza_percepcao)

        with col_percepcao2:
            fig_barra_percepcao = gerar_grafico_barra(contagem_percepcao)
            st.pyplot(fig_barra_percepcao)

        st.write("#### Tabela de Frequência")
        tabela_percepcao = contagem_percepcao.rename_axis("Código da Resposta").reset_index(name="Total de Respostas")
        tabela_percepcao["Resposta"] = tabela_percepcao["Código da Resposta"].map(
            lambda resposta: descrever_resposta_percepcao(pergunta_percepcao_escolhida, resposta)
        )
        tabela_percepcao["Percentual"] = (
            tabela_percepcao["Total de Respostas"] / total_percepcao * 100
        ).round(2)
        tabela_percepcao = tabela_percepcao[["Código da Resposta", "Resposta", "Total de Respostas", "Percentual"]]
        st.dataframe(tabela_percepcao, use_container_width=True)
    else:
        st.warning("Dados do Questionário de Percepção de Prova não encontrados na pasta.")
