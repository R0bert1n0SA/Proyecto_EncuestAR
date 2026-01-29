from src.utils.constants import DATA_OUT_PATH
from src.utils.functions import *

# PARTE A


# INCISO 3 hecho por Franco Alconada
def traducir_genero():
    """A través del análisis de la columna CH04,
    clasifica en "Masculino" y "Femenino".
    SALIDA: nueva columna llamada CH04_str
    """
    file_name = DATA_OUT_PATH / "individual.csv"

    ch04 = get_column_info(file_name, "CH04")
    values = []

    for valor in ch04:
        if valor == "1":
            aux = "Masculino"
        elif valor == "2":
            aux = "Femenino"
        else:
            aux = "Sin información"
        values.append(aux)

    write_new_column_list(file_name, "CH04_str", values)


# INCISO 4
def traducir_nivel_ed():
    """Traduce los valores numéricos de la columna NIVEL_ED a
    formato texto.
    SALIDA: Salida: nueva columna llamada NIVEL_ED_str
    """
    file_name = DATA_OUT_PATH / "individual.csv"

    nivel_ed = get_column_info(file_name, "NIVEL_ED")
    values = []

    for valor in nivel_ed:
        if valor == "1":
            aux = "Primario incompleto"
        elif valor == "2":
            aux = "Primario completo"
        elif valor == "3":
            aux = "Secundario incompleto"
        elif valor == "4":
            aux = "Secundario completo"
        elif valor in ["5", "6"]:
            aux = "Superior o universitario"
        elif valor in ["7", "9"]:
            aux = "Sin informacion"
        else:
            aux = "Sin dato"
        values.append(aux)

    write_new_column_list(file_name, "NIVEL_ED_str", values)


# INCISO 5 ඞ (amongus)
def condicion_laboral():
    """Clasifica el estado laboral del individuo según el valor numérico
    de clasificacion en el archivo individuos.
    SALIDA: columna denominada CONDICION_LABORAL
    """

    file_name = DATA_OUT_PATH / "individual.csv"

    estado = get_column_info(file_name, "ESTADO")
    cat_ocup = get_column_info(file_name, "CAT_OCUP")
    values = []
    for i, j in zip(estado, cat_ocup):
        if int(i) == 1:
            if j in ["1", "2"]:
                aux = "Ocupado autónomo"
            elif j in ["3", "4", "9"]:
                aux = "Ocupado dependiente"
        elif int(i) == 2:
            aux = "Desocupado"
        elif int(i) == 3:
            aux = "Inactivo"
        else:  # usamos else para englobar tanto al Estado 4 como a otras variantes no consideradas
            aux = "Fuera de categoría/sin información"
        values.append(aux)

    write_new_column_list(file_name, "CONDICION_LABORAL", values)


# INCISO 6
def Columna_Universitario():
    """Método que indica si una persona mayor de edad
    ha completado, como mínimo, el Nivel Universitario.
    Salida: nueva columna llamada UNIVERSITARIO
    """
    archivo_salida = DATA_OUT_PATH / "individual.csv"

    columna_edad = get_column_info(archivo_salida, "CH04")
    columna_edu = get_column_info(archivo_salida, "NIVEL_ED")
    values = []

    for edad, nivel_ed in zip(columna_edad, columna_edu):
        if edad.isdigit() and nivel_ed.isdigit():
            if int(edad) < 18:
                values.append("2")
            elif int(nivel_ed) >= 6:
                values.append("1")
            else:
                values.append("0")

    write_new_column_list(archivo_salida, "UNIVERSITARIO", values)


# INCISO 7 uwu
def tipo_hogar():
    """Genera una nueva columna (TIPO_HOGAR) que clasifica el hogar
    según la cantidad de personas:
    -"Unipersonal" (una persona).
    -"Nuclear" (2 a 4 personas).
    -"Extendido" (5 o más personas).
    Salida: nueva columna TIPO_HOGAR
    """
    file_name = DATA_OUT_PATH / "hogares.csv"

    cant_habitantes = get_column_info(file_name, "IX_TOT")
    values = []

    for i in cant_habitantes:
        if int(i) == 1:
            values.append("Unipersonal")
        elif 2 <= int(i) <= 4:
            values.append("Nuclear")
        else:
            values.append("Extendido")

    write_new_column_list(file_name, "TIPO_HOGAR", values)


# INCISO 8
def material_techumbre():
    """Genera una columna que clasifica el tipo de hogar basado
    en la columna 'V4' (tipo de material)
    Salida: nueva columna MATERIAL_TECHUMBRE
    """
    file_name = DATA_OUT_PATH / "hogares.csv"

    column = get_column_info(file_name, "V4")
    values = []

    for item in column:

        if item in "1234":
            values.append("Material durable")
        elif item in "567":
            values.append("Material precario")
        else:  # line["IV4"] in "9":
            values.append("No aplica")

    write_new_column_list(file_name, "MATERIAL_TECHUMBRE", values)


