from csv_es import *
from trazadores import *
from aproximantes import *
from sistema_ec_lineales import *
import matplotlib.pyplot as plt
import numpy as np

def graficar(puntos_x, puntos_y, muestras_x, muestras_y):
    plt.clf()
    plt.plot(puntos_x, puntos_y, "or", label="Puntos")
    plt.plot(muestras_x, muestras_y, "b", label="Función")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()
    plt.show()

def main():
    print("Presione 'Enter' para seleccionar el valor predefinido.\n")

    nombre_archivo = input(
        "Indique el nombre de archivo para los trazadores (trazador.csv): ")
    if nombre_archivo == "":
        nombre_archivo = "trazador.csv"

    try:
        puntos_x, puntos_y, muestras_x = puntos_desde_csv(nombre_archivo)
        trazador = generar_trazador_cubico_sujeto_funcional(puntos_x, puntos_y)
        muestras_y = np.array([trazador(x) for x in muestras_x])
    except (OSError, ValueError) as e:
        print(e.args[0], "Para reintentar este paso reinicie el programa\n",
              sep="\n")
    else:
        graficar(puntos_x, puntos_y, muestras_x, muestras_y)
        print()

    nombre_archivo = input(
        "Indique el nombre de archivo para los aproximantes (aproximante.csv): ")
    if nombre_archivo == "":
        nombre_archivo = "aproximante.csv"

    try:
        puntos_x, puntos_y, muestras_x = puntos_desde_csv(nombre_archivo)
        grado = len(puntos_x) - 1
        posible_grado = input("Indique el grado del polinomio aproximante"
                              " (presione 'Enter' para usar predefinido '%d'): "
                              % grado)
        if posible_grado != "":
            grado = int(posible_grado)
        aproximante = generar_polinomio_min_cuadrados_funcional(
            puntos_x, puntos_y, grado )
    except (OSError, ValueError) as e:
        print(e.args[0], "Para reintentar este paso reinicie el programa\n",
              sep="\n")
    else:
        muestras_y = np.array([aproximante(x) for x in muestras_x])
        graficar(puntos_x, puntos_y, muestras_x, muestras_y)
        print()

    nombre_archivo = input(
        "Indique el nombre de archivo para el sistema de ecuaciones lineales"
        " (sistema_ec_lineales.csv): ")
    if nombre_archivo == "":
        nombre_archivo = "sistema_ec_lineales.csv"

    try:
        coeficientes, terms_indep = sistema_ec_lineales_desde_csv(nombre_archivo)
        print("Solución:", resolver_ec_lineales(coeficientes, terms_indep))
        print()
    except (OSError, TypeError, ValueError) as e:
        print(e.args[0], "Para reintentar este paso reinicie el programa\n",
              sep="\n")

    input("Presione 'Enter' para continuar...")

