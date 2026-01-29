import streamlit as st
from src.utils.backend_streamlit import *
from pathlib import Path
import sys
import json

import numpy as np

print(Path(__file__).absolute().parent.parent.parent)
sys.path.append(str(Path(__file__).absolute().parent.parent.parent))

st.title("Caracteristícas Demograficas 𓀖")
st.subheader("Punto 1.3 - Distribución de la población por grupos de edad y sexo. 𓀀")

st.write("Ingrese un año y trimestre entre: ")
st.write(st.session_state.fi, st.session_state.fd)

ano_inicio = int(st.session_state.fi.split("/")[1])
ano_fin = int(st.session_state.fd.split("/")[1])

ano = st.number_input(
    "Ingresa el año", min_value=ano_inicio, max_value=ano_fin, value=ano_inicio, step=1
)
trimestre = st.selectbox("Selecciona el trimestre", options=[1, 2, 3, 4])

if st.button("Confirmar Periodo"):
    dataF1 = poblacion_por_edad_sexo(st.session_state.datos_i, 2023, trimestre)
    if dataF1 is None:
        st.warning("No hay datos disponibles para ese periodo de tiempo.")
    else:
        st.bar_chart(data=dataF1, use_container_width=True, stack=False)

st.subheader(
    "1.3.2 Ver edad promedio de personas por aglomerado  para el último trimestre y año del cual se cuenta con informacion. 𓀋"
)

if st.button("Desplegar Información "):
    dataF2 = promedio_edad_aglomerado(st.session_state.datos_i)
    if dataF2 is None:
        st.warning("No hay datos disponibles.")
    else:
        dataF2.index.name = "Aglomerado"  # mayusculas
        st.table(dataF2)


st.subheader("1.3.3 Evolución de la dependencia demográﬁca por año y trimestre. 𓀚")

with open("data_out/aglomerados_coordenadas.json", "r", encoding="utf-8") as f:
    aglomerados = json.load(f)

opciones = [(v["nombre"], k) for k, v in aglomerados.items()]

aglomerados_nombres = [
    nombre for nombre, codigo in opciones
]  # obtenemos los nombres pa mostrarlos

seleccion = st.selectbox("Seleccione un aglomerado", aglomerados_nombres)

for nombre, codigo in opciones:  # buscamos el codigo seleccionado
    if nombre == seleccion:
        st.session_state.aglomerado_seleccionado = (
            codigo  # lo guardamos en la sesion actual
        )
        break

if st.button("Confirmar Aglomerado"):

    dataF3 = dependencia_demograﬁca(
        st.session_state.datos_i, st.session_state.aglomerado_seleccionado
    )
    if dataF3 is None:
        st.warning("No hay datos disponibles.")
    else:
        # transformamos el diccionario en dataframe con el formato requerido
        df = dataF3.rename(columns={"ANO4": "Año", "TRIMESTRE": "Trimestre"})
        df = df.sort_values(["Año", "Trimestre"])  # ordenada

        df["Periodo"] = (
            df["Año"].astype(str) + " Trim " + df["Trimestre"].astype(str)
        )  # juntamos el año y trimestre pa q queden juntitos al desplegarlo en el eje x como periodo
        st.line_chart(df, x="Periodo", y="Porcentaje", color="#800080")


st.subheader(
    "1.3.4 Informar para cada año y trimestre almacenado la media y mediana de la edad de la población. 𓀒"
)

if st.button("Desplegar Informacion"):
    st.write("Media y mediana de edad por año y trimestre:")

    dataF4 = get_media_mediana_opti(st.session_state.datos_i)
    if dataF4 is None:
        st.warning("No hay datos disponibles.")
    else:
        st.dataframe(dataF4)
