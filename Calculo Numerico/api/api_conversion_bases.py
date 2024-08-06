from conversiones import *

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

router = APIRouter(prefix="/conversion-bases")

@router.get("/", response_class=PlainTextResponse)
def convertir_numero(numero: str, desde: int, a: int):
    try:
        numero = convertir(numero, desde, a)
    except ValueError as e:
        raise HTTPException(422, detail=[{"msg": e.args[0]}])
    return numero
