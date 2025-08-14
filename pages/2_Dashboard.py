import streamlit as st
import sys
import os
from datetime import datetime

# Adiciona o diretório raiz do projeto ao sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.ui_components import get_image_download_link

st.markdown("<h1 class='main-header'>Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<div class='info-box'>Visualize e organize seus gráficos em um dashboard personalizado.</div>", unsafe_allow_html=True)

# Verificar se existem gráficos no dashboard
if not st.session_state.get("dashboard_charts", []):
    st.warning("Nenhum gráfico adicionado ao dashboard ainda. Use o Assistente de BI para gerar gráficos e adicioná-los aqui.")
else:
    # Opções de organização
    col1, col2 = st.columns(2)
    with col1:
        layout = st.radio("Layout", ["1 coluna", "2 colunas", "3 colunas"])
    with col2:
        sort_by = st.selectbox("Ordenar por", ["Mais recentes", "Mais antigos", "Tipo de gráfico"])

    # Ordenar gráficos
    charts = st.session_state.dashboard_charts.copy()
    if sort_by == "Mais recentes":
        charts = sorted(charts, key=lambda x: x["timestamp"], reverse=True)
    elif sort_by == "Mais antigos":
        charts = sorted(charts, key=lambda x: x["timestamp"])
    elif sort_by == "Tipo de gráfico":
        charts = sorted(charts, key=lambda x: x["type"])

    # Determinar número de colunas
    if layout == "1 coluna":
        num_cols = 1
    elif layout == "2 colunas":
        num_cols = 2
    else:
        num_cols = 3

    # Criar layout de colunas
    cols = st.columns(num_cols)

    # Exibir gráficos no dashboard
    for i, chart_info in enumerate(charts):
        with cols[i % num_cols]:
            with st.container():
                st.markdown(f"<div class='sub-header'>{chart_info['title']}</div>", unsafe_allow_html=True)
                st.plotly_chart(chart_info["fig"], use_container_width=True)

                # Opções para cada gráfico
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Exportar como PNG", key=f"export_png_{i}"):
                        st.markdown(get_image_download_link(chart_info["fig"], f"grafico_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}", "📥 Clique aqui para baixar como PNG"), unsafe_allow_html=True)
                with col2:
                    if st.button("Remover do Dashboard", key=f"remove_{i}"):
                        st.session_state.dashboard_charts.remove(chart_info)
                        st.rerun()

                # Mostrar a consulta que gerou o gráfico
                st.caption(f"Consulta: {chart_info['query']}")

    # Opção para limpar todo o dashboard
    if st.button("Limpar Dashboard"):
        st.session_state.dashboard_charts = []
        st.rerun()
