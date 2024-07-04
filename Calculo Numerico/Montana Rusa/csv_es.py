import csv
import numpy as np

def parametros_desde_csv(nombre_archivo):
    """Obtiene una tupla de tres vectores de numpy desde un archivo csv

    Dos vectores de igual longitud se leen del archivo 'csv' que corresponden
    a las coordenadas de 'x' e 'y' de una serie de puntos.
    Los puntos se ordenan automáticamente de manera creciente, y se genera
    un error si hay dos puntos repetidos.

    El tercer valor leído es una tupla de tres números que corresponden
    con dos valores extremos y una cuenta de valores de muestras 'x'
    para calcular las ordenadas respectivas de esos puntos para una función"""

    try:
        with open(nombre_archivo, newline="") as archivo:
            lector = iter(csv.reader(archivo))
            valores_x = [np.float64(x) for x in next(lector)]
            valores_y = [np.float64(x) for x in next(lector)]
            intervalo = next(lector)
    except OSError as e:
        raise type(e)("No se pudo leer el archivo") from e
    except StopIteration as e:
        raise ValueError("No hay suficientes datos en el archivo") from e

    if len(valores_x) != len(valores_y):
        raise ValueError("La cantidad de coordenadas 'x' e 'y' no coinciden")
    if len(intervalo) != 3:
        raise ValueError("El intervalo debe ser de tres valores")
    intervalo = (float(intervalo[0]), float(intervalo[1]), int(intervalo[2]))

    valores_x, valores_y = ordenar_por_iesimo((valores_x, valores_y), 0)
    anterior = np.float64("-inf")
    for valor in valores_x:
        if anterior == valor:
            raise ValueError("No puede haber puntos con la misma coordenada 'x'")
        anterior = valor

    return (valores_x, valores_y, np.linspace(*intervalo))

def ordenar_por_iesimo(secuencias, indice):
    """Ordena las secuencias tomando como referencia aquella en posición indice.

    Se ordena crecientemente la secuencia en la posición dada por indice;
    las demás secuencias se ordenan de forma tal que el i-ésimo elemento de
    cada secuencia se reubique en la misma posición que el i-ésimo elemento
    de la secuencia de referencia.
    """

    try:
        secuencias[indice]
    except IndexError:
        raise IndexError("Índice fuera de rango (0:%d): %d"
                         % (len(secuencias), indice))

    return tuple(np.array(secuencia) for secuencia in zip(
        * sorted(zip(*secuencias), key=(lambda tupla: tupla[indice]))  ))

    # Otra forma más complicada
    """
    referencia = secuencias[indice]
    largo = len(referencia)
    for i in range(1, largo):
        valores = tuple(secuencia[i] for secuencia in secuencias)
        comparado = valores[indice]
        for j in range(i - 1, 0, -1):
            if referencia[j] < comparado:
                j += 1
                break
            for secuencia in secuencias:
                secuencia[j + 1] = secuencia[j]
        for k, secuencia in enumerate(secuencias):
            secuencia[j] = valores[k]
    """
