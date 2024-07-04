import numpy as np
from sistema_ec_lineales import resolver_ec_lineales

def generar_polinomio_min_cuadrados(valores_x, valores_y, grado):
    """Genera un polinomio de ajuste por mínimos cuadrados."""
    cant_puntos = len(valores_x)
    if cant_puntos != len(valores_y):
        raise ValueError(
            "La cantidad de coordenadas x e y deben ser iguales")
    if grado < 0:
        raise ValueError("El grado debe ser 0 o mayor")
    if grado == 0:
        # Esto evita una validación abajo
        return np.array([valores_y.sum() / cant_puntos])

    potencias_x = valores_x.copy()
    sum_potencias_x = np.empty(2 * grado + 1)
    grado1 = grado + 1  # Será usado bastante
    # Sistema de ecuaciones lineales
    # A[i] = [sum(x**i), ..., sum(x**(i+grado))]
    A = np.empty((grado1, grado1))
    # b[i] = sum(x**i * y)
    b = np.empty(grado1)

    sum_potencias_x[0] = cant_puntos
    b[0] = valores_y.sum()
    for i in range(1, b.size):
        sum_potencias_x[i] = potencias_x.sum()
        b[i] = np.dot(potencias_x, valores_y)
        potencias_x *= valores_x
    for i in range(b.size, len(sum_potencias_x) - 1): # Evita el último producto
        sum_potencias_x[i] = potencias_x.sum()
        potencias_x *= valores_x
    sum_potencias_x[-1] = potencias_x.sum()

    for i in range(grado1):  # b.size == A.shape[0] == grado + 1
        A[i] = sum_potencias_x[i:i + grado1]

    #return np.linalg.solve(A, b)
    return resolver_ec_lineales(A, b)

def generar_polinomio_min_cuadrados_funcional(valores_x, valores_y, grado):
    coeficientes_polinomio = \
       generar_polinomio_min_cuadrados(valores_x, valores_y, grado)
    def aproximante(x):
        potencias = np.float64(
            [x**i for i in range(coeficientes_polinomio.size)] )
        return np.dot(coeficientes_polinomio, potencias)
    return aproximante
