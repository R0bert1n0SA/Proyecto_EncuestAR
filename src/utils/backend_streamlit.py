import plotly.express as px

# from vega_datasets import data
from pathlib import Path
import os

if __name__ == "__main__":
    from constants import *
    from crearCSV import *
else:
    from src.utils.constants import *
    from src.utils.crearCSV import *


import pandas as pd
import json
import warnings
import streamlit as st
from collections import defaultdict
import time

# Funciones Generales


def valido_error(path_hogares, path_individuos):
    """
    Funcion que intenta cargar los archivos CSV de hogares e individuos
    con las primeras tres columnas,
    manejando errores comunes de carga como archivo no encontrado o archivo vacío.

    Parámetros:
        path_hogares (Path o str): Ruta al archivo CSV de datos de hogares.
        path_individuos (Path o str): Ruta al archivo CSV de datos de individuos.

    Retorna:
        tuple: (hogares_datos, individual_datos)
            hogares_datos (DataFrame o None): DataFrame con los datos de hogares
            si la carga fue exitosa, None si hubo error.
            individual_datos (DataFrame o None): DataFrame con los datos de individuos
            si la carga fue exitosa, None si hubo error.
    """

    # variables para debbuging
    er_bug_d = ""
    er_bug_i = ""
    # -------------------------
    try:
        hogares_datos = pd.read_csv(path_hogares, sep=";", on_bad_lines="skip")
    except FileNotFoundError:
        er_bug_d = f"Error: no se encontró el archivo {path_hogares}"
        hogares_datos = None
    except pd.errors.EmptyDataError:
        er_bug_d = f"Error: el archivo {path_hogares} está vacío"
        hogares_datos = None
    try:
        individual_datos = pd.read_csv(path_individuos, sep=";", on_bad_lines="skip")
    except FileNotFoundError:
        er_bug_i = f"Error: no se encontró el archivo {path_individuos}"
        individual_datos = None
    except pd.errors.EmptyDataError:
        er_bug_i = f"Error: el archivo {path_individuos} está vacío"
        individual_datos = None

    # print(er_bug_d)
    # print(er_bug_i)

    return hogares_datos, individual_datos


def obtener_trimestres_desde_csv(individual):
    """
    Extrae el primer y último trimestre disponibles en un DataFrame individual.

    La función elimina duplicados del DataFrame recibido, lo ordena por año (`ANO4`)
    y trimestre (`TRIMESTRE`), y devuelve el primer y último período disponibles
    en formato "TRIMESTRE/AÑO".

    Parameters
    ----------
    individual : pandas.DataFrame
        DataFrame que contiene al menos las columnas 'ANO4' y 'TRIMESTRE'.

    Returns
    -------
    tuple of str
        Una tupla con dos cadenas: el primer trimestre disponible y el último,
        ambos en formato "TRIMESTRE/AÑO".
    """
    # Eliminar duplicados y ordenar por año y trimestre
    df_unique = individual.drop_duplicates().sort_values(["ANO4", "TRIMESTRE"])
    # Obtener el primer y último trimestre
    primer_trimestre = df_unique.iloc[0]
    ultimo_trimestre = df_unique.iloc[-1]
    return (
        f"{primer_trimestre['TRIMESTRE']}/{primer_trimestre['ANO4']}",
        f"{ultimo_trimestre['TRIMESTRE']}/{ultimo_trimestre['ANO4']}",
    )


def planilla(nombre):
    """
    Carga y concatena archivos de datos del hogar o individuales según el nombre dado.

    Dependiendo del valor del parámetro `nombre`, busca y carga todos los archivos
    correspondientes a hogares ("usu_hogar_*.txt") o a individuos ("usu_individual_*.txt")
    desde el directorio especificado por `DATA_PATH`. Los archivos encontrados se leen
    como DataFrames de pandas, ignorando advertencias por tipo de dato. Luego, los
    DataFrames se concatenan en uno solo.

    Parameters
    ----------
    nombre : str
        Cadena que indica el tipo de archivo a procesar. Si contiene 'hogar',
        se buscarán archivos de hogares; en otro caso, se buscarán archivos de individuos.

    Returns
    -------
    pandas.DataFrame or None
        Un DataFrame con todos los datos concatenados si se encontraron archivos;
        `None` en caso contrario.
    """
    print("arranco")
    salida = ""

    if "hogar" in nombre:
        archivos = list(Path(DATA_PATH).rglob("usu_hogar_*.txt"))
        salida = DATA_OUT_PATH / "hogares.csv"
    else:
        archivos = list(Path(DATA_PATH).rglob("usu_individual_*.txt"))
        salida = DATA_OUT_PATH / "individual.csv"

    if not archivos:
        print(f"No se encontraron archivos para {nombre}")
        return None

    # Unir todos los archivos en un solo DataFrame
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=pd.errors.DtypeWarning)
        df = pd.concat(
            [
                pd.read_csv(
                    f,
                    sep=";",
                    encoding="latin1",
                    skip_blank_lines=True,
                    on_bad_lines="skip",
                )
                for f in archivos
            ],
            ignore_index=True,
        )

    print("fin")
    return df


def traducir_genero(datos, salida):
    """A través del análisis de la columna CH04,
    clasifica en 'Masculino' y 'Femenino'.
    SALIDA: nueva columna llamada CH04_str
    """
    datos["CH04_str"] = (
        datos["CH04"]
        .astype(str)
        .apply(
            lambda x: (
                "Masculino"
                if x == "1"
                else "Femenino" if x == "2" else "Sin información"
            )
        )
    )
    print("fin genero")
    return datos


def traducir_nivel_ed(datos, salida):
    """Traduce los valores numéricos de la columna NIVEL_ED a
    formato texto.
    SALIDA: Salida: nueva columna llamada NIVEL_ED_str
    """
    datos["NIVEL_ED_str"] = (
        datos["NIVEL_ED"]
        .astype(str)
        .apply(
            lambda x: (
                "Primario incompleto"
                if x == "1"
                else (
                    "Primario completo"
                    if x == "2"
                    else (
                        "Secundario incompleto"
                        if x == "3"
                        else (
                            "Secundario completo"
                            if x == "4"
                            else (
                                "Superior o universitario"
                                if x in ["5", "6"]
                                else "Sin información"
                            )
                        )
                    )
                )
            )
        )
    )
    print("fin nivel")
    return datos


