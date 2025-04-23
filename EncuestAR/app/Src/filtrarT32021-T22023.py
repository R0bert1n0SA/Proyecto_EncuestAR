from pathlib import Path
import csv

# Constantes
RUTA_BASE = Path('EncuestAR')
RUTA_TXTS = RUTA_BASE / 'data' / 'Txts'
RUTA_SALIDA = RUTA_BASE / 'Archivos-Out'


#Funciones
def obtener_archivos(patrones, archivos):
    for patron in patrones:
        carpetas = RUTA_TXTS.glob(patron)
        for carpeta in carpetas:
            archivos.extend(carpeta.glob('*.txt'))

def filtrar(subarch_ind, subarch_hog, archivos):
    for a in archivos:
        if "individual" in a.name.lower():
            subarch_ind.append(a)
        if "hogar" in a.name.lower():
            subarch_hog.append(a)

def cargar_archs(arch_s, archs, head):
    # Guardar archivo CSV
    with arch_s.open('w') as salida:
        for dato in archs:
            with open(dato) as f:
                encabezado = f.readline()
                if not head:
                    salida.write(encabezado)
                    head = True
                for l in f:
                    salida.write(l)


#Variables
patrones = [
    'EPH_T3_2021_txt', 'EPH_T4_2021_txt',
    'EPH_T1_2022_txt', 'EPH_T2_2022_txt', 'EPH_T3_2022_txt', 'EPH_T4_2022_txt',
    'EPH_T1_2023_txt'
]
archivos = []
subarch_i = []
subarch_h = []
archivo_salida_i = RUTA_SALIDA / "Individual.csv"
archivo_salida_h = RUTA_SALIDA / "Hogar.csv"
head_i = False
head_h = False

#Llamada a funciones
obtener_archivos(patrones, archivos)
filtrar(subarch_i, subarch_h, archivos)
cargar_archs(archivo_salida_i, subarch_i, head_i)
cargar_archs(archivo_salida_h, subarch_h, head_h)