# INCISO 9
def calcular_densidad_hogar():
    """Clasifica la densidad de hogar según la cantidad de personas
    por habitación.
    Salida: nueva columna llamada DENSIDAD_HOGAR
    """
    file_name = DATA_OUT_PATH / "hogares.csv"

    habitaciones = get_column_info(file_name, "IV2")
    personas = get_column_info(file_name, "IX_TOT")
    values = []

    for hab, per in zip(habitaciones, personas):
        try:
            hab = int(hab)
            per = int(per)

            densidad = per / hab if hab > 0 else per

            if densidad < 1:
                values.append("Bajo")
            elif densidad <= 2:
                values.append("Medio")
            else:
                values.append("Alto")
        except:
            values.append("N/D")

    write_new_column_list(file_name, "DENSIDAD_HOGAR", values)
    print("Columna 'DENSIDAD_HOGAR' añadida con éxito.")


# INCISO 10
def condicion_de_habitalidad():
    """Clasifica las viviendas según varias condiciones,
    como la accesibilidad al agua, la forma de extracción de la misma.
    Si poseen baño y dónde está ubicado; los materiales de la casa.
    Salida: nueva columna llamada CONDICION_DE_HABITALIDAD
    """

    criterios = [
        "Clasiﬁcan como CONDICION_DE_HABITABILIDAD buena si los pisos están hechos de mosaico o baldosa o madera o cerámica o alfombra, y el material de techumbre es un material durable; si tiene acceso al agua por cañerías dentro de la vivienda y la misma proviene de red pública; si efectivamente tiene baño y el mismo está ubicado dentro de la vivienda, y posee botón/mochila/cadena y arrastre de agua. Para clasificar, el desagüe del baño debe ser de red pública.",
        "Clasiﬁcan como CONDICION_DE_HABITABILIDAD saludable si los pisos interiores son de cemento o ladrillo fijo, y el material de techumbre es durable; si posee agua dentro de la vivienda y proviene de perforación con bomba a motor. Si posee baño dentro de la vivienda con arrastre de agua sin botón/cadena, o con un desagüe a cámara séptica y pozo ciego.",
        "Clasiﬁcan como CONDICION_DE_HABITABILIDAD regular si los pisos interiores están hechos de ladrillo suelto o tierra, o si el material de techumbre es un material precario; También clasifica si posee agua dentro del terreno pero fuera de la vivienda; si posee baño dentro del terreno pero fuera de la vivienda, y el mismo es por letrina, o el desagüe es a pozo ciego.",
        "Clasiﬁcan como CONDICION_DE_HABITABILIDAD insuﬁciente si los pisos interiores están hechos de ladrillo suelto o tierra, y el material de techumbre es un material precario; si no posee agua dentro del terreno, o su extracción es a través de la perforación con bomba manual / otra fuente. Si no posee baño, o el mismo está fuera del terreno, o el desagüe del baño es a hoyo/excavación en la tierra.",
    ]
    opt = int(
        input(
            "Ingrese 1 para ver los criterios de clasificación. Por favor, ingrese un numero: "
        )
    )
    if opt == 1:
        for elem in criterios:
            print(elem)

    file_name = DATA_OUT_PATH / "hogares.csv"

    filaIV6 = get_column_info(file_name, "IV6")
    filaIV7 = get_column_info(file_name, "IV7")
    filaIV8 = get_column_info(file_name, "IV8")
    filaIV9 = get_column_info(file_name, "IV9")
    filaIV10 = get_column_info(file_name, "IV10")
    filaIV11 = get_column_info(file_name, "IV11")
    filaIV3 = get_column_info(file_name, "IV3")
    filaIVMT = get_column_info(file_name, "MATERIAL_TECHUMBRE")

    values = []

    for iv6, iv7, iv8, iv9, iv10, iv11, iv3, mt in zip(
        filaIV6, filaIV7, filaIV8, filaIV9, filaIV10, filaIV11, filaIV3, filaIVMT
    ):
        # con este print se puede chequear los valores de cada fila
        # print(f'{mt}, iv6 = {iv6}, iv7 = {iv7}, iv8 = {iv8}, iv9 = {iv9}, iv10 = {iv10}, iv11 = {iv11}')

        if mt == "Material durable" and all(
            x == "1" for x in [iv3, iv6, iv7, iv8, iv9, iv10, iv11]
        ):
            values.append("buena")
        elif (
            mt == "Material durable"
            and any(x == "2" for x in [iv3, iv7, iv10, iv11])
            and all(x == "1" for x in [iv6, iv8, iv9])
        ):
            values.append("saludable")
        elif (
            mt == "Material precario"
            and iv8 == "1"
            and any(x == "3" for x in [iv3, iv10, iv11])
            and any(x == "2" for x in [iv6, iv9])
        ):
            values.append("regular")
        else:
            values.append("insuficiente")

    write_new_column_list(file_name, "CONDICION DE HABITALIDAD", values)
    print("Columna añadida!")