def condicion_laboral(datos, salida):
    """Clasifica el estado laboral del individuo según el valor numérico
    de clasificacion en el archivo individuos.
    SALIDA: columna denominada CONDICION_LABORAL
    """
    print("inicio laboral")
    datos["CONDICION_LABORAL"] = datos.apply(
        lambda row: (
            "Ocupado autónomo"
            if str(row["ESTADO"]) == "1" and str(row["CAT_OCUP"]) in ["1", "2"]
            else (
                "Ocupado dependiente"
                if str(row["ESTADO"]) == "1" and str(row["CAT_OCUP"]) in ["3", "4", "9"]
                else (
                    "Desocupado"
                    if str(row["ESTADO"]) == "2"
                    else (
                        "Inactivo"
                        if str(row["ESTADO"]) == "3"
                        else "Fuera de categoría/sin información"
                    )
                )
            )
        ),
        axis=1,
    )
    print("fin laboral")
    return datos


def material_techumbre(datos, salida):
    """Genera una columna que clasifica el tipo de hogar basado
    en la columna 'V4' (tipo de material)
    Salida: nueva columna MATERIAL_TECHUMBRE
    """
    datos["MATERIAL_TECHUMBRE"] = (
        datos["V4"]
        .astype(str)
        .apply(
            lambda x: (
                "Material durable"
                if x in "1234"
                else "Material precario" if x in "567" else "No aplica"
            )
        )
    )
    return datos


def tipo_hogar(datos, salida):
    """Genera una nueva columna (TIPO_HOGAR) que clasifica el hogar
    según la cantidad de personas:
    -"Unipersonal" (una persona).
    -"Nuclear" (2 a 4 personas).
    -"Extendido" (5 o más personas).
    Salida: nueva columna TIPO_HOGAR
    """
    datos["TIPO_HOGAR"] = (
        datos["IX_TOT"]
        .astype(str)
        .apply(
            lambda x: (
                "Unipersonal"
                if x == "1"
                else "Nuclear" if x in ["2", "3", "4"] else "Extendido"
            )
        )
    )
    return datos


def Columna_Universitario(datos, salida):
    """Método que indica si una persona mayor de edad
    ha completado, como mínimo, el Nivel Universitario.
    Salida: nueva columna llamada UNIVERSITARIO
    """
    print("inicio uni")
    datos["UNIVERSITARIO"] = datos.apply(
        lambda fila: (
            "2"
            if str(fila["CH04"]).isdigit()
            or str(fila["NIVEL_ED"]).isdigit()
            or int(fila["CH04"]) < 18
            else "1" if int(fila["NIVEL_ED"]) >= 6 else "0"
        ),
        axis=1,
    )
    print("fin uni")
    return datos


def calcular_densidad_hogar(datos, salida):
    """Clasifica la densidad de hogar según la cantidad de personas
    por habitación.
    Salida: nueva columna llamada DENSIDAD_HOGAR
    """
    densidad = []
    for hab, per in zip(datos["IV2"], datos["IX_TOT"]):
        try:
            hab = int(hab)
            per = int(per)
            ratio = per / hab if hab > 0 else per
            if ratio < 1:
                densidad.append("Bajo")
            elif ratio <= 2:
                densidad.append("Medio")
            else:
                densidad.append("Alto")
        except:
            densidad.append("N/D")
    datos["DENSIDAD_HOGAR"] = densidad
    return datos


def condicion_de_habitalidad(datos, salida):
    """Clasifica las viviendas según varias condiciones,
    como la accesibilidad al agua, la forma de extracción de la misma.
    Si poseen baño y dónde está ubicado; los materiales de la casa.
    Salida: nueva columna llamada CONDICION DE HABITALIDAD
    """

    criterios = [
        "Clasifican como CONDICION_DE_HABITABILIDAD buena si los pisos están hechos de mosaico o baldosa o madera o cerámica o alfombra, y el material de techumbre es un material durable; si tiene acceso al agua por cañerías dentro de la vivienda y la misma proviene de red pública; si efectivamente tiene baño y el mismo está ubicado dentro de la vivienda, y posee botón/mochila/cadena y arrastre de agua. Para clasificar, el desagüe del baño debe ser de red pública.",
        "Clasifican como CONDICION_DE_HABITABILIDAD saludable si los pisos interiores son de cemento o ladrillo fijo, y el material de techumbre es durable; si posee agua dentro de la vivienda y proviene de perforación con bomba a motor. Si posee baño dentro de la vivienda con arrastre de agua sin botón/cadena, o con un desagüe a cámara séptica y pozo ciego.",
        "Clasifican como CONDICION_DE_HABITABILIDAD regular si los pisos interiores están hechos de ladrillo suelto o tierra, o si el material de techumbre es un material precario; También clasifica si posee agua dentro del terreno pero fuera de la vivienda; si posee baño dentro del terreno pero fuera de la vivienda, y el mismo es por letrina, o el desagüe es a pozo ciego.",
        "Clasifican como CONDICION_DE_HABITABILIDAD insuficiente si los pisos interiores están hechos de ladrillo suelto o tierra, y el material de techumbre es un material precario; si no posee agua dentro del terreno, o su extracción es a través de la perforación con bomba manual / otra fuente. Si no posee baño, o el mismo está fuera del terreno, o el desagüe del baño es a hoyo/excavación en la tierra.",
    ]

    # opt = int(input('Ingrese 1 para ver los criterios de clasificación. Por favor, ingrese un número: '))
    # if opt == 1:
    #    for elem in criterios:
    #        print(elem)

    valores = []

    for _, fila in datos.iterrows():
        mt = fila["MATERIAL_TECHUMBRE"]
        iv3 = str(fila["IV3"])
        iv6 = str(fila["IV6"])
        iv7 = str(fila["IV7"])
        iv8 = str(fila["IV8"])
        iv9 = str(fila["IV9"])
        iv10 = str(fila["IV10"])
        iv11 = str(fila["IV11"])

        if mt == "Material durable" and all(
            x == "1" for x in [iv3, iv6, iv7, iv8, iv9, iv10, iv11]
        ):
            valores.append("buena")
        elif (
            mt == "Material durable"
            and any(x == "2" for x in [iv3, iv7, iv10, iv11])
            and all(x == "1" for x in [iv6, iv8, iv9])
        ):
            valores.append("saludable")
        elif (
            mt == "Material precario"
            and iv8 == "1"
            and any(x == "3" for x in [iv3, iv10, iv11])
            and any(x == "2" for x in [iv6, iv9])
        ):
            valores.append("regular")
        else:
            valores.append("insuficiente")
    print("fin habitabilidad")
    datos["CONDICION DE HABITALIDAD"] = valores
    return datos


