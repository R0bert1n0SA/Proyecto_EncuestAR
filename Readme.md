# Miembros: 
# .Spinelli Arcuri Robertino
# .Manuel Vazquez
# .Vera Tellez Guillermo Nahuel
# .Natalia María Gentili
# .Franco Alconada

### Proyecto EncuestAR

Este proyecto consta del desarrollo de una aplicación de búsqueda y visualización de
información relacionada a la Encuesta Permanente de Hogares (EPH). 
El desarrollo de este trabajo involucra el
análisis de los datos con los cuales se trabajarán, su limpieza y preparación necesaria y
finaliza con el desarrollo de una interfaz amigable con el usuario/a.
El proyecto se divide en dos etapas:
    ● **Primera Etapa**: se enfocarán en entender y limpiar los datos de la EPH.Se
trabaja con los archivos que contienen información sobre hogares e individuos,
se aplican filtros y preparan para su uso en la aplicación.
    ● **Segunda Etapa:** se diseñará la interfaz en Streamlit e integrarán los datos procesados.
Se crearán diferentes secciones para mostrar información sobre educación,
ocupación, vivienda y otros temas de interés.

## Requisitos

Para poder ejecutar el proyecto, necesitas tener Python 3.12.9 y las siguientes dependencias instaladas:

- **Jupyter Notebook**: Para ejecutar los notebooks de Python y ver los resultados.
- Si instalas las dependencias desde el archivo `requirements.txt`, podrás asegurarte de que todas las bibliotecas necesarias estén instaladas.


### Instalación de Dependencias

Para instalar las dependencias necesarias para ejecutar el proyecto, ejecuta el siguiente comando:
```bash
pip install -r requirements.txt
```

## Ejecución del Proyecto

1. **Ejecutar el notebook:**

Abre el archivo .ipynb en la carpeta notebooks/ con el siguiente comando:

```bash
jupyter notebook
```


Esto abrirá Jupyter en tu navegador, donde podrás ejecutar las celdas de código en el notebook correspondiente.tambien puedes correrlas en el IDE


2. **Ejecutar el streamlit:**

Abre el archivo .ipynb en la carpeta notebooks/ con el siguiente comando:

```bash
streamlit run app/main.py
```

Esto abrirá streamlit en tu navegador.
