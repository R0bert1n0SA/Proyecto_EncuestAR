import streamlit as st

st.set_page_config(page_title="Encuest.AR", layout="wide")

st.title("Bienvenido a Encuest.AR 👋")

st.write("Elegí una sección para comenzar:")

# Crear 4 columnas del mismo tamaño
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏠 Inicio"):
        st.switch_page("pages/1.Inicio.py")

with col2:
    if st.button("📥 Carga de datos"):
        st.switch_page("pages/2.Carga_de_Datos.py")

with col3:
    if st.button("🔍 Búsqueda por tema"):
        st.switch_page("pages/3.Busqueda_por_Tema.py")

with col4:
    if st.button("📊 Visualización"):
        st.switch_page("pages/4.Visualizacion.py")