# ------------P2 Carga de datos By Spinelli Arcuri Robertino


def comparar(datos_h, datos_i):
    """
    Compara los trimestres disponibles en los datasets de hogares e individuos.

    La función extrae los pares únicos de año y trimestre de ambos DataFrames,
    y verifica si hay coincidencias exactas entre ellos. Si hay trimestres presentes
    en un dataset y no en el otro, se considera que hay inconsistencias.

    Parameters
    ----------
    datos_h : pandas.DataFrame
        DataFrame que contiene datos de hogares, con las columnas 'ANO4' y 'TRIMESTRE'.

    datos_i : pandas.DataFrame
        DataFrame que contiene datos de individuos, con las columnas 'ANO4' y 'TRIMESTRE'.

    Returns
    -------
    tuple
        Una tupla con dos elementos:
        - bool: True si no se encontraron inconsistencias, False en caso contrario.
        - str: Mensaje descriptivo del resultado del chequeo.
    """

    error = ""
    # Crear dataframe de trimestres únicos
    trimestres_h = datos_h[["ANO4", "TRIMESTRE"]].drop_duplicates()
    trimestres_i = datos_i[["ANO4", "TRIMESTRE"]].drop_duplicates()
    # Unir por año y trimestre
    comparacion = trimestres_h.merge(trimestres_i, how="outer", indicator=True)

    # Filtrar los que están solo en uno de los dos
    faltantes_h_en_i = comparacion[comparacion["_merge"] == "left_only"]
    faltantes_i_en_h = comparacion[comparacion["_merge"] == "right_only"]
    if faltantes_h_en_i.empty and faltantes_i_en_h.empty:
        error = "¡Chequeo exitoso! No se encontraron inconsistencias entre archivos de hogares e individuos."
        return True, error
    else:
        error = "Se encontraron inconsistencias"
        return False, error


def verificar_coincidencias():
    """
    Verifica la consistencia de los trimestres entre los datasets de hogares e individuos desde el estado de sesión.

    Recupera los DataFrames `datos_h` y `datos_i` almacenados en `st.session_state`, y los compara usando la función `comparar`.
    Si ambos datasets están presentes, devuelve el resultado de la comparación. Si alguno falta, devuelve un error.

    Returns
    -------
    tuple
        Una tupla con dos elementos:
        - bool: True si los trimestres coinciden entre ambos datasets, False en caso contrario o si faltan datos.
        - str: Mensaje descriptivo del resultado o del error.
    """
    datos_h = st.session_state.get("datos_h")
    datos_i = st.session_state.get("datos_i")
    if datos_h is not None and datos_i is not None:
        iguales, error = comparar(datos_h, datos_i)
        return iguales, error
    else:
        error = "Error al comparar datos"
        return False, error


# ------------P3


def filtro_Ano_Trimestre(ano, trimestre, datos):
    filtro = (datos["ANO4"] == ano) & (datos["TRIMESTRE"] == trimestre)
    return filtro  # retorna mascara


