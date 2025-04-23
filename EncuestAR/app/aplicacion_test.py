import streamlit as st  

# Título de la app
st.title("Mi Primer Interfaz en Streamlit")

# Subtítulo o descripción
st.subheader("Esto es solo la interfaz, todavía no hace nada 😄")

# Campos de entrada
st.text_input("Tu nombre")
st.number_input("Edad", min_value=0, max_value=120)
st.date_input("Fecha de nacimiento")
st.selectbox("Género", ["Seleccionar", "Masculino", "Femenino"])

# Checkbox y slider
st.checkbox("Acepto los términos y condiciones")
st.slider("Nivel de satisfacción", 0, 10)

# Botón
st.button("Enviar")