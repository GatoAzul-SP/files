import sys
sys.path.append(sys.path[0] + "/../Montana Rusa")
import numpy as np
from csv_es import *
from trazadores import *
from aproximantes import *
from sistema_ec_lineales import *
from matplotlib.figure import Figure
from io import BytesIO

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Response, HTTPException
from api_gauss_seidel import SistemaEC

def graficar(puntos_x, puntos_y, muestras_x, muestras_y):
    imagen = Figure()
    grafico = imagen.add_subplot()
    grafico.plot(puntos_x, puntos_y, "or", label="Puntos")
    grafico.plot(muestras_x, muestras_y, "b", label="Función")
    grafico.xlabel("x")
    grafico.ylabel("y")
    grafico.legend()
    salida = BytesIO()
    imagen.savefig(salida)
    datos = salida.getvalue()
    salida.close()
    return datos

class Puntos(BaseModel):
    x: list[float]
    y: list[float]
    muestra_inicial: Optional[float] = None
    muestra_final: Optional[float] = None
    cant_muestras: Optional[int] = None

class PuntosAproximante(Puntos):
    grado: Optional[int] = None

def modelo_a_puntos(puntos):
    puntos_x = puntos["x"]
    puntos_y = puntos["y"]
    intervalo = [puntos["muestra_inicial"], puntos["muestra_final"],
                 puntos["cant_muestras"]]
    if intervalo[0] is None:
        intervalo[0] = puntos_x[0]
    if intervalo[1] is None:
        intervalo[1] = puntos_x[-1]
    if intervalo[2] is None:
        intervalo[2] = 100

    return leer_puntos(puntos_x, puntos_y, intervalo)

router = APIRouter()

@router.post("/trazador")
def trazador(puntos: Puntos) -> Response:
    puntos = puntos.dict()
    try:
        puntos_x, puntos_y, muestras_x = modelo_a_puntos(puntos)
        trazador = generar_trazador_cubico_sujeto_funcional(puntos_x, puntos_y)
        muestras_y = np.array([trazador(x) for x in muestras_x])
    except (ValueError, TypeError) as e:
        raise HTTPException(422, e.args[0])

    imagen = graficar(puntos_x, puntos_y, muestras_x, muestras_y)
    return Response(imagen, media_type="image/png")

@router.post("/aproximante")
def aproximante(puntos: PuntosAproximante) -> Response:
    puntos = puntos.dict()
    try:
        puntos_x, puntos_y, muestras_x = modelo_a_puntos(puntos)
        grado = puntos["grado"]
        if grado is None:
            grado = len(puntos_x) - 1
        aproximante = generar_polinomio_min_cuadrados_funcional(
            puntos_x, puntos_y, grado )
    except (ValueError, TypeError) as e:
        raise HTTPException(422, e.args[0])

    muestras_y = np.array([aproximante(x) for x in muestras_x])
    imagen = graficar(puntos_x, puntos_y, muestras_x, muestras_y)
    return Response(imagen, media_type="image/png")

@router.post("/sistema_ec_lineales")
def sistema_ec_lineales(sistema_ec: SistemaEC):
    sistema_ec = sistema_ec.dict()
    try:
        coeficientes, terms_indep = leer_sistema_ec_lineales(
            sistema_ec["coeficientes"], sistema_ec["terms_indep"])
        solucion = resolver_ec_lineales(coeficientes, terms_indep).tolist()
    except (ValueError, TypeError) as e:
        raise HTTPException(422, e.args[0])

    return {"solucion": solucion}
