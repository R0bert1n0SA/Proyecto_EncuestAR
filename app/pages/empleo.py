"""
Página de Streamlit que presenta visualizaciones sobre la actividad y empleo en base a datos de la EPH.
Incluye análisis por trimestre y año, condición laboral, nivel educativo, tipo de empleo por aglomerado y evolución en el tiempo.
"""

from pathlib import Path
import sys
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import json

# Agrega rutas necesarias al sistema
sys.path.append(str(Path(__file__).absolute().parent.parent.parent))
from src.utils.constants import DATA_OUT_PATH, DATA_PATH, dic_aglomerados

# Configuración de la página
st.set_page_config(page_title="Empleo", layout="wide")
st.title("🧑‍💼 Actividad y empleo")

# Carga de coordenadas de aglomerados
coordenadas_path = Path(DATA_OUT_PATH) / "aglomerados_coordenadas.json"
with open(coordenadas_path, "r", encoding="utf-8") as f:
    coordenadas_aglomerados = json.load(f)

# Validación de datos cargados
if "datos_i" not in st.session_state or st.session_state["datos_i"] is None:
    st.error(
        "❌ No se encontraron datos de individuos. Volvé a la página de carga de datos."
    )
    st.stop()

datos_i = st.session_state["datos_i"]

# Filtro de año y trimestre
st.subheader("🗓️ Filtrar por año y trimestre")
col1, col2 = st.columns(2)
anios = sorted(datos_i["ANO4"].unique())
trimestres = sorted(datos_i["TRIMESTRE"].unique())
with col1:
    anio = st.selectbox("Año", anios, index=len(anios) - 1)
with col2:
    trimestre = st.selectbox("Trimestre", trimestres, index=len(trimestres) - 1)

filtro = (datos_i["ANO4"] == anio) & (datos_i["TRIMESTRE"] == trimestre)
datos_filtrados = datos_i[filtro]

# Gráfico de condición laboral
st.subheader(f"Distribución de la condición laboral ({trimestre}/{anio})")
if datos_filtrados.empty:
    st.warning("No hay datos disponibles para el año y trimestre seleccionados.")
    st.stop()

conteo = (
    datos_filtrados["CONDICION_LABORAL"].fillna("Sin dato").value_counts().sort_index()
)
df_plot = conteo.reset_index()
df_plot.columns = ["Condición Laboral", "Cantidad"]
fig = px.bar(
    df_plot,
    x="Condición Laboral",
    y="Cantidad",
    text_auto=True,
    title=f"Condición laboral - {trimestre}/{anio}",
    labels={"Cantidad": "Cantidad de personas"},
)
st.plotly_chart(fig, use_container_width=True)
if st.checkbox("Mostrar tabla con cantidades"):
    st.dataframe(df_plot)

# Tabla de personas desocupadas según nivel educativo
st.subheader("📊 Personas desocupadas según nivel educativo")
desocupados = datos_filtrados[datos_filtrados["CONDICION_LABORAL"] == "Desocupado"]
mapa_niveles = {
    "Primario incompleto": "Primario",
    "Primario completo": "Primario",
    "Secundario incompleto": "Secundario",
    "Secundario completo": "Secundario",
    "Superior o universitario": "Universitario",
    "Sin información": "Otro",
}
conteo_ed = (
    desocupados["NIVEL_ED_str"]
    .fillna("Sin información")
    .map(mapa_niveles)
    .value_counts()
    .rename_axis("Nivel educativo")
    .reset_index(name="Cantidad")
)
st.dataframe(conteo_ed)

# Evolución de tasas de empleo y desempleo
st.subheader("📈 Evolución de tasas de empleo y desempleo")
agloms = ["Todos"] + list(dic_aglomerados.values())
agl_elegido = st.selectbox("Filtrar por aglomerado", agloms)

df = datos_i.copy()
if agl_elegido != "Todos":
    cod_aglom = [k for k, v in dic_aglomerados.items() if v == agl_elegido][0]
    df = df[df["AGLOMERADO"] == cod_aglom]

grupo = (
    df.groupby(["ANO4", "TRIMESTRE"])["CONDICION_LABORAL"]
    .value_counts()
    .unstack()
    .fillna(0)
)

ocupados = grupo.get("Ocupado autónomo", 0) + grupo.get("Ocupado dependiente", 0)
desocupados = grupo.get("Desocupado", 0)
total = ocupados + desocupados

if isinstance(desocupados, pd.Series) and isinstance(total, pd.Series):
    grupo["Tasa Desempleo"] = (
        np.divide(
            desocupados.values,
            total.values,
            out=np.zeros_like(desocupados.values, dtype=float),
            where=total.values > 0,
        )
        * 100
    )
    grupo["Tasa Empleo"] = (
        np.divide(
            ocupados.values,
            total.values,
            out=np.zeros_like(ocupados.values, dtype=float),
            where=total.values > 0,
        )
        * 100
    )
else:
    grupo["Tasa Desempleo"] = 0
    grupo["Tasa Empleo"] = 0

grupo = grupo.reset_index()

col1, col2 = st.columns(2)
with col1:
    fig_des = px.line(
        grupo,
        x="ANO4",
        y="Tasa Desempleo",
        color="TRIMESTRE",
        markers=True,
        title="Tasa de Desempleo",
    )
    st.plotly_chart(fig_des, use_container_width=True)
