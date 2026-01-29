import streamlit as st
from src.utils.backend_streamlit import *
from pathlib import Path
from src.utils.constants import *
import sys

sys.path.append(str(Path(__file__).absolute().parent.parent.parent))


st.title("Análisis de las características de las viviendas")
st.subheader("Punto 1.4 - Características de la vivienda")

st.markdown(
    """
En esta sección se visualizará información relacionada a las características de las viviendas
de la población argentina según la Encuesta Permanente de Hogares (EPH). 
Todas las visualizaciones se basan en un único valor de año ingresado por el usuario en
esta sección.
"""
)

# --- Selector de Año  ---
col1 = st.columns(1)
anios = list(range(2023, 2025))
anios.append("Todos")

anno = st.selectbox("Seleccione un año:", anios)


st.markdown("---")

# --- Botón para ejecutar el análisis ---
if st.button("Analizar"):
    st.info("🔍 Procesando información... ")
    if anno == "Todos":
        anno = 100
    else:
        int(anno)
    filtrados = filtrar_anio_trimestre(st.session_state.datos_h, selec=anno)
    procesar_datos__1_4_1(filtrados)
    procesar_datos__1_4_2(filtrados)
    procesar_datos__1_4_3(filtrados)
    procesar_datos__1_4_4(filtrados)
    procesar_datos__1_4_6(filtrados)
    procesar_datos__1_4_7(filtrados)

st.subheader("1.4.5 Evolución del régimen de tenencia")
# ---- ELECCIÓN DE AGLOMERADO------
opciones_aglomerado = ["Seleccione un aglomerado"] + list(dic_aglomerados.keys())
aglo_sel = st.selectbox(
    "Seleccione aglomerado",
    options=opciones_aglomerado,
    format_func=lambda x: (
        dic_aglomerados.get(x, x) if x != "Seleccione un aglomerado" else x
    ),
)

seleccion = st.multiselect(
    "Seleccione tipo(s) de tenencia",
    options=list(tipos_dict.keys()),
    placeholder="Elegí uno o más tipos...",
)

hogar_temp = st.session_state.datos_h

if st.button("Analizar Aglomerado"):
    evolucion = procesar_datos__1_4_5(anno, aglo_sel, seleccion, hogar_temp)
    st.bar_chart(evolucion.T)  # Transponer para que II7 estén en eje X
