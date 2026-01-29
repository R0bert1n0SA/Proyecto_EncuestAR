from pathlib import Path
import sys

sys.path.append(str(Path(__file__).absolute().parent.parent.parent))

import streamlit as st
from src.utils.crearCSV import *
from src.utils.backend_streamlit import *


st.sidebar.header("Carga de Datos")
st.title("Carga de Datos")

# Inicializa las variables si no existen aún
for key in ["fi", "fd", "datos_i", "datos_h"]:
    if key not in st.session_state:
        st.session_state[key] = None


fecha_d = st.session_state.fi
fecha_h = st.session_state.fd

if fecha_d == None or fecha_h == None:
    st.error("Sin Datos")

st.write(
    "El sistema contiene informacion desde el {} hasta el {}".format(fecha_d, fecha_h)
)

# Botón para actualizar
st.button("Actualizar dataset", on_click=principal())

# Verificar consistencias entre hogares e individuos
st.subheader("Verificación de consistencia de archivos")
inconsistencias, msj = verificar_coincidencias()

if not inconsistencias:
    st.warning(msj)
else:
    st.success(msj)
