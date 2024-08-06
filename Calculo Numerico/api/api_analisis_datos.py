from analisis import *
import os
from base64 import b64encode

from fastapi import APIRouter, Body, Response, HTTPException
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/analisis")

DIR_TEMP = "temp"
RUTA_DATOS = DIR_TEMP + "/datos_viento.txt"
try:
    os.mkdir(DIR_TEMP)
except FileExistsError:
    pass
EXCEPCION_DATOS_MAL_FORMADOS = HTTPException(422, detail=
                        [{"msg": "Datos mal formados. Cárguelos nuevamente"}])

@router.put("/cargar-datos", status_code=204)
def cargar_datos(datos: str = Body()) -> None:
    archivo = open(RUTA_DATOS, "w")
    archivo.write(datos)
    archivo.flush()
    archivo.close()

@router.get("/dispersion-primeros-1000")
def dispersion_primeros_1000() -> Response:
    try:
        datos = leer_modelo(RUTA_DATOS)
    except ValueError:
        raise EXCEPCION_DATOS_MAL_FORMADOS
    imagen = graficar_dispersion_primeros_1000(datos)
    return Response(imagen, media_type="imagen/png")

@router.get("/dispersion-1000-mayor-rapidez")
def dispersion_1000_mayor_rapidez() -> Response:
    try:
        datos = leer_modelo(RUTA_DATOS)
    except ValueError:
        raise EXCEPCION_DATOS_MAL_FORMADOS
    imagen = graficar_dispersion_1000_mayor_rapidez(datos)
    return Response(imagen, media_type="imagen/png")

@router.get("/histograma-rapidez")
def histograma_rapidez() -> Response:
    try:
        datos = leer_modelo(RUTA_DATOS)
    except ValueError:
        raise EXCEPCION_DATOS_MAL_FORMADOS
    imagen = graficar_histograma_rapidez(datos)
    return Response(imagen, media_type="imagen/png")

@router.get("/rapidez_media_mensual")
def rapidez_media_mensual():
    try:
        datos = leer_modelo(RUTA_DATOS)
    except ValueError:
        raise EXCEPCION_DATOS_MAL_FORMADOS
    tabla, imagen = rapidez_media_mensual(datos)
    return {"tabla": tabla, "imagen": b64encode(imagen)}

@router.get("/tabla-rapidez-media-mensual", response_class=HTMLResponse)
def tabla_rapidez_media_mensual():
    try:
        datos = leer_modelo(RUTA_DATOS)
    except ValueError:
        raise EXCEPCION_DATOS_MAL_FORMADOS
    tabla = tabla_desde_historico(rapidez_media_mensual_aux(datos))
    return tabla

@router.get("/rapidez_media_mensual_anual")
def rapidez_media_mensual_anual():
    try:
        datos = leer_modelo(RUTA_DATOS)
    except ValueError:
        raise EXCEPCION_DATOS_MAL_FORMADOS
    imagen = graficar_historico_mensual(
        tabla_desde_historico_aux(rapidez_media_mensual_aux(datos)) )
    return Response(imagen, media_type="imagen/png")
