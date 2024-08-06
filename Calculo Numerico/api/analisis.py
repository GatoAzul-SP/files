# Analisis de datos de viento
import os
from io import BytesIO
import pandas as pd
import matplotlib as mpl
import matplotlib.style
from matplotlib.figure import Figure

def graficar_dispersion_primeros_1000(modelo):
    imagen, grafico = crear_imagen_y_grafico()
    pd.plotting.scatter_matrix(modelo[:1000], ax=grafico)
    imagen.suptitle("Matriz de dispersion primeros 1000")
    return grafico_a_bytes(imagen)

def graficar_dispersion_1000_mayor_rapidez(modelo):
    imagen, grafico = crear_imagen_y_grafico()
    pd.plotting.scatter_matrix(modelo.nlargest(1000, "Rapidez (m/s)"),
                               ax=grafico)
    imagen.suptitle("Matriz de dispersion 1000 mayor rapidez")
    return grafico_a_bytes(imagen)

def graficar_histograma_rapidez(modelo):
    imagen, grafico = crear_imagen_y_grafico()
    modelo.plot.hist("Rapidez (m/s)", bins=36, alpha=0.75, edgecolor='black',
                     ax=grafico)
    grafico.set_xlabel("Rapidez (m/s)")
    grafico.set_ylabel("Frecuencia")
    grafico.set_title("Histograma de la rapidez del viento")
    return grafico_a_bytes(imagen)

def rapidez_media_mensual_aux(modelo):
    mensual = modelo["Rapidez (m/s)"].groupby([modelo.index.year,
                                              modelo.index.month]).mean()
    mensual.rename_axis(index=["Año", "Mes"], inplace=True)
    return mensual

def rapidez_media_mensual(modelo):
    mensual = rapidez_media_mensual_aux(modelo)

    tabla = mensual.to_frame("Rapidez media (m/s)").to_html()
    imagen, grafico = crear_imagen_y_grafico((15, 5))
    mensual.plot(ax=grafico)
    grafico.set_ylabel("Rapidez media (m/s)")
    grafico.set_title("Historico mensual de la rapidez media del viento")
    return tabla, grafico_a_bytes(imagen)

def tabla_desde_historico_aux(mensual):
    return mensual.unstack()

def tabla_desde_historico(mensual):
    return tabla_desde_historico_aux(mensual).to_html()

def graficar_historico_mensual(tabla_mensual):
    tabla_mensual = tabla_mensual.T

    imagen, grafico = crear_imagen_y_grafico((15, 5))
    tabla_mensual.plot(linewidth=1.5, ax=grafico)
    grafico.set_ylabel("Rapidez media (m/s)")
    grafico.legend(loc="upper right", ncol=8)
    grafico.set_title("Rapidez media mensual del viento por año")
    return grafico_a_bytes(imagen)

def leer_modelo(archivo):
    modelo = pd.read_csv(archivo, sep="\s+", skiprows=3,
                         usecols=["YYYYMMDD", "HHMM", "M(m/s)", "D(deg)"],
                         parse_dates={"Fecha": [0, 1]}, index_col="Fecha")
    modelo.rename(columns={"M(m/s)": "Rapidez (m/s)",
                           "D(deg)": "Direccion (grados)"},
                  inplace=True)
    return modelo

def crear_imagen_y_grafico(figsize=None):
    mpl.style.use("bmh")
    imagen = Figure() if figsize is None else Figure(figsize=figsize)
    grafico = imagen.add_subplot()
    return imagen, grafico

def grafico_a_bytes(imagen):
    salida = BytesIO()
    imagen.savefig(salida)
    datos = salida.getvalue()
    salida.close()
    return datos
