import numpy as np

def resolver_ec_lineales(A, b):
    #return np.linalg.solve(A, b)
    return cramer(A, b)

def cramer(A, b):
    detA = determinante(A)
    if detA < 1e-16:
        raise ValueError("El sistema de ecuaciones lineales no tiene solución")
    resultado = []
    for i in range(A.shape[0]):
        Ab = A.copy()
        Ab[:, i] = b
        resultado.append(determinante(Ab) / detA)
    return np.array(resultado)

def determinante(matriz):
    if not isinstance(matriz, np.ndarray):
        raise TypeError("'matriz' no es un ndarray de numpy")
    if matriz.size == 0:
        raise TypeError("'matriz' no tiene elementos")
    if matriz.ndim != 2:
        raise TypeError("'matriz' no es una matriz (2D)")
    if matriz.shape[0] != matriz.shape[1]:
        raise TypeError("la matriz no es cuadrada")
    return determinante_rec(matriz)

def determinante_rec(matriz, i_fila=0, columnas_excluidas=[]):
    if i_fila < matriz.shape[0] - 1:
        negativo = False
        resultado = 0
        for j in range(matriz.shape[0]):
            if j in columnas_excluidas:
                continue
            columnas_excluidas.append(j)
            factor = matriz[i_fila, j] * determinante_rec(matriz, i_fila + 1)
            columnas_excluidas.pop()
            if negativo:
                resultado -= factor
            else:
                resultado += factor
            negativo = not negativo
        return resultado
    else:
        for j in range(matriz.shape[0]):
            if j not in columnas_excluidas:
                return matriz[i_fila][j]
        raise RuntimeError("esto no debería pasar")

