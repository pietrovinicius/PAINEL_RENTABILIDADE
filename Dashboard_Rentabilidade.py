import streamlit as st
import pandas as pd
import os
import datetime
import plotly.express as px
import io
import locale

# Configuração da página Streamlit
st.set_page_config(layout="wide", initial_sidebar_state="collapsed", page_title="Dashboard de Rentabilidade")

# Função para obter o timestamp atual
def obter_timestamp_atual():
    """Retorna o timestamp atual no formato YYYY-MM-DD HH-MM-SS."""
    print('Retorna o timestamp atual no formato YYYY-MM-DD HH-MM-SS.')
    return datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    
def preparar_download_excel(df, filename="dados.xlsx"):
    """Converte um DataFrame em um arquivo Excel na memória para download."""
    print("preparar_download_excel()")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        print("Converte um DataFrame em um arquivo Excel na memória para download.")
        print("df.to_excel(writer, sheet_name='Sheet1', index=False)")
        df.to_excel(writer, sheet_name='Sheet1', index=False)
    return output.getvalue()
    
# 1. Criar Dados Fictícios e Salvar em XLSX
def criar_dados_ficticios():
    """Cria dados fictícios e salva em um arquivo XLSX."""
    print(f'\n====criar_dados_ficticios()')
    # Cria datas de forma incremental
    data_inicial = datetime.date(2022, 1, 1)
    data_final = datetime.date(2024, 12, 31)
    datas = []
    while data_inicial <= data_final:
        datas.append(data_inicial)
        data_inicial += datetime.timedelta(days=31)
    
    # Cria listas para os anos e meses
    anos = [data.year for data in datas]
    meses = [data.month for data in datas]
    
    # Cria dados fictícios para receita
    receitas = [50000 + (i * 10000) + (i * 5000 * (i % 2)) for i in range(len(datas))]
    df_receitas = pd.DataFrame({'ANO': anos, 'MES': meses, 'RECEITA': receitas})
    print(f'df_receitas: {df_receitas.shape}')
    
    # Cria dados fictícios para custos diretos
    custos_diretos = [25000 + (i * 2000) + (i * 2500 * (i % 3)) for i in range(len(datas))]
    df_custos_diretos = pd.DataFrame({'ANO': anos, 'MES': meses, 'CUSTO_DIRETO': custos_diretos})
    print(f'df_custos_diretos: {df_custos_diretos.shape}')
    
    # Cria dados fictícios para custos fixos
    custos_fixos = [10000 + (i * 500) for i in range(len(datas))]
    df_custos_fixos = pd.DataFrame({'ANO': anos, 'MES': meses, 'CUSTO_FIXO': custos_fixos})
    print(f'df_custos_fixos: {df_custos_fixos.shape}')
    
    # Concatena os dataframes em um dicionário
    dict_dataframes_ficticios = {
        'df_receitas': df_receitas,
        'df_custos_diretos': df_custos_diretos,
        'df_custos_fixos': df_custos_fixos
    }
    
    # Salva os dataframes em um único arquivo xlsx
    with pd.ExcelWriter('dados_ficticios_rentabilidade.xlsx', engine='xlsxwriter') as writer:
        for key, dataframe in dict_dataframes_ficticios.items():
            print(f'dataframe.to_excel(writer, sheet_name=key, index=False)')
            dataframe.to_excel(writer, sheet_name=key, index=False)
    
    st.success("Dados fictícios gerados e salvos em dados_ficticios_rentabilidade.xlsx!")
    print('Dados fictícios gerados e salvos em dados_ficticios_rentabilidade.xlsx!')

