from src.utils.constants import *
import csv


def obtener_trimestres_desde_csv():
    ruta_csv = DATA_OUT_PATH / "individual.csv"
    datos = []

    with open(ruta_csv, newline="", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo, delimiter=";")
        for fila in lector:
            anio = int(fila["ANO4"])
            trimestre = int(fila["TRIMESTRE"])
            datos.append((anio, trimestre))

    if not datos:
        return None, None

    # Obtener año más chico y más grande
    anos = [a for a, _ in datos]
    ano_min = min(anos)
    ano_max = max(anos)

    # Filtrar por año y sacar el trimestre mínimo/máximo
    trimestre_min = min([t for a, t in datos if a == ano_min])
    trimestre_max = max([t for a, t in datos if a == ano_max])

    return f"{trimestre_min}/{ano_min}", f"{trimestre_max}/{ano_max}"


def write_new_column(archivo_salida, filas, columns):
    """_summary_

    Args:
        archivo_salida (_type_): _description_
        filas (_type_): _description_
        columns (_type_): _description_
    """
    with archivo_salida.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, delimiter=";")
        writer.writeheader()
        writer.writerows(filas)
    print("Columna confirmada!")


def write_new_column_list(
    file_name, new_header, values
):  # cambiar file_name por archivo_salida
    """
    recibe nombre de archivo,nombre de nueva fila y una lista, y escribe en este el header y sus valores correspondientes
    """
    with open(file_name, mode="r", newline="") as f:
        reader = csv.reader(f, delimiter=";")

        # Headers mas el nuevo
        headers = next(reader)

        # veo si no existe ya
        if new_header in headers:
            print(f"La columna {new_header} ya existe")
        else:
            headers.append(new_header)

        # El resto de las filas
        # [[Dato_columna1_fila1,Dato_columna1_fila1...] ... [Dato_columna1_filaN,Dato_columna2_filaN...]]
        data = list(reader)

    with open(file_name, mode="w", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(headers)

        for row, value in zip(data, values):  # Recorre las filas y los nuevos valores
            row.append(value)  # Añadir el nuevo valor al final de la fila
            writer.writerow(row)  # Escribir la fila actualizada


def get_column_info(archivo_nombre: str, column_name: str):
    """
    recibe el nombre del archivo y del header y devuelve todos los datos
    de las celdas correspondientes en una lista
    """
    listaux = []

    with open(archivo_nombre, "r") as f:
        d = csv.DictReader(f, delimiter=";")

        # Verifica si la columna existe en el archivo
        if column_name not in d.fieldnames:  # lista de headers
            raise ValueError(
                f"La columna '{column_name}' no existe en el archivo '{archivo_nombre}'."
            )

        for row in d:  # cada row es un diccionario
            listaux.append(
                row[column_name]
            )  # deberia simplemente cambiar esto por row.get pa ahorrarme tanto quilombo?

    return listaux


def actualizar_anos(anos, row: dict):
    ano_act = row.get("ANO4")
    if ano_act in anos:  # actualizar key
        if int(row.get("CH06")) > 6:
            pondera = row.get("PONDERA")
            anos[ano_act]["cant_total"] += int(pondera)
            if row.get("CH09") != "1":
                anos[ano_act]["cant_analfa"] += int(pondera)
    else:  # añadir key
        anos[ano_act] = {"cant_total": 0, "cant_analfa": 0}


# Modulo extra para el funcionamiento del inciso 4 y 12
def sumar_hogar(hog_tot, hog_spec, valor_aglo, spec_state=False):
    if valor_aglo not in hog_tot:
        hog_spec[valor_aglo] = 0
        hog_tot[valor_aglo] = 0
    hog_tot[valor_aglo] += 1
    if spec_state:
        hog_spec[valor_aglo] += 1
    return
