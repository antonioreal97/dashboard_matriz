import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import unicodedata
import re

# Função de senha precisa ser definida antes de ser chamada

def check_password():
    def password_entered():
        if st.session_state["password"] == "PCF2025":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Remove a senha da sessão por segurança
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Digite a senha para acessar o dashboard:", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("Digite a senha para acessar o dashboard:", type="password", on_change=password_entered, key="password")
        st.error("Senha incorreta. Tente novamente.")
        st.stop()
    else:
        return True

check_password()

# Paleta de cores personalizada
COLOR_PRIMARY = '#2F473F'  # 50%
COLOR_SECONDARY = '#69C655'  # 25%
COLOR_ACCENT = '#CC4A23'  # 15%
COLOR_LIST = [COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT]

# Função para ler e organizar os dados
@st.cache_data
def load_data(path):
    # Ler o arquivo Excel
    df = pd.read_excel(path, header=[0,1])  # Usar as duas primeiras linhas como cabeçalho
    # Preencher valores ausentes na coluna 'Bloco' para garantir filtro correto
    if 'Bloco' in df.columns:
        df['Bloco'] = df['Bloco'].fillna(method='ffill')
    elif ('GERAL', 'Bloco') in df.columns:
        df[('GERAL', 'Bloco')] = df[('GERAL', 'Bloco')].fillna(method='ffill')
    return df

def normalize(s):
    if not isinstance(s, str):
        return ''
    return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII').lower().replace(' ', '')

def get_blocos():
    return [
        ('BLOCO 1', 'Estratégia de Coleta e Redistribuição', ['Articulação', 'Triagem e Logística', 'Enriquecimento da captação']),
        ('BLOCO 2', 'Operação do Banco de Alimentos', ['Estrutura', 'Processos']),
        ('BLOCO 3', 'Sustentabilidade Financeira', ['Aporte Inicial', 'Custos de Operação']),
        ('BLOCO 4', 'Sustentabilidade e Prevenção de Descarte', ['Sustentabilidade do Banco de Alimentos', 'Sustentabilidade da Ceasa']),
        ('BLOCO 5', 'Monitoramento e Gestão', ['Resultados de Eficiência']),
        ('BLOCO 6', 'Estrutura Física', ['Edificação'])
    ]

def get_regioes():
    return ['Belem/PA', 'São Luis/MA', 'CEAGESP/SP', 'Mais Nutrição/CE', 'PRODAL/MG', 'Curitiba/PR', 'GLOBAL']

def find_column(df, region, pattern):
    """Encontra a coluna que contém a região e o padrão especificado"""
    normalized_cols = {normalize(col): col for col in df.columns}
    normalized_region = normalize(region)
    normalized_pattern = normalize(pattern)
    
    matching_cols = [
        original_col for norm_col, original_col in normalized_cols.items()
        if normalized_region in norm_col and normalized_pattern in norm_col
    ]
    
    return matching_cols[0] if matching_cols else None

def extrair_dados(df):
    blocos = get_blocos()
    regioes = get_regioes()
    dados = []
    
    # Para cada região
    for reg in regioes:
        # Encontrar as colunas relevantes para esta região
        pontuacao_col = (reg, f'{reg} pontuação')
        bloco_col = (reg, 'Pontuação no Bloco ')
        perc_col = (reg, f'{reg} %')  # coluna de porcentagem
        
        # Verificar se a coluna de porcentagem existe
        perc_col_exists = perc_col in df.columns
        
        # Para cada bloco
        for bloco_idx, (bloco_nome, bloco_titulo, atividades) in enumerate(blocos):
            try:
                # Calcular os índices das linhas para este bloco
                inicio = sum(len(b[2]) for b in blocos[:bloco_idx])  # Soma das atividades dos blocos anteriores
                fim = inicio + len(atividades)
                
                # Extrair pontuações das atividades
                pontuacoes = df.loc[inicio:fim-1, pontuacao_col].astype(float).values
                
                # Extrair pontuação do bloco (primeira linha do bloco)
                pontuacao_bloco = float(df.loc[inicio, bloco_col])
                
                # Extrair porcentagem do bloco (primeira linha do bloco)
                if perc_col_exists:
                    try:
                        porcentagem_bloco = float(df.loc[inicio, perc_col])
                    except Exception:
                        porcentagem_bloco = None
                else:
                    porcentagem_bloco = None
                
                dados.append({
                    'Região': reg,
                    'Bloco': bloco_nome,
                    'Título': bloco_titulo,
                    'Pontuação no Bloco': pontuacao_bloco,
                    'Porcentagem no Bloco': porcentagem_bloco,
                    'Atividades': atividades,
                    'Pontuações': pontuacoes.tolist()
                })
            except Exception as e:
                st.warning(f"Erro ao processar {reg} - {bloco_nome}: {str(e)}")
                continue
    
    if not dados:
        st.error("Nenhum dado foi extraído da planilha. Verifique o formato dos dados.")
        return pd.DataFrame()
    
    return pd.DataFrame(dados)

