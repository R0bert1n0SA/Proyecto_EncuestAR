import streamlit as st
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).absolute().parent.parent.parent))
import matplotlib.pyplot as plt
from src.utils.backend_streamlit import *

st.title("Punto 1, Parte 6 - Educacion")

st.subheader("Parte 6.1 - Cantidad de personas según el máximo nivel educativo.")

# se le provee al ususario un selector para elegir el año a visualizar
num = st.number_input(
    label="Seleccionar año (Entre 2016 a 2024)", min_value=2016, max_value=2024
)
# se crea el dataframe con al cantidad de persons por nivel educativo para el año seleccionado
data_for_graph_1 = cant_per_nivel(st.session_state.datos_i, num)
# se revisa que el dataframe no este vacio.
if not data_for_graph_1.empty:
    # se empeiza a crear el grafico de torta con matplotlib
    fig_1, ax1 = plt.subplots()
    ax1.bar(data_for_graph_1["Niveles"], data_for_graph_1["Cantidad"])
    ax1.set_title("Niveles alcanzados en el año " + str(num))
    ax1.tick_params(axis="x", labelrotation=45, labelsize=8)
    ax1.axis("tight")
    fig_1.tight_layout()
    st.pyplot(fig_1)
else:
    st.info("No hay datos disponibles para el año seleccionado.")
st.subheader("Parte 6.2 - nivel educacional alcanzado más común")

niv_educativos = [
    "Jardín/preescolar",
    "Primario",
    "EGB",
    "Secundario",
    "Polimodal",
    "Terciario",
    "Universitario",
    "Posgrado universitario",
    "Educación especial (discapacidad)",
]
options = st.multiselect(
    "Seleccione que rangos de edad desea visualizar.",
    [
        "Entre 20 a 30 años",
        "Entre 30 a 40 años",
        "Entre 40 a 50 años",
        "Entre 50 a 60 años",
        "Mayores de 60 años",
    ],
    default=["Entre 20 a 30 años"],
)
data_for_graph_2 = niv_mas_comun(st.session_state.datos_i, options)
fig_2, ax2 = plt.subplots()
ax2.stem(
    data_for_graph_2["Rango de edad"],
    data_for_graph_2["Nivel educativo más común"],
)
ax2.set_title("Nivel educativo más común por rango de edad")
ax2.set_xlabel("Rango de edad")
ax2.set_ylabel("Nivel educativo")
ax2.set_xticklabels(data_for_graph_2["Rango de edad"], rotation=45, ha="right")
ax2.set_yticklabels(niv_educativos, rotation=45, ha="right")
ax2.set_yticks(range(1, 10))
st.pyplot(fig_2)

st.subheader(
    "Parte 6.3 - Visualizacion y exportacion del inciso 4 de la sección B del TI parte 1"
)

st.download_button(
    label="Descargar CSV",
    data=csv_inc_4(),
    file_name="top5_aglomerados_con_2_o_mas_universitarios.csv",
    icon="📝",
)

st.subheader(
    "Parte 6.4 - Porcentaje de personas mayores a 6 años capaces e incapaces de leer y escribir, anualmente"
)

data_for_graph_3 = lit_may_6(st.session_state.datos_i)
x_label_3 = data_for_graph_3["Año"].astype(str)
# Creamos el primer grafico, para la iliteracidad
(
    fig_3,
    ax3,
) = plt.subplots()
ax3.bar(
    x_label_3,
    data_for_graph_3["Porcentaje de iliteracidad"],
)
ax3.set_title(
    "Porcentaje de personas mayores a 6 años incapaces de leer y escribir, anualmente"
)
ax3.set_xlabel("Año")
ax3.set_ylabel("Porcentaje")
ax3.set_ylim(0, 100)
for i, valor in enumerate(data_for_graph_3["Porcentaje de iliteracidad"]):
    # Agregamos los valores encima de las barras
    ax3.text(i, valor + 0.5, f"{valor:.2f}%", ha="center", va="bottom")
# Creamos el segundo grafico, para la literacidad
(
    fig_4,
    ax4,
) = plt.subplots()
ax4.bar(
    x_label_3,
    data_for_graph_3["Porcentaje de literacidad"],
)
ax4.set_title(
    "Porcentaje de personas mayores a 6 años capaces de leer y escribir, anualmente"
)
ax4.set_xlabel("Año")
ax4.set_ylabel("Porcentaje")
ax4.set_ylim(0, 100)
for i, valor in enumerate(data_for_graph_3["Porcentaje de literacidad"]):
    # Agregamos los valores encima de las barras
    ax4.text(i, valor + 0.5, f"{valor:.2f}%", ha="center", va="bottom")

st.pyplot(fig_3)
st.pyplot(fig_4)
