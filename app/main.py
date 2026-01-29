from pathlib import Path
import sys

sys.path.append(str(Path(__file__).absolute().parent.parent))


import streamlit as st
from src.utils.backend_streamlit import *
from src.utils.functions import *

st.set_page_config(page_title="Encuest.AR", layout="wide")
st.title("Bienvenido a Encuest.AR ")
principal()
if "datos_i" not in st.session_state or st.session_state["datos_i"] is None:
    st.info("📌 Cargá los datos desde la sección 'Carga de datos'")


st.write("Elegí una sección para comenzar:")

# Crear columnas del mismo tamaño
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)


with col1:
    if st.button("🏠 Inicio"):
        st.switch_page("pages/inicio.py")

with col2:
    if st.button("📥 Carga de datos"):
        st.switch_page("pages/carga_de_datos.py")
# agreguen lo suyo
# - P3 ---------------------
with col3:
    if st.button("👥 Características demográﬁcas"):
        st.switch_page("pages/demograficas.py")

# - P4 ---------------------
with col4:
    if st.button("🏠 viviendas"):
        st.switch_page("pages/viviendas.py")

# - P4 ---------------------
with col5:
    if st.button("🧑‍💼 Empleo"):
        st.switch_page("pages/empleo.py")

# - P6 ---------------------
with col6:
    if st.button("📕 Educacion"):
        st.switch_page("pages/educacion.py")

# --------------------------

with col7:
    if st.button("$ ingresos"):
        st.switch_page("pages/ingresos.py")