def poblacion_por_edad_sexo(datos, ano, trimestre):
    # datos = datos_i
    if ano not in datos["ANO4"].values:
        return None

    filtro = filtro_Ano_Trimestre(ano, trimestre, datos)
    # filtrado = datos.loc[filtro, ['CH06', 'PONDERA','CH04']]

    filtrado = datos[
        filtro
    ].copy()  # aplicamos la mascara, copy pa no modificar el rial

    filtrado = filtrado[filtrado["CH06"] >= 0]  # edades negativas

    # columna con rango de edad 10 en 10
    filtrado["RANGO_EDAD"] = (filtrado["CH06"] // 10) * 10
    filtrado["RANGO_EDAD"] = filtrado["RANGO_EDAD"].astype(int)

    filtrado["SEXO"] = filtrado["CH04"].map({1: "M", 2: "F"})  # mapeo sexos

    tabla_anos = (
        filtrado.groupby(["RANGO_EDAD", "SEXO"])["PONDERA"].sum().unstack(fill_value=0)
    )

    tabla_anos.index = [str(i) + "-" + str(i + 9) for i in tabla_anos.index]

    return tabla_anos


def promedio_edad_aglomerado(datos):
    max_ano = datos["ANO4"].max()
    aux = datos[
        datos["ANO4"] == max_ano
    ]  # se aplica la mascara de booleanos datos.ANO4==max_ano al dataframe
    max_trim = aux["TRIMESTRE"].max()

    filtro = filtro_Ano_Trimestre(
        max_ano, max_trim, datos
    )  # busco en el mayor año y en el mayor trimestre q este posee
    filtrado = datos[filtro].copy()

    if (
        filtrado.empty
    ):  # si el trimestre del año, y/o el aglomerado no cuenta con datos Ej: el ultimo año triemstre no cuenta con datos del ultimo trimestre
        # print("No hay datos disponibles después del filtro.")
        return None

    with open("data_out/aglomerados_coordenadas.json", "r", encoding="utf-8") as f:
        aglomerados_info = json.load(f)

    filtrado = filtrado[filtrado["CH06"] >= 0]

    filtrado["EDAD_PONDERADA"] = (
        filtrado["CH06"] * filtrado["PONDERA"]
    )  # guardamos en una nueva columna la edad con su pondera
    agrupado = (
        filtrado.groupby("AGLOMERADO")
        .agg({"EDAD_PONDERADA": "sum", "PONDERA": "sum"})
        .reset_index()
    )
    agrupado["Edad Promedio"] = agrupado["EDAD_PONDERADA"] / agrupado["PONDERA"]

    nombres_aglos = []
    for aglomerado in agrupado["AGLOMERADO"]:
        codigo_str = f"{int(aglomerado):02}"  # lo pasamos a formato 0numero
        nombre_aglo = aglomerados_info.get(codigo_str, {}).get(
            "nombre", f"Aglomerado {codigo_str}"
        )
        nombres_aglos.append(nombre_aglo)
    agrupado["AGLOMERADO"] = nombres_aglos

    dataF = agrupado[["AGLOMERADO", "Edad Promedio"]].set_index("AGLOMERADO")
    return dataF


def dependencia_demograﬁca(datos, aglomerado):

    aglo_datos = datos[
        datos["AGLOMERADO"] == int(aglomerado)
    ].copy()  # se mascarea y guarda los datos con aglomerado q quiero

    if aglo_datos.empty:
        return None

    aglo_datos = aglo_datos[aglo_datos["CH06"] >= 0]
    aglo_datos["Laburante"] = aglo_datos["CH06"].between(15, 64)  # columna de booleanos

    # multiplica por true o false (1 o 0)
    aglo_datos["cantDependiente"] = (~aglo_datos["Laburante"]) * aglo_datos["PONDERA"]
    aglo_datos["cantLaburante"] = aglo_datos["Laburante"] * aglo_datos["PONDERA"]

    estadisticas = (
        aglo_datos.groupby(["ANO4", "TRIMESTRE"])[["cantDependiente", "cantLaburante"]]
        .sum()
        .reset_index()
    )
    estadisticas = estadisticas[estadisticas["cantLaburante"] > 0]  # divisision por 0
    estadisticas["Porcentaje"] = (
        estadisticas["cantDependiente"] / estadisticas["cantLaburante"]
    ) * 100  # porcentajeamos

    return estadisticas[["ANO4", "TRIMESTRE", "Porcentaje"]]


def get_media_mediana_opti(datos):

    dataF = datos[datos["CH06"] >= 0].copy()

    # Media ponderada por año y trimestre
    dataF["cantEdad"] = dataF["CH06"] * dataF["PONDERA"]
    media_df = dataF.groupby(["ANO4", "TRIMESTRE"]).agg(
        {"cantEdad": "sum", "PONDERA": "sum"}
    )
    media_df["media"] = (media_df["cantEdad"] / media_df["PONDERA"]).round(2)
    media_df = media_df[["media"]].reset_index()

    # Mediana ponderada
    estadisticas = []

    for (anoAct, trimAct), grupo in dataF.groupby(["ANO4", "TRIMESTRE"]):
        grupo_ordenado = grupo.sort_values("CH06")
        grupo_ordenado["acumulado"] = grupo_ordenado["PONDERA"].cumsum()
        total = grupo_ordenado["PONDERA"].sum()
        mitad = total / 2

        mediana_row = grupo_ordenado[grupo_ordenado["acumulado"] >= mitad].iloc[0]
        mediana = mediana_row["CH06"]

        estadisticas.append({"ANO4": anoAct, "TRIMESTRE": trimAct, "mediana": mediana})

    mediana_df = pd.DataFrame(estadisticas)

    estadisticas_por_ano = pd.merge(
        media_df, mediana_df, on=["ANO4", "TRIMESTRE"]
    )  # fusionamos Meida y Mediana

    estadisticas_por_ano_bonito = estadisticas_por_ano.pivot(
        index="ANO4", columns="TRIMESTRE"
    )  # dejo el diccionario bonito pa estrimlit

    estadisticas_por_ano_bonito = estadisticas_por_ano_bonito.reset_index().rename(
        columns={"ANO4": "Año"}
    )

    return estadisticas_por_ano_bonito


# ------------P4
# path_hogares = Path(DATA_OUT_PATH /'hogares.csv' )


def filtrar_anio_trimestre(df, filtrado="ANO4", selec=100):
    """Filtra de la encuesta de hogares/individual el parametro de anio/trimestre.

    Args:
        df (DataFrame): DataFrame de personas o viviendas (EPH individual o hogares).
        filtrado (str, optional): Columna por la cual se desea filtrar, como 'ANO4' o 'TRIMESTRE'. Por defecto es 'ANO4'
        selec (int, list, optional): Valor único o lista de valores a filtrar. Si se pasa 100 (por defecto), no se aplica ningún filtro.
    Returns:
        df (DataFrame): anio/trimestre resultado de la filtracion
    """

    if selec == 100:
        return df
    elif isinstance(selec, list):
        return df[df[filtrado].isin(selec)]
    else:
        return df[df[filtrado] == selec]

    # 1.4.1


def procesar_datos__1_4_1(df_filtrado):
    """Genera una salida con la cantidad de viviendas para incluidas
    en la encuesta para un anio seleccionado / todos los anios disponibles

    Args:
        df_filtrado (DataFrame): DataFrame filtrado por el/los anio/anios de interés
    """
    st.subheader("1.4.1 Cantidad total de viviendas")
    total_viviendas = 0
    tot_prueba = 0
    for inte in df_filtrado["PONDERA"]:
        tot_prueba += inte
    total_viviendas = df_filtrado["PONDERA"].sum()
    print(f"Prueba de valores {tot_prueba}")
    st.metric(label="Total viviendas", value=total_viviendas)


# 1.4.2
# IV1
# Tipo de vivienda (por observación)
# 1 = Casa
# 2 = Departamento
# 3 = Pieza en inquilinato
# 4 = Pieza en hotel/pensión
# 5 = Local no construido para habitación
def procesar_datos__1_4_2(df_filtrado):
    """
    Cuenta la proporción de viviendas según su tipo,
    generando un gráfico en forma de torta con los respectivos valores.

    Args:
        df_filtrado (DataFrame): DataFrame filtrado por el/los anios seleccionados.
    """
    st.subheader("1.4.2 Proporción según tipo de vivienda")

    tipo_counts = df_filtrado["IV1"].value_counts().reset_index()
    tipo_counts.columns = ["tipo", "cantidad"]

    etiquetas = {
        1: "Casa",
        2: "Departamento",
        3: "Pieza en inquilinato",
        4: "Pieza en hotel/pensión",
        5: "Local no contruido para habitacion",
    }

    tipo_counts["tipo"] = tipo_counts["tipo"].map(etiquetas).fillna("Otro")
    fig = px.pie(tipo_counts, names="tipo", values="cantidad", title="Tipo de vivienda")
    st.plotly_chart(fig)


# 1.4.3
# IV3
# ¿Los pisos interiores son principalmente de...
# 1 = ...mosaico/baldosa/madera/cerámica/alfombra
# 2 = ...cemento/ladrillo fijo?
# 3 = ...ladrillo suelto/tierra?
def procesar_datos__1_4_3(df_filtrado):
    """Clasifica, por aglomerado, según el material predominante
    de las viviendas.

    Args:
        df_filtrado (DataFrame): DataFrame filtrado por el/los anios seleccionados.
    """
    st.subheader("1.4.3 Material predominante de pisos por aglomerado")

    # Toma el material mas comun entre todos por cada aglomerado
    predominante = df_filtrado.groupby("AGLOMERADO")["IV3"].agg(lambda x: x.mode()[0])

    df_predominante = predominante.reset_index()
    df_predominante.columns = ["AGLOMERADO", "Material Predominante"]

    material = {
        1: "Mosaico/Baldosa/Madera/Cerámica/Alfombra",
        2: "Cemento/Ladrillo fijo",
        3: "Ladrillo suelto/Tierra",
    }

    # Con el siguiente código se puede verificar que el material predominante por aglomerado es siempre el 1
    # for aglo in df_filtrado['AGLOMERADO'].unique():
    #    st.write(f"Aglomerado {aglo}")
    #    st.write(df_filtrado[df_filtrado['AGLOMERADO'] == aglo]['IV3'].value_counts())

    # aplicamos un mapeo para reemplazar el codigo por el nombre de aglomerado
    df_predominante["AGLOMERADO"] = (
        df_predominante["AGLOMERADO"].astype(str).str.zfill(2)
    )
    df_predominante["AGLOMERADO"] = df_predominante["AGLOMERADO"].map(dic_aglomerados)
    # volvemos a mapear para realizar lo mismo pero acorde al material
    df_predominante["Material Predominante"] = df_predominante[
        "Material Predominante"
    ].map(material)

    st.dataframe(df_predominante)


# 1.4.4
# IV8
# ¿Tiene baño/letrina?
# 1 = Sí
# 2 = No
def procesar_datos__1_4_4(df_filtrado):
    """Genera un gráfico de barras según la proporción de viviendas que disponen de baño dentro
    del hogar.

    Args:
        df_filtrado (DataFrame): DataFrame filtrado por el/los anios seleccionados.
    """
    st.subheader("1.4.4 Proporción de viviendas con baño por aglomerado")
    proporciones = (
        df_filtrado.groupby("AGLOMERADO")["IV8"]
        .value_counts(normalize=True)
        .unstack()
        .fillna(0)
        * 100
    )

    proporciones = proporciones.rename(columns={1: "Con baño", 2: "Sin baño"})

    # Convertimos el índice a string, con ceros a la izquierda si es necesario
    proporciones.index = proporciones.index.astype(str).str.zfill(2)
    # Mapeamos con nombres de aglomerado
    proporciones.index = proporciones.index.map(dic_aglomerados)

    # Reset index para plotly
    proporciones = proporciones.reset_index().rename(
        columns={proporciones.index.name: "Aglomerado"}
    )

    fig = px.bar(
        proporciones,
        x=["Con baño", "Sin baño"],
        y="Aglomerado",
        title="Proporción de viviendas con y sin baño por aglomerado",
        labels={"value": "Porcentaje", "Aglomerado": "Aglomerado"},
        barmode="stack",
    )

    st.plotly_chart(fig, use_container_width=True)


# 1.4.5
# II7
# ¿Este hogar es...
# 1 = ...propietario de la vivienda y el terren o?
# 2 = ...propietario de la vivienda solamente?
# 3 = ...inquilino/arrendatario de la vivienda?
# 4 = ...ocupante por pago de impuestos/expensas?
# 5 = ...ocupante en relación de dependencia?
# 6 = ...ocupante gratuito (con permiso)?
# 7 = ...ocupante de hecho (sin permiso)?
# 8 = ...está en sucesión?
def procesar_datos__1_4_5(anno, aglomerado, tenencia, hogares):
    aglo = int(aglomerado)  # Por las dudas

    # Si anno es "Todos", no filtramos por año
    if anno == "Todos":
        if len(tenencia) == 0:
            filtrado = hogares[hogares["AGLOMERADO"] == aglo]
        else:
            filtrado = hogares[
                (hogares["AGLOMERADO"] == aglo) & (hogares["II7"].isin(tenencia))
            ]
    else:
        if len(tenencia) == 0:
            filtrado = hogares[
                (hogares["ANO4"] == anno) & (hogares["AGLOMERADO"] == aglo)
            ]
        else:
            filtrado = hogares[
                (hogares["ANO4"] == anno)
                & (hogares["AGLOMERADO"] == aglo)
                & (hogares["II7"].isin(tenencia))
            ]

    # Agrupamos por año y tipo de tenencia
    evolucion = filtrado.groupby(["ANO4", "II7"]).size().unstack(fill_value=0)
    return evolucion


# 1.4.6
# IV12_3
# ¿La vivienda está ubicada en villa de emergencia? (por observación)
# 1 = Sí
# 2 = No
def procesar_datos__1_4_6(df_filtrado):
    st.subheader("1.4.6 Viviendas en villas de emergencia por aglomerado")

    villa = df_filtrado[df_filtrado["IV12_3"] == 1]
    conteo_villa = villa.groupby("AGLOMERADO").size()
    total_por_aglo = df_filtrado.groupby("AGLOMERADO").size()
    porcentaje = (conteo_villa / total_por_aglo * 100).fillna(0)

    resultado = pd.DataFrame(
        {"Cantidad": conteo_villa, "Porcentaje": porcentaje}
    ).sort_values(by="Cantidad", ascending=False)

    st.dataframe(resultado)


# 1.4.7
def procesar_datos__1_4_7(df_filtrado):
    st.subheader("1.4.7 Condición de habitabilidad")
    cond_hab = df_filtrado.groupby(["AGLOMERADO", "CONDICION DE HABITALIDAD"])[
        "PONDERA"
    ].sum()
    totales = df_filtrado.groupby("AGLOMERADO")["PONDERA"].sum()
    totales.index.name = "AGLOMERADO"
    porcentajes = (cond_hab / totales).unstack().fillna(0) * 100

    with open("data_out/aglomerados_coordenadas.json", "r", encoding="utf-8") as f:
        aglo_info = json.load(f)

    nombres = {int(k): v.get("nombre", f"Aglomerado {k}") for k, v in aglo_info.items()}

    for i in porcentajes.index:
        nuevo_nombre = nombres.get(i, f"Aglomerado {i}")
        porcentajes.rename(index={i: nuevo_nombre}, inplace=True)
    porcentajes.index.name = "Aglomerado"

    st.table(porcentajes)

    # Exportar
    csv = porcentajes.to_csv().encode("utf-8")
    st.download_button(
        "📥 Descargar CSV",
        data=csv,
        file_name="habitabilidad_por_aglomerado.csv",
        mime="text/csv",
    )


# ------------P5


# ------------P6


# Funcion para el inciso 6.1
# CH12 niv edicacion, 1 hasta 9
def cant_per_nivel(individuos, anio):
    # Filtramos individuos por año y nivel educativo
    indiv_filtrados = individuos[individuos["ANO4"] == anio]
    indiv_filtrados = indiv_filtrados[indiv_filtrados["CH12"].isin(range(1, 10))]
    if indiv_filtrados.empty:
        df = pd.DataFrame({"Niveles": [], "Cantidad": []})
    else:
        # Si hay individuos, creamos un DataFrame con los niveles educativos y sus conteos
        df = pd.DataFrame(
            {
                "Niveles": [
                    "Jardín/preescolar",
                    "Primario",
                    "EGB",
                    "Secundario",
                    "Polimodal",
                    "Terciario",
                    "Universitario",
                    "Posgrado universitario",
                    "Educación especial (discapacidad)",
                ],
                "Cantidad": [
                    indiv_filtrados["CH12"].value_counts().get(i, 0)
                    for i in range(1, 10)
                ],
            }
        )
    return df


# Funciones para el inciso 6.2
# CH06 es años cumplidos. CH12 es nivel educacional.
def edad_a_rango(edad):
    """
    Convierte la edad en integer a un rango de edad en string.
       Parámetros:
           edad (int): Edad del individuo.
       Retorna:
           ret_str: String de rango de edad.
    """
    if edad < 20:
        ret_str = "No valido."
    elif edad >= 20 and edad < 30:
        ret_str = "Entre 20 a 30 años"
    elif edad >= 30 and edad < 40:
        ret_str = "Entre 30 a 40 años"
    elif edad >= 40 and edad < 50:
        ret_str = "Entre 40 a 50 años"
    elif edad >= 50 and edad <= 60:
        ret_str = "Entre 50 a 60 años"
    elif edad > 60:
        ret_str = "Mayores de 60 años"
    return ret_str


def conteo_por_rango(individuos, rangos):
    """
    Cuenta la cantidad de individuos en cada nivel educativo por rango de edad.
       Parámetros:
           individuos (DataFrame): DataFrame que contiene los datos de los individuos.
           rangos (list): Lista de rangos de edad para agrupar los datos.
       Retorna:
           conteo (dict): Diccionario con la cantidad de individuos por nivel educativo y rango de edad.
    """
    ind_edades = individuos.copy()
    # Se agarran todas las edades y se las convierte a string
    ind_edades["Edades por rango"] = individuos["CH06"].apply(edad_a_rango)
    # se inicia el diccionario de conteo
    conteo = {rango: {cat: 0 for cat in range(1, 10)} for rango in rangos}
    # se filtran los individuos por aquellos que estan dentro de los rangos de edad proveidos como parametro
    filtrado = ind_edades[ind_edades["Edades por rango"].isin(rangos)]
    # se agrupan los inviduos filtrads por nivel educativo
    agrupado = filtrado.groupby(["Edades por rango", "CH12"]).size()
    # se recorren los individuos agrupados, tomando la cantidad total y agregandola al conteo
    for (rango, categoria), cantidad in agrupado.items():
        if categoria in conteo[rango]:
            conteo[rango][categoria] = cantidad
    return conteo


def niv_mas_comun(individuos, rangos):
    """
    Calcula el nivel educativo más común de individuos por rango de edad.
       Parámetros:
           individuos (DataFrame): DataFrame que contiene los datos de los individuos.
           rangos (list): Lista de rangos de edad para agrupar los datos.
       Retorna:
           df_ret: Un DataFrame con los niveles educativos más comunes por rango de edad.
    """
    conteo = conteo_por_rango(individuos, rangos)
    resultado = {}
    for rango in rangos:
        if sum(conteo[rango].values()) > 0:
            mas_comun = max(conteo[rango], key=conteo[rango].get)
        else:
            mas_comun = None
        resultado[rango] = mas_comun
    df_ret = pd.DataFrame(
        [(rango, nivel) for rango, nivel in resultado.items()],
        columns=["Rango de edad", "Nivel educativo más común"],
    )
    df_ret.index.name = "Rango de edad"
    return df_ret


def csv_inc_4():
    """
    Utiliza la funcion de la parte B de la parte 1 'porc_dos_o_mas_uni' y lo retorna en un csv.
       Retorna:
           csv: Un DataFrame con los resultados de la funcion 'porc_dos_o_mas_uni'.
    """
    from .incisos_parte_B import porc_dos_o_mas_uni

    dict_result = porc_dos_o_mas_uni()
    df = pd.DataFrame(dict_result, columns=["Aglomerado", "Porcentaje"])
    return df.to_csv()


def lit_may_6(individuos):
    """
    Calcula el porcentaje de literacidad e iliteracidad de individuos mayores de 6 años por año.
       Parámetros:
           individuos (DataFrame): DataFrame que contiene los datos de los individuos.
       Retorna:
           df: Un DataFrame con los porcentajes de literacidad e iliteracidad por año.
    """
    # tomampos los individuos mayores de 6 años
    ind_may_6 = individuos[individuos["CH06"] > 6]
    # agrupamos por año
    ind_agrup = ind_may_6.groupby("ANO4")
    dict_por_an = {}
    for anio, grupo in ind_agrup:
        # Tomamos la cantidad de individuos totales
        tot_per_an = len(grupo)
        # Tomamos la cantidad de individuos que son literados
        tot_per_an_lye = len(grupo[grupo["CH09"] == 1])
        # Tomamos la cantidad de individuos que son no literados a partir de la cantidad total
        # y la cantidad de literados
        tot_per_an_nl = tot_per_an - tot_per_an_lye
        if tot_per_an > 0:
            # Convertimos los totales a porcentaje
            dict_por_an[anio] = {
                "Porcentaje de literacidad": (
                    (tot_per_an_lye / tot_per_an) * 100 if tot_per_an > 0 else 0
                ),
                "Porcentaje de iliteracidad": (
                    (tot_per_an_nl / tot_per_an) * 100 if tot_per_an > 0 else 0
                ),
            }
    # Creamos el dataframe de los resultados
    df = pd.DataFrame.from_dict(dict_por_an, orient="index").reset_index()
    # Renombramos las columnas
    df = df.rename(
        columns={
            "index": "Año",
            "Porcentaje de literacidad": "Porcentaje de literacidad",
            "Porcentaje de iliteracidad": "Porcentaje de iliteracidad",
        }
    )
    # Ordenamos por año
    df.sort_values(by="Año")
    return df


# ------------P7 Inputs by Spinelli Arcuri Robertino


def abrir_canasta():
    """
    Abre el archivo CSV con los valores de la canasta básica mensual desde el directorio de salida.

    Returns
    -------
    pandas.DataFrame
        DataFrame que contiene los valores históricos de la canasta básica alimentaria (CBA)
        y la canasta básica total (CBT) mensuales desde el año 2016.
    """
    path_canasta = Path(
        DATA_OUT_PATH
        / "valores-canasta-basica-alimentos-canasta-basica-total-mensual-2016.csv"
    )
    return pd.read_csv(path_canasta, sep=",", on_bad_lines="skip")


def filtrar_agrupar(hogares, anno, trimestre):
    """
    Filtra hogares del trimestre y año indicados, seleccionando solo hogares con 4 integrantes.
    Luego agrupa por hogar para sumar el ingreso total familiar (ITF).

    Parameters
    ----------
    hogares : pandas.DataFrame
        DataFrame con los datos de hogares, que incluye las columnas 'ANO4', 'TRIMESTRE',
        'II7', 'CODUSU', 'NRO_HOGAR' e 'ITF'.

    anno : int
        Año a filtrar.

    trimestre : int
        Trimestre a filtrar (1 a 4).

    Returns
    -------
    pandas.DataFrame
        DataFrame de hogares con 4 integrantes y su ingreso total agregado.
    """
    hogares_filtrados = hogares[
        (hogares["ANO4"] == anno) & (hogares["TRIMESTRE"] == trimestre)
    ]
    hogares_4 = hogares_filtrados[hogares_filtrados["II7"] == 4]
    ingresos = (
        hogares_4.groupby(["CODUSU", "NRO_HOGAR"])["ITF"]
        .sum()
        .reset_index(name="Ingreso")
    )
    return hogares_4.merge(ingresos, on=["CODUSU", "NRO_HOGAR"])


def clasificar(itf, cba_x4, cbt_x4):
    """
    Clasifica el estado económico de un hogar según su ingreso total familiar (ITF),
    comparándolo con los umbrales de pobreza e indigencia ajustados a un hogar de 4 personas.

    Parameters
    ----------
    itf : float
        Ingreso total familiar del hogar.

    cba_x4 : float
        Valor de la canasta básica alimentaria multiplicada por 4 integrantes.

    cbt_x4 : float
        Valor de la canasta básica total multiplicada por 4 integrantes.

    Returns
    -------
    str
        Una de las siguientes categorías: 'Indigente', 'Pobre', o 'No pobre'.
    """
    if itf < cba_x4:
        return "Indigente"
    elif itf < cbt_x4:
        return "Pobre"
    else:
        return "No pobre"


def calcular_estadisticas(df_hogares, anno, trimestre):
    """
    Calcula la cantidad y porcentaje de hogares en cada condición económica.

    Parameters
    ----------
    df_hogares : pandas.DataFrame
        DataFrame que debe contener una columna 'CONDICION' con las etiquetas
        'Indigente', 'Pobre' o 'No pobre' para cada hogar.

    anno : int
        Año del período analizado.

    trimestre : int
        Trimestre del período analizado.

    Returns
    -------
    pandas.DataFrame
        DataFrame con columnas 'CONDICION', 'Cantidad', 'Porcentaje', 'Año' y 'Trimestre'.
    """
    total = len(df_hogares)
    conteo = df_hogares["CONDICION"].value_counts()
    porcentajes = (conteo / total * 100).round(2)

    # Armamos un DataFrame para devolver
    resultados = pd.DataFrame(
        {
            "CONDICION": ["Indigente", "Pobre", "No pobre"],
            "Cantidad": [
                conteo.get("Indigente", 0),
                conteo.get("Pobre", 0),
                conteo.get("No pobre", 0),
            ],
            "Porcentaje": [
                porcentajes.get("Indigente", 0.0),
                porcentajes.get("Pobre", 0.0),
                porcentajes.get("No pobre", 0.0),
            ],
        }
    )

    resultados["Año"] = anno
    resultados["Trimestre"] = trimestre

    return resultados


def verificar_ingreso(hogares, anno, trimestre):
    """
    Verifica cuántos hogares de 4 integrantes se encuentran por debajo de la línea de indigencia,
    pobreza o fuera de ambas, para un año y trimestre específicos.

    Se basa en los valores mensuales de la canasta básica alimentaria (CBA) y total (CBT),
    calcula su promedio trimestral, y clasifica cada hogar en función de su ingreso total (ITF).

    Parameters
    ----------
    hogares : pandas.DataFrame
        DataFrame con datos de hogares, incluyendo columnas como 'ANO4', 'TRIMESTRE',
        'II7', 'ITF', 'CODUSU', y 'NRO_HOGAR'.

    anno : int
        Año a analizar.

    trimestre : int
        Trimestre a analizar (1 a 4).

    Returns
    -------
    pandas.DataFrame
        DataFrame con la cantidad y porcentaje de hogares en cada categoría económica,
        junto con el año y trimestre analizados.
    """
    canasta = abrir_canasta()
    df_hogares = filtrar_agrupar(hogares, anno, trimestre)

    # --- PROCESAR CANASTA BÁSICA ---
    # Filtramos solo los 3 meses del trimestre elegido
    meses_trimestre = {
        1: ["01", "02", "03"],
        2: ["04", "05", "06"],
        3: ["07", "08", "09"],
        4: ["10", "11", "12"],
    }
    meses = meses_trimestre[trimestre]
    fechas = [f"{anno}-{m}" for m in meses]

    canasta_trim = canasta[canasta["indice_tiempo"].str[:7].isin(fechas)]
    # Sacamos el promedio del trimestre
    cba_prom = canasta_trim["canasta_basica_alimentaria"].mean()
    cbt_prom = canasta_trim["canasta_basica_total"].mean()
    # --- DETERMINAR CONDICIÓN DE CADA HOGAR ---
    cba_x4 = cba_prom * 4
    cbt_x4 = cbt_prom * 4

    df_hogares["CONDICION"] = df_hogares["ITF"].apply(
        lambda itf: clasificar(itf, cba_x4, cbt_x4)
    )
    return calcular_estadisticas(df_hogares, anno, trimestre)


# ------------Metodo principal---------------------------------
# si no corre en windows comenten los 2 procesar e inicio 2
"""
def procesar_datos_h():
    datos_h = planilla('usu_hogar_')
    if datos_h is None:
        return None
    datos_h = material_techumbre(datos_h, None)
    datos_h = tipo_hogar(datos_h, None)
    datos_h = calcular_densidad_hogar(datos_h, None)
    datos_h = condicion_de_habitalidad(datos_h, None)
    return datos_h


def procesar_datos_i():
    datos_i = planilla('usu_individual_')
    if datos_i is None:
        return None
    datos_i = traducir_genero(datos_i, None)
    datos_i = traducir_nivel_ed(datos_i, None)
    datos_i = condicion_laboral(datos_i, None)
    datos_i = Columna_Universitario(datos_i, None)
    return datos_i

from concurrent.futures import ProcessPoolExecutor


def iniciar_2(path_hogares, path_individuos):
    with ProcessPoolExecutor() as executor:
        futuro_h = executor.submit(procesar_datos_h)
        futuro_i = executor.submit(procesar_datos_i)

        datos_h = futuro_h.result()
        datos_i = futuro_i.result()

    # Recién acá escribimos los CSV
    print("escribiendo...")
    if datos_h is not None:
        datos_h.to_csv(path_hogares, index=False, sep=';', encoding='utf-8')
    if datos_i is not None:
        datos_i.to_csv(path_individuos, index=False, sep=';', encoding='utf-8')

    return datos_h, datos_i


from concurrent.futures import ProcessPoolExecutor
import sys
import platform

def iniciar_2(path_hogares, path_individuos):
    def _procesar():
        from src.utils.crearCSV import procesar_datos_h, procesar_datos_i  # importa dentro por multiproceso
        with ProcessPoolExecutor() as executor:
            futuro_h = executor.submit(procesar_datos_h)
            futuro_i = executor.submit(procesar_datos_i)

            datos_h = futuro_h.result()
            datos_i = futuro_i.result()

            # Recién acá escribimos los CSV
            print("escribiendo...")
            if datos_h is not None:
                datos_h.to_csv(path_hogares, index=False, sep=';', encoding='utf-8')
            if datos_i is not None:
                datos_i.to_csv(path_individuos, index=False, sep=';', encoding='utf-8')

            return datos_h, datos_i

    if platform.system() == "Windows":
        if __name__ == "__main__":
            return _procesar()
    else:
        return _procesar()
"""


def iniciar(path_hogares, path_individuos):
    """
    Procesa y guarda los datasets de hogares e individuos aplicando transformaciones y traducciones.

    Carga los datos brutos desde archivos TXT, aplica funciones de limpieza y transformación
    específicas para cada dataset, y guarda los resultados como archivos CSV.

    Parameters
    ----------
    path_hogares : pathlib.Path
        Ruta donde se guardará el archivo CSV procesado de hogares.

    path_individuos : pathlib.Path
        Ruta donde se guardará el archivo CSV procesado de individuos.

    Returns
    -------
    tuple
        Una tupla con dos elementos:
        - pandas.DataFrame: Datos procesados de hogares.
        - pandas.DataFrame: Datos procesados de individuos.
    """
    datos_h = planilla("usu_hogar_")
    datos_i = planilla("usu_individual_")
    if datos_h is not None:
        datos_h = material_techumbre(datos_h, path_hogares)
        datos_h = tipo_hogar(datos_h, path_hogares)
        datos_h = calcular_densidad_hogar(datos_h, path_hogares)
        datos_h = condicion_de_habitalidad(datos_h, path_hogares)
        datos_h.to_csv(path_hogares, index=False, sep=";", encoding="utf-8")
    if datos_i is not None:
        datos_i = traducir_genero(datos_i, path_individuos)
        datos_i = traducir_nivel_ed(datos_i, path_individuos)
        datos_i = condicion_laboral(datos_i, path_individuos)
        datos_i = Columna_Universitario(datos_i, path_individuos)
        datos_i.to_csv(path_individuos, index=False, sep=";", encoding="utf-8")
    return datos_h, datos_i


@st.cache_data
def principal():
    """
    Función principal para cargar, procesar y almacenar los datasets en caché y en el estado de sesión.

    Llama a `iniciar` para procesar los datos de hogares e individuos, guarda los resultados
    en archivos CSV, y almacena los DataFrames y los trimestres disponibles en `st.session_state`
    para su uso posterior en la aplicación de Streamlit. También mide y muestra el tiempo total de ejecución.

    Returns
    -------
    None
    """
    path_hogares = Path(DATA_OUT_PATH / "hogares.csv")
    path_individuos = Path(DATA_OUT_PATH / "individual.csv")
    start = time.perf_counter()
    datos_h, datos_i = iniciar(path_hogares, path_individuos)
    print("fin carga")
    end = time.perf_counter()
    print(f"Tiempo total: {end - start:.2f} segundos")
    # Guardar en session_state para que lo usen otras funciones
    st.session_state.fi, st.session_state.fd = obtener_trimestres_desde_csv(datos_i)
    st.session_state.datos_h = datos_h
    st.session_state.datos_i = datos_i


# -------------------------------Zona de pruebas
if __name__ == "__main__":
    path_hogares = Path(DATA_OUT_PATH / "hogares.csv")
    path_individuos = Path(DATA_OUT_PATH / "individual.csv")
    datos_h, datos_i = valido_error(path_hogares, path_individuos)
    if datos_h is not None and datos_i is not None:
        # ---Prueba P2 Cargar datos---------------------------
        son_iguales, mensaje = comparar(datos_h, datos_i)
        # print("¿Coinciden los trimestres?", son_iguales)
        # print("Mensaje:", mensaje)
    # -----------------------------------------------------
    # verificar_ingreso(datos_h,datos_i, 2024,2)

    # METODO GENERAL - Prueba filtrar anio/trimestre  ---------------------
    # filtrados= filtrar_anio_trimestre(datos_h, selec= 2023)

    # downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    # Nombre del archivo
    # archivo = os.path.join(downloads_path, "filtrado_completo.csv")
    # Guardar el DataFrame
    # filtrados.to_csv(archivo, index=False, sep=';')
    # print(f"Archivo guardado en: {archivo}")
    # Pruebas P3 ---------------------------------------------------------
    # poblacion_por_edad_sexo(2023,4)
    # promedio_edad_aglomerado(31)
    # Pruebas P4 ---------------------------------------------------------
    # procesar_datos__1_4_1(filtrados)
    # procesar_datos__1_4_2(filtrados)
    # procesar_datos__1_4_3(filtrados)
    # procesar_datos__1_4_4(filtrados)
    # procesar_datos__1_4_5(filtrados)
    # procesar_datos__1_4_6(filtrados)
    # procesar_datos__1_4_7(filtrados)

    # -----------------------------------------------------
    else:
        print("Error no hay datos o no exite un archivo")
