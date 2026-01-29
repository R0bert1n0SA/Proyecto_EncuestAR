from src.utils.constants import DATA_OUT_PATH, dic_aglomerados
import csv

# import math - Nunca se utiliza este import.
from src.utils.functions import actualizar_anos, sumar_hogar

# PARTE B


# INCISO 1  ( =ω=)
def porcentaje_analfabetizacion():
    """
    Informa por cada año,el porcentaje de personas mayores a 6 años
    capaces e incapaces de leer y escribir.
    Returns:
        dict: porcentaje de personas inalfabetas de leer y escribir.
        dict: porcentaje de personas alfabetas de leer y escribir.
    """
    file_name = DATA_OUT_PATH / "individual.csv"

    anos = {}
    porcentajes = {}

    with open(file_name, mode="r", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")

        for row in reader:
            if row.get("TRIMESTRE") == "4":
                actualizar_anos(anos, row)

    for ano in anos:
        if anos[ano]["cant_total"] > 0:  # Revisamos division por 0
            porcentaje = (anos[ano]["cant_analfa"] / anos[ano]["cant_total"]) * 100
        else:
            porcentaje = 0
        porcentajes[ano] = porcentaje
    porcentaje2 = {}

    for key, value in porcentajes.items():
        porcentaje2[str(key)] = 100 - value

    return porcentajes, porcentaje2


# INCISO 2 hecho por Franco Alconada


def porcentaje_extranjeros_universitarios():
    """
    Solicita un año y trimestre, y calcula el porcentaje de personas no nacidas en Argentina
    que hayan cursado un nivel universitario o superior en ese período.

    Usa los campos:
    - CH15: Lugar de nacimiento (4 = país limítrofe, 5 = otro país)
    - NIVEL_ED: Nivel educativo (8 = Universitario, 9 = Posgrado)
    - ANO4 y TRIMESTRE: para filtrar por período

    Retorna:
        str: Mensaje indicando el porcentaje o una advertencia si no hay datos.
    """

    archivo_csv_i = DATA_OUT_PATH / "individual.csv"

    anio = int(input("Ingrese el año deseado: "))
    trimestre = int(input("Ingrese el trimestre deseado (1-4): "))

    total_extranjeros = 0
    extranjeros_con_universidad = 0

    with open(archivo_csv_i, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            if int(row["ANO4"]) == anio and int(row["TRIMESTRE"]) == trimestre:
                if row["CH15"] in ["4", "5"]:  # nacidos en país limítrofe u otro país
                    total_extranjeros += 1
                    if row["NIVEL_ED"] in ["6", "8"]:  # universitario o superior
                        extranjeros_con_universidad += 1

    if total_extranjeros == 0:
        return "No se encontraron personas extranjeras en ese período."

    porcentaje = (extranjeros_con_universidad / total_extranjeros) * 100

    return f"En {anio} T{trimestre}, el {porcentaje:.2f}% de las personas no nacidas en Argentina cursaron nivel universitario o superior."


# INCISO 3 hecho por Franco Alconada
def menor_desocupacion():
    """
    Recorre el archivo individual.csv y determina el año y trimestre con menor porcentaje de desocupación.

    Usa los campos:
    - ESTADO: condición de actividad (2 = desocupado)
    - PONDERA: factor de expansión
    - ANO4 y TRIMESTRE: para agrupar los datos por período

    Retorna:
        str: "mensaje con el año y trimestre con menor desocupación, y el porcentaje correspondiente.

    """

    archivo_csv = DATA_OUT_PATH / "individual.csv"
    desocupacion_por_periodo = {}

    with open(archivo_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            try:
                estado = int(row["ESTADO"])
                anio = row["ANO4"]
                trimestre = row["TRIMESTRE"]
                pondera = int(row["PONDERA"])
            except (ValueError, KeyError):
                continue

            clave = (anio, trimestre)
            if clave not in desocupacion_por_periodo:
                desocupacion_por_periodo[clave] = {"total": 0, "desocupados": 0}

            desocupacion_por_periodo[clave]["total"] += pondera
            if estado == 2:
                desocupacion_por_periodo[clave]["desocupados"] += pondera

    menor = None
    menor_porcentaje = 101  # mayor que cualquier porcentaje posible

    for (anio, trim), datos in desocupacion_por_periodo.items():
        if datos["total"] > 0:
            porcentaje = datos["desocupados"] / datos["total"] * 100
            if porcentaje < menor_porcentaje:
                menor_porcentaje = porcentaje
                menor = (anio, trim)

    if menor:
        return f" Menor desocupación: {menor[1]}/{menor[0]} con {menor_porcentaje:.2f}%"
    else:
        return " No se encontraron datos válidos."


def actualizar_tabla(tabla, row: dict):

    if int(row["CH06"]) < 18:  # veamos q sean mayores de edad
        return
    anoAct = row["ANO4"]
    trimestreAct = row["TRIMESTRE"]
    datosAct = {
        "primario incompleto": 0,
        "Primario completo": 0,
        "Secundario Incompleto": 0,
        "Secundario Completo": 0,
        "Superior o universitario": 0,
    }
    nivelAct = int(row["CH12"])
    Validacion_nivelAct = row["CH13"] == "1"  # si completo es true
    Pondera = int(row["PONDERA"])

    if nivelAct == 2:  # educacion primaria
        datosAct[
            "Primario completo" if Validacion_nivelAct else "primario incompleto"
        ] += Pondera  # si esta completo suma a ese sino al otro
    elif nivelAct == 3:  # EGB primaria y 2 de secundaria
        if Validacion_nivelAct:
            datosAct["Primario completo"] += Pondera
            datosAct["Secundario Incompleto"] += Pondera
        else:
            datosAct["primario incompleto"] += Pondera
    elif nivelAct in [4, 5]:  # Polimodal secundaria
        datosAct["Primario completo"] += Pondera
        datosAct[
            "Secundario Completo" if Validacion_nivelAct else "Secundario Incompleto"
        ] += Pondera
    elif nivelAct in [6, 7, 8]:
        datosAct["Primario completo"] += Pondera
        datosAct["Secundario Completo"] += Pondera
        datosAct["Superior o universitario"] += Pondera

    if anoAct in tabla:
        if trimestreAct in tabla[anoAct]:
            # act datos
            for key in datosAct:
                tabla[anoAct][trimestreAct][key] += datosAct[key]
        else:
            # crear dict del trimestre  inicializado con los datos conseguidos en esta row
            tabla[anoAct][trimestreAct] = datosAct
    else:
        # crear dic del ano con el trismestre act inicializado con los datos conseguidos en esta row
        tabla[anoAct] = {trimestreAct: datosAct}


# Implementacion inciso 4
# Hecho por: Manuel Vazquez
def porc_dos_o_mas_uni():
    """Ranking de los 5 aglomerados con mayor porcentaje de hogares con dos
    o más ocupantes con estudios universitarios o superiores ﬁnalizados.
    Información obtenida a partir del par de archivos más recientes.
    Returns:
        str: Top 5 aglomerados con mayor porcentaje de hogares con 2 o más universitarios
    """
    archivo_csv_h = DATA_OUT_PATH / "hogares.csv"
    archivo_csv_i = DATA_OUT_PATH / "individual.csv"
    hog_tot = {}
    hog_univ = {}
    with open(archivo_csv_h, mode="r") as file_h:
        reader_h = list(csv.DictReader(file_h, delimiter=";"))
        may_anio = max(int(row["ANO4"]) for row in reader_h)
        may_trim = max(
            int(row["TRIMESTRE"]) for row in reader_h if int(row["ANO4"]) == may_anio
        )
        # se toman el mayor año y trimestre
        h_filtered = [
            row
            for row in reader_h
            if int(row["ANO4"]) == may_anio and int(row["TRIMESTRE"]) == may_trim
        ]
        # Se filtran los hogares por año y trimestre
        with open(archivo_csv_i, mode="r") as file_i:
            ind_por_casa = {}
            # se crea un diccionario para guardar los individuos de cada hogar, distinguidos por la columna "COSDUSU"
            h_filter_ids = {row["CODUSU"] for row in h_filtered}
            # se crea un diccionario de codigos de hogar en base a los hogares filtrados
            for row in csv.DictReader(file_i, delimiter=";"):
                # se procesa el archivo de individuos
                cod_hogar = row["CODUSU"]
                if cod_hogar in h_filter_ids:
                    # ya que no nos interesa el resto de hogares, si el codigo de hogar del individuo no esta en el diccionario de hogares filtrados, no se procesa
                    if cod_hogar not in ind_por_casa:
                        # si no existe el codigo de hogar en el diccionario, se crea un registro dentro de este usando el codigo de hogar como key
                        ind_por_casa[cod_hogar] = []
                    ind_por_casa[cod_hogar].append(row)
                    # se agrega al individuo al diccionario, dentro de la key de su hogar respectivo
            for row in h_filtered:
                # se comienzan a recorrer los hogares filtrados
                if int(row["IX_TOT"]) >= 2:
                    # si hay mas de 2 personas en el hogar, se revisa si hay 2 o mas universitarios
                    cod_hogar = row["CODUSU"]
                    tot_univ = 0
                    for row_i in ind_por_casa.get(cod_hogar, []):
                        if int(row_i["CH12"]) in (7, 8) and int(row_i["CH13"]) == 1:
                            tot_univ += 1
                    # se procesan todos los individuos del hogar usando el diccionario de individuos por hogar, y se suma a tot_univ si son universitarios que han finalizado sus estudios
                    if tot_univ >= 2:
                        sumar_hogar(hog_tot, hog_univ, row["AGLOMERADO"], True)
                        # si hay 2 o mas universitarios se suma al contados de hogares con universiarios
                    else:
                        sumar_hogar(hog_tot, hog_univ, row["AGLOMERADO"])
                else:
                    sumar_hogar(hog_tot, hog_univ, row["AGLOMERADO"])
                # si no, solo se suma al contador total
    hog_top = {}
    # se crea un diccionario con los porcentajes de hogares con 2 o mas universitarios por algomerado
    for key in hog_univ:
        hog_top[key] = (hog_univ[key] / hog_tot[key]) * 100
    # se filtran los 5 aglomerados con mayor porcentaje
    hog_top = sorted(hog_top.items(), key=lambda x: x[1], reverse=True)[:5]
    """
    ret_string = 'Top 5 aglomerados con mayor porcentaje de hogares con 2 o más universitarios:\n'
    for key in hog_top:
         ret_string += f'{key[0]}: {key[1]:.2f}%\n'
    #retorna un string para que se pueda implementar con notebook
    return ret_string     
    """
    # retorna un diccionario para implementar con streamlit
    return hog_top


# Implementacion inciso 5
# Hecho por: Manuel Vazquez
def porc_viv_propiet():
    """Informar para cada aglomerado el porcentaje de
    viviendas ocupadas por sus propietarios.
    Returns:
        str
    """
    archivo_csv_h = DATA_OUT_PATH / "hogares.csv"
    # se inician los diccionarios de total de hogares y hogares con propietario en ellas
    aglom_tot = {}
    aglom_con_propi = {}
    with open(archivo_csv_h, mode="r") as f:
        reader = csv.DictReader(f, delimiter=";")
        # se comienzan a leer las filas del archivo
        for row in reader:
            valor = row["AGLOMERADO"]
            # si el valor no existe en el diccionario total se agrega y inicializa el contador
            if valor not in aglom_tot:
                aglom_tot[valor] = 1
                # si el valor no existe en el diccionario de hogares con propietario se agrega y se inicalizan los contadores correspondientemente
                try:
                    # se utiliza try para evitar errores de conversion de string a int (particularmente porque pueden estar vacios si esta desfasado el archivo)
                    if int(row["II7"]) in (1, 2):
                        # si el hogar es ocupado por su propietario se inicializa en 1 al contador de hogares con propietario, si no, se inicializa en 0
                        aglom_con_propi[valor] = 1
                    else:
                        aglom_con_propi[valor] = 0
                except ValueError:
                    print(
                        f"El valor {row['II7']} de la fila {row} no se pudo convertir a entero"
                    )
                    print(
                        "Si uno de estos valores esta vacio, se deberia de revisar si el archivo csv tiene errores de formato."
                    )
            else:
                # si ya existe el valor se suma 1 al contador de total, y si el hogar es ocupado por su propietario se suma 1 al contador de hogares con propietario
                aglom_tot[valor] += 1
                try:
                    if int(row["II7"]) in (1, 2):
                        aglom_con_propi[valor] += 1
                except ValueError:
                    print(
                        f"El valor {row['II7']}, de la fila {row} no se pudo convertir a entero"
                    )
    str_retornable = ""
    for key in aglom_tot:
        # se calcula el porcentaje de hogares ocupados por su propietario en cada aglomerado
        porcent_value = (aglom_con_propi[key] / aglom_tot[key]) * 100
        str_retornable = (
            str_retornable
            + (
                f"El aglomerado {key} tiene un {porcent_value:.2f}% de hogares en los cuales viven sus propietarios."
            )
            + "\n"
        )
    # retorna un string para que se pueda implementar con streamlit
    return str_retornable


# Implementacion inciso 6
# Hecho por: Manuel Vazquez
def cont_aglo_tres_no_banio():
    """Informar el aglomerado con mayor cantidad de viviendas con más de dosocupantes y sin baño.
    Informar también la cantidad de ellas.
    """
    archivo_csv_h = DATA_OUT_PATH / "hogares.csv"
    # se inicia el diccionario de conteo por aglomerado
    cont_aglos = {}
    with open(archivo_csv_h, mode="r") as f:
        reader = csv.DictReader(f, delimiter=";")
        # se comienzan a leer las filas del archivo
        for row in reader:
            aglo = row["AGLOMERADO"]
            # si el aglomerado no existe en el diccionario se agrega y se inicializa el contador, correspondientemente a las condiciones
            if aglo not in cont_aglos:
                try:
                    # se utiliza try para evitar errores de conversion de string a int (particularmente porque pueden estar vacios si esta desfasado el archivo)
                    if int(row["IX_TOT"]) > 2 and int(row["IV8"]) == 2:
                        cont_aglos[aglo] = 1
                    else:
                        cont_aglos[aglo] = 0
                except ValueError:
                    print(
                        f'El valor "{row["IX_TOT"]}" o "{row["IV8"]}" de la fila {row} no se pudo convertir a entero'
                    )
                    print(
                        "Si uno de estos valores esta vacio, se deberia de revisar si el archivo csv tiene errores de formato."
                    )
            # si el aglomerado ya existe solo se revisa si el hogar cumple las condiciones y si fuera el caso se suma 1 al contador
            else:
                try:
                    if int(row["IX_TOT"]) > 2 and int(row["IV8"]) == 2:
                        cont_aglos[aglo] += 1
                except ValueError:
                    print(
                        f'El valor "{row["IX_TOT"]}" o "{row["IV8"]}" de la fila {row} no se pudo convertir a entero'
                    )
                    print(
                        "Si uno de estos valores esta vacio, se deberia de revisar si el archivo csv tiene errores de formato."
                    )
    top1 = sorted(cont_aglos.items(), key=lambda x: x[1], reverse=True)
    # retorna un string para que se pueda implementar con streamlit
    return f"El aglomerado con mas hogares de tres o mas personas sin baño es {top1[0][0]} con {top1[0][1]} hogares."


# Implementacion ej. 7
# Hecho por: Manuel Vazquez
def porc_niv_uni():
    """Informar para cada aglomerado el porcentaje de personas
    que hayan cursadode al menos en nivel universitario o superior.
    Returns:
        str
    """
    archivo_csv_i = DATA_OUT_PATH / "individual.csv"
    # se incializan los diccionarios de individuos totales y aquellos que hayan cursado nivel universiatario
    aglom_tot = {}
    aglom_univ = {}
    with open(archivo_csv_i, mode="r") as f:
        reader = csv.DictReader(f, delimiter=";")
        # se comienzan a leer las filas del archivo
        for row in reader:
            valor = row["AGLOMERADO"]
            # si el valor no existe en el diccionario total se agrega y se inicializa el contador
            if valor not in aglom_tot:
                aglom_tot[valor] = 1
                # si el valor no existe en el diccionario de individuos con nivel universitario se agrega y se inicaliza el contador correspondientemente
                if int(row["CH12"]) in (7, 8):
                    aglom_univ[valor] = 1
                else:
                    aglom_univ[valor] = 0
            # si ya existe el valor se suma 1 al contador de total, y si la persona tiene nivel universitario se suma 1 al contador de individuos con nivel universitario
            else:
                aglom_tot[valor] += 1
                if int(row["CH12"]) in (7, 8):
                    aglom_univ[valor] += 1
    str_retornable = ""
    for key in aglom_tot:
        # se calcula el porcentaje de individuos con nivel universitario en cada aglomerado
        porcent_value = (aglom_univ[key] / aglom_tot[key]) * 100
        str_retornable = (
            str_retornable
            + (
                f"El aglomerado {key} tiene un {porcent_value:.2f}% de individuos con nivel universitario."
            )
            + "\n"
        )

    return str_retornable


# inciso 8
def regiones_descendente():
    """Informar las regiones en orden descendente según el porcentaje de
    inquilinos de cada una.
    """
    archivo_salida = DATA_OUT_PATH / "hogares.csv"

    with open(archivo_salida, mode="r", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        filas = [row for row in reader if None not in row]

    regiones = {
        "1": ["Gran Buenos Aires", 0, 0],
        "40": ["NOROESTE", 0, 0],
        "41": ["NORESTE", 0, 0],
        "42": ["CUYO", 0, 0],
        "43": ["PAMPEANA", 0, 0],
        "44": ["PATAGONIA", 0, 0],
    }

    for fila in filas:
        # por cada fila
        region = fila.get("REGION", "")
        total_hogar = int(fila.get("IX_TOT") or 0)
        pondera = int(fila.get("PONDERA") or 0)
        es_inquilino = int(fila.get("II7") or 0) == 3

        total_personas_representadas = total_hogar * pondera
        if region in regiones:
            regiones[region][1] += total_personas_representadas
            if es_inquilino:
                regiones[region][2] += pondera
        else:
            print("Region desconocida")

            # Se puede controlar los valores de inquilinos con el siguiente codigo
            # reg = sorted(
            # regiones.items(),
            # key=lambda x: (x[1][2] / x[1][1]) if x[1][1] > 0 else 0,
            # reverse=True
            # )
            # for codigo, total in reg:
            #    print(f'Región {codigo:<4}: {total[0]:<19} | {total[2]:>8} personas representadas | {total[1]:>8} inquilinos')
    print()

    porcentaje_inquilinos = regiones = {
        "1": ["Gran Buenos Aires", ((regiones["1"][2] / regiones["1"][1]) * 100)],
        "40": ["NOROESTE", ((regiones["40"][2] / regiones["40"][1]) * 100)],
        "41": ["NORESTE", ((regiones["41"][2] / regiones["41"][1]) * 100)],
        "42": ["CUYO", ((regiones["42"][2] / regiones["42"][1]) * 100)],
        "43": ["PAMPEANA", ((regiones["43"][2] / regiones["43"][1]) * 100)],
        "44": ["PATAGONIA", ((regiones["44"][2] / regiones["44"][1]) * 100)],
    }

    reg = sorted(porcentaje_inquilinos.items(), key=lambda x: x[1][1], reverse=True)

    for codigo, total in reg:
        print(f"Región {codigo:<4}: {total[0]:>20} | {total[1]:>20}% de inquilinos ")


# INCISO 9   ಥ_ಥ
def nivel_educacion_tabla():
    """Pide al usuario que seleccione un aglomerado y a partir de la información contenida
    retornar una tabla que contenga la cantidad de personas mayores de edad según su nivel
    de estudios alcanzados.
    Returns
        Dict: aglomerados.
        Dict: tabla ordenada
    """
    archivo_salida = DATA_OUT_PATH / "individual.csv"

    tabla = {}
    print("Aglomerados: ")
    for i, j in dic_aglomerados.items():
        print(i + " = " + j)

    while True:
        try:
            aglomerado = int(input("Ingrese el numero del aglomerado a seleccionar "))
        except ValueError:
            print("Se ingreso un valor nulo")
        else:
            if (2 <= aglomerado <= 38) or (aglomerado in [91, 93]):
                break
            else:
                print("Numero fuera de rango ")
    with open(archivo_salida, "r") as f:
        d = csv.DictReader(f, delimiter=";")
        for row in d:
            if row["AGLOMERADO"] == str(aglomerado):
                actualizar_tabla(tabla, row)
    tabla_ordenada = {
        ano: dict(sorted(trimestre.items())) for ano, trimestre in sorted(tabla.items())
    }

    return dic_aglomerados[str(aglomerado)], tabla_ordenada


# inciso 10
def secundario_incompleto_may():
    """Pide al usuario que seleccione dos aglomerados y a partir de la información contenida...

    Returns:
        list[tuple]: una tabla que contenga el porcentaje de personas mayores de edad con secundario incompleto.
    """
    print("Aglomerados: ")
    for i, j in dic_aglomerados.items():
        print(i + " = " + j)

    while True:
        try:
            ag1 = int(input("Ingrese el primer código de aglomerado (entre 2 y 93): "))
            ag2 = int(input("Ingrese el segundo código de aglomerado (entre 2 y 93): "))
            if 2 <= ag1 <= 93 and 2 <= ag2 <= 93:
                break
            else:
                print("Ambos códigos deben estar entre 2 y 93.")
        except ValueError:
            print("Debe ingresar números válidos.")

    archivo_salida = DATA_OUT_PATH / "individual.csv"

    with open(archivo_salida, mode="r", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        filas = [row for row in reader if None not in row]

    datos = {}

    for fila in filas:
        anio = fila.get("ANO4") or ""
        trim = fila.get("TRIMESTRE") or ""
        clave = (anio, trim)

        if clave not in datos:
            datos[clave] = [0, 0, 0, 0, 0, 0]

        ch06 = int(fila.get("CH06") or 0)  # edad
        nivel_ed = int(fila.get("NIVEL_ED") or 0)
        # nivel_ed debe ser menor o igual a 3 ya que 4 es "Secundario completo" o 7 (sin instruccion).
        # Ns / Nr se contará aparte
        aglomerado = int(fila.get("AGLOMERADO", ""))
        pondera = int(fila.get("PONDERA") or 0)

        if aglomerado == ag1:
            datos[clave][4] += pondera
            if nivel_ed < 7:
                datos[clave][0] += pondera  # sec inc ag 1
            else:
                datos[clave][1] += pondera  # ns / nr ag1

        elif aglomerado == ag2:
            datos[clave][5] += pondera
            if ch06 > 17 and (nivel_ed < 4 or nivel_ed > 6):
                if nivel_ed < 7:
                    datos[clave][2] += pondera  # sec inc ag2
                else:
                    datos[clave][3] += pondera  # ns/ nc ag2

    for clave, elem in datos.items():
        try:
            datos[clave][0] = round((datos[clave][0] / datos[clave][4]) * 100)
            datos[clave][1] = round((datos[clave][1] / datos[clave][4]) * 100)
            datos[clave][2] = round((datos[clave][2] / datos[clave][5]) * 100)
            datos[clave][3] = round((datos[clave][3] / datos[clave][5]) * 100)
        except ZeroDivisionError:
            print(f"División por cero en clave {clave}")

    ordenar_tabla = sorted(datos.items())

    return ordenar_tabla


# Inciso 11


def porcentaje_techos_precarios(anio):
    """Pedir al usuario que seleccione un año, y busque en el último trimestre almacenado
    del mencionado año, el aglomerado con mayor porcentaje de viviendas de “Material precario” y el aglomerado con menor porcentaje de viviendas de “Material precario”.
    """
    archivo_csv = DATA_OUT_PATH / "hogares.csv"
    trimestre_final = {"2023": "4", "2024": "3"}
    trimestre = trimestre_final[str(anio)]
    with open(archivo_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        filas = [row for row in reader if None not in row]
    conteo = {}
    for fila in filas:
        fila_anio = fila.get("ANO4", "")
        fila_tri = fila.get("TRIMESTRE", "")
        aglo = fila.get("AGLOMERADO", "")
        techo = fila.get("Material techumbre", "").strip().lower()

        if fila_anio == str(anio) and fila_tri == trimestre and aglo:
            if aglo not in conteo:
                conteo[aglo] = [0, 0]  # [total_hogares, hogares_precarios]

            conteo[aglo][0] += 1
            if techo == "material precario":
                conteo[aglo][1] += 1

    porcentajes = []
    for aglo, (total, precarios) in conteo.items():
        porcentaje = (precarios / total) * 100 if total > 0 else 0
        porcentajes.append((aglo, porcentaje))

    if not porcentajes:
        return "No hay datos disponibles para ese año."

    aglo_mayor = max(porcentajes, key=lambda x: x[1])
    aglo_menor = min(porcentajes, key=lambda x: x[1])

    return {
        "mayor": {"aglomerado": aglo_mayor[0], "porcentaje": round(aglo_mayor[1], 2)},
        "menor": {"aglomerado": aglo_menor[0], "porcentaje": round(aglo_menor[1], 2)},
    }


# Inciso 12
# Manuel Vazquez
def det_porc_jub_habit():
    """A partir de la información del último trimestre almacenado en
    el sistema se debe retornar para cada aglomerado el porcentaje de jubilados
    que vivan en una vivienda con CONDICION_DE_HABITABILIDAD insuﬁciente.

    Returns:
        str
    """
    archivo_csv_h = DATA_OUT_PATH / "hogares.csv"
    archivo_csv_i = DATA_OUT_PATH / "individual.csv"
    hog_jub = {}
    hog_tot = {}
    with open(archivo_csv_h, mode="r") as f:
        reader_h = list(csv.DictReader(f, delimiter=";"))
        may_anio = max(int(row["ANO4"]) for row in reader_h)
        may_trim = max(
            int(row["TRIMESTRE"]) for row in reader_h if int(row["ANO4"]) == may_anio
        )
        h_filtered = [
            row
            for row in reader_h
            if int(row["ANO4"]) == may_anio and int(row["TRIMESTRE"]) == may_trim
        ]
        # se filtran los hogares por año y trimestre
        with open(archivo_csv_i, mode="r") as f_i:
            ind_por_casa = {}
            # se crea un diccionario para guardar los individuos de cada hogar, distinguidos por la columna "COSDUSU"
            h_filtered_ids = {row["CODUSU"] for row in h_filtered}
            # se crea un diccionario de codigos de hogar en base a los hogares filtrados
            for row in csv.DictReader(f_i, delimiter=";"):
                # Se procesa el archivo de individuos
                cod_hogar = row["CODUSU"]
                if cod_hogar in h_filtered_ids:
                    # ya que no nos interesa el resto de hogares, si el codigo de hogar del individuo no esta en el diccionario de hogares filtrados, no se procesa
                    if cod_hogar not in ind_por_casa:
                        ind_por_casa[cod_hogar] = []
                        # si no existe el codigo de hogar en el diccionario, se crea un registro dentro de este usando el codigo de hogar como key
                    ind_por_casa[cod_hogar].append(row)
                    # se agrega al individuo al diccionario, dentro de la key de su hogar respectivo
            # se comienzan a recorrer los hogares filtrados
            for row in h_filtered:
                aglo = row["AGLOMERADO"]
                # se revisa si el hogar tiene suficiente condicion de habitabilidad
                if row["CONDICION DE HABITALIDAD"] == "insuficiente":
                    cod_hogar = row["CODUSU"]
                    tiene_jub = False
                    # se revisa si el hogar contiene al menos un jubilado
                    for row_i in ind_por_casa.get(cod_hogar, []):
                        if row_i["CAT_INAC"] == "1":
                            tiene_jub = True
                    sumar_hogar(hog_tot, hog_jub, aglo, tiene_jub)
                    # se llama a sumar_hogar para sumar al contador de hogares totales y de jubilados, utilizando la variable tiene_jub para saber si el hogar tiene por lo minimo un jubilado
                else:
                    sumar_hogar(hog_tot, hog_jub, aglo)
                # si el hogar tiene suficiente condicion, simplemente se suma al contador de hogares totales
    str_retornable = ""
    for key in hog_tot:
        # se calcula el porcentaje de hogares con jubilados en cada aglomerado
        porcent_value = (hog_jub[key] / hog_tot[key]) * 100
        str_retornable = (
            str_retornable
            + (
                f"El aglomerado {key} tiene un {porcent_value}% de hogares con jubilados que viven en condiciones insuficientes."
            )
            + "\n"
        )

    return str_retornable


# INCISO 13 hecho por Franco Alconada
def universitarios_en_hogares_insuficientes():
    """
    Solicita un año al usuario y calcula cuántas personas con educación universitaria o superior
    viven en hogares con condición de habitabilidad 'insuficiente', en el cuarto trimestre del año.

    Cruza:
        - hogares.csv: para identificar hogares con CONDICION_DE_HABITALIDAD == 'insuficiente'
        - individual.csv: para contar personas con NIVEL_ED == 8 o 9 en esos hogares

    Devuelve:
        str: mensaje indicando la cantidad encontrada.

    """

    anio = input("Ingrese el año: ").strip()
    trimestre = "4"  # según consigna, usar siempre último trimestre

    # Cargar hogares con condición insuficiente
    hogares_path = DATA_OUT_PATH / "hogares.csv"
    hogares_insuficientes = set()

    with open(hogares_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            if row.get("ANO4") == anio and row.get("TRIMESTRE") == trimestre:
                if row.get("CONDICION_DE_HABITALIDAD", "").lower() == "insuficiente":
                    hogar_id = (row.get("CODUSU"), row.get("NRO_HOGAR"))
                    hogares_insuficientes.add(hogar_id)

    # Contar personas con nivel universitario que vivan en esos hogares
    individual_path = DATA_OUT_PATH / "individual.csv"
    contador = 0

    with open(individual_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            if row.get("ANO4") == anio and row.get("TRIMESTRE") == trimestre:
                hogar_id = (row.get("CODUSU"), row.get("NRO_HOGAR"))
                if hogar_id in hogares_insuficientes:
                    nivel_ed = int(row.get("NIVEL_ED", 0))
                    if nivel_ed in (6, 8):  # universitario o superior
                        contador += 1

    return f"En el {trimestre}° trimestre de {anio}, hay {contador} personas con nivel universitario o superior en hogares con condición de habitabilidad insuficiente."