def get_destaques(df_blocos):
    if df_blocos.empty:
        return {}
    
    destaques = {}
    for bloco in df_blocos['Bloco'].unique():
        bloco_df = df_blocos[df_blocos['Bloco'] == bloco]
        max_idx = bloco_df['Pontuação no Bloco'].idxmax()
        min_idx = bloco_df['Pontuação no Bloco'].idxmin()
        destaques[bloco] = {
            'maior': (bloco_df.loc[max_idx, 'Região'], bloco_df.loc[max_idx, 'Pontuação no Bloco']),
            'menor': (bloco_df.loc[min_idx, 'Região'], bloco_df.loc[min_idx, 'Pontuação no Bloco'])
        }
    return destaques

# Forçar tema claro do Streamlit
st.set_page_config(page_title='Dashboard Matriz Avaliativa', layout='wide', page_icon='📊')
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Yrsa:wght@400;600&display=swap" rel="stylesheet">
    <style>
    :root {
      --font-primary: 'Poppins', sans-serif;
      --font-secondary: 'Yrsa', serif;
      --color-secondary: #69C655;
    }
    html, body, .stApp, [data-testid="stSidebar"], .css-1d391kg, .css-1v0mbdj, .css-1cpxqw2 {
        background-color: #fff !important;
        color: #222 !important;
        font-family: var(--font-primary) !important;
    }
    * {
        font-family: var(--font-primary) !important;
    }
    /* Header/topo branco e sem sombra */
    header, .st-emotion-cache-18ni7ap, .st-emotion-cache-1avcm0n, .st-emotion-cache-6qob1r {
        background: #fff !important;
        box-shadow: none !important;
        color: #2F473F !important;
    }
    header * {
        color: #2F473F !important;
    }
    /* Sidebar: título Filtros */
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] h4 {
        font-size: 2em !important;
        color: #2F473F !important;
        font-weight: 800 !important;
        margin-bottom: 18px !important;
        font-family: var(--font-primary) !important;
    }
    /* Sidebar: títulos dos expanders */
    section[data-testid="stSidebar"] .st-expander > summary {
        font-size: 1.18em !important;
        color: #2F473F !important;
        font-weight: 700 !important;
        margin-bottom: 6px !important;
        font-family: var(--font-primary) !important;
    }
    /* Sidebar: radio buttons */
    section[data-testid="stSidebar"] .stRadio label, section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label, section[data-testid="stSidebar"] .stRadio span, section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > div,
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] span, section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label span, section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label div {
        color: #2F473F !important;
        font-weight: 600 !important;
        font-size: 1em !important;
        opacity: 1 !important;
        font-family: var(--font-primary) !important;
    }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        opacity: 1 !important;
    }
    /* Espaçamento extra entre seções da sidebar */
    section[data-testid="stSidebar"] .st-expander, section[data-testid="stSidebar"] .stRadio {
        margin-bottom: 18px !important;
    }
    /* Filtros: cards */
    .stMultiSelect, .stSelectbox, .stSlider, .stTextInput, .stNumberInput, .st-bw, .st-c3 {
        background-color: #2F473F !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(47,71,63,0.08);
        color: #fff !important;
        border: 1.5px solid #2F473F !important;
        margin-bottom: 12px !important;
        padding: 6px 8px !important;
        font-family: var(--font-primary) !important;
    }
    /* Radio button: garantir texto visível */
    .stRadio label, .stRadio div[role="radiogroup"] > label, .stRadio span, .stRadio div[role="radiogroup"] > div,
    .stRadio div[role="radiogroup"] span, .stRadio div[role="radiogroup"] label span, .stRadio div[role="radiogroup"] label div {
        color: #2F473F !important;
        font-weight: 600 !important;
        font-size: 1.08em !important;
        opacity: 1 !important;
        font-family: var(--font-primary) !important;
    }
    .stRadio div[role="radiogroup"] label {
        opacity: 1 !important;
    }
    /* Chips/tags das opções selecionadas */
    .stMultiSelect .css-1r6slb0, .stMultiSelect .css-12jo7m5 {
        background-color: #69C655 !important;
        color: #222 !important;
        border-radius: 8px !important;
        margin: 2px 4px !important;
        font-weight: 600;
        font-size: 1em;
        border: 1.5px solid #69C655 !important;
        box-shadow: 0 1px 4px rgba(105,198,85,0.10);
        font-family: var(--font-primary) !important;
    }
    /* Botão X das tags ao passar o mouse */
    .stMultiSelect .css-xb97g8:hover, .stMultiSelect .css-1wa3eu0 .css-xb97g8:hover {
        background-color: #CC4A23 !important;
        color: #fff !important;
        border-radius: 50% !important;
    }
    /* Títulos dos filtros */
    .stMarkdown h4, .stMarkdown h5, .stMarkdown h6, .stMarkdown h3, .stMarkdown h2, .stMarkdown h1 {
        color: #2F473F !important;
        font-weight: 700;
        margin-bottom: 8px;
        font-family: var(--font-primary) !important;
    }
    /* Ajuste para o container dos filtros na área principal */
    .block-container > div > .stMarkdown, .block-container > div > .stMultiSelect, .block-container > div > .stSelectbox, .block-container > div > .stSlider {
        margin-bottom: 18px !important;
    }
    /* Fonte secundária para elementos específicos (exemplo de uso) */
    .fonte-secundaria {
        font-family: var(--font-secondary) !important;
    }
    /* Botão de download customizado */
    .stDownloadButton button {
        background-color: var(--color-secondary) !important;
        color: #111 !important;
        font-weight: 700 !important;
        font-size: 1.08em !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 10px 24px !important;
        box-shadow: 0 2px 8px rgba(105,198,85,0.10);
        margin-bottom: 18px !important;
        font-family: var(--font-primary) !important;
    }
    .stDownloadButton button:hover {
        background-color: #57a94d !important;
        color: #fff !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Logo no topo
st.image('1.png', width=200)

st.title('Dashboard Matriz Avaliativa das Ceasas')

# Legenda dos Blocos
with st.expander('Legenda dos Blocos', expanded=False):
    st.markdown("""
    <div style='font-size:1.3em; font-weight:bold; margin-bottom: 0.7em; color:#222;'>Legenda dos Blocos</div>
    <div style='line-height:1.6; color:#222;'>
    <div style='margin-bottom: 1.2em;'><span style='font-size:1.1em; font-weight:bold;'>BLOCO 1:</span> Estratégia de Coleta e Redistribuição<br><span style='color:#69C655; font-size:1em;'>Atividades:</span> Articulação, Triagem e Logística, Enriquecimento da captação</div>
    <div style='margin-bottom: 1.2em;'><span style='font-size:1.1em; font-weight:bold;'>BLOCO 2:</span> Operação do Banco de Alimentos<br><span style='color:#69C655; font-size:1em;'>Atividades:</span> Estrutura, Processos</div>
    <div style='margin-bottom: 1.2em;'><span style='font-size:1.1em; font-weight:bold;'>BLOCO 3:</span> Sustentabilidade Financeira<br><span style='color:#69C655; font-size:1em;'>Atividades:</span> Aporte Inicial, Custos de Operação</div>
    <div style='margin-bottom: 1.2em;'><span style='font-size:1.1em; font-weight:bold;'>BLOCO 4:</span> Sustentabilidade e Prevenção de Descarte<br><span style='color:#69C655; font-size:1em;'>Atividades:</span> Sustentabilidade do Banco de Alimentos, Sustentabilidade da Ceasa</div>
    <div style='margin-bottom: 1.2em;'><span style='font-size:1.1em; font-weight:bold;'>BLOCO 5:</span> Monitoramento e Gestão<br><span style='color:#69C655; font-size:1em;'>Atividades:</span> Resultados de Eficiência</div>
    <div style='margin-bottom: 0.5em;'><span style='font-size:1.1em; font-weight:bold;'>BLOCO 6:</span> Estrutura Física<br><span style='color:#69C655; font-size:1em;'>Atividades:</span> Edificação</div>
    </div>
    """, unsafe_allow_html=True)

# Upload ou uso do arquivo local
file_path = 'Matriz_Avaliativa_Ceasas.xlsx'
if not Path(file_path).exists():
    file_path = st.file_uploader('Envie a planilha Excel', type=['xlsx'])
    if not file_path:
        st.stop()

# Carregar dados
df = load_data(file_path)

# Extrair dados processados
df_blocos = extrair_dados(df)

if df_blocos.empty:
    st.stop()

# Calcular destaques
destaques = get_destaques(df_blocos)

# Filtros
st.sidebar.header('Filtros')
with st.sidebar.expander('Selecione os Ceasas', expanded=False):
    regioes_sel = st.multiselect('', df_blocos['Região'].unique(), default=df_blocos['Região'].unique(), key='regioes_sidebar')
with st.sidebar.expander('Selecione os blocos', expanded=False):
    blocos_sel = st.multiselect('', df_blocos['Bloco'].unique(), default=df_blocos['Bloco'].unique(), key='blocos_sidebar')
with st.sidebar.expander('Selecione as atividades (exibe blocos que contêm)', expanded=False):
    atividades_unicas = sorted(set(sum(df_blocos['Atividades'].tolist(), [])))
    atividades_sel = st.multiselect('', atividades_unicas, default=atividades_unicas, key='atividades_sidebar')
pontuacao_min = float(df_blocos['Pontuação no Bloco'].min())
pontuacao_max = float(df_blocos['Pontuação no Bloco'].max())
with st.sidebar.expander('Faixa de pontuação do bloco', expanded=False):
    faixa_pontuacao = st.slider('', min_value=pontuacao_min, max_value=pontuacao_max, value=(pontuacao_min, pontuacao_max), key='faixa_sidebar')

# Seletor de tipo de visualização
tipo_viz = st.sidebar.radio('Tipo de visualização', ['Gráfico de Barras', 'Radar', 'Tabela'])

def bloco_contem_atividade(row):
    return any(a in atividades_sel for a in row['Atividades'])

# Filtragem
filtro = (
    df_blocos['Região'].isin(regioes_sel) &
    df_blocos['Bloco'].isin(blocos_sel) &
    df_blocos.apply(bloco_contem_atividade, axis=1) &
    df_blocos['Pontuação no Bloco'].between(*faixa_pontuacao)
)
df_blocos_filt = df_blocos[filtro]

# Ordenar do maior para o menor
if not df_blocos_filt.empty:
    df_blocos_filt = df_blocos_filt.sort_values('Pontuação no Bloco', ascending=False)

# Exibir o painel 'Destaques por Bloco' apenas quando tipo_viz == 'Gráfico de Barras'
if tipo_viz == 'Gráfico de Barras' and destaques and not df_blocos_filt.empty:
    # Ordenar blocos pelo maior destaque (pontuação) de forma decrescente
    blocos_ordenados = [bloco for bloco in blocos_sel if bloco in destaques]
    destaques_html = "<div style='display: flex; flex-direction: row; justify-content: flex-start; align-items: flex-start; gap: 36px; flex-wrap: nowrap; overflow-x: auto; padding-bottom: 8px;'>"
    for idx, bloco in enumerate(blocos_ordenados, 1):
        destaques_html += (
            f"<div style='min-width: 160px; margin-bottom:0px;'><span style='font-size:1em; font-weight:bold;'>{idx}. {bloco}</span><br>"
            f"<span style='font-size:1.05em;'>{destaques[bloco]['maior'][0]}: {destaques[bloco]['maior'][1]:.1f}</span><br>"
            f"<span style='font-size:0.9em;'>Menor: {destaques[bloco]['menor'][0]} ({destaques[bloco]['menor'][1]:.1f})</span></div>"
        )
    destaques_html += "</div>"
    st.markdown(
        f"""
        <div style='background:#2F473F; color:#fff; border-radius:10px; padding: 24px 24px 12px 24px; margin-bottom: 24px;'>
        <div style='font-size:1.3em; font-weight:bold; margin-bottom: 18px;'>Destaques por Bloco</div>
        {destaques_html}
        </div>
        """,
        unsafe_allow_html=True
    )

# Visualização
if not df_blocos_filt.empty:
    if tipo_viz == 'Gráfico de Barras':
        # Definir ordem dos blocos
        ordem_blocos = ['BLOCO 1', 'BLOCO 2', 'BLOCO 3', 'BLOCO 4', 'BLOCO 5', 'BLOCO 6']
        fig = px.bar(
            df_blocos_filt,
            x='Bloco',
            y='Pontuação no Bloco',
            color='Região',
            barmode='group',
            color_discrete_map={
                'GLOBAL': '#4A90E2',
                'Belem/PA': '#2F473F',
                'São Luis/MA': '#69C655',
                'Mais Nutrição/CE': '#A3D9A5',
                'PRODAL/MG': '#4CAF50',
                'Curitiba/PR': '#81C784',
                'CEAGESP/SP': '#388E3C',
            },
            text='Pontuação no Bloco',
            title='Pontuação por Bloco do Ceasa',
            category_orders={'Bloco': ordem_blocos}
        )
        fig.update_traces(textfont_size=18, textfont_color='#2F473F')
        fig.update_layout(
            font=dict(size=18, color='#2F473F'),
            legend=dict(font=dict(size=16, color='#2F473F'), bgcolor='#fff'),
            xaxis_title_font=dict(size=18, color='#2F473F'),
            yaxis_title_font=dict(size=18, color='#2F473F'),
            title_font=dict(size=22, color='#2F473F'),
            plot_bgcolor='#fff',
            paper_bgcolor='#fff',
            xaxis=dict(color='#2F473F', tickfont=dict(color='#2F473F')),
            yaxis=dict(color='#2F473F', tickfont=dict(color='#2F473F'))
        )
        st.plotly_chart(fig, use_container_width=True)

        # Exibir o segundo gráfico de barras (Distribuição Percentual das Regiões) apenas se tipo_viz == 'Gráfico de Barras'
        # Função para obter tipos de percentual, renomeando para exibir sempre '% em relação ao Bloco'
        def get_percentual_types(df):
            tipos = set()
            for col in df.columns:
                if '%' in str(col[1]):
                    if str(col[1]).strip().lower() == '% em relação ao bloco 1':
                        tipos.add('% em relação ao Bloco')
                    else:
                        tipos.add(str(col[1]))
            return sorted(list(tipos))

        percentual_types = get_percentual_types(df)
        percentual_type = st.selectbox(
            'Selecione o tipo de percentual para o gráfico:',
            percentual_types,
            index=0
        )
        percentual_type_real = '% em relação ao Bloco 1' if percentual_type == '% em relação ao Bloco' else percentual_type
        percentage_cols = [col for col in df.columns if str(col[1]).strip().lower() == percentual_type_real.strip().lower()]
        col_bloco = None
        if 'Bloco' in df.columns:
            col_bloco = 'Bloco'
        elif ('GERAL', 'Bloco') in df.columns:
            col_bloco = ('GERAL', 'Bloco')

        # Se o tipo de percentual for geral, desabilitar filtro de bloco e não mostrar no título
        is_percentual_geral = percentual_type in ['% em relação a Matriz Total', '% em relação ao Total do Bloco']
        if is_percentual_geral:
            bloco_selecionado = None
            st.selectbox('Selecione o bloco:', ['Todos os blocos'], index=0, disabled=True)
        else:
            blocos_disponiveis = df[col_bloco].unique().tolist()
            bloco_selecionado = st.selectbox('Selecione o bloco:', blocos_disponiveis)

        # Filtrar os dados
        if is_percentual_geral:
            # Calcular a média dos percentuais para cada região (ignorando NaN)
            valores = []
            regioes = []
            for col in percentage_cols:
                media = df[col].dropna().mean()
                if pd.notnull(media):
                    valores.append(media)
                    regioes.append(col[0])
            titulo_grafico = f'Distribuição {percentual_type.replace("%", "Percentual").replace("em relacao", "em relação").capitalize()} dos Ceasas'
        else:
            linha_bloco = df[df[col_bloco] == bloco_selecionado]
            valores = []
            regioes = []
            for col in percentage_cols:
                valor = linha_bloco.iloc[0][col] if not linha_bloco.empty else None
                if pd.notnull(valor):
                    valores.append(valor)
                    regioes.append(col[0])
            titulo_grafico = f'Distribuição {percentual_type.replace("%", "Percentual").replace("em relacao", "em relação").capitalize()} dos Ceasas - {bloco_selecionado}'

        # Ordenar e plotar
        dados = sorted(zip(regioes, valores), key=lambda x: x[1], reverse=True)
        regioes_ord, valores_ord = zip(*dados) if dados else ([],[])
        if valores_ord:
            color_discrete_map = {
                'GLOBAL': '#4A90E2',
                'Belem/PA': '#2F473F',
                'São Luis/MA': '#69C655',
                'Mais Nutrição/CE': '#A3D9A5',
                'PRODAL/MG': '#4CAF50',
                'Curitiba/PR': '#81C784',
                'CEAGESP/SP': '#388E3C',
            }
            textpositions = ['inside' if v >= 0.9 else 'outside' for v in valores_ord]
            y_max = max(valores_ord) * 1.15
            fig = px.bar(
                x=regioes_ord,
                y=valores_ord,
                text=[f'<b>{v:.2%}</b>' for v in valores_ord],
                color=regioes_ord,
                color_discrete_map=color_discrete_map,
                title=titulo_grafico
            )
            fig.update_traces(
                textposition=textpositions,
                textfont_size=20,
                textfont_color='#222',
                marker_line_color='#fff',
                marker_line_width=2,
                hovertemplate='<b>%{x}</b><br>%{y:.2%} do bloco<extra></extra>'
            )
            fig.update_layout(
                font=dict(size=18, color='#2F473F'),
                legend=dict(font=dict(size=16, color='#2F473F'), bgcolor='#fff'),
                title_font=dict(size=22, color='#2F473F'),
                plot_bgcolor='#fff',
                paper_bgcolor='#fff',
                xaxis_title='Região',
                yaxis_title='Percentual (%)',
                yaxis=dict(tickformat='.0%', color='#2F473F', tickfont=dict(size=16), range=[0, y_max]),
                xaxis=dict(tickfont=dict(size=16, color='#2F473F'))
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info('Não há dados de porcentagem disponíveis para este bloco.')

    elif tipo_viz == 'Radar':
        regioes_radar = st.multiselect('Selecione os Ceasas para o Radar', df_blocos_filt['Região'].unique(), default=df_blocos_filt['Região'].unique())
        fig = go.Figure()
        color_discrete_map = {
            'GLOBAL': '#4A90E2',
            'Belem/PA': '#2F473F',
            'São Luis/MA': '#69C655',
            'Mais Nutrição/CE': '#A3D9A5',
            'PRODAL/MG': '#4CAF50',
            'Curitiba/PR': '#81C784',
            'CEAGESP/SP': '#388E3C',
        }
        # Obter pontuação máxima de cada bloco do gabarito geral
        # Supondo que o arquivo Excel tem MultiIndex e a linha do gabarito geral é única por bloco
        # Vamos buscar no DataFrame original (df) a pontuação máxima de cada bloco
        pontuacao_maxima_blocos = {}
        if ('GERAL', 'Bloco') in df.columns and ('GERAL', 'Pontuação Maxima por Bloco') in df.columns:
            for idx, row in df.iterrows():
                bloco = row[('GERAL', 'Bloco')]
                pontuacao_max = row[('GERAL', 'Pontuação Maxima por Bloco')]
                if pd.notnull(bloco) and pd.notnull(pontuacao_max):
                    pontuacao_maxima_blocos[bloco] = pontuacao_max
        else:
            # Alternativa: tentar buscar do df_blocos se não achar no df
            for bloco in df_blocos_filt['Bloco'].unique():
                pontuacao_max = df_blocos_filt[df_blocos_filt['Bloco'] == bloco]['Pontuação no Bloco'].max()
                pontuacao_maxima_blocos[bloco] = pontuacao_max
        for i, reg in enumerate(regioes_radar):
            dados = df_blocos_filt[df_blocos_filt['Região'] == reg]
            cor = color_discrete_map.get(reg, '#2F473F')
            # Calcular percentual de acertos por bloco
            percentuais = []
            blocos = []
            for idx, row in dados.iterrows():
                bloco = row['Bloco']
                pontuacao = row['Pontuação no Bloco']
                pontuacao_max = pontuacao_maxima_blocos.get(bloco, None)
                if pontuacao_max and pontuacao_max > 0:
                    percentual = pontuacao / pontuacao_max * 100
                else:
                    percentual = 0
                percentuais.append(percentual)
                blocos.append(bloco)
            fig.add_trace(go.Scatterpolar(
                r=percentuais,
                theta=blocos,
                fill='toself',
                name=reg,
                line_color=cor,
                text=[f'{p:.1f}%' for p in percentuais],
                textfont=dict(size=18, color='#2F473F')
            ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, tickfont=dict(size=16, color='#2F473F'), gridcolor='#ccc', linecolor='#2F473F', showline=True, range=[0, 100], tickformat='.0f', title='Percentual (%)')),
            showlegend=True,
            legend=dict(font=dict(size=16, color='#2F473F'), bgcolor='#fff'),
            title='Perfil dos Blocos por Ceasa (Percentual de Acertos)',
            font=dict(size=18, color='#2F473F'),
            title_font=dict(size=22, color='#2F473F'),
            plot_bgcolor='#fff',
            paper_bgcolor='#fff'
        )
        st.plotly_chart(fig, use_container_width=True)

    elif tipo_viz == 'Tabela':
        # Filtros específicos para a tabela
        st.markdown('#### Filtros da Tabela')
        with st.expander('Filtrar por Ceasa', expanded=False):
            regioes_tab = st.multiselect('', df_blocos_filt['Região'].unique(), default=df_blocos_filt['Região'].unique(), key='regiao_tab')
        with st.expander('Filtrar por Bloco', expanded=False):
            blocos_tab = st.multiselect('', df_blocos_filt['Bloco'].unique(), default=df_blocos_filt['Bloco'].unique(), key='bloco_tab')
        with st.expander('Filtrar por Atividade', expanded=False):
            atividades_tab = st.multiselect('', sorted(set(sum(df_blocos_filt['Atividades'].tolist(), []))), default=sorted(set(sum(df_blocos_filt['Atividades'].tolist(), []))), key='atividade_tab')
        with st.expander('Filtrar por Faixa de Pontuação', expanded=False):
            faixa_tab = st.slider('', float(df_blocos_filt['Pontuação no Bloco'].min()), float(df_blocos_filt['Pontuação no Bloco'].max()), (float(df_blocos_filt['Pontuação no Bloco'].min()), float(df_blocos_filt['Pontuação no Bloco'].max())), key='faixa_tab')
        def bloco_contem_atividade_tab(row):
            return any(a in atividades_tab for a in row['Atividades'])
        filtro_tab = (
            df_blocos_filt['Região'].isin(regioes_tab) &
            df_blocos_filt['Bloco'].isin(blocos_tab) &
            df_blocos_filt.apply(bloco_contem_atividade_tab, axis=1) &
            df_blocos_filt['Pontuação no Bloco'].between(*faixa_tab)
        )
        df_tabela = df_blocos_filt[filtro_tab]
        # Remover a coluna 'Porcentagem no Bloco' se existir
        if 'Porcentagem no Bloco' in df_tabela.columns:
            df_tabela = df_tabela.drop(columns=['Porcentagem no Bloco'])
        # Remover a coluna 'Pontuação no Bloco' se existir
        if 'Pontuação no Bloco' in df_tabela.columns:
            df_tabela = df_tabela.drop(columns=['Pontuação no Bloco'])
        # Ajustar a coluna '% em relação ao Total do Bloco' para exibir como porcentagem
        if '% em relação ao Total do Bloco' in df_tabela.columns:
            def formatar_percentual(val):
                if isinstance(val, list):
                    return [f'{v*100:.2f}%' if v is not None and not pd.isna(v) else '' for v in val]
                elif val is not None and not pd.isna(val):
                    return f'{val*100:.2f}%'
                else:
                    return ''
            df_tabela['% em relação ao Total do Bloco'] = df_tabela['% em relação ao Total do Bloco'].apply(formatar_percentual)
        # Adicionar coluna de porcentagem de acertos por bloco em relação ao geral
        if 'Pontuação no Bloco' in df_tabela.columns and 'Pontuação Maxima da Matriz' in df_tabela.columns:
            df_tabela['Porcentagem de Acertos no Bloco (em relação ao Geral)'] = (
                df_tabela['Pontuação no Bloco'] / df_tabela['Pontuação Maxima da Matriz'] * 100
            ).round(2)
        # Corrigir a coluna '% em relação ao Bloco' para buscar o valor correto de '% em relação ao Total do Bloco' no DataFrame original e renomear a coluna
        if 'Bloco' in df_tabela.columns and 'Região' in df_tabela.columns and 'Atividades' in df_tabela.columns:
            valores_percentuais = []
            for idx, row in df_tabela.iterrows():
                bloco = row['Bloco']
                regiao = row['Região']
                atividades = row['Atividades']
                percentuais_atividade = []
                for atividade in atividades:
                    filtro = (
                        ((df['Bloco'] == bloco) if 'Bloco' in df.columns else (df[('GERAL', 'Bloco')] == bloco)) &
                        ((df['Atividade'] == atividade) if 'Atividade' in df.columns else (df[('GERAL', 'Atividade')] == atividade))
                    )
                    col_tuple = None
                    for col in df.columns:
                        if isinstance(col, tuple):
                            if col[0] == regiao and col[1].strip().lower() == '% em relação ao total do bloco':
                                col_tuple = col
                                break
                    valor = None
                    if col_tuple is not None:
                        linha_df = df[filtro]
                        if not linha_df.empty:
                            valor = linha_df.iloc[0][col_tuple]
                    percentuais_atividade.append(valor)
                if len(percentuais_atividade) == 1:
                    valores_percentuais.append(percentuais_atividade[0])
                else:
                    valores_percentuais.append(percentuais_atividade)
            df_tabela['% em relação ao Total do Bloco'] = valores_percentuais
            if '% em relação ao Bloco' in df_tabela.columns:
                df_tabela = df_tabela.drop(columns=['Porcentagem no Bloco'])
        # Botão para download do CSV
        csv = df_tabela.to_csv(index=False, sep=';', encoding='utf-8')
        st.download_button(
            label='Baixar tabela filtrada em CSV',
            data=csv,
            file_name='tabela_filtrada.csv',
            mime='text/csv',
            help='Baixe a tabela exatamente como está filtrada na tela.'
        )
        st.markdown(
            df_tabela.to_html(
                index=False,
                escape=False,
                border=0,
                classes='tabela-branca',
                justify='center'
            ),
            unsafe_allow_html=True
        )
        st.markdown(
            """
            <style>
            .tabela-branca {
                background: #fff !important;
                color: #222 !important;
                border-radius: 10px;
                border-collapse: separate;
                border-spacing: 0;
                width: 100%;
                font-size: 1.05em;
            }
            .tabela-branca th, .tabela-branca td {
                background: #fff !important;
                color: #222 !important;
                padding: 8px 10px;
                border: 1px solid #e0e0e0;
            }
            .tabela-branca th {
                font-weight: bold;
                background: #f5f5f5 !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        ) 