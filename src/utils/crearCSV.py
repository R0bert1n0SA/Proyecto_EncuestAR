import os
from src.utils.constants import DATA_PATH, DATA_OUT_PATH
import pandas as pd
import streamlit as st


def planilla_boton():
    planilla("hogar")
    planilla("individual")

    indiv = pd.read_csv(DATA_OUT_PATH / "individual.csv", delimiter=";")
    hogar = pd.read_csv(DATA_OUT_PATH / "hogares.csv", delimiter=";")

    # Guardar en session_state
    st.session_state["datos_i"] = indiv
    st.session_state["datos_h"] = hogar

    # Guardar fechas mínimas y máximas
    try:
        anios = indiv["ANO4"]
        trimestres = indiv["TRIMESTRE"]
        st.session_state["fi"] = f"{trimestres.min()}/{anios.min()}"
        st.session_state["fd"] = f"{trimestres.max()}/{anios.max()}"
    except Exception:
        st.session_state["fi"] = None
        st.session_state["fd"] = None


def planilla(nombre):
    if "hogar" in nombre:
        archivo_salida = DATA_OUT_PATH / "hogares.csv"

    else:
        archivo_salida = DATA_OUT_PATH / "individual.csv"

    encabezado = False

    with archivo_salida.open("w") as salida:
        for trimestre in DATA_PATH.iterdir():  # .glob('EPH_usu_1_Trim*'):

            for sub_carpeta in trimestre.iterdir():
                for archivo in sub_carpeta.glob(nombre + "*"):
                    # print(f'procesando: {archivo.name}')
                    # procesa el archivo, lo imprime y lo CIERRA. tmb captura si hay un error
                    with archivo.open() as f:
                        header = f.readline()
                        if not encabezado:
                            salida.write(header)
                            encabezado = True
                        for line in f:
                            salida.write(line)
    return
