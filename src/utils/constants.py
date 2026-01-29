import streamlit as st
from pathlib import Path
from pathlib import Path

PROJECT_PATH = Path(__file__).parent.parent.parent
DATA_PATH = PROJECT_PATH / "data_eph"
DATA_OUT_PATH = PROJECT_PATH / "data_out"


# actualiza la session state cada vez que re refresca el streamlit
def init_session_state():
    keys = {"datos_h": None, "datos_i": None, "fi": None, "fd": None}
    for k, v in keys.items():
        if k not in st.session_state:
            st.session_state[k] = v


dic_aglomerados = {
    "02": "Gran La Plata",
    "03": "Bahía Blanca-Cerri",
    "04": "Gran Rosario",
    "05": "Gran Santa Fe",
    "06": "Gran Paraná",
    "07": "Posadas",
    "08": "Gran Resistencia",
    "09": "Comodoro Rivadavia-Rada Tilly",
    "10": "Gran Mendoza",
    "12": "Corrientes",
    "13": "Gran Córdoba",
    "14": "Concordia",
    "15": "Formosa",
    "17": "Neuquén-Plottier",
    "18": "Santiago del Estero-La Banda",
    "19": "Jujuy-Palpalá",
    "20": "Río Gallegos",
    "22": "Gran Catamarca",
    "23": "Gran Salta",
    "25": "La Rioja",
    "26": "Gran San Luis",
    "27": "Gran San Juan",
    "29": "Gran Tucumán-Tafí Viejo",
    "30": "Santa Rosa-Toay",
    "31": "Ushuaia-Río Grande",
    "32": "Ciudad Autónoma de Buenos Aires",
    "33": "Partidos del Gran Buenos Aires",
    "34": "Mar del Plata",
    "36": "Río Cuarto",
    "38": "San Nicolás-Villa Constitución",
    "91": "Rawson-Trelew",
    "93": "Viedma-Carmen de Patagones",
}

tipos_dict = {
    1: "Propietario vivienda y terreno",
    2: "Propietario solo vivienda",
    3: "Inquilino",
    4: "Pago expensas/impuestos",
    5: "Relación de dependencia",
    6: "Gratuito (con permiso)",
    7: "Ocupante de hecho",
    8: "En sucesión",
}
