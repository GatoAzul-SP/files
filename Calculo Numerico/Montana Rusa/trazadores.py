import numpy as np

def generar_trazador_cubico(valores_x, valores_y, frontera=None):
    """Genera un trazador cúbico a partir de los puntos con las coordenadas dadas.

    La frontera debe ser None para un trazador natural, o un número para
    un trazador cuyas primeras derivadas en los extremos sean el número dado.

    Devuelve una matriz numpy.ndarray que contiene cuatro coeficientes
    por cada polinimio generado, ordenado crecientemente."""

    cant_puntos = len(valores_x)
    if cant_puntos != len(valores_y):
        raise ValueError(
            "La cantidad de coordenadas x e y deben ser iguales")

    # Sistema de ecuaciones lineales de 4n-4 incognitas/ecuaciones
    # para n puntos
    n = 4*cant_puntos - 4
    A = np.zeros((n, n))  # Matriz de coeficientes
    b = np.zeros(n)       # Vector de términos independientes
    del n

    # Los segmentos deben coincidir con los puntos en los valores que toman
    # Si(x[i]) = y[i] & Si(x[i+1]) = y[i+1]
    # Si(x) = ai + bi*x + ci*x**2 + di*x**3
    # 2(n - 1) = 2n - 2 ecuaciones
    i_0 = 0  # Guardar indice inicial en A para el siguiente ciclo
    for i in range(cant_puntos - 1):
        x_izq = valores_x[i]
        x_der = valores_x[i + 1]
        # En filas pares, Si en límite izquierdo; en impares, en límite derecho
        i2 = i * 2;  i4 = i * 4
        x = 1
        for j in range(4):
            A[i2, i4 + j] = x
            x *= x_izq
        b[i2] = valores_y[i]
        x = 1
        for j in range(4):
            A[i2 + 1, i4 + j] = x
            x *= x_der
        b[i2 + 1] = valores_y[i + 1]
        i_0 += 2
    # i_0 == 2*cant_puntos - 2

    # Las primeras derivadas en los puntos interiores deben ser iguales
    # para los polinomios que los comparten
    # Si'(x[i+1]) = Si+1'(x[i+1]) => Si'(x[i+1]) - Si+1'(x[i+1]) = 0
    # Si'(x) = bi + 2ci*x + 3di*x**2
    # n - 2 ecuaciones
    for i in range(cant_puntos - 2):
        x_medio = valores_x[i + 1]
        i4 = i * 4;  i44 = i4 + 4   # Para Si y Si+1
        A[i_0, i4 + 1] = 1
        A[i_0, i44 + 1] = -1

        x = x_medio
        A[i_0, i4 + 2] = 2 * x
        A[i_0, i44 + 2] = -2 * x

        x *= x_medio
        A[i_0, i4 + 3] = 3 * x
        A[i_0, i44 + 3] = -3 * x
        i_0 += 1
    # i_0 == 3*cant_puntos - 4

    # Las segundas derivadas en los puntos interiores deben ser iguales
    # para los polinomios que los comparten
    # Si''(x[i+1]) = Si+1''(x[i+1]) => Si''(x[i+1]) - Si+1''(x[i+1]) = 0
    # Si''(x) = 2ci + 6di*x
    # n - 2 ecuaciones
    for i in range(cant_puntos - 2):
        x_medio = 6 * valores_x[i + 1]
        i4 = i * 4;  i44 = i4 + 4
        # for j in range(2, 4) -> iterar por 2 y 3
        A[i_0, i4 + 2] = 2
        A[i_0, i4 + 3] = x_medio
        A[i_0, i44 + 2] = -2
        A[i_0, i44 + 3] = -x_medio
        i_0 += 1
    # i_0 == 4*cant_puntos - 6

    if frontera is None:  # Trazador cúbico natural
        # Los polinomios en los extremos de la interpolante deben tener
        # segunda derivada igual a 0 en los extremos respectivos
        # S0''(x[0]) = Sn-1''(x[n]) = 0
        A[i_0, 2] = 2
        A[i_0, 3] = 6 * valores_x[0]
        i_0 += 1
        A[i_0, i_0 - 1] = 2
        A[i_0, i_0] = 6 * valores_x[cant_puntos - 1]
    else:  # Trazador cúbico sujeto
        # Los polinomios en los extremos de la interpolante deben tener
        # primera derivada igual a 'frontera' en los extremos respectivos
        # S0'(x[0]) = Sn-1'(x[n]) = 0
        x = valores_x[0]
        A[i_0, 1] = 1
        A[i_0, 2] = 2 * x
        A[i_0, 3] = 3 * x**2
        i_0 += 1
        x = valores_x[cant_puntos - 1]
        A[i_0, i_0 - 2] = 1
        A[i_0, i_0 - 1] = 2 * x
        A[i_0, i_0] = 3 * x**2

    # ¿Depuración?
    i_0 += 1
    if not i_0 == 4*cant_puntos - 4:
        raise Exception("Esto no debería pasar: indices no coinciden: %s=%s"
                        % (i_0, 4*cant_puntos - 4) )

    return np.linalg.solve(A, b).reshape(-1, 4)

# Para la montaña rusa, la frontera probablemente debería ser 0, de modo que
# el tren parta y llegue con pendiente cero, al inicio y final del recorrido
def generar_trazador_cubico_sujeto(valores_x, valores_y):
    "Véase la documentación de generar_trazador_cubico"
    return generar_trazador_cubico(valores_x, valores_y, 0)

def generar_trazador_cubico_sujeto_funcional(valores_x, valores_y):
    coeficientes_polinomios = generar_trazador_cubico_sujeto(valores_x,
                                                             valores_y)
    def trazador(x):
        en_rango = False
        for i in range(len(valores_x) - 1):
            if valores_x[i] <= x < valores_x[i + 1]:
                en_rango = True
                break
        if not en_rango:
            if x != valores_x[-1]:
                raise ValueError("'%f' está fuera del dominio del trazador: [%f; %f]"
                                 % (x, valores_x[0], valores_x[-1]))
            #else:
            #    i = len(valores_x) - 2
        potencias = np.float64(
            [x**i for i in range(coeficientes_polinomios.shape[1])] )
        return np.dot(coeficientes_polinomios[i], potencias)

    return trazador

