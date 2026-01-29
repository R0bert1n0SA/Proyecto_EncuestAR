from pathlib import Path
import sys

sys.path.append(str(Path(__file__).absolute().parent.parent.parent))
import streamlit as st
from src.utils.backend_streamlit import *

st.title("Análisis de Ingresos del Hogar")
st.subheader("Punto 1.7 - Línea de Pobreza e Indigencia")

st.markdown(
    """
Este módulo permite visualizar la cantidad y porcentaje de hogares de 4 integrantes 
que se encuentran por debajo de la línea de pobreza e indigencia, 
según la Encuesta Permanente de Hogares (EPH).
"""
)

# --- Selectores de Año y Trimestre ---
col1, col2 = st.columns(2)

with col1:
    anno = st.selectbox("Seleccione un año:", list(range(2023, 2025)))

with col2:
    trimestre = st.selectbox("Seleccione un trimestre:", [1, 2, 3, 4])

st.markdown("---")

# --- Botón para ejecutar el análisis ---
if st.button("Analizar"):
    st.info("🔍 Procesando información... (a implementar)")
    st.subheader("📊 Resultados del análisis")
    resultados = verificar_ingreso(st.session_state.datos_h, anno, trimestre)
    st.dataframe(resultados)

    # Pie chart usando Plotly
    fig = px.pie(
        resultados,
        names="CONDICION",
        values="Cantidad",
        title=f"Distribución de hogares - Año {anno}, Trimestre {trimestre}",
        color_discrete_sequence=px.colors.qualitative.Set3,
    )

    st.plotly_chart(fig)