with col2:
    fig_emp = px.line(
        grupo,
        x="ANO4",
        y="Tasa Empleo",
        color="TRIMESTRE",
        markers=True,
        title="Tasa de Empleo",
    )
    st.plotly_chart(fig_emp, use_container_width=True)

# Tipo de empleo por aglomerado
st.subheader("🏢 Tipo de empleo por aglomerado")
ocupados = datos_filtrados[
    datos_filtrados["CONDICION_LABORAL"].str.startswith("Ocupado")
]
if "PP04A" not in ocupados.columns:
    st.warning(
        "No se encontró la columna PP04A (tipo de empleo). Asegurate de incluirla en individual.csv"
    )
else:
    ocupados = ocupados.copy()
    sector_map = {1: "Estatal", 2: "Privado", 3: "Otro"}
    ocupados["Sector"] = ocupados["PP04A"].map(
        lambda x: (
            sector_map.get(int(float(x)), "Sin dato") if pd.notna(x) else "Sin dato"
        )
    )

    tabla_sector = (
        ocupados.groupby(["AGLOMERADO", "Sector"]).size().unstack(fill_value=0)
    )
    tabla_sector["Total"] = tabla_sector.sum(axis=1)
    for sector in ["Estatal", "Privado", "Otro"]:
        if sector in tabla_sector.columns:
            tabla_sector[sector + " %"] = (
                tabla_sector[sector] / tabla_sector["Total"] * 100
            ).round(2)

    st.dataframe(tabla_sector[[c for c in tabla_sector.columns if "%" in c]])

    fig_sector = px.bar(
        tabla_sector.reset_index(),
        x="AGLOMERADO",
        y=[c for c in tabla_sector.columns if "%" in c],
        barmode="stack",
        title="Distribución porcentual de tipo de empleo por aglomerado",
    )
    st.plotly_chart(fig_sector, use_container_width=True)

# Mapa de evolución de empleo/desempleo entre períodos extremos
st.subheader("🗺️ Evolución de empleo/desempleo entre períodos extremos")
tipo_tasa = st.radio("Seleccioná qué tasa comparar", ["Tasa Empleo", "Tasa Desempleo"])
primero = (
    datos_i.groupby(["ANO4", "TRIMESTRE"])
    .size()
    .reset_index()
    .sort_values(["ANO4", "TRIMESTRE"])
    .iloc[0]
)
ultimo = (
    datos_i.groupby(["ANO4", "TRIMESTRE"])
    .size()
    .reset_index()
    .sort_values(["ANO4", "TRIMESTRE"])
    .iloc[-1]
)
df_primero = datos_i[
    (datos_i["ANO4"] == primero["ANO4"])
    & (datos_i["TRIMESTRE"] == primero["TRIMESTRE"])
]
df_ultimo = datos_i[
    (datos_i["ANO4"] == ultimo["ANO4"]) & (datos_i["TRIMESTRE"] == ultimo["TRIMESTRE"])
]


def calcular_tasa(df, tipo="empleo"):
    """
    Calcula la tasa de empleo o desempleo para cada aglomerado en el DataFrame dado.

    Parámetros:
        df (pd.DataFrame): El DataFrame con los datos filtrados por año y trimestre.
        tipo (str): Tipo de tasa a calcular. Puede ser 'empleo' o 'desempleo'.

    Retorna:
        pd.DataFrame: Un DataFrame con columnas ['AGLOMERADO', 'Tasa'] indicando el porcentaje correspondiente.
    """
    resultado = []
    for aglo in df["AGLOMERADO"].unique():
        sub = df[df["AGLOMERADO"] == aglo]
        oc = (sub["CONDICION_LABORAL"].str.startswith("Ocupado")).sum()
        des = (sub["CONDICION_LABORAL"] == "Desocupado").sum()
        if oc + des == 0:
            tasa = 0
        else:
            tasa = (
                (oc / (oc + des) * 100)
                if tipo == "empleo"
                else (des / (oc + des) * 100)
            )
        resultado.append({"AGLOMERADO": aglo, "Tasa": tasa})
    return pd.DataFrame(resultado)


tasa_1 = calcular_tasa(
    df_primero, "empleo" if tipo_tasa == "Tasa Empleo" else "desempleo"
)
tasa_2 = calcular_tasa(
    df_ultimo, "empleo" if tipo_tasa == "Tasa Empleo" else "desempleo"
)
df_diff = pd.merge(tasa_1, tasa_2, on="AGLOMERADO", suffixes=("_ini", "_fin"))
df_diff["color"] = df_diff.apply(
    lambda row: "green" if row["Tasa_fin"] > row["Tasa_ini"] else "red", axis=1
)

# Filtrar aglomerados con coordenadas definidas
df_diff = df_diff[
    df_diff["AGLOMERADO"].astype(str).isin(coordenadas_aglomerados.keys())
]
df_diff["nombre"] = df_diff["AGLOMERADO"].map(dic_aglomerados)
df_diff["lat"] = df_diff["AGLOMERADO"].map(
    lambda x: coordenadas_aglomerados[str(x)]["coordenadas"][0]
)
df_diff["lon"] = df_diff["AGLOMERADO"].map(
    lambda x: coordenadas_aglomerados[str(x)]["coordenadas"][1]
)

fig_map = px.scatter_mapbox(
    df_diff,
    lat="lat",
    lon="lon",
    hover_name="nombre",
    color="color",
    zoom=3,
    height=500,
    color_discrete_map={"green": "green", "red": "red"},
)
fig_map.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig_map, use_container_width=True)
