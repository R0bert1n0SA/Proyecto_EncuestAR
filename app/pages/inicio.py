import streamlit as st


st.title("Encuest.AR")
st.divider()
st.write("""Esta aplicación te permite...""")
st.divider()
st.page_link("pages/carga_de_datos.py", label="Ir a carga de datos", icon="📥")

st.page_link("pages/demograficas.py", label="Ir a Demograficas", icon="👥")


st.page_link("pages/viviendas.py", label="Ir a viviendas", icon="🏠")


st.page_link("pages/ingresos.py", label="Ir a Ingresos", icon="💲")

st.divider()
st.write("Por favor, calificá nuestro trabajo :D")
st.feedback("stars")