# 2. Carregar os Dados do XLSX
def carregar_dados_xlsx():
    """Carrega os dados do arquivo XLSX."""
    print(f'\n====carregar_dados_xlsx()')
    try:
        dict_dataframes_ficticios = pd.read_excel('dados_ficticios_rentabilidade.xlsx', sheet_name=None)
        
        df_receitas = dict_dataframes_ficticios['df_receitas']
        df_custos_diretos = dict_dataframes_ficticios['df_custos_diretos']
        df_custos_fixos = dict_dataframes_ficticios['df_custos_fixos']
        
        print(f'Dados fictícios carregados do arquivo XLSX!')
        st.success("Dados fictícios carregados do arquivo XLSX! " + obter_timestamp_atual())
        return df_receitas, df_custos_diretos, df_custos_fixos
    except Exception as e:
        print(f'carregar_dados_xlsx() except {Exception}')
        st.error(f"Erro ao carregar dados do XLSX: {e}. {obter_timestamp_atual()}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# 3. Calcular Indicadores
def calcular_indicadores(df_receitas, df_custos_diretos, df_custos_fixos):
    """Calcula os indicadores de rentabilidade."""
    print('\n====calcular_indicadores\n')
    
    # Mesclando os dataframes
    df_merged = pd.merge(df_receitas, df_custos_diretos, on=['ANO', 'MES'], how='outer', suffixes=('_receita', '_custo_direto'))
    df_merged = pd.merge(df_merged, df_custos_fixos, on=['ANO', 'MES'], how='outer')
    df_merged = df_merged.fillna(0)
    
    print(f'df_merged:\n{df_merged.head(3)}')
    
    # Calcula os indicadores
    df_merged['LUCRO_BRUTO'] = df_merged['RECEITA'] - df_merged['CUSTO_DIRETO']
    df_merged['MARGEM_LUCRO'] = (df_merged['LUCRO_BRUTO'] / df_merged['RECEITA']) * 100
    df_merged['LUCRO_LIQUIDO'] = df_merged['LUCRO_BRUTO'] - df_merged['CUSTO_FIXO']
    df_merged['LUCRATIVIDADE'] = (df_merged['LUCRO_LIQUIDO'] / df_merged['RECEITA']) * 100
    
    print(f'df_merged com calculos shape: {df_merged.shape}')
    print(f'df_merged com calculos:\n{df_merged.head(3)}')
    
    return df_merged

def exibir_indicadores_principais(df_indicadores_filtered):
    """Exibe os indicadores principais."""
    print('exibir_indicadores_principais()')
    # Colunas para exibir indicadores:
    col1,col2,col3,col4 = st.columns(4)
    with col1:
        # Exibe os dados de Receita:
        receita_formatada = locale.format_string("R$ %.2f", df_indicadores_filtered['RECEITA'].sum(), grouping=True)
        st.metric("Receita total:", value=f"{receita_formatada}")
    with col2:
        # Exibe os dados de Lucro Bruto:
        lucro_bruto_formatado = locale.format_string("R$ %.2f", df_indicadores_filtered['LUCRO_BRUTO'].sum(), grouping=True)
        st.metric("Lucro Bruto total:", value=f"{lucro_bruto_formatado}")
    with col3:
         # Exibe os dados de Margem de Lucro:
         margem_lucro_formatada = locale.format_string("%.2f", df_indicadores_filtered['MARGEM_LUCRO'].mean(), grouping=True)
         st.metric("Margem de Lucro total:", value=f"{margem_lucro_formatada}%")
    with col4:
        # Exibe os dados de Lucratividade:
        lucratividade_formatada = locale.format_string("%.2f", df_indicadores_filtered['LUCRATIVIDADE'].mean(), grouping=True)
        st.metric("Lucratividade total:", value=f"{lucratividade_formatada}%")
        
def exibir_graficos(df_indicadores_filtered):
    """Exibe os gráficos do painel."""
    print('exibir_graficos()')
    st.write("---")  # Linha separadora

    col1,col2,col3 = st.columns(3)
    with col1:
       #Gerando o grafico de linha de receita
       print('Gerando o grafico de linha de receita')
       fig_receita = px.line(df_indicadores_filtered, x="MES", y="RECEITA", title="Receita por Mês",
                            labels={'MES': 'Mês', 'RECEITA': 'Receita'}, # Melhora os rótulos dos eixos
                            )
       fig_receita.update_traces(
          hovertemplate="<b>Mês:</b> %{x}<br><b>Receita:</b> R$ %{y:.2f}" # Melhorando o hover
          )
       fig_receita.update_layout(showlegend=True) # adiciona legenda para o gráfico
       st.plotly_chart(fig_receita, use_container_width=True)
    with col2:
       #Gerando o grafico de linha de lucro
       print('Gerando o grafico de linha de lucro')
       fig_lucro = px.line(df_indicadores_filtered, x="MES", y="LUCRO_LIQUIDO", title="Lucro Líquido por Mês",
                            labels={'MES': 'Mês', 'LUCRO_LIQUIDO': 'Lucro Líquido'}, # Melhora os rótulos dos eixos
                            color_discrete_sequence=['darkgreen'] # Define a cor da linha para verde escuro
                            )
       fig_lucro.update_traces(
           hovertemplate="<b>Mês:</b> %{x}<br><b>Lucro Líquido:</b> R$ %{y:.2f}" # Melhorando o hover
           )
       fig_lucro.update_layout(showlegend=True) # adiciona legenda para o gráfico
       st.plotly_chart(fig_lucro, use_container_width=True)
    with col3:
       #Gerando o grafico de barras da lucratividade:
       print('Gerando o grafico de barras da lucratividade')
       fig_lucratividade = px.bar(df_indicadores_filtered, x="MES", y="LUCRATIVIDADE", title="Lucratividade por Mês",
                               text_auto=True,
                               labels={'MES': 'Mês', 'LUCRATIVIDADE': 'Lucratividade'}, # Melhora os rótulos dos eixos
                               color_discrete_sequence=['green'] # Define a cor da barra para verde
                               )
       fig_lucratividade.update_traces(
           marker_color='lightseagreen',
           hovertemplate="<b>Mês:</b> %{x}<br><b>Lucratividade:</b> %{y:.2f}%" # Melhorando o hover
       )
       st.plotly_chart(fig_lucratividade, use_container_width=True)
       st.write("---")  # Linha separadora
    
     
    
def exibir_dataframe_geral(df_indicadores_filtered):
    """Exibe o dataframe geral e o botão de download."""
    print('exibir_dataframe_geral()')
    st.write("---")  # Linha separadora
    
    #Dataframe Geral
    st.subheader("Dataframe Geral:")
    st.dataframe(df_indicadores_filtered,hide_index=True, use_container_width=True)
    
    # Disponibilizar o botão de download
    print('Disponibilizar o botão de download')
    download_xlsx = preparar_download_excel(df_indicadores_filtered)
    st.download_button(
       label="Download em XLSX",
       data=download_xlsx,
       file_name='dados_rentabilidade.xlsx',
       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
   )

# 4. Exibir os Resultados
def main():
    st.title("Painel de Rentabilidade (Dados Fictícios)")
    print("main()")
    
    # Define o locale para português do Brasil
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    # Verifica se o arquivo existe
    print('Verifica se o arquivo existe')
    if not os.path.exists('dados_ficticios_rentabilidade.xlsx'):
        # Cria dados fictícios se o arquivo nao existe
        criar_dados_ficticios()

    # Carrega os dados do XLSX
    print('Carrega os dados do XLSX')
    df_receitas, df_custos_diretos, df_custos_fixos = carregar_dados_xlsx()
    
    if df_receitas.empty or df_custos_diretos.empty or df_custos_fixos.empty:
        st.warning("Não há dados para exibir o painel de rentabilidade!")
        return
        
    # Calcula os indicadores
    print('Calcula os indicadores')
    df_indicadores = calcular_indicadores(df_receitas, df_custos_diretos, df_custos_fixos)
    
    # Obtendo a lista de anos distintos
    print('Obtendo a lista de anos distintos')
    anos_distintos = sorted(df_indicadores['ANO'].unique(), reverse=True)
    
    # Inicializa o ano mais recente
    print('Inicializa o ano mais recente')
    if 'ano_selecionado' not in st.session_state:
        st.session_state['ano_selecionado'] = anos_distintos[0] if anos_distintos else None
    
    with st.sidebar:
       # Inicializa o ano mais recente
       print(f'st.sidebar: Inicializa o ano mais recente')
       if anos_distintos:
           st.session_state['ano_selecionado'] = st.selectbox("Selecione o Ano", anos_distintos)
       else:
           st.warning("Não há dados para exibir os filtros de anos.")
    
    
    # Filtrando o Data Frame pelo ano selecionado
    print('Filtrando o Data Frame pelo ano selecionado')
    if st.session_state['ano_selecionado'] is not None:
        df_indicadores_filtered = df_indicadores[df_indicadores['ANO'] == st.session_state['ano_selecionado']]
    else:
        df_indicadores_filtered = df_indicadores.copy()
    
    print('exibir_indicadores_principais(df_indicadores_filtered)')
    print('exibir_graficos(df_indicadores_filtered)')
    print('exibir_dataframe_geral(df_indicadores_filtered)')
    
    exibir_indicadores_principais(df_indicadores_filtered)
    exibir_graficos(df_indicadores_filtered)
    exibir_dataframe_geral(df_indicadores_filtered)
    

if __name__ == "__main__":
    print('\n\n\__name__ == "__main__"\n')
    main()