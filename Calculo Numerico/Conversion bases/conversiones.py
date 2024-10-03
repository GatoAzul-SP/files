import math, sys

def leer_float(numero):
    if not isinstance(numero, str):
        raise TypeError("'numero' debe ser de tipo 'str'")
    numero = numero.replace(",", ".").split(".")
    if len(numero) > 2:
        raise ValueError("No puede haber más de un separador decimal")
    elif len(numero) > 1:
        if len(numero[0]) == len(numero[1]) == 0:
            raise ValueError(
                "La parte entera y decimal no pueden ser ambas vacías")
    elif len(numero[0]) == 0:
        raise ValueError("No hay número a convertir")

    negativo = False
    if len(numero[0]) > 0 and numero[0][0] == "-":
        numero[0] = numero[0][1:]
        negativo = True
    entero = decimal = ""
    if len(numero) == 1:
        entero = numero[0]
    else:
        if len(numero[0]) > 0:
            entero = numero[0]
        if len(numero[1]) > 0:
            decimal = numero[1]
    entero, decimal = entero.lstrip("0"), decimal.rstrip("0")
    if entero == "":
        entero = "0"
    if decimal == "":
        decimal == "0"

    return entero, decimal, negativo

def entero_desde_base(base, entero, funcion):
    parte_entera = 0
    for digito in entero:
        parte_entera *= base
        parte_entera += funcion(digito)
    return parte_entera

def desde_base(base, entero, decimal, funcion, negativo=False):
    parte_entera = entero_desde_base(base, entero, funcion)

    parte_decimal = entero_desde_base(base, decimal, funcion)
    parte_decimal /= base ** len(decimal)

    numero = parte_entera + parte_decimal
    return -numero if negativo else numero

def desde_binario(numero):
    entero, decimal, negativo = leer_float(numero)
    if len(entero.strip("01") + decimal.strip("01")) > 0:
        raise ValueError(
            "El número contiene caracteres aparte de dígitos binarios")
    return desde_base(2, entero, decimal, int, negativo)

def desde_ternario(numero):
    entero, decimal, negativo = leer_float(numero)
    if len(entero.strip("012") + decimal.strip("012")) > 0:
        raise ValueError(
            "El número contiene caracteres aparte de dígitos ternarios")
    return desde_base(3, entero, decimal, int, negativo)

def desde_octal(numero):
    entero, decimal, negativo = leer_float(numero)
    if len((entero + decimal).strip("01234567")) > 0:
        raise ValueError(
            "El número contiene caracteres aparte de dígitos octales")
    return desde_base(8, entero, decimal, int, negativo)

def desde_digito_hexadecimal(digito):
    if digito in ("A", "B", "C", "D", "E", "F"):
        digito = ord(digito) - ord("A") + 10
    else:
        digito = int(digito)
    return digito

def desde_hexadecimal(numero):
    entero, decimal, negativo = leer_float(numero)
    entero, decimal = entero.upper(), decimal.upper()
    if len((entero + decimal).strip("0123456789ABCDEF")) > 0:
        raise ValueError(
            "El número contiene caracteres aparte de dígitos hexadecimales")
    return desde_base(16, entero, decimal, desde_digito_hexadecimal, negativo)

def partir_float(numero):
    negativo = numero < 0
    numero = abs(numero)
    entero = int(numero)
    decimal = numero - entero
    return entero, decimal, negativo

def entero_a_base_aux(base, entero, funcion):
    numero = []
    if entero == 0:
        return ["0"]
    while entero > 0:
        digito = entero % base
        entero //= base
        numero.append(funcion(digito))
    numero.reverse()
    return numero

try:
    ulp = math.ulp
except NameError:
    def ulp(x):
        exponente = math.frexp(x)[1] - 1
        return math.ldexp(sys.float_info.epsilon, exponente)

def contar_decimales(decimal, base):
    "Realmente cuenta la cantidad de digítos reservada por un float para"
    " sus decimales."
    exponente = -(math.frexp(ulp(decimal))[1] - 1)
    exponente /= math.log2(base)
    if math.ceil(exponente) != exponente:
        exponente -= ulp(exponente)
        exponente = math.ceil(exponente)
    return int(exponente)

def a_base(base, entero, decimal, funcion, negativo=False):
    numero = ["-"] if negativo else []

    if decimal > 0:
        cant_decimales = contar_decimales(decimal, base)
        decimal_ajustado = decimal + ulp(decimal)
        if decimal_ajustado >= 1:
            entero += 1
            decimal_ajustado -= 1
            decimal = round(decimal_ajustado, contar_decimales(decimal, 10) - 1)
        decimal *= base ** cant_decimales

    numero += entero_a_base_aux(base, entero, funcion)
    if decimal > 0:
        numero.append(".")
        parte_decimal = entero_a_base_aux(base, int(decimal), funcion)
        numero += ["0"] * (cant_decimales - len(parte_decimal))
        numero += parte_decimal

    numero = "".join(numero)
    if numero != "0" and decimal > 0:
        numero = numero.rstrip("0")
    return numero

def a_binario(numero):
    entero, decimal, negativo = partir_float(numero)
    return a_base(2, entero, decimal, str, negativo)

def a_ternario(numero):
    entero, decimal, negativo = partir_float(numero)
    return a_base(3, entero, decimal, str, negativo)

def a_octal(numero):
    entero, decimal, negativo = partir_float(numero)
    return a_base(8, entero, decimal, str, negativo)

def a_digito_hexadecimal(digito):
    if digito >= 10:
        digito = chr(digito - 10 + ord("A"))
    else:
        digito = str(digito)
    return digito

def a_hexadecimal(numero):
    entero, decimal, negativo = partir_float(numero)
    return a_base(16, entero, decimal, a_digito_hexadecimal, negativo)

funciones_desde = {2: desde_binario, 3: desde_ternario,
                   8: desde_octal, 16: desde_hexadecimal}
funciones_a = {2: a_binario, 3: a_ternario,
               8: a_octal, 16: a_hexadecimal}
def convertir(numero, desde, a):
    try:
        desde = funciones_desde[desde]
        a = funciones_a[a]
    except KeyError:
        raise ValueError("Tipo de conversión inválido") from None
    return a(desde(numero))
